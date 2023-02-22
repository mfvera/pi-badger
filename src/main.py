import asyncio as aio
import os
import time
from datetime import date

import listeners
from screen import LCD_COLUMNS, open_screen
from ui import Frame, FrameController

"""
1. Refactor main to be a stateful class
2. Adapt read mode to "r+" so we can do a once-over to read the existing content
3. Refactor Frame initialization to use decorators (for shits and giggles)
4. Add the ability to export the user list at-will via developer provided callback
"""

def centered(text: str) -> str:
    return text.center(LCD_COLUMNS)

script_location = os.path.dirname(__file__)
out_filename = os.path.join(script_location, f"../outputs/attendance_{date.today().isoformat()}")

with open_screen() as screen, open(out_filename, mode="a+") as output_file:
    login_count = 0
    screen.cursor = True
    screen.blink = True

    loop = aio.get_event_loop()

    def render_main_frame(*args, **kwargs):
        if len(args) > 0:
            global login_count
            login_count += 1
            screen.clear()
            screen.message = f"Welcome:\n{centered(args[0])}"
            time.sleep(1.5)
        screen.clear()
        screen.message = "Ready..."
    main_frame = Frame(render_main_frame)

    def render_total_attendees_frame(*args, **kwargs):
        screen.clear()
        screen.message = f"Total guests:\n{centered(str(login_count))}"
    total_attendees_frame = Frame(render_total_attendees_frame)

    def render_shutdown_frame(*args, **kwargs):
        screen.clear()
        screen.message = f"{centered('Shutdown?')}\n{centered('<- N | Y ->')}"
    shutdown_frame = Frame(render_shutdown_frame)

    def render_shutdown_for_sure(*args, **kwargs):
        screen.clear()
        screen.message = f"{centered('Are you certain?')}\n{centered('<- N | Y ->')}"
    shutdown_for_sure_frame = Frame(render_shutdown_for_sure)

    def render_final_shutdown(*args, **kwargs):
        screen.clear()
        screen.display = False
        screen.color = [0,0,0]
        loop.stop()
    final_shutdown_frame = Frame(render_final_shutdown)

    main_frame.add_neighbor("right_button", total_attendees_frame)
    total_attendees_frame.add_neighbor("left_button", main_frame)

    total_attendees_frame.add_neighbor("right_button", shutdown_frame)
    shutdown_frame.add_neighbor("left_button", total_attendees_frame)

    shutdown_frame.add_neighbor("right_button", shutdown_for_sure_frame)
    shutdown_for_sure_frame.add_neighbor("left_button", total_attendees_frame)

    shutdown_for_sure_frame.add_neighbor("right_button", final_shutdown_frame)
    # There is no return from this frame :)

    menu = FrameController(main_frame)
    menu.render()

    def handle_badge_input(badge_id):
        menu.reset(badge_id)
        output_file.write(f"{badge_id}\n")
        output_file.flush()

    button_task = loop.create_task(listeners.listen_buttons(screen, menu.advance))
    keyboard_task = loop.create_task(listeners.listen_keyboard(handle_badge_input))
    loop.run_forever()

os.system("sudo shutdown now -P")