#MacOS build: uv run pyinstaller --onefile --windowed --name=TypeCorrect --add-data "key_layout.json:." type_correct.py
#Windows build: uv run pyinstaller --onefile --noconsole --name=TypeCorrect --add-data "key_layout.json;." type_correct.py

from pynput import keyboard
from PIL import Image, ImageDraw
import pystray
import json
import os
import sys

# Determine the directory where assets will be located. 
if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

def load_key_layouts():
    file_path = os.path.join(script_dir, 'key_layout.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading layouts: {e}")
        return {"QWERTZ": {}}

app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else script_dir
settings_path = os.path.join(app_dir, 'settings.json')

def load_settings():
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass
    return {"enabled": True, "layout": "QWERTZ"}

def save_settings(settings):
    try:
        with open(settings_path, 'w', encoding='utf-8') as file:
            json.dump(settings, file)
    except Exception:
        pass

settings = load_settings()
layouts = load_key_layouts()

if settings.get("layout") not in layouts and layouts:
    settings["layout"] = list(layouts.keys())[0]

app_state = {
    "enabled": settings.get("enabled", True),
    "current_layout": settings.get("layout", "QWERTZ"),
    "keyboard_listener": None,
    "icon": None
}

shift_keys = {
    "left": False,
    "right": False
}

controller = keyboard.Controller()

def on_press(key):
    if not app_state["enabled"]:
        return
        
    try:
        # Check for shift keys specifically
        if key == keyboard.Key.shift_l:
            shift_keys['left'] = True
        elif key == keyboard.Key.shift_r:
            shift_keys['right'] = True
        elif str(key) == "Key.shift":
            print("[DEBUG] OS emitted generic 'Key.shift'. Cannot determine Left/Right layout safely.")
            # We can't know which one they pressed safely, so maybe mapping both? No, that ruins enforcement.

        diagonal_keys = layouts.get(app_state["current_layout"], {})
        
        char = getattr(key, 'char', None)
        
        # Log to the terminal for debugging
        if char:
            print(f"[DEBUG] Typed: '{char}', LeftShift: {shift_keys['left']}, RightShift: {shift_keys['right']}")
            
            if char in diagonal_keys:
                required_shift = diagonal_keys[char]
                print(f"[DEBUG] Character '{char}' REQUIRES '{required_shift}' shift.")
                
                if not shift_keys[required_shift]:
                    print(f"[DEBUG] Validation FAILED! Attempting to backspace.")
                    try:
                        controller.press(keyboard.Key.backspace)
                        controller.release(keyboard.Key.backspace)
                        print(f"[DEBUG] Backspace injected.")
                    except Exception as inner_e:
                        print(f"[ERROR] Could not press backspace! Do you have Accessibility permissions enabled? Exception: {inner_e}")
                else:
                    print(f"[DEBUG] Validation PASSED.")
    except Exception as e:
        print(f"[ERROR] in on_press: {e}")

def on_release(key):
    if key == keyboard.Key.shift_l:
        shift_keys['left'] = False
    elif key == keyboard.Key.shift_r:
        shift_keys['right'] = False
    elif str(key) == "Key.shift":
        # Fallback clearing
        shift_keys['left'] = False
        shift_keys['right'] = False

def generate_icon(enabled):
    size = 64
    image = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(image)
    white = (255, 255, 255, 255)
    
    if enabled:
        # Solid keycap
        d.rounded_rectangle([12, 12, 52, 52], radius=6, fill=white)
        
        # Erase the arrow shape by modifying the alpha channel to 0 (completely transparent cutout)
        alpha = image.split()[3]
        mask_d = ImageDraw.Draw(alpha)
        # Stem cutout
        mask_d.rectangle([29, 30, 35, 42], fill=0) 
        # Arrowhead cutout
        mask_d.polygon([(32, 18), (22, 30), (42, 30)], fill=0)
        image.putalpha(alpha)
    else:
        # Outlined keycap (completely transparent background)
        d.rounded_rectangle([12, 12, 52, 52], radius=6, outline=white, width=2)
        
        # Outlined arrow stem
        d.line([32, 30, 32, 42], fill=white, width=2)
        # Outlined arrowhead
        d.polygon([(32, 18), (24, 30), (40, 30)], outline=white, width=2)
    
    return image

def toggle_enabled(icon, item):
    app_state["enabled"] = not app_state["enabled"]
    settings["enabled"] = app_state["enabled"]
    save_settings(settings)
    icon.icon = generate_icon(app_state["enabled"])

def is_enabled(item):
    return app_state["enabled"]

def set_layout(layout_name):
    def _set(icon, item):
        app_state["current_layout"] = layout_name
        settings["layout"] = layout_name
        save_settings(settings)
    return _set

def is_layout_checked(layout_name):
    def _check(item):
        return app_state["current_layout"] == layout_name
    return _check

def quit_app(icon, item):
    icon.stop()
    if app_state["keyboard_listener"]:
        app_state["keyboard_listener"].stop()

def setup_icon():
    layout_items = []
    for layout_name in layouts.keys():
        layout_items.append(pystray.MenuItem(
            layout_name, 
            set_layout(layout_name),
            radio=True,
            checked=is_layout_checked(layout_name)
        ))

    menu = pystray.Menu(
        pystray.MenuItem('Enable Enforcement', toggle_enabled, checked=is_enabled),
        pystray.MenuItem('Layouts', pystray.Menu(*layout_items)),
        pystray.MenuItem('Quit', quit_app)
    )

    app_state["icon"] = pystray.Icon("TypeCorrect", generate_icon(app_state["enabled"]), "TypeCorrect", menu)
    
    # Start the keyboard listener
    app_state["keyboard_listener"] = keyboard.Listener(on_press=on_press, on_release=on_release)
    app_state["keyboard_listener"].start()

    print("[DEBUG] TypeCorrect is running. Checking logs...")
    app_state["icon"].run()

if __name__ == "__main__":
    setup_icon()
