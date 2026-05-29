"""
Script to replace specific colors in all GIF files in strokeorder_gifs directory.
Supports exact color matching with tolerance.
"""

import os
from pathlib import Path
import imageio
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
import csv


def add_watermark_to_frame(frame, watermark_icon=None, watermark_text=None, 
                           region=None, text_color=(255, 255, 255), 
                           font=None):
    """
    Add watermark (icon + text) to a frame in the specified region.
    
    Args:
        frame: NumPy array of the frame
        watermark_icon: Pre-loaded and pre-resized PIL Image object for icon (or None)
        watermark_text: Text to display
        region: Tuple (x1, y1, x2, y2) defining the watermark area
        text_color: RGB tuple for text color
        font: Pre-loaded PIL ImageFont object (or None to use default)
    
    Returns:
        Modified frame as NumPy array
    """
    if region is None:
        return frame
    
    x1, y1, x2, y2 = region
    pil_img = Image.fromarray(frame)
    
    # Add icon if provided (icon is already resized)
    if watermark_icon is not None:
        # Position icon on the left side of region
        icon_x = x1 + 5
        icon_y = y1 + (y2 - y1 - watermark_icon.height) // 2
        
        # Paste icon with transparency if available
        if watermark_icon.mode == 'RGBA':
            pil_img.paste(watermark_icon, (icon_x, icon_y), watermark_icon)
        else:
            pil_img.paste(watermark_icon, (icon_x, icon_y))
        
        icon_width = watermark_icon.width
    else:
        icon_width = 0
    
    # Add text if provided
    if watermark_text:
        draw = ImageDraw.Draw(pil_img)
        
        # Use provided font or default
        text_font = font if font is not None else ImageFont.load_default()
        
        # Position text to the right of icon
        text_x = x1 + icon_width + 10
        text_y = y1 + (y2 - y1 - (font.size if font else 11)) // 2
        
        draw.text((text_x, text_y), watermark_text, fill=text_color, font=text_font)
    
    return np.array(pil_img)


