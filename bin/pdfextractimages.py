# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pymupdf",
#     "pillow",
# ]
# ///

import fitz  # PyMuPDF
import os
import hashlib
import io
import json
from PIL import Image
import sys
from operator import itemgetter

Image.MAX_IMAGE_PIXELS = None  # Disable DecompressionBombError


def get_image_hash(image_bytes):
    """Generate a hash of the image to detect duplicates."""
    return hashlib.md5(image_bytes).hexdigest()

def get_image_info(image, position=None):
    """Extract detailed information about the image."""
    info = {
        'format': image.format,
        'mode': image.mode,
        'size': f"{image.width}x{image.height}",
        'color_space': image.mode,
    }
    
    # Try multiple methods to determine DPI
    dpi = None
    
    # Method 1: Get DPI from image metadata
    try:
        dpi = image.info.get('dpi', None)
        if dpi and dpi[0] > 0 and dpi[1] > 0:
            info['dpi'] = f"{int(dpi[0])}x{int(dpi[1])}"
            info['dpi_source'] = 'image metadata'
            return info
    except:
        pass
    
    # Method 2: Calculate DPI from PDF placement if available
    if position:
        try:
            # Calculate DPI based on image dimensions and PDF placement
            width_dpi = image.width / float(position['width'])  # pixels / inches
            height_dpi = image.height / float(position['height'])
            info['dpi'] = f"{int(width_dpi)}x{int(height_dpi)}"
            info['dpi_source'] = 'calculated from PDF placement'
            return info
        except:
            pass
    
    # Method 3: Use common default
    info['dpi'] = '96x96'  # Standard screen resolution
    info['dpi_source'] = 'default value'
    
    return info

def save_image_preserving_quality(image_bytes, image_ext, image_path):
    """
    Saves images in their original quality without recompression,
    unless necessary for format compatibility.
    """
    image = Image.open(io.BytesIO(image_bytes))

    if image_ext in ["jpg", "jpeg"]:
        # Save JPEG as is (no quality loss)
        image.save(image_path, format="JPEG", quality=100)  
    elif image_ext == "png":
        # Save PNG as is (no loss, with optimization)
        image.save(image_path, format="PNG", optimize=True)
    else:
        # Save unknown formats in their best quality available
        image.save(image_path)  

def extract_high_quality_images_from_pdf(pdf_path, output_folder):
    """Extracts embedded images from a PDF with the highest quality possible."""
    """Extracts embedded images from a PDF with the highest quality possible."""
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)
    seen_hashes = set()
    image_count = 0
    all_images = []  # Store all image data for sorting and saving

    for page_number, page in enumerate(doc, start=1):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Get image position from page
            try:
                # Get all instances of this image on the page
                img_list = page.get_images()
                for img_index, img_info in enumerate(img_list):
                    if img_info[0] == xref:  # Match our current image
                        # Get the image rectangle/location
                        img_rect = page.get_image_rects(img_info[0])[0]
                        x0, y0, x1, y1 = img_rect
                        
                        # Convert to inches (72 points per inch in PDF)
                        width_inches = (x1 - x0) / 72
                        height_inches = (y1 - y0) / 72
                        
                        # PDF coordinates start from bottom-left
                        position = {
                            'x': f"{x0/72:.2f}",
                            'y': f"{y0/72:.2f}",
                            'width': f"{width_inches:.2f}",
                            'height': f"{height_inches:.2f}"
                        }
                        break
                else:
                    position = None
            except Exception as e:
                print(f"Warning: Could not get position info: {e}")
                position = None

            # Generate hash to avoid duplicates
            image_hash = get_image_hash(image_bytes)
            if image_hash in seen_hashes:
                continue  
            seen_hashes.add(image_hash)

            # Save without altering quality
            image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)

            # Get additional image metadata
            image = Image.open(io.BytesIO(image_bytes))
            image_info = get_image_info(image, position)
            
            save_image_preserving_quality(image_bytes, image_ext, image_path)
            image_count += 1
            
            # Collect image data
            image_data = {
                "filename": image_filename,
                "format": image_info['format'],
                "size": image_info['size'],
                "color_space": image_info['color_space'],
                "dpi": image_info['dpi'],
                "file_size_kb": f"{len(image_bytes)/1024:.1f}",
                "saved_path": image_path,
                "page": page_number
            }
            
            if position:
                image_data.update({
                    "position_x": float(position['x']),
                    "position_y": float(position['y']),
                    "width": float(position['width']),
                    "height": float(position['height'])
                })
            
            all_images.append(image_data)
            
            # Print detailed information
            print(f"\nImage: {image_filename}")
            print(f"Format: {image_info['format']}")
            print(f"Size: {image_info['size']} pixels")
            print(f"Color Space: {image_info['color_space']}")
            print(f"DPI: {image_info['dpi']} ({image_info['dpi_source']})")
            print(f"File Size: {len(image_bytes)/1024:.1f} KB")
            if position:
                print(f"Position: ({position['x']}\", {position['y']}\") from bottom-left")
                print(f"Dimensions on page: {position['width']}\" × {position['height']}\"")
            else:
                print("Position: Not available")
            print(f"Saved to: {image_path}")
            print("-" * 50)

    # Sort images by page, then top-to-bottom, then left-to-right
    sorted_images = sorted(all_images, 
                         key=lambda x: (x['page'], 
                                      -x.get('position_y', 0),  # Negative for top-to-bottom
                                      x.get('position_x', 0)))
    
    # Add relative position information
    for i, img in enumerate(sorted_images):
        img['order'] = i + 1
        img['relative_position'] = f"Page {img['page']}, {'Top' if i == 0 else 'Below ' + sorted_images[i-1]['filename']}"
        if i > 0 and img['page'] == sorted_images[i-1]['page']:
            if abs(img.get('position_y', 0) - sorted_images[i-1].get('position_y', 0)) < 1:
                img['relative_position'] = f"Page {img['page']}, Right of {sorted_images[i-1]['filename']}"
    
    # Save metadata to JSON
    metadata_file = os.path.join(output_folder, "image_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(sorted_images, f, indent=2)
    
    print(f"\nExtraction complete! {image_count} images saved in '{output_folder}'.")
    print(f"Image metadata saved to {metadata_file}")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_images.py <PDF_FILE> [OUTPUT_FOLDER]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    # Create default output directory name based on PDF filename
    default_output = os.path.splitext(os.path.basename(pdf_file))[0] + "_images"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else default_output

    extract_high_quality_images_from_pdf(pdf_file, output_dir)
