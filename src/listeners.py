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

    def is_button_pressed(button_name):
        current_button_state = getattr(keypad, button_name)
        if current_button_state != button_states[button_name]:
            button_states[button_name] = current_button_state
            return current_button_state
        return False

    while True:
        # Only get the 'first' pressed button.
        pressed_button = next((button for button in button_names if is_button_pressed(button)), None)
        if (pressed_button):
            callback(pressed_button)
        await aio.sleep(0.1)

async def listen_keyboard(callback):
    while True:
        # Prompt is unnecessary for headless usage, but I like it for debugging. 
        value = await aioconsole.ainput("Badge: ")
        callback(value)