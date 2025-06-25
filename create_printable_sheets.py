from PIL import Image
import os
import math

def create_card_sheets(input_dir='print_ready', output_dir='print_sheets', cards_per_sheet=8):
    """
    Create printable sheets with 8 cards each (2 rows x 4 columns, rotated 90°)
    For 8.5" x 11" paper in landscape orientation
    """
    
    # Sheet dimensions for 8.5x11" at 300 DPI
    SHEET_WIDTH = int(11 * 300)   # 3300px (landscape)
    SHEET_HEIGHT = int(8.5 * 300) # 2550px
    
    # Card dimensions (keep original: 2.25" x 3.5")
    CARD_WIDTH = 675    # Original width
    CARD_HEIGHT = 1050  # Original height
    
    # Layout: 4 cards wide, 2 cards tall
    COLS = 4
    ROWS = 2
    
    # Calculate spacing to center the grid
    total_cards_width = COLS * CARD_WIDTH
    total_cards_height = ROWS * CARD_HEIGHT
    margin_x = (SHEET_WIDTH - total_cards_width) // 2
    margin_y = (SHEET_HEIGHT - total_cards_height) // 2
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PNG files
    png_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    png_files.sort()  # Sort for consistent ordering
    
    total_sheets = math.ceil(len(png_files) / cards_per_sheet)
    
    for sheet_num in range(total_sheets):
        # Create blank sheet (white background)
        sheet = Image.new('RGB', (SHEET_WIDTH, SHEET_HEIGHT), 'white')
        
        # Add cards to this sheet
        for i in range(cards_per_sheet):
            card_index = sheet_num * cards_per_sheet + i
            
            if card_index >= len(png_files):
                break  # No more cards
                
            # Load card (no rotation needed)
            card_path = os.path.join(input_dir, png_files[card_index])
            card = Image.open(card_path)
            
            # Calculate position on sheet
            col = i % COLS
            row = i // COLS
            
            x = margin_x + col * CARD_WIDTH
            y = margin_y + row * CARD_HEIGHT
            
            # Paste card onto sheet
            sheet.paste(card, (x, y))
        
        # Save sheet
        sheet_filename = f'sheet_{sheet_num + 1:03d}.png'
        sheet_path = os.path.join(output_dir, sheet_filename)
        sheet.save(sheet_path, dpi=(300, 300))
        
        print(f"Created {sheet_filename} with {min(cards_per_sheet, len(png_files) - sheet_num * cards_per_sheet)} cards")
    
    print(f"\n✅ Generated {total_sheets} print sheets from {len(png_files)} cards")
    print(f"📁 Saved to '{output_dir}' directory")
    print(f"📄 Each sheet fits on 8.5\"x11\" paper (landscape)")

def create_sheets_with_cut_lines(input_dir='print_ready', output_dir='print_sheets_with_guides'):
    """
    Same as above but adds cut lines for easier trimming
    """
    from PIL import ImageDraw
    
    # Same dimensions as above
    SHEET_WIDTH = int(11 * 300)
    SHEET_HEIGHT = int(8.5 * 300)
    CARD_WIDTH = 675    # Keep original dimensions
    CARD_HEIGHT = 1050
    COLS = 4
    ROWS = 2
    
    total_cards_width = COLS * CARD_WIDTH
    total_cards_height = ROWS * CARD_HEIGHT
    margin_x = (SHEET_WIDTH - total_cards_width) // 2
    margin_y = (SHEET_HEIGHT - total_cards_height) // 2
    
    os.makedirs(output_dir, exist_ok=True)
    
    png_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    png_files.sort()
    
    total_sheets = math.ceil(len(png_files) / 8)
    
    for sheet_num in range(total_sheets):
        sheet = Image.new('RGB', (SHEET_WIDTH, SHEET_HEIGHT), 'white')
        draw = ImageDraw.Draw(sheet)
        
        # Add cards
        for i in range(8):
            card_index = sheet_num * 8 + i
            if card_index >= len(png_files):
                break
                
            card_path = os.path.join(input_dir, png_files[card_index])
            card = Image.open(card_path)
            
            col = i % COLS
            row = i // COLS
            x = margin_x + col * CARD_WIDTH
            y = margin_y + row * CARD_HEIGHT
            
            sheet.paste(card, (x, y))
        
        # Add cut lines (light gray, dashed-looking)
        line_color = '#cccccc'
        
        # Vertical cut lines
        for col in range(1, COLS):
            x = margin_x + col * CARD_WIDTH
            draw.line([(x, margin_y), (x, margin_y + total_cards_height)], 
                     fill=line_color, width=2)
        
        # Horizontal cut lines  
        for row in range(1, ROWS):
            y = margin_y + row * CARD_HEIGHT
            draw.line([(margin_x, y), (margin_x + total_cards_width, y)], 
                     fill=line_color, width=2)
        
        # Outer border
        draw.rectangle([(margin_x, margin_y), 
                       (margin_x + total_cards_width, margin_y + total_cards_height)], 
                      outline=line_color, width=2)
        
        sheet_filename = f'sheet_{sheet_num + 1:03d}_with_guides.png'
        sheet_path = os.path.join(output_dir, sheet_filename)
        sheet.save(sheet_path, dpi=(300, 300))
        
        print(f"Created {sheet_filename}")
    
    print(f"\n✅ Generated {total_sheets} print sheets with cut guides")

if __name__ == '__main__':
    # Create basic sheets
    create_card_sheets()
    
    # Also create sheets with cut lines
    create_sheets_with_cut_lines()