"""
Task 3: Preprocess Text Transcripts
Extracts text from PDF files and applies required preprocessing steps
"""

import os
import sys
import re
import string
from pathlib import Path
from tqdm import tqdm
from num2words import num2words
import PyPDF2

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def convert_numbers_to_words(text):
    """
    Convert all numbers in text to their spoken word form.
    
    Args:
        text: Input text
        
    Returns:
        Text with numbers converted to words
    """
    def replace_number(match):
        try:
            number = int(match.group(0))
            return num2words(number)
        except (ValueError, OverflowError):
            return match.group(0)
    
    # Replace all sequences of digits
    return re.sub(r'\b\d+\b', replace_number, text)

def preprocess_text(text):
    """
    Apply all preprocessing steps to text.
    
    Steps:
    1. Convert to lowercase
    2. Remove punctuation
    3. Convert numbers to words
    4. Normalize whitespace
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Step 1: Convert to lowercase
    text = text.lower()
    
    # Step 2: Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Step 3: Convert numbers to words
    text = convert_numbers_to_words(text)
    
    # Step 4: Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def process_pdfs(input_dir, output_dir):
    """
    Process all PDF files in directory.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save processed text files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"\nNo PDF files found in {input_dir}")
        print("Note: If you're using YouTube subtitles, they're already in text format")
        print("      and don't need PDF extraction.")
        return
    
    print(f"\nProcessing {len(pdf_files)} PDF files...")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}\n")
    
    successful = 0
    failed = 0
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            # Extract text from PDF
            raw_text = extract_text_from_pdf(str(pdf_file))
            
            if not raw_text:
                tqdm.write(f"  Warning: No text extracted from {pdf_file.name}")
                failed += 1
                continue
            
            # Preprocess text
            processed_text = preprocess_text(raw_text)
            
            # Save to text file
            output_file = Path(output_dir) / f"{pdf_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(processed_text)
            
            successful += 1
            
        except Exception as e:
            tqdm.write(f"  Error processing {pdf_file.name}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Successful: {successful}/{len(pdf_files)}")
    if failed > 0:
        print(f"  Failed: {failed}")
    print(f"{'='*60}\n")

def process_text_files(input_dir):
    """
    Process existing text files (e.g., from YouTube subtitles).
    
    Args:
        input_dir: Directory containing text files
    """
    txt_files = list(Path(input_dir).glob("*.txt"))
    
    if not txt_files:
        return
    
    print(f"\nPreprocessing {len(txt_files)} existing text files...")
    
    for txt_file in tqdm(txt_files, desc="Processing text"):
        try:
            # Read text
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Preprocess
            processed_text = preprocess_text(text)
            
            # Save back
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(processed_text)
                
        except Exception as e:
            tqdm.write(f"  Error processing {txt_file.name}: {e}")
    
    print(f"Text preprocessing complete!\n")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python task3_preprocess_text.py <input_directory> [output_directory]")
        print("\nExamples:")
        print("  Process PDFs: python task3_preprocess_text.py data/transcripts_pdf data/transcripts_txt")
        print("  Process existing text: python task3_preprocess_text.py data/transcripts_txt")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else input_dir
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    print("=" * 60)
    print("TASK 3: PREPROCESSING TEXT")
    print("=" * 60)
    
    # Check if input contains PDFs or text files
    has_pdfs = len(list(Path(input_dir).glob("*.pdf"))) > 0
    has_txt = len(list(Path(input_dir).glob("*.txt"))) > 0
    
    if has_pdfs:
        # Process PDFs
        process_pdfs(input_dir, output_dir)
    elif has_txt:
        # Process existing text files
        process_text_files(input_dir)
    else:
        print(f"\nNo PDF or text files found in {input_dir}")
        print("Please ensure the directory contains transcript files.")

if __name__ == "__main__":
    main()
