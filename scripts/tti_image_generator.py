from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os
import pandas as pd
import time
import argparse
from PIL import Image
import io

# model = "stable-diffusion-3.5-large"
model = "flux-schnell"

def convert_png_to_jpg_bytes(png_bytes, quality=85, optimize=True):
    """
    Convert PNG bytes to JPG bytes format.
    
    Args:
        png_bytes (bytes): PNG image data as bytes
        quality (int): JPG quality (1-100)
        optimize (bool): Whether to optimize the JPG
    
    Returns:
        bytes: JPG image data as bytes, or None if conversion failed
    """
    try:
        # Open the PNG image from bytes
        with Image.open(io.BytesIO(png_bytes)) as img:
            # Convert to RGB if necessary (JPG doesn't support transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPG bytes with specified quality and optimization
            jpg_buffer = io.BytesIO()
            img.save(
                jpg_buffer,
                'JPEG',
                quality=quality,
                optimize=optimize,
                progressive=True  # Progressive JPG for better web loading
            )
            
            return jpg_buffer.getvalue()
            
    except Exception as e:
        print(f"Error converting PNG to JPG: {str(e)}")
        return None

def generate_image_for_hanzi_example(chinese_text, definition_id, example_sn, api_key, quality=85, optimize=True):
    """Generate image for a single hanzi example using Chinese prompt"""
    file_name = f"hanzi_example_{definition_id}_{example_sn}.jpg"
    png_file_name = f"hanzi_example_{definition_id}_{example_sn}.png"
    if os.path.exists(f'./generated_images/{file_name}') or os.path.exists(f'./generated_images/{png_file_name}'):
        # print(f"- Skip. Image already exists for definition_id {definition_id}, example {example_sn}")
        return
    
    # Create a descriptive prompt that represents what the sentence describes
    prompt = f"场景插图：{chinese_text}\n要求：清晰生动的画面，适合学习记忆，高质量插图风格，不要有文字"
    
    print(f"Generating image for definition_id {definition_id}, example {example_sn}")
    print(f"Chinese text: {chinese_text}")
    print(f"Prompt: {prompt}")
    
    # 同步调用
    rsp = ImageSynthesis.call(model=model,
                              api_key=api_key,
                              prompt=prompt,
                              negative_prompt="garfield, cartoon, modern, digital art, abstract, text, calligraphy",
                              n=1,
                              size='768*512')
    
    if rsp.status_code == HTTPStatus.OK and rsp.output.task_status == "SUCCEEDED":
        print(f"Success! Generated image for definition_id {definition_id}")
        # print(f"Rsp.out:{rsp.output}")
        # print(f"Rsp.usage:{rsp.usage}")
        # 保存图片到当前文件夹，使用有意义的文件名
        for result in rsp.output.results:
            # Download the PNG image from the API
            png_content = requests.get(result.url).content
            
            # Convert PNG to JPG with specified quality and optimization settings
            # This reduces file size while maintaining good visual quality
            jpg_content = convert_png_to_jpg_bytes(png_content, quality, optimize)
            
            if jpg_content:
                # Save the converted JPG image
                with open(f'./generated_images/{file_name}', 'wb+') as f:
                    f.write(jpg_content)
                print(f"Saved JPG image as: {file_name} (quality: {quality})")
            else:
                # Fallback: save original PNG if conversion fails
                png_file_name = f"hanzi_example_{definition_id}_{example_sn}.png"
                with open(f'./generated_images/{png_file_name}', 'wb+') as f:
                    f.write(png_content)
                print(f"Conversion failed, saved PNG image as: {png_file_name}")
    else:
        print(f'Failed for definition_id {definition_id}, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.output.code, rsp.output.message))
        
    # Add a small delay to avoid rate limiting
    # time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description='Generate images for hanzi examples using DashScope API')
    parser.add_argument('--api-key', required=True, help='DashScope API key')
    parser.add_argument('--start-index', type=int, default=0, help='Starting index for processing (default: 0)')
    parser.add_argument('--end-index', type=int, help='Ending index for processing (default: all)')
    parser.add_argument('--quality', '-q', type=int, default=85, choices=range(1, 101), 
                       metavar='1-100', help='JPG quality (default: 85)')
    parser.add_argument('--no-optimize', action='store_true', 
                       help='Disable JPG optimization (faster but larger files)')
    
    args = parser.parse_args()
    
    # Validate API key
    if not args.api_key or args.api_key.strip() == '':
        print("Error: API key is required")
        return
    
    print(f"Starting image generation with API key: {args.api_key[:10]}...")
    print(f"JPG Quality: {args.quality}")
    print(f"JPG Optimization: {not args.no_optimize}")
    
    # Create output directory if it doesn't exist
    os.makedirs('./generated_images', exist_ok=True)
    
    # Read the reranked CSV file
    csv_path = 'others/hanzi_examples_v7_reranked.csv'
    df = pd.read_csv(csv_path)
    
    # Apply index filtering if specified
    if args.end_index:
        df = df.iloc[args.start_index:args.end_index]
    else:
        df = df.iloc[args.start_index:]
    
    print(f"Processing {len(df)} hanzi examples (from index {args.start_index})")
    
    size = len(df)
    # Process each example
    for index, row in df.iterrows():
        definition_id = row['definition_id']
        example_sn = row['example_sn']
        chinese_text = row['example_cn']
        
        # print(f"\n\n[{index}/{size}]")
        # Skip if Chinese text is empty or NaN
        if pd.isna(chinese_text) or chinese_text.strip() == '':
            print(f"Skipping empty Chinese text for definition_id {definition_id}")
            continue
            
        try:
            generate_image_for_hanzi_example(chinese_text, definition_id, example_sn, args.api_key, 
                                           args.quality, not args.no_optimize)
        except Exception as e:
            print(f"Error processing definition_id {definition_id}: {str(e)}")
            continue

if __name__ == '__main__':
    main()