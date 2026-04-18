#MacOS build: uv run pyinstaller --onefile --windowed --name=TypeCorrect --add-data "key_layout.json:." type_correct.py
#Windows build: uv run pyinstaller --onefile --noconsole --name=TypeCorrect --add-data "key_layout.json;." type_correct.py

from pynput import keyboard
from PIL import Image, ImageDraw
import pystray
import json
import os
import sys
import time
import logging
from pathlib import Path

# Setup application data directory in the user's Library folder
user_app_support = Path.home() / 'Library' / 'Application Support' / 'TypeCorrect'
user_app_support.mkdir(parents=True, exist_ok=True)

# Setup robust logging
log_file = Path.home() / 'Library' / 'Logs' / 'TypeCorrect.log'
logging.basicConfig(filename=str(log_file), level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting TypeCorrect application...")

# Determine the directory where assets will be located. 
if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS
    # For macOS bundles, datas may go to Resources
    if 'TypeCorrect.app' in sys.executable:
        bundle_resources = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'Resources')
        if os.path.exists(os.path.join(bundle_resources, 'key_layout.json')):
            script_dir = bundle_resources
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

def load_key_layouts():
    file_path = os.path.join(script_dir, 'key_layout.json')
    logging.info(f"Looking for key_layout.json at: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"FATAL: key_layout.json not found at {file_path}!")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(f"Loaded layouts: {list(data.keys())}")
            return data
    except Exception as e:
        logging.error(f"Error loading layouts: {e}")
        return {"QWERTZ": {}}

# Save settings to stable App Support directory instead of read-only App Bundle
settings_path = user_app_support / 'settings.json'

def load_settings():
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.warning(f"Failed to load settings: {e}")
    return {"enabled": True, "layout": "QWERTZ"}

def save_settings(settings):
    try:
        with open(settings_path, 'w', encoding='utf-8') as file:
            json.dump(settings, file)
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")

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
    logging.debug(f"RAW KEY PRESSED: {key}")
    if not app_state["enabled"]:
        return
        
    try:
        # Check for shift keys specifically
        if key == keyboard.Key.shift_l:
            shift_keys['left'] = True
        elif key == keyboard.Key.shift_r:
            shift_keys['right'] = True
        elif str(key) == "Key.shift":
            logging.debug("OS emitted generic 'Key.shift'. Cannot determine Left/Right layout safely.")

        diagonal_keys = layouts.get(app_state["current_layout"], {})
        char = getattr(key, 'char', None)
        
        # Log keystroke resolution
        if char:
            logging.debug(f"Typed: '{char}', LShift: {shift_keys['left']}, RShift: {shift_keys['right']}")
            
            if char in diagonal_keys:
                required_shift = diagonal_keys[char]
                logging.info(f"Character '{char}' REQUIRES '{required_shift}' shift.")
                
                if not shift_keys[required_shift]:
                    logging.warning(f"Validation FAILED! User missed right shift combo.")
                    try:
                        # Yield temporarily to OS so the incorrect letter finishes rendering before backspace deletes it
                        time.sleep(0.02)
                        controller.press(keyboard.Key.backspace)
                        controller.release(keyboard.Key.backspace)
                        logging.info("Backspace injected to block invalid keypress.")
                    except Exception as inner_e:
                        logging.error(f"Could not press backspace! Accessibility permissions block? Exception: {inner_e}")
                else:
                    logging.info("Validation PASSED.")
    except Exception as e:
        logging.error(f"Error in on_press loop: {e}")

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

def check_accessibility():
    if sys.platform != "darwin": return True
    try:
        import ctypes
        app_services = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
        return bool(app_services.AXIsProcessTrusted())
    except Exception:
        return True

def open_accessibility(icon, item):
    if sys.platform == "darwin":
        os.system("open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'")

def open_input_monitoring(icon, item):
    if sys.platform == "darwin":
        os.system("open 'x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent'")

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

    trusted = check_accessibility()
    status_label = "🟢 Permissions: OK" if trusted else "🔴 Permissions: MISSING!"

    diagnostic_items = [
        pystray.MenuItem(status_label, lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("1. Open Accessibility Settings", open_accessibility),
        pystray.MenuItem("2. Open Input Monitoring Settings", open_input_monitoring)
    ]

    menu = pystray.Menu(
        pystray.MenuItem('Enable Enforcement', toggle_enabled, checked=is_enabled),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Layouts', pystray.Menu(*layout_items)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Troubleshoot', pystray.Menu(*diagnostic_items)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Quit', quit_app)
    )

    app_state["icon"] = pystray.Icon("TypeCorrect", generate_icon(app_state["enabled"]), "TypeCorrect", menu)
    
    # Start the keyboard listener
    app_state["keyboard_listener"] = keyboard.Listener(on_press=on_press, on_release=on_release)
    app_state["keyboard_listener"].start()

    logging.info("Starting pystray user interface...")
    app_state["icon"].run()

if __name__ == "__main__":
    setup_icon()
