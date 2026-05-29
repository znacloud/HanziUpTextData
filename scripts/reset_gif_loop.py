"""
Script to reset GIF loop count to infinite (loop=0) for all GIFs in a directory.
This fixes GIFs that only play once by making them loop forever.

Uses gifsicle for lossless metadata-only modification (no re-encoding).
Install gifsicle:
  - Windows: scoop install gifsicle  OR  choco install gifsicle
  - Mac: brew install gifsicle
  - Linux: sudo apt-get install gifsicle
"""

import os
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm
import argparse


def check_gifsicle():
    """Check if gifsicle is installed."""
    # Check for local gifsicle.exe first
    script_dir = Path(__file__).parent.parent
    local_gifsicle = script_dir / "gifsicle.exe"
    
    if local_gifsicle.exists():
        return str(local_gifsicle)
    
    # Check system PATH
    if shutil.which("gifsicle") is not None:
        return "gifsicle"
    
    print("ERROR: gifsicle is not installed or not in PATH")
    print("\nInstallation instructions:")
    print("  Windows: scoop install gifsicle  OR  choco install gifsicle")
    print("  Mac:     brew install gifsicle")
    print("  Linux:   sudo apt-get install gifsicle")
    return None


def reset_gif_loop(input_path, output_path, in_place=False, gifsicle_cmd="gifsicle"):
    """
    Reset a single GIF to loop infinitely using gifsicle (lossless).
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to save the modified GIF
        in_place: If True, modify the file in place
        gifsicle_cmd: Path to gifsicle executable
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if in_place:
            # Modify in place with -b flag
            cmd = [gifsicle_cmd, "-b", "--loop=0", str(input_path)]
        else:
            # Save to output path
            cmd = [gifsicle_cmd, "--loop=0", str(input_path), "-o", str(output_path)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error processing {input_path}: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def batch_reset_loop(input_dir, output_dir=None, overwrite=False):
    """
    Reset loop count for all GIFs in a directory.
    
    Args:
        input_dir: Directory containing GIF files
        output_dir: Output directory (if None, modifies in place)
        overwrite: Whether to overwrite existing files
    """
    gifsicle_cmd = check_gifsicle()
    if not gifsicle_cmd:
        return
    
    input_dir = Path(input_dir)
    in_place = output_dir is None
    
    if not in_place:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all GIF files
    gif_files = list(input_dir.glob("*.gif"))
    
    if not gif_files:
        print(f"No GIF files found in {input_dir}")
        return
    
    print(f"Found {len(gif_files)} GIF files")
    print(f"Using gifsicle: {gifsicle_cmd}")
    
    success_count = 0
    skip_count = 0
    
    for gif_file in tqdm(gif_files, desc="Resetting GIF loops"):
        if in_place:
            output_path = gif_file
        else:
            output_path = output_dir / gif_file.name
            
            # Skip if output exists and overwrite is False
            if output_path.exists() and not overwrite:
                skip_count += 1
                continue
        
        if reset_gif_loop(gif_file, output_path, in_place=in_place, gifsicle_cmd=gifsicle_cmd):
            success_count += 1
    
    print(f"\nCompleted!")
    print(f"Successfully processed: {success_count}")
    if skip_count > 0:
        print(f"Skipped (already exists): {skip_count}")
    print(f"Failed: {len(gif_files) - success_count - skip_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reset GIF loop count to infinite for all GIFs in a directory"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="strokeorder_gifs_modified",
        help="Input directory containing GIF files (default: strokeorder_gifs_modified)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: None, modifies files in place)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in output directory (only used when --output-dir is set)"
    )
    
    args = parser.parse_args()
    
    # Get absolute paths relative to script parent directory
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / args.input_dir
    
    if args.output_dir:
        output_dir = script_dir / args.output_dir
    else:
        output_dir = None
    
    batch_reset_loop(
        input_dir=input_dir,
        output_dir=output_dir,
        overwrite=args.overwrite
    )
