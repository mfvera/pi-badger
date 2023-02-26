import asyncio as aio
import os
import time
from collections.abc import Set
from datetime import date
from io import SEEK_END, TextIOWrapper

from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C

import listeners
from screen import LCD_COLUMNS, open_screen
from ui import Frame, FrameController

"""
1. Add the ability to export the user list at-will via developer provided callback
"""

def centered(text: str) -> str:
    return text.center(LCD_COLUMNS)

script_location = os.path.dirname(__file__)
badge_filename = os.path.join(script_location, f"../outputs/attendance_{date.today().isoformat()}")

class PiBadger(FrameController):
    def __init__(self,
                 badge_id_file: TextIOWrapper,
                 event_loop: aio.AbstractEventLoop,
                 screen: Character_LCD_RGB_I2C):
        self.file = badge_id_file

        self.loop = event_loop
        self.loop.create_task(listeners.listen_buttons(screen, self.advance))
        self.loop.create_task(listeners.listen_keyboard(self.handle_badge_input))

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

    def handle_badge_input(self, badge_id):
        # Ensure that we show the "welcome" message every time a user badges
        self.restart()
        self.render(badge_id)
    
        if badge_id not in self.badges:
            self.login_count += 1
        self.file.write(f"{badge_id}\n")
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
            self.screen.display = False
            self.screen.color = [0,0,0]
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

    def _read_existing_attendees(self) -> Set[str]:
        badge_ids = set(line.strip() for line in self.file)
        # Ensure the file is ready to append names by placing cursor at the end.
        self.file.seek(0, SEEK_END)

        return badge_ids

with open_screen() as screen, open(badge_filename, mode="w+") as badge_file:
    loop = aio.get_event_loop()
    badger = PiBadger(badge_file, loop, screen)
    # Shutdown is handled on the "shutdown" frame renderer
    badger.start()

os.system("sudo shutdown now -P")