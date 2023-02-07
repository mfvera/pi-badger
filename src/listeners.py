import asyncio as aio
import aioconsole

async def listen_buttons(keypad, callback):
    button_states = {
        "left_button": False,
        "right_button": False,
        "up_button": False,
        "down_button": False,
        "select_button": False
    }
    button_names = list(button_states.keys())

    def is_button_pressed(name):
        value = getattr(keypad, name)
        if value != button_states[name]:
            button_states[name] = value
            return value
        return False

    while True:
        # Only get the 'first' pressed button.
        pressed_button = next((name for name in button_names if is_button_pressed(name)), None)
        if (pressed_button):
            callback(pressed_button)
        await aio.sleep(0.1)

async def listen_keyboard(callback):
    while True:
        value = await aioconsole.ainput("Message:")
        callback(value)