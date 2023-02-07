from screen import open_screen
import asyncio as aio
import listeners

"""
TODO: Add main to the system bootup.
TODO: Save input content to a file named with today's date
TODO: Add the ability to quit the pi
    * Consider using an FSM per https://eli.thegreenplace.net/2009/08/29/co-routines-as-an-alternative-to-state-machines/
TODO: Add installation instructions
"""

with open_screen() as screen:
    def write_screen(content):
        print("Received:", content)
        screen.clear()
        screen.message = content

    screen.display = True
    screen.message = "Ready..."
    screen.cursor = True
    screen.blink = True
    
    loop = aio.get_event_loop()
    button_task = loop.create_task(listeners.listen_buttons(screen, write_screen))
    keyboard_task = loop.create_task(listeners.listen_keyboard(write_screen))

    loop.run_forever()