# MMRPG Power Cards V2
![Accuracy_1](https://github.com/user-attachments/assets/45b4567f-c0bd-4a31-85ab-db822f11709d)



![Animated_Illusion](https://github.com/user-attachments/assets/6bcf537f-1948-4b3b-babd-8498fb41db26)


Generate printable playing cards for Marvel Multiverse RPG powers and abilities.

## Features

- **Automated card generation** from JSON Data
- **Print-ready layouts** (8 cards per 8.5"×11" sheet)
- **High-quality output** (300 DPI PNG files)
- **Professional card design** with proper spacing and typography

## Quick Start

1. **Generate individual cards:**
   ```bash
   python generate_cards.py
   ```

2. **Create print sheets:**
   ```bash
   python create_sheets.py
   ```

3. **Print:** Use landscape orientation, actual size (no scaling)

## Output

- `cards/` - Individual card PNGs (675×1050px, 2.25"×3.5")
- `print_sheets/` - Ready-to-print sheets (8 cards each)
- `print_sheets_with_guides/` - Same with cut lines

## Card Format

Each card includes:
- Power name and description
- Power set, action type, duration
- Prerequisites and cost
- Complete effect description

## Requirements

- Python 3.x
- PIL (Pillow): `pip install pillow`

## Printing Tips

- **Paper:** 8.5"×11" landscape orientation
- **Quality:** Use cardstock (110lb recommended)
- **Settings:** Print at actual size (100%, no auto-fit)
- **Cutting:** Follow the guide lines for clean edges

## File Structure

```
├── data/               # Source CSV files
├── cards/              # Individual card images
├── print_sheets/       # Printable layouts
├── generate_cards.py   # Main card generator
└── create_sheets.py    # Print layout creator
```

Perfect for home printing or professional print shops!
