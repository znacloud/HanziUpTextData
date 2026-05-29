import pandas as pd
import json
import sys
import os
import math

# Add the scripts directory to the path to import pinyin_converter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pinyin_converter import pinyin_to_number

    # EDUCATIONAL_VOICES = {
    # "beginner": "zh-CN-XiaoxiaoNeural",      # Clear, friendly female
    # "intermediate": "zh-CN-YunxiNeural",     # Young male, good for learning
    # "advanced": "zh-CN-YunyangNeural",       # Mature male, authoritative
    # "children": "zh-CN-XiaoyiNeural",        # Young female, very clear
    # "formal": "zh-CN-YunjianNeural"          # Formal, news-like
    # }
def generate_pinyin_ssml(pinyin, voice_name="zh-CN-XiaoqiuNeural"):
    """
    Generate SSML for pinyin pronunciation using pinyin_converter.
    
    Args:
        pinyin (str): Pinyin string (e.g., "wǒ men", "de", "zhōng guó")
        voice_name (str): Azure TTS voice name
    
    Returns:
        str: SSML markup for the pinyin pronunciation
    """
    
    # Split pinyin by spaces for multi-character words
    pinyin_parts = pinyin.split()
    
    if len(pinyin_parts) == 1:
        # Single character - simple pronunciation
        return generate_single_pinyin_ssml(pinyin, voice_name)
    else:
        # Multi-character word - character-by-character pronunciation
        return generate_multi_pinyin_ssml(pinyin_parts, voice_name)

def get_pitch_for_tone(tone_num):
    """
    Map Mandarin tone number to SSML pitch value.
    """
    # tone_pitch_map = {
    #     '1': '+1.0st',   # High level
    #     '2': '+0.6st',   # Rising
    #     '3': '+0.2st',   # Falling-rising
    #     '4': '-0.2st',   # Falling
    #     '5': '0st'       # Neutral
    # }
    tone_pitch_map = {
        '1': '0st',   # High level
        '2': '-0.4st',   # Rising
        '3': '-0.8st',   # Falling-rising
        '4': '-1.2st',   # Falling
        '5': '-1st'       # Neutral
    }
    return tone_pitch_map.get(str(tone_num), '0st')


def generate_single_pinyin_ssml(pinyin, voice_name):
    """
    Generate SSML for single pinyin pronunciation, adjusting pitch by tone, using x-loud volume, and adding emphasis.
    """
    phoneme_result = pinyin_to_number(pinyin)
    parts = phoneme_result.split()
    if len(parts) == 2:
        phoneme, tone_num = parts
    else:
        phoneme, tone_num = phoneme_result, '5'
    pitch = get_pitch_for_tone(tone_num)
    rate = get_rate_for_syllable(phoneme_result.split()[0])
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
    <voice name="{voice_name}">
        <prosody rate="{rate}" volume="x-loud">
            <emphasis>
                <phoneme alphabet="sapi" ph="{phoneme_result}">{pinyin}</phoneme>
            </emphasis>
        </prosody>
    </voice>
</speak>'''
    return ssml

def get_rate_for_syllable(syllable):
    """
    Determine the SSML rate for a syllable based on its length.
    Uses a smooth, granular mapping for more natural results.
    Shorter syllables get a faster rate, longer ones slower.
    """
    # Remove tone numbers and non-alpha chars for length calculation
    # base = ''.join([c for c in syllable if c.isalpha()])
    length = len(syllable)
    # Base rate and minimum rate
    base_rate = 0.6
    min_rate = 0.5
    # For each extra letter above 2, slow down by 0.04
    # e.g., da (2) -> 0.68, dai (3) -> 0.64, zhuang (6) -> 0.48 (but clamp to min_rate)
    rate = base_rate - max(0, (length - 2)) * 0.025
    rate = max(rate, min_rate)
    # Round to 2 decimal places for SSML
    return f"{rate:.2f}"


def generate_multi_pinyin_ssml(pinyin_parts, voice_name):
    """
    Generate SSML for multi-character pinyin with clear character separation, adjusting pitch by tone, rate by syllable length, using x-loud volume, and adding emphasis.
    """
    ssml_parts = []
    for i, part in enumerate(pinyin_parts):
        if part == 'r':
            phoneme_result = 'er 5'
            tone_num = '5'
        else:
            phoneme_result = pinyin_to_number(part)
            split_parts = phoneme_result.split()
            if len(split_parts) == 2:
                _, tone_num = split_parts
            else:
                tone_num = '5'
        pitch = get_pitch_for_tone(tone_num)
        rate = get_rate_for_syllable(phoneme_result.split()[0])
        ssml_parts.append(f'''
        <prosody rate="{rate}" volume="x-loud">
            <emphasis>
                <phoneme alphabet="sapi" ph="{phoneme_result}">{part}</phoneme>
            </emphasis>
        </prosody>''')
        # if i < len(pinyin_parts) - 1:
        #     ssml_parts.append('<break time="50ms"/>')
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
    <voice name="{voice_name}">
        {''.join(ssml_parts)}
    </voice>
</speak>'''
    return ssml

