import json
import os
import requests
import time
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MicrosoftTTSGenerator:
    def __init__(self, subscription_key, region, voice_name="zh-CN-XiaoqiuNeural"):
        """
        Initialize Microsoft TTS generator.
        
        Args:
            subscription_key (str): Azure Speech Service subscription key
            region (str): Azure region (e.g., "eastus", "westeurope")
            voice_name (str): Voice name to use for synthesis
        """
        self.subscription_key = subscription_key
        self.region = region
        self.voice_name = voice_name
        self.base_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        self.headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
            'User-Agent': 'HanziUpTTSGenerator'
        }
    
    def generate_audio(self, ssml, output_filename):
        """
        Generate audio file from SSML.
        
        Args:
            ssml (str): SSML markup
            output_filename (str): Output audio file path
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=ssml.encode('utf-8')
            )
            
            if response.status_code == 200:
                # Save audio file
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Error generating audio: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return False
    
    def sanitize_filename(self, pinyin):
        """
        Sanitize pinyin string to create valid filename.
        
        Args:
            pinyin (str): Pinyin string
        
        Returns:
            str: Sanitized filename
        """
        # Replace spaces with underscores
        filename = pinyin.replace(' ', '_')
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename

def load_pinyin_ssml_map(json_file):
    """
    Load pinyin to SSML mapping from JSON file.
    
    Args:
        json_file (str): Path to JSON file
    
    Returns:
        dict: Pinyin to SSML mapping
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {str(e)}")
        return {}

def create_output_directory(output_dir):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir (str): Output directory path
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

def generate_voice_files(pinyin_ssml_map, tts_generator, output_dir, start_index=0, end_index=None, delay=0.1):
    """
    Generate voice files for pinyin pronunciations.
    
    Args:
        pinyin_ssml_map (dict): Pinyin to SSML mapping
        tts_generator (MicrosoftTTSGenerator): TTS generator instance
        output_dir (str): Output directory for audio files
        start_index (int): Starting index for processing
        end_index (int): Ending index for processing (None for all)
        delay (float): Delay between requests in seconds
    
    Returns:
        tuple: (success_count, total_count)
    """
    pinyin_list = list(pinyin_ssml_map.keys())
    
    if end_index is None:
        end_index = len(pinyin_list)
    
    pinyin_list = pinyin_list[start_index:end_index]
    total_count = len(pinyin_list)
    success_count = 0
    skip_count = 0
    
    print(f"Generating voice files for {total_count} pinyin pronunciations...")
    print(f"Output directory: {output_dir}")
    print(f"Voice: {tts_generator.voice_name}")
    print("-" * 50)
    
    for i, pinyin in enumerate(pinyin_list, start=start_index + 1):
        ssml = pinyin_ssml_map[pinyin]
        
        # Create sanitized filename
        filename = tts_generator.sanitize_filename(pinyin)
        output_filename = os.path.join(output_dir, f"{filename}.mp3")
        # Check if file already exists
        if os.path.exists(output_filename):
            # print(f" - Skipping: {pinyin} -> {output_filename} (already exists)")
            skip_count += 1
            continue
        
        print(f"[{i}/{total_count}] Generating: {pinyin} -> {output_filename}")
        
        # Generate audio
        if tts_generator.generate_audio(ssml, output_filename):
            success_count += 1
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed")
        
        # Add delay to avoid rate limiting
        if delay > 0 and i < total_count:
            time.sleep(delay)
    
    return success_count, total_count, skip_count

def main():
    parser = argparse.ArgumentParser(description='Generate voice files using Microsoft TTS')
    parser.add_argument('--subscription-key', default=os.getenv('MS_KEY'), help='Azure Speech Service subscription key')
    parser.add_argument('--region', default='australiaeast', help='Azure region (e.g., eastus, westeurope)')
    parser.add_argument('--voice', default='zh-CN-XiaoqiuNeural', help='Voice name to use')
    parser.add_argument('--input', default='voice_data/pinyin_to_ssml_map.json', help='Input JSON file with pinyin to SSML mapping')
    parser.add_argument('--output', default='voice_data/voice_files', help='Output directory for audio files')
    parser.add_argument('--start', type=int, default=0, help='Starting index for processing')
    parser.add_argument('--end', type=int, default=None, help='Ending index for processing')
    parser.add_argument('--delay', type=float, default=0.1, help='Delay between requests in seconds')
    parser.add_argument('--test', action='store_true', help='Test with first 5 pronunciations only')
    
    args = parser.parse_args()
    
    # Load pinyin to SSML mapping
    print(f"Loading pinyin to SSML mapping from {args.input}...")
    pinyin_ssml_map = load_pinyin_ssml_map(args.input)
    
    if not pinyin_ssml_map:
        print("Failed to load pinyin to SSML mapping. Exiting.")
        return
    
    print(f"Loaded {len(pinyin_ssml_map)} pinyin pronunciations")
    
    # Create output directory
    create_output_directory(args.output)
    
    # Initialize TTS generator
    tts_generator = MicrosoftTTSGenerator(
        subscription_key=args.subscription_key,
        region=args.region,
        voice_name=args.voice
    )
    
    # Adjust end index for test mode
    if args.test:
        args.end = min(5, len(pinyin_ssml_map))
        print(f"TEST MODE: Processing first {args.end} pronunciations only")
    
    # Generate voice files
    success_count, total_count, skip_count = generate_voice_files(
        pinyin_ssml_map=pinyin_ssml_map,
        tts_generator=tts_generator,
        output_dir=args.output,
        start_index=args.start,
        end_index=args.end,
        delay=args.delay
    )
    
    # Print summary
    print("\n" + "=" * 50)
    print("GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total processed: {total_count}")
    print(f"Skipped: {skip_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count - skip_count}")
    print(f"Success rate: {(success_count/max(1,total_count-skip_count))*100:.1f}%")
    print(f"Output directory: {args.output}")

if __name__ == "__main__":
    main() 