import re
import json
from bs4 import BeautifulSoup
import quopri

def decode_mhtml_file(filename='marvel_powers.html'):
    """
    Decode MHTML file and return the HTML content.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found!")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None
    
    # Check if it's MHTML/encoded content
    if '=3D' in html_content:
        print("🔄 Decoding MHTML content...")
        try:
            decoded = quopri.decodestring(html_content).decode('latin-1')
            print("✅ Successfully decoded MHTML content!")
            return decoded
        except Exception as e:
            print(f"❌ Failed to decode: {e}")
            return None
    
    return html_content

def field_to_key(field):
    """
    Map field names to snake_case keys.
    """
    return field.strip().lower().replace(' ', '_').replace('-', '_')

def extract_field_value(element):
    """
    Extract the value from a field element, handling various HTML structures.
    """
    # Get the text content of the element
    text = element.get_text().strip()
    
    # Remove the field name (everything before the colon)
    if ':' in text:
        # Find the first colon and get everything after it
        colon_pos = text.find(':')
        value = text[colon_pos + 1:].strip()
        return value
    
    return text

def parse_marvel_powers(filename='marvel_powers.html'):
    """
    Parse Marvel powers from the HTML file and return structured data.
    """
    # Decode the file first
    html_content = decode_mhtml_file(filename)
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all h3 tags with class="normal" (these are power names)
    power_h3_tags = soup.find_all('h3', class_='normal')
    
    powers = []
    
    for h3_tag in power_h3_tags:
        power = {}
        power['power'] = h3_tag.get_text().strip()
        
        # Find the next sibling elements that contain power details
        description = ""
        fields = {}
        
        # Start from the h3 tag and look through siblings until the next h3.normal
        current_element = h3_tag.find_next_sibling()
        
        while current_element and not (current_element.name == 'h3' and 'normal' in (current_element.get('class') or [])):
            if current_element.name == 'p':
                # Look for description (em tag)
                em_tag = current_element.find('em')
                if em_tag and not description:
                    description = em_tag.get_text().strip()
                
                # Look for field labels (strong tags)
                strong_tags = current_element.find_all('strong')
                for strong in strong_tags:
                    field_text = strong.get_text().strip()
                    if ':' in field_text:
                        field_name = field_text.rstrip(':')
                        # Get the value after the strong tag
                        value = ""
                        
                        # Try to get text after the strong tag
                        next_sibling = strong.next_sibling
                        if next_sibling:
                            value = next_sibling.strip()
                        
                        # If no direct sibling, try to get remaining text from the paragraph
                        if not value:
                            full_text = current_element.get_text().strip()
                            field_start = full_text.find(field_text)
                            if field_start != -1:
                                value_start = field_start + len(field_text)
                                value = full_text[value_start:].strip()
                        
                        if value:
                            fields[field_to_key(field_name)] = value
                    else:
                        # Handle fields without colons (like "Power Set")
                        field_name = field_text
                        # Get the value from the rest of the paragraph
                        full_text = current_element.get_text().strip()
                        field_start = full_text.find(field_text)
                        if field_start != -1:
                            value_start = field_start + len(field_text)
                            value = full_text[value_start:].strip()
                            if value:
                                fields[field_to_key(field_name)] = value
            
            current_element = current_element.find_next_sibling()
        
        if description:
            power['description'] = description
        
        # Add all extracted fields to the power
        power.update(fields)
        powers.append(power)
    
    return powers

def save_powers_to_json(powers, filename='marvel_powers.json'):
    """
    Save the parsed powers to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(powers, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(powers)} powers to {filename}")

def print_power_summary(powers):
    """
    Print a summary of the parsed powers.
    """
    print(f"\n📊 Parsed {len(powers)} powers:")
    
    # Show first few powers as examples
    for i, power in enumerate(powers[:5]):
        print(f"\n{i+1}. {power['power']}")
        if 'description' in power:
            print(f"   Description: {power['description'][:100]}...")
        
        # Show field names
        field_names = [k for k in power.keys() if k not in ('power', 'description')]
        if field_names:
            print(f"   Fields: {', '.join(field_names)}")
    
    # Count common field types
    all_fields = set()
    for power in powers:
        all_fields.update([k for k in power.keys() if k not in ('power', 'description')])
    
    print(f"\n🔍 Found {len(all_fields)} unique field types:")
    for field in sorted(all_fields):
        count = sum(1 for power in powers if field in power)
        print(f"   {field}: {count} powers")

def parse_marvel_powers_txt(filename='marvel_powers.txt'):
    """
    Parse Marvel powers from a raw text file and return structured data.
    Structure:
    - First line: power name
    - Second line: quote
    - Remaining lines: fields (Field: Value), always ending with Effect
    - Powers separated by a new power name (not by blank lines)
    """
    import re
    powers = []
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f]
    field_pattern = re.compile(r'^([A-Za-z][A-Za-z \-]*):\s*(.*)$')
    current_block = []
    last_was_blank = True
    for line in lines:
        if not line.strip():
            last_was_blank = True
            continue
        # New power name: non-empty line after a blank, not a field
        if last_was_blank and not field_pattern.match(line):
            if current_block:
                powers.append(current_block)
                current_block = []
            current_block.append(line.strip())
        else:
            current_block.append(line.strip())
        last_was_blank = False
    if current_block:
        powers.append(current_block)
    # Now parse each block
    parsed_powers = []
    for block in powers:
        block_lines = [l for l in block if l]
        if len(block_lines) < 3:
            continue
        power = {}
        power['power'] = block_lines[0]
        power['quote'] = block_lines[1]
        i = 2
        last_field = None
        while i < len(block_lines):
            m = field_pattern.match(block_lines[i])
            if m:
                field = m.group(1).strip()
                value = m.group(2).strip()
                key = field.lower().replace(' ', '_').replace('-', '_')
                # If this is the Effect field, it may be multi-line (but always last)
                if key == 'effect':
                    effect_lines = [value]
                    i += 1
                    while i < len(block_lines):
                        effect_lines.append(block_lines[i])
                        i += 1
                    power[key] = ' '.join(effect_lines).strip()
                    break  # Effect is always last
                else:
                    power[key] = value
                last_field = key
            else:
                # Multi-line field value (rare, but possible)
                if last_field:
                    power[last_field] += ' ' + block_lines[i]
            i += 1
        parsed_powers.append(power)
    return parsed_powers

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--txt':
        print("🚀 Starting Marvel Powers TXT Parser...")
        powers = parse_marvel_powers_txt()
        if powers:
            print_power_summary(powers)
            save_powers_to_json(powers, 'marvel_powers.json')
        else:
            print("❌ No powers found!")
    else:
        print("🚀 Starting Marvel Powers Parser...")
        powers = parse_marvel_powers()
        
        if powers:
            print_power_summary(powers)
            save_powers_to_json(powers)
        else:
            print("❌ No powers found!") 