def process_all_pinyin_data():
    """
    Process all pinyin data from CSV files and generate SSML for unique pronunciations only.
    """
    
    # Read pinyin data
    pinyin_df = pd.read_csv('jjhy_csv/core_pinyin/jjhy_pinyin_spaced_fixed.csv')
    
    # Get unique pinyin entries first
    unique_pinyin = pinyin_df['updated_pinyin'].unique()
    
    print(f"Found {len(pinyin_df)} total pinyin entries")
    print(f"Found {len(unique_pinyin)} unique pinyin pronunciations")
    
    pinyin_to_ssml_map = {}
    
    for pinyin in unique_pinyin:
        # Generate SSML only for unique pinyin
        ssml = generate_pinyin_ssml(pinyin)
        pinyin_to_ssml_map[pinyin] = ssml
    
    return pinyin_to_ssml_map



def test_pinyin_conversion():
    """
    Test the pinyin conversion and SSML generation.
    """
    
    test_cases = [
        "de",           # Single character
        "rén",          # Single character with tone
        "wǒ men",       # Two characters
        "zhōng guó",    # Two characters
        "xué xí",       # Two characters
        "dǎ diàn huà",  # Three characters
        "lǎo shī",      # Two characters
        "nǚ ér"         # Two characters with ü
    ]
    
    print("=== PINYIN CONVERSION TEST ===")
    for pinyin in test_cases:
        print(f"\n--- {pinyin} ---")
        
        # Test pinyin converter
        phoneme_result = pinyin_to_number(pinyin)
        print(f"Phoneme: {phoneme_result}")
        
        # Test SSML generation
        ssml = generate_pinyin_ssml(pinyin)
        print(f"SSML: {ssml}")

def main():
    """
    Main function to process all data and generate SSML.
    """
    
    print("Starting pinyin SSML generation...")
    
    # Test the conversion first
    test_pinyin_conversion()
    
    print("\n" + "="*50)
    print("Processing all pinyin data...")
    
    # Process all data and get unique pinyin to SSML map
    pinyin_to_ssml_map = process_all_pinyin_data()
    
    # Save the unique pinyin to SSML map
    with open('voice_data/jjhy_core_pinyin_to_ssml_map.json', 'w', encoding='utf-8') as f:
        json.dump(pinyin_to_ssml_map, f, ensure_ascii=False, indent=2)
    
    print(f"Saved unique pinyin to SSML map with {len(pinyin_to_ssml_map)} entries to pinyin_to_ssml_map.json")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Unique pinyin pronunciations: {len(pinyin_to_ssml_map)}")
    
    # Count multi-character words
    multi_char_count = sum(1 for pinyin in pinyin_to_ssml_map.keys() if len(pinyin.split()) > 1)
    print(f"Multi-character words: {multi_char_count}")
    
    # Show some examples
    print("\n=== EXAMPLES ===")
    for i, (pinyin, ssml) in enumerate(list(pinyin_to_ssml_map.items())[:5]):
        print(f"{i+1}. {pinyin}")
        print(f"   SSML: {ssml}")
        print()

if __name__ == "__main__":
    main() 