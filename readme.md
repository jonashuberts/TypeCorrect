# TypeCorrect

**TypeCorrect** is a lightweight, background utility for macOS and Windows that enforces the correct use of the left and right `Shift` keys. Designed for touch typists and those looking to break bad typing habits, TypeCorrect silently monitors your keystrokes and ensures you strictly follow diagonal shift rules based on your keyboard layout.

## Features

- **Unobtrusive Background Utility**: Runs seamlessly in the macOS menu bar or Windows system tray without an open terminal.
- **Strict Shift Enforcement**: Maps every key to precisely require either the left or right `Shift` key for capitalization and special characters. 
- **On-the-Fly Control**: Instantly toggle enforcement on or off directly from the tray menu.
- **Dynamic Layout Selection**: Switch between multiple keyboard layouts (like QWERTZ and QWERTY) instantly without restarting or editing code.
- **Persistent State**: Remembers your preferred layout and enabled/disabled state across system reboots.
- **Customizable Rulesets**: Easily add or modify keyboard layouts by editing the `key_layout.json` configuration.

## Installation & Setup

TypeCorrect utilizes `uv` for lightning-fast dependency management and `pyinstaller` for building standalone executables.

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Building from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TypeCorrect.git
   cd TypeCorrect
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Build the Standalone App:**
   Compiling the application prevents terminal windows from appearing and integrates TypeCorrect natively into your OS.

   **macOS:**
   ```bash
   uv run pyinstaller TypeCorrect.spec
   ```
   > [!CAUTION]
   > macOS strictly governs keyboard listeners. You must run the compiled `.app` file, not the terminal Python script. After building, open the `dist/` folder, double-click `TypeCorrect.app`, and grant it permissions under **System Settings > Privacy & Security > Accessibility**.

   **Windows:**
   ```bash
   uv run pyinstaller --onefile --noconsole --name=TypeCorrect --add-data "key_layout.json;." type_correct.py
   ```

## Auto-Start Configuration

To have TypeCorrect launch silently in the background when your computer boots:

**macOS:**
1. Move `TypeCorrect.app` from the `dist/` folder into your `Applications/` directory.
2. Navigate to **System Settings > General > Login Items**.
3. Click the `+` button and add `TypeCorrect.app`.

**Windows:**
1. Press `Win + R`, type `shell:startup`, and press Enter.
2. Move the built `TypeCorrect.exe` from the `dist/` folder into the Startup folder that opens.

## Configuration

You can fully customize which Shift key is required for any character by modifying the `key_layout.json` file. 

Example mapping:
```json
{
  "QWERTZ": {
    "Q": "right",
    "A": "right",
    "P": "left"
  }
}
```
*Note: Any new layouts added to this JSON file will automatically become selectable in the app's tray menu upon restart.*
