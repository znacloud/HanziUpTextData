#!/usr/bin/env python3
"""
Script to rename all .jpg files to .png files in the generated_images directory.
"""
from pathlib import Path

def rename_images_to_png():
    """
    Rename all .jpg files to .png files in the generated_images directory.
    """
    # Get the script directory and construct path to generated_images
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    images_dir = project_root / "generated_images"
    
    # Check if the directory exists
    if not images_dir.exists():
        print(f"Error: Directory {images_dir} does not exist")
        return
    
    # Find all .jpg files
    jpg_files = list(images_dir.glob("*.jpg"))
    
    if not jpg_files:
        print("No .jpg files found in the generated_images directory.")
        return
    
    print(f"Found {len(jpg_files)} .jpg files to rename.")
    
    # Counter for successful renames
    renamed_count = 0
    error_count = 0
    
    # Rename each file
    for jpg_file in jpg_files:
        # Create new filename with .png extension
        png_file = jpg_file.with_suffix('.png')
        
        # Check if the target file already exists
        if png_file.exists():
            print(f"Warning: {png_file.name} already exists, skipping {jpg_file.name}")
            error_count += 1
            continue
        
        try:
            # Rename the file
            jpg_file.rename(png_file)
            print(f"Renamed: {jpg_file.name} -> {png_file.name}")
            renamed_count += 1
        except OSError as e:
            print(f"Error renaming {jpg_file.name}: {e}")
            error_count += 1
    
    # Print summary
    print(f"\nSummary:")
    print(f"Successfully renamed: {renamed_count} files")
    print(f"Errors: {error_count} files")
    print(f"Total processed: {len(jpg_files)} files")

if __name__ == "__main__":
    rename_images_to_png() 