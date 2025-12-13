#!/usr/bin/env python3
"""
PDF to Markdown Converter for Scientific Articles

Converts PDF scientific articles to Markdown format preserving:
- Text content with proper spacing
- Section headings (Abstract, Introduction, Methods, etc.)
- Tables
- Lists and bullet points
- Bold/Italic formatting
- References

Usage:
    python pdf_to_markdown.py article.pdf
    python pdf_to_markdown.py article.pdf -o output.md
    python pdf_to_markdown.py article.pdf --images
"""

import argparse
import sys
from pathlib import Path

try:
    import pymupdf4llm
except ImportError:
    print("Error: pymupdf4llm is required. Install with: pip install pymupdf4llm")
    sys.exit(1)


def pdf_to_markdown(pdf_path: str, output_path: str = None, extract_images: bool = False) -> str:
    """
    Convert a PDF scientific article to Markdown format.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Optional path for the output markdown file
        extract_images: Whether to extract and embed images
        
    Returns:
        The markdown content as a string
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Convert using pymupdf4llm - optimized for scientific documents
    result = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=False,
        write_images=extract_images,
        image_path=str(pdf_path.parent / "images") if extract_images else None,
        show_progress=True,
    )
    
    # Save to file if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.write_text(result, encoding="utf-8")
        print(f"Markdown saved to: {output_path}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF scientific articles to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_markdown.py article.pdf
  python pdf_to_markdown.py article.pdf -o output.md
  python pdf_to_markdown.py article.pdf --images
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file to convert"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output markdown file path (default: same name as PDF with .md extension)"
    )
    
    parser.add_argument(
        "--images",
        action="store_true",
        help="Extract and embed images from the PDF"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    pdf_path = Path(args.pdf_file)
    if args.output:
        output_path = args.output
    else:
        output_path = pdf_path.with_suffix(".md")
    
    try:
        markdown = pdf_to_markdown(args.pdf_file, output_path, extract_images=args.images)
        print(f"Successfully converted {args.pdf_file}")
        print(f"Output: {output_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error converting PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
