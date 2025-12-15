"""
Task 4: Create Training Manifest File
Generates train_manifest.jsonl in the required format for speech-to-text training
"""

import os
import sys
import json
import librosa
from pathlib import Path
from tqdm import tqdm

def get_audio_duration(audio_path):
    """
    Get duration of audio file in seconds.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds (float)
    """
    try:
        audio, sr = librosa.load(audio_path, sr=None)
        duration = len(audio) / sr
        return round(duration, 2)
    except Exception as e:
        print(f"Error getting duration for {audio_path}: {e}")
        return None

def create_manifest(audio_dir, transcript_dir, output_file):
    """
    Create training manifest file.
    
    Args:
        audio_dir: Directory containing audio files
        transcript_dir: Directory containing transcript text files
        output_file: Path to output manifest file
    """
    # Get all audio files
    audio_files = sorted(list(Path(audio_dir).glob("*.wav")))
    
    if not audio_files:
        print(f"Error: No audio files found in {audio_dir}")
        return
    
    print(f"\nCreating manifest from {len(audio_files)} audio files...")
    print(f"Audio directory: {audio_dir}")
    print(f"Transcript directory: {transcript_dir}")
    print(f"Output file: {output_file}\n")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    successful = 0
    skipped = 0
    
    with open(output_file, 'w', encoding='utf-8') as manifest:
        for audio_file in tqdm(audio_files, desc="Creating manifest"):
            # Get corresponding transcript file
            video_id = audio_file.stem
            transcript_file = Path(transcript_dir) / f"{video_id}.txt"
            
            # Skip if transcript doesn't exist
            if not transcript_file.exists():
                tqdm.write(f"  Warning: No transcript for {video_id}")
                skipped += 1
                continue
            
            # Get audio duration
            duration = get_audio_duration(str(audio_file))
            if duration is None:
                skipped += 1
                continue
            
            # Read transcript text
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
            except Exception as e:
                tqdm.write(f"  Error reading transcript for {video_id}: {e}")
                skipped += 1
                continue
            
            # Skip if text is empty
            if not text:
                tqdm.write(f"  Warning: Empty transcript for {video_id}")
                skipped += 1
                continue
            
            # Create manifest entry
            # Format matches the example from the challenge:
            # {"audio_filepath": "data/courses/106106184/audio/lec_1_2.wav", "duration": 1847.5, "text": "..."}
            entry = {
                "audio_filepath": str(audio_file).replace('\\', '/'),
                "duration": duration,
                "text": text
            }
            
            # Write to manifest
            manifest.write(json.dumps(entry, ensure_ascii=False) + '\n')
            successful += 1
    
    print(f"\n{'='*60}")
    print(f"Manifest creation complete!")
    print(f"  Total entries: {successful}")
    if skipped > 0:
        print(f"  Skipped: {skipped} (missing transcripts or errors)")
    print(f"  Output: {output_file}")
    print(f"{'='*60}\n")
    
    return successful

def validate_manifest(manifest_file):
    """
    Validate the manifest file.
    
    Args:
        manifest_file: Path to manifest file
    """
    print("Validating manifest...")
    
    total_duration = 0
    total_words = 0
    line_count = 0
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                    
                    # Check required fields
                    if 'audio_filepath' not in entry:
                        print(f"  Error on line {line_num}: Missing 'audio_filepath'")
                        return False
                    if 'duration' not in entry:
                        print(f"  Error on line {line_num}: Missing 'duration'")
                        return False
                    if 'text' not in entry:
                        print(f"  Error on line {line_num}: Missing 'text'")
                        return False
                    
                    # Accumulate statistics
                    total_duration += entry['duration']
                    total_words += len(entry['text'].split())
                    line_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"  Error on line {line_num}: Invalid JSON - {e}")
                    return False
        
        # Display statistics
        print(f"\n✓ Manifest is valid!")
        print(f"\nDataset Statistics:")
        print(f"  Total utterances: {line_count}")
        print(f"  Total duration: {total_duration:.2f} seconds ({total_duration/3600:.2f} hours)")
        print(f"  Total words: {total_words:,}")
        print(f"  Average duration: {total_duration/line_count:.2f} seconds")
        print(f"  Average words per utterance: {total_words/line_count:.0f}")
        
        return True
        
    except FileNotFoundError:
        print(f"  Error: Manifest file not found: {manifest_file}")
        return False
    except Exception as e:
        print(f"  Error validating manifest: {e}")
        return False

def show_sample_entries(manifest_file, num_samples=3):
    """
    Display sample entries from manifest.
    
    Args:
        manifest_file: Path to manifest file
        num_samples: Number of samples to show
    """
    print(f"\nSample Manifest Entries (first {num_samples}):")
    print("=" * 60)
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= num_samples:
                    break
                
                entry = json.loads(line)
                print(f"\nEntry {i+1}:")
                print(f"  audio_filepath: {entry['audio_filepath']}")
                print(f"  duration: {entry['duration']} seconds")
                text_preview = entry['text'][:100] + "..." if len(entry['text']) > 100 else entry['text']
                print(f"  text: {text_preview}")
    except Exception as e:
        print(f"Error reading samples: {e}")

def main():
    """Main function."""
    if len(sys.argv) != 4:
        print("Usage: python task4_create_manifest.py <audio_dir> <transcript_dir> <output_file>")
        print("\nExample:")
        print("  python task4_create_manifest.py data/final_audios data/transcripts_txt output/train_manifest.jsonl")
        sys.exit(1)
    
    audio_dir = sys.argv[1]
    transcript_dir = sys.argv[2]
    output_file = sys.argv[3]
    
    # Validate directories
    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory '{audio_dir}' does not exist")
        sys.exit(1)
    
    if not os.path.exists(transcript_dir):
        print(f"Error: Transcript directory '{transcript_dir}' does not exist")
        sys.exit(1)
    
    print("=" * 60)
    print("TASK 4: CREATING TRAINING MANIFEST")
    print("=" * 60)
    
    # Create manifest
    num_entries = create_manifest(audio_dir, transcript_dir, output_file)
    
    if num_entries and num_entries > 0:
        # Validate manifest
        if validate_manifest(output_file):
            # Show sample entries
            show_sample_entries(output_file)
            print("\n" + "=" * 60)
            print("✓ Task 4 complete!")
            print("=" * 60)
        else:
            print("\n✗ Manifest validation failed")
            sys.exit(1)
    else:
        print("\n✗ No manifest entries created")
        sys.exit(1)

if __name__ == "__main__":
    main()
