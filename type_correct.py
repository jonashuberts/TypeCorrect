from pynput import keyboard
import json
import os

# Load key layout from a JSON configuration file
def load_key_layout(layout_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    file_path = os.path.join(script_dir, 'key_layout.json')  # Construct file path
    with open(file_path, 'r') as file:
        layouts = json.load(file)  # Load JSON data
        return layouts.get(layout_name)  # Return specific layout

# Dictionary to track state of left and right shift keys
shift_keys = {
    "left": False,
    "right": False
}

# Initialize keyboard controller for simulating key presses
controller = keyboard.Controller()

# Load the specified keyboard layout
diagonal_keys = load_key_layout("QWERTZ")  # Change layout name as needed

# Function to handle key press events
def on_press(key):
    try:
        if key == keyboard.Key.shift_l:
            shift_keys['left'] = True  # Track left shift key press
        elif key == keyboard.Key.shift_r:
            shift_keys['right'] = True  # Track right shift key press

        # Process character keys based on the loaded layout
        if hasattr(key, 'char') and key.char in diagonal_keys:
            required_shift = diagonal_keys[key.char]  # Determine required shift key
            if not shift_keys[required_shift]:
                controller.press(keyboard.Key.backspace)  # Delete incorrect input
                controller.release(keyboard.Key.backspace)
    except AttributeError:
        pass  # Ignore non-character keys

# Function to handle key release events
def on_release(key):
    if key == keyboard.Key.shift_l:
        shift_keys['left'] = False  # Update left shift state
    elif key == keyboard.Key.shift_r:
        shift_keys['right'] = False  # Update right shift state

# Start the keyboard listener to capture events
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()  # Keep the listener active
