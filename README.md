# WPF Theme Color Cheatsheet

A visual reference guide for Windows WPF app theme colors, displaying all available brushes in both Light and Dark themes.

[WPF Theme Color Cheatsheet](https://hetima.github.io/WpfThemeColorCheatsheet/)

## Features

- **Dual Theme Support**: View colors in both Light and Dark themes
- **Color Preview**: Visual color boxes with HEX values and opacity percentages
- **Search & Filter**: Real-time search by brush name or opacity (e.g., `>30`, `<50`, `100`)
- **Sorting**: Sort brushes by name or color brightness
- **Click to Copy**: Click any brush card to copy its name to clipboard
- **Transparency Visualization**: Colors displayed against theme-appropriate backgrounds

## Usage

1. Open [WPF Theme Color Cheatsheet](https://hetima.github.io/WpfThemeColorCheatsheet/) in your browser
2. Use the search bar to filter brushes by name or opacity
3. Click sort buttons to reorder brushes
4. Click any brush card to copy its name to clipboard
5. Press ESC to clear the search

## Generation

The HTML file is generated from XAML resource dictionaries using `generate.py`:

```bash
python generate.py
```

This script parses `Light.xaml` and `Dark.xaml` files and generates `index.html` with all theme color brushes.

## License

MIT
