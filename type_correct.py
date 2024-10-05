from pynput import keyboard
import json
import os

# Load key layout from JSON configuration
def load_key_layout(layout_name):
    # Get the absolute path of the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the key_layout.json file
    file_path = os.path.join(script_dir, 'key_layout.json')
    
    with open(file_path, 'r') as file:
        layouts = json.load(file)
        return layouts.get(layout_name)

# Track which shift keys are pressed
shift_keys = {
    "left": False,
    "right": False
}

# Initialize controller once
controller = keyboard.Controller()

# Load the desired key layout (e.g., QWERTZ or QWERTY)
diagonal_keys = load_key_layout("QWERTZ")  # You can change this to "QWERTY" or any other layout

def on_press(key):
    try:
        if key == keyboard.Key.shift_l:
            shift_keys['left'] = True
        elif key == keyboard.Key.shift_r:
            shift_keys['right'] = True
        
        # Check only if the pressed key is a character that we care about
        if hasattr(key, 'char') and key.char in diagonal_keys:
            required_shift = diagonal_keys[key.char]
            if not shift_keys[required_shift]:
                # Block the incorrect input by deleting the character
                controller.press(keyboard.Key.backspace)
                controller.release(keyboard.Key.backspace)
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.shift_l:
        shift_keys['left'] = False
    elif key == keyboard.Key.shift_r:
        shift_keys['right'] = False

# Start listening to the keyboard
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
