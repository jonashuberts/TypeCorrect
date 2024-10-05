# TypeCorrect

**TypeCorrect** is a Python-based tool designed to enforce the correct use of the left and right `Shift` keys based on keyboard layout. The program ensures that users follow specific diagonal shift rules when typing, making it an ideal tool for those looking to improve their typing habits or for enforcing custom typing rules.

## Features

- **Enforced Shift Key Usage**: Each key can be mapped to require either the left or right `Shift` key for capital letters, special characters, and umlauts.
- **Multiple Keyboard Layouts**: TypeCorrect supports different keyboard layouts, like QWERTZ and QWERTY, with the ability to easily add more layouts via a configuration file.
- **Cross-Platform**: Works on Windows and macOS, with easy startup integration for both platforms.
- **Customizable Layouts**: Modify and add new layouts with ease using the `key_layout.json` file.

## Installation

### Prerequisites

- Python 3.x
- `pynput` library for keyboard input handling

To install the required dependencies, run:

```bash
pip install pynput
```

### Download and Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/TypeCorrect.git
   cd TypeCorrect
   ```

2. Add your desired keyboard layout (e.g., `QWERTZ`) in the `key_layout.json` file.

### Running the Program

To run the program, use the following command:

```bash
python type_correct.py
```

## Adding TypeCorrect to Startup

### Windows

1. Move the `TypeCorrect.exe` file into your Windows startup folder:
   - Press `Win + R`, type `shell:startup`, and press Enter.
   - Copy the `TypeCorrect.exe` file into the opened folder.
2. TypeCorrect will now run automatically when Windows starts.

### macOS

1. Move the app 'TypeCorrect' from the dist folder to the `Login Items`:
   - Go to `System Settings > General > Login Items`.
   - Click the `+` button and add your built app to the list.
2. The app will now run when macOS starts.
3. Give the app permissions by going to `System Settings > Security & Privacy > Privacy > Input` and enabling the `Terminal` option and by going to `System Settings > Security & Privacy > Privacy > Accessibility` and enabling the `Terminal` option.

## Configuration

The `key_layout.json` file allows you to customize the key bindings for different layouts. It maps each character to the required `Shift` key (`left` or `right`).

Example `key_layout.json`:

```json
{
  "QWERTZ": {
    "Q": "right",
    "W": "right",
    "E": "right",
    "R": "right",
    "T": "right",
    "Z": "left",
    "U": "left",
    "I": "left",
    "O": "left",
    "P": "left",
    "Ä": "left",
    "Ö": "left",
    "Ü": "left",
    "!": "right",
    "?": "left"
  }
}
```

To load a different layout, modify the layout in the `shift.py` script:

```python
diagonal_keys = load_key_layout("QWERTZ")  # Change to "QWERTY" if needed
```
