# PDF Image Extractor

A command-line tool that extracts high-quality images from PDF files while preserving their original quality and metadata.

## Features

- Extracts images in their original quality without recompression
- Preserves image metadata including DPI, color space, and format
- Detects and skips duplicate images
- Records image positions and ordering within the PDF
- Generates detailed metadata in JSON format
- Handles large images safely
- Supports various image formats (JPEG, PNG, etc.)

## Installation

```bash
brew tap nealcaren/tools
brew install pdfextractimages
```

## Usage

Basic usage:
```bash
pdfextractimages input.pdf [output_directory]
```

If no output directory is specified, images will be saved to a directory named `input_images`.

### Output

The tool creates:
- Extracted images named by page and position
- A `image_metadata.json` file containing detailed information about each image:
  - Filename and location
  - Image format and size
  - Color space and DPI
  - Position on the PDF page
  - Relative positioning to other images
  - File size

### Example Output

```
Image: page_1_img_0.jpg
Format: JPEG
Size: 1200x800 pixels
Color Space: RGB
DPI: 300x300 (image metadata)
File Size: 245.3 KB
Position: (1.2", 5.5") from bottom-left
Dimensions on page: 4.0" × 2.67"
```

## Requirements

- [uv](https://github.com/astral-sh/uv) package installer
  - All Python dependencies will be automatically installed in an isolated virtual environment
  - No system-wide Python packages are needed or modified

## License

MIT License
