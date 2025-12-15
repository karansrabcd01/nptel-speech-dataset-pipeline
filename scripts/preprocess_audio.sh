#!/bin/bash
# Task 2: Audio Preprocessing Script
# Converts audio files to 16kHz mono WAV format using ffmpeg

# Check if correct number of arguments provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    echo "Example: $0 data/raw_audios data/processed_audios"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' does not exist"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed"
    echo "Please install ffmpeg first"
    exit 1
fi

echo "============================================================"
echo "TASK 2: AUDIO PREPROCESSING"
echo "============================================================"
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Count total files
total_files=$(find "$INPUT_DIR" -maxdepth 1 -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.m4a" \) | wc -l)
echo "Total audio files found: $total_files"
echo ""

# Process each audio file
count=0
for input_file in "$INPUT_DIR"/*.{wav,mp3,m4a} 2>/dev/null; do
    # Skip if no files found
    [ -e "$input_file" ] || continue
    
    # Get filename without path
    filename=$(basename "$input_file")
    # Get filename without extension
    base_name="${filename%.*}"
    # Output file path
    output_file="$OUTPUT_DIR/${base_name}.wav"
    
    # Skip if already processed
    if [ -f "$output_file" ]; then
        echo "[$((count+1))/$total_files] Skipping $filename (already exists)"
        ((count++))
        continue
    fi
    
    echo "[$((count+1))/$total_files] Processing: $filename"
    
    # Convert to 16kHz mono WAV
    ffmpeg -i "$input_file" \
           -ar 16000 \
           -ac 1 \
           -y \
           -loglevel error \
           "$output_file"
    
    if [ $? -eq 0 ]; then
        echo "    ✓ Converted to 16kHz mono WAV"
    else
        echo "    ✗ Error processing $filename"
    fi
    
    ((count++))
done

echo ""
echo "============================================================"
echo "PREPROCESSING COMPLETE"
echo "============================================================"
echo "Processed: $count files"
echo "Output directory: $OUTPUT_DIR"
echo ""
