"""
Task 2: Preprocess Audio Files
Converts audio to 16kHz mono WAV format and removes trailing silence.
"""

import os
import subprocess
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Configuration
INPUT_DIR = "data/raw_audios"
PROCESSED_DIR = "data/processed_audios"
FINAL_DIR = "data/final_audios"
SAMPLE_RATE = 16000
CHANNELS = 1
NUM_CPUS = 4  # Adjust based on your system
SILENCE_THRESHOLD = 0.01  # Amplitude threshold for silence detection

def create_directories():
    """Create necessary directories for processed audio."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)
    print("✅ Directories created")

def convert_to_16khz_mono(input_file, output_file):
    """
    Convert audio file to 16kHz mono WAV format using ffmpeg.
    
    Args:
        input_file (str): Path to input audio file
        output_file (str): Path to output audio file
        
    Returns:
        bool: True if conversion successful, False otherwise
    """
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-loglevel", "error",  # Only show errors
        "-i", input_file,
        "-ac", str(CHANNELS),  # Mono
        "-ar", str(SAMPLE_RATE),  # 16kHz
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {input_file}: {e.stderr.decode()}")
        return False

def process_single_audio(filename):
    """
    Process a single audio file (wrapper for multiprocessing).
    
    Args:
        filename (str): Name of the audio file
        
    Returns:
        tuple: (filename, success)
    """
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(PROCESSED_DIR, filename)
    
    # Skip if already processed
    if os.path.exists(output_path):
        return (filename, True)
    
    success = convert_to_16khz_mono(input_path, output_path)
    return (filename, success)

def parallel_convert_audio():
    """
    Convert all audio files to 16kHz mono using parallel processing.
    
    Returns:
        tuple: (successful_count, failed_count)
    """
    print(f"\n🎵 Converting audio files to {SAMPLE_RATE}Hz mono...")
    
    # Get all WAV files
    audio_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".wav")]
    
    if not audio_files:
        print("❌ No audio files found in", INPUT_DIR)
        return (0, 0)
    
    print(f"📊 Total files: {len(audio_files)}")
    print(f"🔧 Using {NUM_CPUS} CPU cores")
    
    # Process in parallel
    successful = 0
    failed = 0
    
    with Pool(NUM_CPUS) as pool:
        results = list(tqdm(
            pool.imap(process_single_audio, audio_files),
            total=len(audio_files),
            desc="Converting"
        ))
    
    for filename, success in results:
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"✅ Conversion complete: {successful}/{len(audio_files)} successful")
    if failed > 0:
        print(f"❌ Failed: {failed} files")
    
    return (successful, failed)

def trim_trailing_silence(audio, threshold=SILENCE_THRESHOLD):
    """
    Remove trailing silence from audio using amplitude-based detection.
    
    Args:
        audio (np.ndarray): Audio signal
        threshold (float): Amplitude threshold for silence detection
        
    Returns:
        np.ndarray: Trimmed audio signal
    """
    # Calculate energy (absolute amplitude)
    energy = np.abs(audio)
    
    # Find indices where energy exceeds threshold
    idx = np.where(energy > threshold)[0]
    
    if len(idx) == 0:
        # If no audio detected, return original
        return audio
    
    # Trim to last non-silent sample
    return audio[:idx[-1] + 1]

def remove_silence_from_all():
    """
    Remove trailing silence from all processed audio files.
    
    Returns:
        tuple: (successful_count, failed_count)
    """
    print(f"\n🔇 Removing trailing silence (threshold={SILENCE_THRESHOLD})...")
    
    audio_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".wav")]
    
    if not audio_files:
        print("❌ No processed audio files found")
        return (0, 0)
    
    successful = 0
    failed = 0
    
    for filename in tqdm(audio_files, desc="Trimming silence"):
        input_path = os.path.join(PROCESSED_DIR, filename)
        output_path = os.path.join(FINAL_DIR, filename)
        
        # Skip if already processed
        if os.path.exists(output_path):
            successful += 1
            continue
        
        try:
            # Load audio
            audio, sr = librosa.load(input_path, sr=SAMPLE_RATE)
            
            # Trim silence
            trimmed_audio = trim_trailing_silence(audio, threshold=SILENCE_THRESHOLD)
            
            # Save trimmed audio
            sf.write(output_path, trimmed_audio, sr)
            successful += 1
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            failed += 1
    
    print(f"✅ Silence removal complete: {successful}/{len(audio_files)} successful")
    if failed > 0:
        print(f"❌ Failed: {failed} files")
    
    return (successful, failed)

def get_audio_stats():
    """Display statistics about processed audio files."""
    print("\n📊 Audio Statistics:")
    
    final_files = [f for f in os.listdir(FINAL_DIR) if f.endswith(".wav")]
    
    if not final_files:
        print("   No final audio files found")
        return
    
    total_duration = 0
    durations = []
    
    print(f"   Analyzing {len(final_files)} files...")
    
    for filename in tqdm(final_files[:10], desc="Sampling"):  # Sample first 10
        filepath = os.path.join(FINAL_DIR, filename)
        try:
            audio, sr = librosa.load(filepath, sr=None)
            duration = len(audio) / sr
            durations.append(duration)
            total_duration += duration
        except Exception as e:
            print(f"   Error reading {filename}: {e}")
    
    if durations:
        avg_duration = np.mean(durations)
        print(f"\n   Total files: {len(final_files)}")
        print(f"   Sample size: {len(durations)}")
        print(f"   Average duration: {avg_duration:.2f} seconds ({avg_duration/60:.2f} minutes)")
        print(f"   Estimated total: {avg_duration * len(final_files) / 3600:.2f} hours")

def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg not found. Please install it:")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print("   Linux: sudo apt-get install ffmpeg")
        print("   macOS: brew install ffmpeg")
        return False

def main():
    """Main execution function."""
    print("=" * 60)
    print("TASK 2: PREPROCESSING AUDIO")
    print("=" * 60)
    
    # Check dependencies
    if not check_ffmpeg():
        return
    
    # Create directories
    create_directories()
    
    # Step 1: Convert to 16kHz mono
    convert_success, convert_failed = parallel_convert_audio()
    
    if convert_success == 0:
        print("❌ No files converted. Exiting.")
        return
    
    # Step 2: Remove trailing silence
    trim_success, trim_failed = remove_silence_from_all()
    
    # Display statistics
    get_audio_stats()
    
    print("\n" + "=" * 60)
    print("✅ TASK 2 COMPLETE")
    print("=" * 60)
    print(f"   Final audio files saved to: {FINAL_DIR}")

if __name__ == "__main__":
    main()
