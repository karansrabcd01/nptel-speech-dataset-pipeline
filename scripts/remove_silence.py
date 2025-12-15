"""
Task 2 Bonus: Remove Trailing Silence from NPTEL Lectures
Addresses the issue of trailing silence/music at the end of lectures
"""

import os
import sys
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from tqdm import tqdm

def trim_trailing_silence(audio, sr, threshold=0.01, min_silence_duration=1.0):
    """
    Remove trailing silence from audio.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        threshold: Amplitude threshold for silence detection
        min_silence_duration: Minimum duration of silence to trim (seconds)
        
    Returns:
        Trimmed audio signal
    """
    # Calculate energy
    energy = np.abs(audio)
    
    # Find indices where energy exceeds threshold
    idx = np.where(energy > threshold)[0]
    
    if len(idx) == 0:
        return audio
    
    # Get last non-silent sample
    last_sound_idx = idx[-1]
    
    # Add small buffer (0.5 seconds)
    buffer_samples = int(0.5 * sr)
    end_idx = min(last_sound_idx + buffer_samples, len(audio))
    
    return audio[:end_idx]

def process_directory(input_dir, output_dir):
    """
    Process all audio files in directory to remove trailing silence.
    
    Args:
        input_dir: Directory containing input audio files
        output_dir: Directory to save processed files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all WAV files
    audio_files = list(Path(input_dir).glob("*.wav"))
    
    if not audio_files:
        print(f"No WAV files found in {input_dir}")
        return
    
    print(f"\nProcessing {len(audio_files)} files...")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}\n")
    
    successful = 0
    failed = 0
    
    for audio_file in tqdm(audio_files, desc="Removing silence"):
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_file), sr=16000)
            
            # Get original duration
            original_duration = len(audio) / sr
            
            # Trim trailing silence
            trimmed_audio = trim_trailing_silence(audio, sr)
            
            # Get new duration
            new_duration = len(trimmed_audio) / sr
            
            # Save processed audio
            output_file = Path(output_dir) / audio_file.name
            sf.write(str(output_file), trimmed_audio, sr)
            
            # Calculate time saved
            time_saved = original_duration - new_duration
            
            if time_saved > 1.0:  # Only report if significant
                tqdm.write(f"  {audio_file.name}: Removed {time_saved:.1f}s of silence")
            
            successful += 1
            
        except Exception as e:
            tqdm.write(f"  Error processing {audio_file.name}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Successful: {successful}/{len(audio_files)}")
    if failed > 0:
        print(f"  Failed: {failed}")
    print(f"{'='*60}\n")

def main():
    """Main function."""
    if len(sys.argv) != 3:
        print("Usage: python remove_silence.py <input_directory> <output_directory>")
        print("Example: python remove_silence.py data/processed_audios data/final_audios")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    print("=" * 60)
    print("TASK 2 BONUS: REMOVE TRAILING SILENCE")
    print("=" * 60)
    
    process_directory(input_dir, output_dir)

if __name__ == "__main__":
    main()
