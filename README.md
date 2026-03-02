# WPF Theme Color Cheatsheet

A visual reference guide for Windows WPF app theme colors, displaying all available brushes in both Light and Dark themes.

[WPF Theme Color Cheatsheet](https://hetima.github.io/WpfThemeColorCheatsheet/)

## Features

- **Dual Theme Support**: View colors in both Light and Dark themes
- **Click to Copy**: Click any brush card to copy its name to clipboard
- **Brushes & Colors Modes**: Toggle between Brushes and Colors datasets
- **Color Preview**: Visual color boxes with HEX values and opacity percentages
- **Transparency Visualization**: Colors displayed against theme-appropriate backgrounds
- **Advanced Search**: Search by opacity or color name
- **Quick Search Button**: Click the search icon on each card to quickly search for related items
- **Sorting**: Sort by name or color brightness

## Usage

1. Open [WPF Theme Color Cheatsheet](https://hetima.github.io/WpfThemeColorCheatsheet/) in your browser
2. Toggle between Brushes and Colors modes using the dataset buttons
3. Use the search bar to filter by:
   - Name (partial match)
   - Opacity (e.g., `>30`, `<50`, `>=20`, `<=80`, `==50`, `100`)
   - Color name in Brushes mode (e.g., `c:FillColor` for partial match, `c:"FillColor"` for exact match)
4. Click sort buttons to reorder by name or color brightness
5. Click search icon on any card to quickly search for related items
6. Click any brush card to copy its name to clipboard
7. Press ESC to clear the search

## Generation

The HTML file is generated from XAML resource dictionaries using `generate.py`:

```bash
python generate.py
```

This script parses `Light.xaml` and `Dark.xaml` files and generates `index.html` with all theme color brushes.

## License

MIT
