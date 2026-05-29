#!/usr/bin/env python3
"""
PNG to JPG Converter Script

This script converts PNG images to JPG format with balanced quality and size.
It uses optimized parameters to maintain good image quality while reducing file size.

Usage:
    python png_to_jpg_converter.py [input_dir] [output_dir] [quality]

Parameters:
    input_dir: Directory containing PNG images (default: ../generated_images)
    output_dir: Directory to save JPG images (default: ../converted_images)
    quality: JPG quality (1-100, default: 85)
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('png_to_jpg_conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def convert_png_to_jpg(input_path, output_path, quality=85, optimize=True):
    """
    Convert a single PNG image to JPG format.
    
    Args:
        input_path (str): Path to input PNG file
        output_path (str): Path to output JPG file
        quality (int): JPG quality (1-100)
        optimize (bool): Whether to optimize the JPG
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        # Open the PNG image
        with Image.open(input_path) as img:
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
            
            # Save as JPG with specified quality and optimization
            img.save(
                output_path,
                'JPEG',
                quality=quality,
                optimize=optimize,
                progressive=True  # Progressive JPG for better web loading
            )
            
        return True
        
    except Exception as e:
        logger.error(f"Error converting {input_path}: {str(e)}")
        return False

def get_file_size_mb(file_path):
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def convert_directory(input_dir, output_dir, quality=85, optimize=True):
    """
    Convert all PNG images in a directory to JPG format.
    
    Args:
        input_dir (str): Input directory path
        output_dir (str): Output directory path
        quality (int): JPG quality (1-100)
        optimize (bool): Whether to optimize JPG files
    
    Returns:
        dict: Statistics about the conversion
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PNG files
    png_files = list(input_path.glob('*.png'))
    
    if not png_files:
        logger.warning(f"No PNG files found in {input_dir}")
        return {'converted': 0, 'failed': 0, 'total_size_saved': 0}
    
    logger.info(f"Found {len(png_files)} PNG files to convert")
    
    converted = 0
    failed = 0
    total_size_saved = 0
    
    for png_file in png_files:
        # Create output filename
        jpg_filename = png_file.stem + '.jpg'
        jpg_file = output_path / jpg_filename
        
        logger.info(f"Converting {png_file.name} to {jpg_filename}")
        
        # Convert the image
        if convert_png_to_jpg(str(png_file), str(jpg_file), quality, optimize):
            converted += 1
            
            # Calculate size difference
            original_size = get_file_size_mb(png_file)
            converted_size = get_file_size_mb(jpg_file)
            size_saved = original_size - converted_size
            
            logger.info(f"  Original: {original_size:.2f} MB")
            logger.info(f"  Converted: {converted_size:.2f} MB")
            logger.info(f"  Size saved: {size_saved:.2f} MB")
            
            total_size_saved += size_saved
        else:
            failed += 1
    
    return {
        'converted': converted,
        'failed': failed,
        'total_size_saved': total_size_saved
    }

def main():
    """Main function to handle command line arguments and run conversion."""
    parser = argparse.ArgumentParser(
        description='Convert PNG images to JPG format with balanced quality and size',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'input_dir',
        nargs='?',
        default='./generated_images',
        help='Directory containing PNG images (default: ../generated_images)'
    )
    
    parser.add_argument(
        'output_dir',
        nargs='?',
        default='./converted_images',
        help='Directory to save JPG images (default: ../converted_images)'
    )
    
    parser.add_argument(
        '--quality',
        '-q',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='1-100',
        help='JPG quality (default: 85)'
    )
    
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='Disable JPG optimization (faster but larger files)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input path is not a directory: {args.input_dir}")
        sys.exit(1)
    
    logger.info(f"Starting PNG to JPG conversion")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Quality: {args.quality}")
    logger.info(f"Optimize: {not args.no_optimize}")
    
    # Run conversion
    stats = convert_directory(
        args.input_dir,
        args.output_dir,
        args.quality,
        not args.no_optimize
    )
    
    # Print summary
    logger.info("=" * 50)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Successfully converted: {stats['converted']} files")
    logger.info(f"Failed conversions: {stats['failed']} files")
    logger.info(f"Total size saved: {stats['total_size_saved']:.2f} MB")
    
    if stats['converted'] > 0:
        avg_size_saved = stats['total_size_saved'] / stats['converted']
        logger.info(f"Average size saved per file: {avg_size_saved:.2f} MB")
    
    logger.info("=" * 50)

if __name__ == '__main__':
    main() 