def replace_color_in_gif(input_path, output_path, color_pairs=None, tolerance=10, regions=None, region_colors=None, exclude_colors=None, exclusive_tolerance=0, loaded_watermark_icon=None, watermark_text=None, watermark_region=None, watermark_text_color=(255,255,255), loaded_watermark_font=None):
    """
    Replace specific colors in all frames of a GIF.
    
    Args:
        input_path: Path to input GIF
        output_path: Path to save modified GIF
        color_pairs: List of tuples [(old_color1, new_color1), (old_color2, new_color2), ...]
                    Each color is an RGB tuple (r, g, b)
        tolerance: Color matching tolerance (0-255)
        regions: Optional list of tuples [(x1, y1, x2, y2), ...] defining rectangular areas to fill
        region_colors: Optional list of RGB tuples for filling each region. If single color provided, uses for all regions.
        exclude_colors: Optional list of RGB tuples to exclude from region fill
        exclusive_tolerance: Tolerance for matching excluded colors (0-255)
        loaded_watermark_icon: Pre-loaded and pre-resized PIL Image object for watermark icon
        watermark_text: Text for watermark
        watermark_region: Region tuple (x1,y1,x2,y2) for watermark placement
        watermark_text_color: RGB tuple for watermark text color
        loaded_watermark_font: Pre-loaded PIL ImageFont object for watermark text
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read all frames
        frames = imageio.mimread(input_path)
        modified_frames = []
        
        for frame in frames:
            img = frame.copy()
            height, width = img.shape[:2]
            
            # First: Replace colors globally using color pairs
            if color_pairs:
                for old_color, new_color in color_pairs:
                    # Create mask for colors matching old_color within tolerance
                    if tolerance == 0:
                        # Exact color match
                        mask = np.all(img == old_color, axis=-1)
                    else:
                        # Color match with tolerance
                        diff = np.abs(img.astype(int) - np.array(old_color))
                        mask = np.all(diff <= tolerance, axis=-1)
                    
                    # Replace color
                    img[mask] = new_color
            
            # Second: Fill regions with their respective colors
            if regions is not None and region_colors is not None:
                for i, region in enumerate(regions):
                    x1, y1, x2, y2 = region
                    # Clamp coordinates to image bounds
                    x1 = max(0, min(x1, width))
                    x2 = max(0, min(x2, width))
                    y1 = max(0, min(y1, height))
                    y2 = max(0, min(y2, height))
                    
                    # Use corresponding color, or last color if not enough colors provided
                    region_color = region_colors[i] if i < len(region_colors) else region_colors[-1]
                    
                    # Create mask for region
                    region_img = img[y1:y2, x1:x2].copy()
                    mask = np.ones((y2-y1, x2-x1), dtype=bool)
                    
                    # Exclude specific colors if specified
                    if exclude_colors:
                        for exclude_color in exclude_colors:
                            # Create exclusion mask
                            if exclusive_tolerance == 0:
                                exclude_mask = np.all(region_img == exclude_color, axis=-1)
                            else:
                                diff = np.abs(region_img.astype(int) - np.array(exclude_color))
                                exclude_mask = np.all(diff <= exclusive_tolerance, axis=-1)
                            # Remove excluded pixels from mask
                            mask = mask & ~exclude_mask
                    
                    # Apply region color only to non-excluded pixels
                    region_img[mask] = region_color
                    img[y1:y2, x1:x2] = region_img

                # Do the region filling again for only last region by ignoring exclude colors
                if regions is not None and region_colors is not None and len(regions) > 0:
                    last_region = regions[-1]
                    x1, y1, x2, y2 = last_region
                    x1 = max(0, min(x1, width))
                    x2 = max(0, min(x2, width))
                    y1 = max(0, min(y1, height))
                    y2 = max(0, min(y2, height))
                    last_region_color = region_colors[-1]
                    region_img = img[y1:y2, x1:x2].copy()
                    mask = np.ones((y2-y1, x2-x1), dtype=bool)
                    region_img[mask] = last_region_color
                    img[y1:y2, x1:x2] = region_img
            
            # Add watermark if specified
            if loaded_watermark_icon or watermark_text:
                img = add_watermark_to_frame(
                    img, 
                    watermark_icon=loaded_watermark_icon,
                    watermark_text=watermark_text,
                    region=watermark_region,
                    text_color=watermark_text_color,
                    font=loaded_watermark_font
                )
            
            modified_frames.append(img)
        
        # Save modified GIF with original duration and infinite loop
        imageio.mimsave(output_path, modified_frames, duration=0.1, loop=0)
        return True
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def batch_replace_color(
    input_dir,
    output_dir,
    color_pairs=None,
    tolerance=10,
    regions=None,
    region_colors=None,
    exclude_colors=None,
    exclusive_tolerance=0,
    watermark_icon=None,
    watermark_text=None,
    watermark_region=None,
    watermark_text_color=(255,255,255),
    watermark_font_size=20,
    watermark_font_path=None,
    overwrite=False,
    test=False,
    filter_csv=None
):
    """
    Batch process all GIF files in a directory.
    
    Args:
        input_dir: Directory containing input GIFs
        output_dir: Directory to save modified GIFs
        color_pairs: List of tuples [(old_color1, new_color1), (old_color2, new_color2), ...]
        tolerance: Color matching tolerance
        regions: Optional list of tuples [(x1, y1, x2, y2), ...] for rectangular areas to fill
        region_colors: Optional list of RGB tuples for filling each region
        exclude_colors: Optional list of RGB tuples to exclude from region fill
        overwrite: If True, overwrite files in input_dir; if False, save to output_dir
        test: If True, only process the first file for testing
        filter_csv: Path to CSV file containing gif_filename column to filter which GIFs to process
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir) if not overwrite else input_path
    
    # Load watermark resources once for all GIF files
    loaded_icon = None
    loaded_font = None
    
    if watermark_icon and os.path.exists(watermark_icon):
        try:
            loaded_icon = Image.open(watermark_icon)
            # Resize icon once based on watermark region
            if watermark_region:
                x1, y1, x2, y2 = watermark_region
                region_height = y2 - y1
                icon_height = int(region_height * 0.8)
                aspect_ratio = loaded_icon.width / loaded_icon.height
                icon_width = int(icon_height * aspect_ratio)
                loaded_icon = loaded_icon.resize((icon_width, icon_height), Image.Resampling.LANCZOS)
            print(f"Loaded watermark icon")
        except Exception as e:
            print(f"Warning: Failed to load watermark icon: {e}")
    
    if watermark_text:
        try:
            if watermark_font_path and os.path.exists(watermark_font_path):
                loaded_font = ImageFont.truetype(watermark_font_path, watermark_font_size)
            else:
                # Try to use a default system font
                try:
                    loaded_font = ImageFont.truetype("arial.ttf", watermark_font_size)
                except:
                    loaded_font = ImageFont.load_default(watermark_font_size)
            print(f"Loaded watermark font")
        except Exception as e:
            print(f"Warning: Failed to load font, using default: {e}")
            loaded_font = ImageFont.load_default(watermark_font_size)
    
    # Load CSV filter if specified
    allowed_gif_filenames = None
    if filter_csv:
        csv_path = Path(filter_csv)
        if csv_path.exists():
            try:
                allowed_gif_filenames = set()
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'gif_filename' in row:
                            allowed_gif_filenames.add(row['gif_filename'])
                print(f"Loaded {len(allowed_gif_filenames)} GIF filenames from {filter_csv}")
            except Exception as e:
                print(f"Warning: Failed to load CSV filter: {e}")
                allowed_gif_filenames = None
        else:
            print(f"Warning: CSV file not found: {filter_csv}")
    
    # Create output directory if it doesn't exist
    if not overwrite:
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all GIF files
    gif_files = list(input_path.glob("*.gif"))
    
    # Filter by CSV if specified
    if allowed_gif_filenames:
        original_count = len(gif_files)
        gif_files = [f for f in gif_files if f.name in allowed_gif_filenames]
        print(f"Filtered from {original_count} to {len(gif_files)} GIF files based on CSV")
    
    if not gif_files:
        print(f"No GIF files found in {input_dir}")
        return
    
    # Limit to one file in test mode
    if test:
        gif_files = gif_files[:1]
        print(f"TEST MODE: Processing only 1 file: {gif_files[0].name}")
    else:
        print(f"Found {len(gif_files)} GIF files")
    
    # Show what operations will be performed
    if color_pairs:
        print(f"Global color replacements (tolerance: {tolerance}):")
        for old_color, new_color in color_pairs:
            print(f"  {old_color} -> {new_color}")
    if regions:
        if region_colors:
            print(f"Region fills:")
            for i, region in enumerate(regions):
                region_color = region_colors[i] if i < len(region_colors) else region_colors[-1]
                print(f"  {region} -> {region_color}")
        if exclude_colors:
            print(f"  Excluding colors: {exclude_colors}")
    
    print(f"Output directory: {output_path}")
    
    # Process each GIF
    success_count = 0
    fail_count = 0
    
    for gif_file in tqdm(gif_files, desc="Processing GIFs"):
        output_file = output_path / gif_file.name
        
        if replace_color_in_gif(gif_file, output_file, color_pairs, tolerance, regions, region_colors, exclude_colors, exclusive_tolerance, loaded_icon, watermark_text, watermark_region, watermark_text_color, loaded_font):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\nCompleted!")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {fail_count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Replace colors in GIF files")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="strokeorder_gifs",
        help="Input directory containing GIF files"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="strokeorder_gifs_modified",
        help="Output directory for modified GIFs (ignored if --overwrite is set)"
    )
    parser.add_argument(
        "--old-color",
        type=str,
        default=None,
        help="RGB color to replace (e.g., '255,255,255' for white). Can be used multiple times with --new-color."
    )
    parser.add_argument(
        "--new-color",
        type=str,
        default=None,
        help="RGB replacement color (e.g., '0,0,0' for black). Can be used multiple times with --old-color."
    )
    parser.add_argument(
        "--color-pairs",
        type=str,
        default=None,
        help="Multiple color pairs in format 'old1_r,g,b:new1_r,g,b;old2_r,g,b:new2_r,g,b' (e.g., '255,255,255:0,0,0;100,186,244:251,243,255')"
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=10,
        help="Color matching tolerance (0-255). Higher values match more similar colors."
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Rectangular region(s) to fill. Single: 'x1,y1,x2,y2'. Multiple: 'x1,y1,x2,y2;x1,y1,x2,y2' (e.g., '10,20,100,150;200,300,400,450')."
    )
    parser.add_argument(
        "--region-color",
        type=str,
        default=None,
        help="RGB color(s) for filling regions. Single: 'r,g,b'. Multiple: 'r,g,b;r,g,b' (e.g., '255,0,0;0,255,0'). If fewer colors than regions, last color is reused."
    )
    parser.add_argument(
        "--exclude-colors",
        type=str,
        default=None,
        help="Colors to exclude from region fill, separated by semicolons (e.g., '255,255,255;0,0,0' excludes white and black)"
    )
    parser.add_argument(
        "--exclusive-tolerance",
        type=int,
        default=0,
        help="Tolerance for matching excluded colors (default: 0 for exact match)"
    )
    parser.add_argument(
        "--watermark-icon",
        type=str,
        default=None,
        help="Path to watermark icon image (PNG with transparency recommended)"
    )
    parser.add_argument(
        "--watermark-text",
        type=str,
        default=None,
        help="Text to display in watermark"
    )
    parser.add_argument(
        "--watermark-region",
        type=str,
        default=None,
        help="Region for watermark in format 'x1,y1,x2,y2' (e.g., '300,460,490,490')"
    )
    parser.add_argument(
        "--watermark-text-color",
        type=str,
        default="255,255,255",
        help="RGB color for watermark text (default: white '255,255,255')"
    )
    parser.add_argument(
        "--watermark-font-size",
        type=int,
        default=20,
        help="Font size for watermark text (default: 20)"
    )
    parser.add_argument(
        "--watermark-font",
        type=str,
        default=None,
        help="Path to TTF font file for watermark text"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original files instead of creating new ones"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: only process the first file for testing"
    )
    parser.add_argument(
        "--filter-csv",
        type=str,
        default=None,
        help="Path to CSV file with 'gif_filename' column to filter which GIFs to process (e.g., 'hanzi_gifs.csv')"
    )
    
    args = parser.parse_args()
    
    # Parse color pairs
    color_pairs = []
    
    if args.color_pairs:
        # Parse multiple pairs from --color-pairs
        try:
            pairs = args.color_pairs.split(";")
            for pair in pairs:
                old_str, new_str = pair.split(":")
                old_color = tuple(map(int, old_str.split(",")))
                new_color = tuple(map(int, new_str.split(",")))
                if len(old_color) != 3 or len(new_color) != 3:
                    print("Error: Colors must be in RGB format")
                    exit(1)
                color_pairs.append((old_color, new_color))
        except ValueError:
            print("Error: --color-pairs must be in format 'r,g,b:r,g,b;r,g,b:r,g,b'")
            exit(1)
    elif args.old_color and args.new_color:
        # Parse single pair from --old-color and --new-color
        try:
            old_color = tuple(map(int, args.old_color.split(",")))
            new_color = tuple(map(int, args.new_color.split(",")))
            if len(old_color) != 3 or len(new_color) != 3:
                print("Error: Colors must be in RGB format (e.g., '255,255,255')")
                exit(1)
            color_pairs.append((old_color, new_color))
        except ValueError:
            print("Error: Colors must be in format 'r,g,b'")
            exit(1)
    
    # Parse region if specified
    regions = None
    if args.region:
        try:
            regions = []
            # Split by semicolon for multiple regions
            for region_str in args.region.split(";"):
                region = tuple(map(int, region_str.split(",")))
                if len(region) != 4:
                    print("Error: Each region must have 4 values (x1,y1,x2,y2)")
                    exit(1)
                regions.append(region)
        except ValueError:
            print("Error: Region(s) must be in format 'x1,y1,x2,y2' or 'x1,y1,x2,y2;x1,y1,x2,y2'")
            exit(1)
    
    # Parse region_color if specified
    region_colors = None
    if args.region_color:
        try:
            region_colors = []
            # Split by semicolon for multiple colors
            for color_str in args.region_color.split(";"):
                color = tuple(map(int, color_str.split(",")))
                if len(color) != 3:
                    print("Error: Each region color must be in RGB format (e.g., '255,0,0')")
                    exit(1)
                region_colors.append(color)
        except ValueError:
            print("Error: Region color(s) must be in format 'r,g,b' or 'r,g,b;r,g,b'")
            exit(1)
    
    # Parse exclude_colors if specified
    exclude_colors = None
    if args.exclude_colors:
        try:
            exclude_colors = []
            for color_str in args.exclude_colors.split(";"):
                color = tuple(map(int, color_str.split(",")))
                if len(color) != 3:
                    print("Error: Exclude colors must be in RGB format")
                    exit(1)
                exclude_colors.append(color)
        except ValueError:
            print("Error: Exclude colors must be in format 'r,g,b;r,g,b'")
            exit(1)
    
    # Parse watermark region if specified
    watermark_region = None
    if args.watermark_region:
        try:
            watermark_region = tuple(map(int, args.watermark_region.split(",")))
            if len(watermark_region) != 4:
                print("Error: Watermark region must be in format 'x1,y1,x2,y2'")
                exit(1)
        except ValueError:
            print("Error: Watermark region must be in format 'x1,y1,x2,y2'")
            exit(1)
    
    # Parse watermark text color
    watermark_text_color = tuple(map(int, args.watermark_text_color.split(",")))
    if len(watermark_text_color) != 3:
        print("Error: Watermark text color must be in RGB format")
        exit(1)
    
    # Get absolute paths
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / args.input_dir
    output_dir = script_dir / args.output_dir
    
    batch_replace_color(
        input_dir=input_dir,
        output_dir=output_dir,
        color_pairs=color_pairs,
        tolerance=args.tolerance,
        regions=regions,
        region_colors=region_colors,
        exclude_colors=exclude_colors,
        exclusive_tolerance=args.exclusive_tolerance,
        watermark_icon=args.watermark_icon,
        watermark_text=args.watermark_text,
        watermark_region=watermark_region,
        watermark_text_color=watermark_text_color,
        watermark_font_size=args.watermark_font_size,
        watermark_font_path=args.watermark_font,
        overwrite=args.overwrite,
        test=args.test,
        filter_csv=args.filter_csv
    )
