import json
import os
import re
import svgwrite
from textwrap import wrap

# Card size in pixels (2.5in x 3.6in at 300 DPI)
CARD_WIDTH_PX = 750
CARD_HEIGHT_PX = 1080
PADDING = 45  # px
BODY_WIDTH = CARD_WIDTH_PX - 2 * PADDING
HEADER_MARGIN_X = 30  # px, margin for header text
HEADER_AVAILABLE_WIDTH = CARD_WIDTH_PX - 2 * HEADER_MARGIN_X

HEADER_HEIGHT = 135  # px
FOOTER_HEIGHT = 105  # px

FONT_FAMILY = 'Arial, Helvetica, sans-serif'

# Colors
BLACK = '#222'
DARK_GRAY = '#444'
WHITE = '#fff'
GRAY = '#eee'
VERT_LINE = '#bbb'
VERT_LINE_WIDTH = 4

# Fields to display in order
FIELD_ORDER = [
    'power_set', 'action', 'trigger', 'duration', 'cost', 'range', 'effect', 'prerequisites'
]
FIELD_LABELS = {
    'power_set': 'Power Set',
    'action': 'Action',
    'trigger': 'Trigger',
    'duration': 'Duration',
    'cost': 'Cost',
    'range': 'Range',
    'effect': 'Effect',
    'prerequisites': 'Prerequisites',
}

LABEL_X = PADDING
VALUE_X = PADDING + 210  # revert to original margin
MAX_TEXT_WIDTH = BODY_WIDTH
MAX_VALUE_WIDTH = BODY_WIDTH - 210

# Header font sizes (do not change unless requested)
HEADER_FONT_SIZE = 42
HEADER_LETTER_SPACING = 6
MIN_HEADER_FONT_SIZE = 24

# Body font sizes
LABEL_FONT_SIZE = 26
VALUE_FONT_SIZE = 26
DESC_FONT_SIZE = 26
MIN_LABEL_FONT_SIZE = 16
MIN_VALUE_FONT_SIZE = 16
MIN_DESC_FONT_SIZE = 16
LINE_SPACING = 36
MIN_LINE_SPACING = 22
UNDERLINE_SPACING = 8

# Estimate chars per line for wrapping (for fallback)
def estimate_chars_per_line(font_size, width):
    # Arial/Helvetica: ~0.6 * font_size per char for uppercase, ~0.55 for mixed
    return int(width / (font_size * 0.55))

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def wrap_text_pixel(text, font_size, max_width):
    # Estimate chars per line for this font size and width
    chars_per_line = estimate_chars_per_line(font_size, max_width)
    return wrap(text, width=chars_per_line)

def estimate_card_height(power, desc_font, value_font, label_font, line_spacing):
    y = HEADER_HEIGHT + PADDING
    desc = power.get('description', '')
    if desc:
        desc_lines = wrap_text_pixel(desc, desc_font, BODY_WIDTH)
        y += len(desc_lines) * (desc_font + 6) + 12
    for field in FIELD_ORDER:
        if field in power and power[field]:
            value = str(power[field])
            value_lines = wrap_text_pixel(value, value_font, BODY_WIDTH - 210)
            y += len(value_lines) * (value_font + 3)
            y += UNDERLINE_SPACING + 6 - 3
    y += FOOTER_HEIGHT + PADDING // 2
    return y

def fit_header_font_and_wrap(name, font_size=HEADER_FONT_SIZE, min_font_size=MIN_HEADER_FONT_SIZE, available_width=HEADER_AVAILABLE_WIDTH, letter_spacing=HEADER_LETTER_SPACING):
    name = name.upper()
    char_count = len(name)
    while font_size > min_font_size:
        est_width = char_count * font_size * 0.6 + (char_count-1)*letter_spacing
        if est_width <= available_width:
            return [name], font_size
        font_size -= 2
    words = name.split()
    if len(words) < 2:
        return [name], min_font_size
    best_split = len(words) // 2
    line1 = ' '.join(words[:best_split])
    line2 = ' '.join(words[best_split:])
    while font_size > min_font_size:
        est1 = len(line1) * font_size * 0.6 + (len(line1)-1)*letter_spacing
        est2 = len(line2) * font_size * 0.6 + (len(line2)-1)*letter_spacing
        if est1 <= available_width and est2 <= available_width:
            return [line1, line2], font_size
        font_size -= 2
    return [line1, line2], min_font_size

