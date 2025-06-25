import os
import xml.etree.ElementTree as ET

SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)

FIELDS_TO_UNDERLINE = ['Power Set', 'Action', 'Duration', 'Cost', 'Effect']
LABEL_X = 45
VALUE_X = 255
LINE_X1 = str(LABEL_X)
LINE_X2 = str(750 - LABEL_X)
LINE_COLOR = '#e0e0e0'
LINE_WIDTH = '2'
Y_OFFSET = 4 # px below last value line


def add_lines_to_svg(svg_path, fields_to_underline=FIELDS_TO_UNDERLINE):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': SVG_NS}

    # Find all text elements
    texts = root.findall('.//svg:text', ns)
    # Build a list of (label, y, idx) for field labels
    label_positions = []
    for idx, t in enumerate(texts):
        txt = (t.text or '').strip(':')
        if txt in fields_to_underline and t.attrib.get('x') == str(LABEL_X):
            label_positions.append((txt, float(t.attrib['y']), idx))

    # For each label, find the last value line after it (until next label or end)
    for i, (label, label_y, label_idx) in enumerate(label_positions):
        # Skip the last field in the underline list
        if i == len(label_positions) - 1:
            continue
        # Find next label or end
        next_label_idx = label_positions[i+1][2] if i+1 < len(label_positions) else len(texts)
        # Find all value lines for this field
        value_ys = []
        for t in texts[label_idx+1:next_label_idx]:
            # Value lines are at VALUE_X
            if t.attrib.get('x') == str(VALUE_X):
                value_ys.append(float(t.attrib['y']))
        if value_ys:
            last_value_y = max(value_ys)
            line_y = last_value_y + Y_OFFSET
        else:
            # If no value lines, put line below label
            line_y = label_y + 32
        # Insert line element after the last value line
        line = ET.Element(f'{{{SVG_NS}}}line', {
            'x1': LINE_X1, 'x2': LINE_X2,
            'y1': str(line_y), 'y2': str(line_y),
            'stroke': LINE_COLOR, 'stroke-width': LINE_WIDTH
        })
        root.append(line)

    tree.write(svg_path, encoding='utf-8', xml_declaration=True)


def print_label_distances(svg_path, field_labels=FIELDS_TO_UNDERLINE):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': SVG_NS}
    texts = root.findall('.//svg:text', ns)
    label_ys = []
    for t in texts:
        txt = (t.text or '').strip(':')
        if txt in field_labels and t.attrib.get('x') == str(LABEL_X):
            label_ys.append(float(t.attrib['y']))
    label_ys.sort()
    distances = [label_ys[i+1] - label_ys[i] for i in range(len(label_ys)-1)]
    print(f'  Label y-positions: {label_ys}')
    print(f'  Distances between labels: {distances}')


def process_all_svgs(cards_dir='cards'):
    for fname in os.listdir(cards_dir):
        if fname.lower().endswith('.svg'):
            svg_path = os.path.join(cards_dir, fname)
            print(f'Processing {svg_path}...')
            add_lines_to_svg(svg_path)
            print_label_distances(svg_path)

if __name__ == '__main__':
    process_all_svgs() 