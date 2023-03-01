import asyncio as aio
import os
import time
from collections.abc import MutableSet
from datetime import date
from io import SEEK_END, TextIOWrapper

from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C

import listeners
from screen import LCD_COLUMNS, open_screen
from ui import Frame, FrameController

"""
TODO:
1. Add the ability to export the user list at-will via developer provided callback
"""

def centered(text: str) -> str:
    return text.center(LCD_COLUMNS)

class PiBadger(FrameController):
    def __init__(self,
                 badge_id_file: TextIOWrapper,
                 event_loop: aio.AbstractEventLoop,
                 screen: Character_LCD_RGB_I2C):
        self.file = badge_id_file

        self.loop = event_loop
        self.loop.create_task(listeners.listen_buttons(screen, self.advance))
        self.loop.create_task(listeners.listen_keyboard(self._handle_badge_input))

        self.screen = screen
        self.screen.cursor = True
        self.screen.blink = True

        self.badges = self._read_existing_attendees()
        self.login_count = len(self.badges)

        starting_frame = self._build_frames()

        super().__init__(starting_frame)

    def start(self):
        self.render()
        self.loop.run_forever()

    def _handle_badge_input(self, badge_id) -> None:
        # Ensure that we show the "welcome" message every time a user badges
        self.restart()
        self.render(badge_id)
    
        if badge_id not in self.badges:
            self.badges.add(badge_id)
            self.login_count += 1

            self.file.write(f"{badge_id}\n")
            # Ensure the file is written in case of power loss or other interruption.
            self.file.flush()

    def _build_frames(self) -> "Frame":
        @Frame
        def main_frame(badge_id = ""):
            if badge_id:
                self.screen.clear()
                self.screen.message = f"Welcome:\n{centered(badge_id)}"
                time.sleep(1.5)
            self.screen.clear()
            self.screen.message = "Ready..."

        @Frame
        def total_attendees_frame():
            self.screen.clear()
            self.screen.message = f"Total guests:\n{centered(str(self.login_count))}"

        @Frame
        def shutdown_frame():
            self.screen.clear()
            self.screen.message = f"{centered('Shutdown?')}\n{centered('<- N | Y ->')}"

        @Frame
        def shutdown_for_sure_frame():
            self.screen.clear()
            self.screen.message = f"{centered('Are you certain?')}\n{centered('<- N | Y ->')}"

        @Frame
        def final_shutdown_frame():
            self.screen.clear()
            self.loop.stop()

        main_frame.add_neighbor("right_button", total_attendees_frame)
        total_attendees_frame.add_neighbor("left_button", main_frame)

        total_attendees_frame.add_neighbor("right_button", shutdown_frame)
        shutdown_frame.add_neighbor("left_button", total_attendees_frame)

        shutdown_frame.add_neighbor("right_button", shutdown_for_sure_frame)
        shutdown_for_sure_frame.add_neighbor("left_button", total_attendees_frame)

        shutdown_for_sure_frame.add_neighbor("right_button", final_shutdown_frame)
        # There is no return from this frame :)

        return main_frame

    def _read_existing_attendees(self) -> MutableSet[str]:
        badge_ids = set(line.strip() for line in self.file)
        # I'm unsure if this is absolutely necessary due to iterating the file already, but I didn't find a satisfying SO post to prove it.
        self.file.seek(0, SEEK_END)

        return badge_ids

"""
Why "a+"? Because file modes in python are a tad goofy imo.
* w+ will create the file and allow us to read and write to it, however it will 'truncate'/delete the contents of the file if it already exists. Not great.
* r+ will allow reads and writes, however it will not allow creation of the file. Also not ideal.
* a+ gives us reading, writing, *and* creation, however it places the seek postion at the end of the file. Certainly not perfect, but we can work around this.

One more alternative would involve opening the file twice, once with a/a+ to ensure existence of the file, and then again with r+ to perform reads/writes.
I chose to open the file only once since this alternative method feels a smidgen wonky to me.
"""
script_location = os.path.dirname(__file__)
badge_filename = os.path.join(script_location, f"../outputs/attendance_{date.today().isoformat()}")
with open_screen() as screen, open(badge_filename, mode="a+") as badge_file:
    badge_file.seek(0)
    loop = aio.get_event_loop()
    badger = PiBadger(badge_file, loop, screen)
    # This will block until the final shutdown frame is rendered, at which point we resume here.
    badger.start()

os.system("sudo shutdown now -P")