def draw_card(power, outdir='cards'):
    os.makedirs(outdir, exist_ok=True)
    name = power.get('power', 'Unknown Power')
    filename = os.path.join(outdir, sanitize_filename(name) + '.svg')

    # Fit header (do not change unless requested)
    header_lines, header_font = fit_header_font_and_wrap(name, font_size=HEADER_FONT_SIZE, min_font_size=MIN_HEADER_FONT_SIZE, available_width=HEADER_AVAILABLE_WIDTH, letter_spacing=HEADER_LETTER_SPACING)

    # Calculate max y for content (above footer)
    max_content_y = CARD_HEIGHT_PX - FOOTER_HEIGHT - PADDING

    # Try to fit body content: start with default, reduce if needed
    label_font = LABEL_FONT_SIZE
    value_font = VALUE_FONT_SIZE
    desc_font = DESC_FONT_SIZE
    line_spacing = LINE_SPACING
    min_label_font = MIN_LABEL_FONT_SIZE
    min_value_font = MIN_VALUE_FONT_SIZE
    min_desc_font = MIN_DESC_FONT_SIZE
    min_line_spacing = MIN_LINE_SPACING
    truncated = False

    def estimate_total_content_height(power, desc_font, value_font, label_font, line_spacing):
        y = HEADER_HEIGHT + PADDING
        quote = power.get('quote', '')
        if quote:
            quote_lines = wrap_text_pixel(quote, desc_font, BODY_WIDTH)
            y += len(quote_lines) * (desc_font + 6) + 12
        present_fields = [f for f in FIELD_ORDER if f in power and power[f]]
        for field in present_fields:
            value = str(power[field])
            value_lines = wrap_text_pixel(value, value_font, BODY_WIDTH - 210)
            y += label_font + len(value_lines) * (value_font + 3)
            y += value_font + 14  # spacing after field
        return y

    # Reduce font sizes and spacing until content fits above footer
    while True:
        est_height = estimate_total_content_height(power, desc_font, value_font, label_font, line_spacing)
        if est_height <= max_content_y:
            break
        # Reduce font sizes and line spacing
        if label_font > min_label_font:
            label_font -= 1
        if value_font > min_value_font:
            value_font -= 1
        if desc_font > min_desc_font:
            desc_font -= 1
        if line_spacing > min_line_spacing:
            line_spacing -= 1
        # If at minimums and still doesn't fit, stop
        if (label_font <= min_label_font and value_font <= min_value_font and desc_font <= min_desc_font and line_spacing <= min_line_spacing):
            break

    dwg = svgwrite.Drawing(filename, size=(CARD_WIDTH_PX, CARD_HEIGHT_PX))
    # Dot pattern background (matches SVG test)
    dot_pattern = dwg.pattern(id="dotPattern", size=(16, 16), patternUnits="userSpaceOnUse")
    dot_pattern.add(dwg.circle(center=(8, 8), r=1.5, fill="#e0e0e0"))
    dwg.defs.add(dot_pattern)
    # Linen pattern overlay
    linen_pattern = dwg.pattern(id="linen", size=(40, 40), patternUnits="userSpaceOnUse")
    linen_pattern.add(dwg.rect(insert=(0, 0), size=(40, 40), fill="none"))
    linen_pattern.add(dwg.line(start=(0, 0), end=(40, 40), stroke="#eee", stroke_width=0.5))
    linen_pattern.add(dwg.line(start=(40, 0), end=(0, 40), stroke="#eee", stroke_width=0.5))
    dwg.defs.add(linen_pattern)
    # Header/footer gradients
    header_grad = dwg.linearGradient(id="headerGradient", start=(0, 0), end=(0, 1))
    header_grad.add_stop_color(0, "#444")
    header_grad.add_stop_color(1, "#555")
    dwg.defs.add(header_grad)
    footer_grad = dwg.linearGradient(id="footerGradient", start=(0, 0), end=(0, 1))
    footer_grad.add_stop_color(0, "#444")
    footer_grad.add_stop_color(1, "#555")
    dwg.defs.add(footer_grad)
    # Header gloss
    gloss_grad = dwg.linearGradient(id="headerGloss", start=(0, 0), end=(0, 1))
    gloss_grad.add_stop_color(0, "#fff", opacity=0.25)
    gloss_grad.add_stop_color(0.6, "#fff", opacity=0)
    dwg.defs.add(gloss_grad)
    # Card shadow filter (optional, for web preview)
    # Border
    dwg.add(dwg.rect(insert=(1, 1), size=(CARD_WIDTH_PX-2, CARD_HEIGHT_PX-2), fill="none", stroke="#ccc", stroke_width=2))
    # Dot pattern
    dwg.add(dwg.rect(insert=(0, 0), size=(CARD_WIDTH_PX, CARD_HEIGHT_PX), fill="url(#dotPattern)"))
    # Linen overlay
    dwg.add(dwg.rect(insert=(0, 0), size=(CARD_WIDTH_PX, CARD_HEIGHT_PX), fill="url(#linen)", opacity=0.10))
    # Header bar (gradient)
    dwg.add(dwg.rect(insert=(0, 0), size=(CARD_WIDTH_PX, HEADER_HEIGHT), fill="url(#headerGradient)"))
    # Footer bar (gradient)
    dwg.add(dwg.rect(insert=(0, CARD_HEIGHT_PX - FOOTER_HEIGHT), size=(CARD_WIDTH_PX, FOOTER_HEIGHT), fill="url(#footerGradient)"))
    # Header gloss
    dwg.add(dwg.rect(insert=(0, 0), size=(CARD_WIDTH_PX, 40), fill="url(#headerGloss)"))
    # Vertical gray lines flush with card edge
    dwg.add(dwg.rect(insert=(0, HEADER_HEIGHT), size=(VERT_LINE_WIDTH, CARD_HEIGHT_PX - HEADER_HEIGHT - FOOTER_HEIGHT), fill="#e0e0e0"))
    dwg.add(dwg.rect(insert=(CARD_WIDTH_PX - VERT_LINE_WIDTH, HEADER_HEIGHT), size=(VERT_LINE_WIDTH, CARD_HEIGHT_PX - HEADER_HEIGHT - FOOTER_HEIGHT), fill="#e0e0e0"))

    # S.H.I.E.L.D. watermark (centered, no ellipse, subtle)
    shield_group = dwg.g(transform="translate(375,540) scale(1.71) translate(-175,-174)")
    shield_group.add(dwg.path(
        d="M 62 52.21 a 167.2 167.2 0 0 0 -27 32.24 l 140 154.37 L 314.47 84 a 166.25 166.25 0 0 0 -27.54 -32.22 L 211 112.24 l -18.14 -38.43 s 4.46 -13.61 20.25 -6.75 c 0 0 4.12 -15.06 -20.24 -15.06 H 172 s -7.32 -1.17 -13.11 11 l -23.33 48.82 L 61.3 53.53",
        fill="#222", fill_opacity=0.04
    ))
    shield_group.add(dwg.path(
        d="M 76 306.78 a 167.08 167.08 0 0 0 195.41 1.93 l -64.62 -98 -32 35.41 -33.61 -35.41 z M 326.22 242.69 A 163.62 163.62 0 0 0 341 183.34 L 281.7 131 l -27.1 33.49 z M 341.14 178.16 c 0 -1.39 .11 -2.77 .11 -4.16 a 163.83 163.83 0 0 0 -24.49 -86.4 l -32.55 40.26 z M 252.06 167.63 l -27.32 33.8 68.79 88.48 a 165.78 165.78 0 0 0 30.84 -43.32 z M 21.77 242.69 A 163.62 163.62 0 0 1 7 183.34 L 66.29 131 l 27.09 33.52 z M 6.85 178.16 c 0 -1.39 -.11 -2.77 -.11 -4.16 a 163.83 163.83 0 0 1 24.49 -86.4 l 32.55 40.26 z M 95.93 167.63 l 27.32 33.8 -68.79 88.48 a 165.78 165.78 0 0 1 -30.84 -43.32 z",
        fill="#222", fill_opacity=0.04
    ))
    dwg.add(shield_group)

    # Header (centered, with margin, dynamic font and wrapping)
    header_y = HEADER_HEIGHT/2 + 10
    if len(header_lines) == 1:
        dwg.add(dwg.text(header_lines[0],
            insert=(CARD_WIDTH_PX/2, header_y),
            text_anchor='middle',
            alignment_baseline='middle',
            font_size=header_font,
            font_family=FONT_FAMILY,
            fill=WHITE,
            font_weight='bold',
            letter_spacing=HEADER_LETTER_SPACING,
        ))
    else:
        y1 = HEADER_HEIGHT/2 - header_font/2 + 10
        y2 = HEADER_HEIGHT/2 + header_font/2 + 10
        dwg.add(dwg.text(header_lines[0],
            insert=(CARD_WIDTH_PX/2, y1),
            text_anchor='middle',
            alignment_baseline='middle',
            font_size=header_font,
            font_family=FONT_FAMILY,
            fill=WHITE,
            font_weight='bold',
            letter_spacing=HEADER_LETTER_SPACING,
        ))
        dwg.add(dwg.text(header_lines[1],
            insert=(CARD_WIDTH_PX/2, y2),
            text_anchor='middle',
            alignment_baseline='middle',
            font_size=header_font,
            font_family=FONT_FAMILY,
            fill=WHITE,
            font_weight='bold',
            letter_spacing=HEADER_LETTER_SPACING,
        ))

    y = HEADER_HEIGHT + PADDING
    # Render quote (if present) at the top, italicized and centered
    quote = power.get('quote', '')
    if quote:
        quote_lines = wrap_text_pixel(quote, desc_font, BODY_WIDTH - 20)
        if truncated and len(quote_lines) > 3:
            quote_lines = quote_lines[:3]
            quote_lines[-1] += '...'
        for line in quote_lines:
            dwg.add(dwg.text(line,
                insert=(CARD_WIDTH_PX/2, y),
                text_anchor='middle',
                font_size=desc_font,
                font_family=FONT_FAMILY,
                fill=BLACK,
                font_style='italic',
                style='font-style:italic;',
            ))
            y += desc_font + 6
        y += 12

    # Determine which fields are present, in canonical order
    present_fields = [f for f in FIELD_ORDER if f in power and power[f]]
    last_field = present_fields[-1] if present_fields else None

    effect_field_idx = None
    for idx, field in enumerate(present_fields):
        if field == 'effect':
            effect_field_idx = idx
            break

    underline_fields = {'power_set', 'action', 'duration', 'cost', 'effect'}  # unused now
    for idx, field in enumerate(present_fields):
        label = FIELD_LABELS.get(field, field.title())
        value = str(power[field])
        # Field label (navy, bold)
        dwg.add(dwg.text(f'{label}:',
            insert=(LABEL_X, y),
            font_size=label_font,
            font_family=FONT_FAMILY,
            fill="#223355",
            font_weight='bold',
        ))
        value_lines = wrap_text_pixel(value, value_font, BODY_WIDTH - 210)
        if truncated and len(value_lines) > 4:
            value_lines = value_lines[:4]
            value_lines[-1] += '...'
        value_y = y
        for vline in value_lines:
            dwg.add(dwg.text(vline,
                insert=(VALUE_X, value_y),
                font_size=value_font,
                font_family=FONT_FAMILY,
                fill="#222",
            ))
            value_y += value_font + 3
        value_y -= 3  # last value line baseline
        # Only add spacing between fields, no underlines
        y = value_y + value_font  # tighter spacing before next field

    # POWER text
    footer_text_y = CARD_HEIGHT_PX - FOOTER_HEIGHT/2 + 10
    dwg.add(dwg.text('POWER',
        insert=(CARD_WIDTH_PX/2, footer_text_y),
        text_anchor='middle',
        alignment_baseline='middle',
        font_size=36,
        font_family=FONT_FAMILY,
        fill=WHITE,
        font_weight='bold',
        letter_spacing=6,
    ))
    # Red underline under POWER (rounded rect, 200px wide, 6px high, centered at y=1060)
    dwg.add(dwg.rect(
        insert=(CARD_WIDTH_PX/2 - 100, 1060),
        size=(200, 6),
        fill="#c00",
        rx=3
    ))
    dwg.save()

def main():
    with open('marvel_powers.json', encoding='utf-8') as f:
        powers = json.load(f)
    for power in powers:
        draw_card(power)
    print(f"✅ Generated {len(powers)} SVG cards in the 'cards/' directory.")

if __name__ == '__main__':
    main() 