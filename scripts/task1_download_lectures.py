"""
Task 1: Download NPTEL Lectures with Audio and Subtitles
Downloads audio lectures and auto-generated/manual subtitles from YouTube.
"""

import os
import re
import requests
import subprocess
from pathlib import Path
from tqdm import tqdm

# Configuration
COURSE_URL = "https://nptel.ac.in/courses/106106184"
RAW_AUDIO_DIR = "data/raw_audios"
TRANSCRIPTS_DIR = "data/transcripts_txt"  # Changed to txt since we're getting subtitles
COOKIES_FILE = "cookies.txt"  # Optional: for authenticated downloads

def create_directories():
    """Create necessary directories for downloads."""
    os.makedirs(RAW_AUDIO_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    print("[OK] Directories created")

def extract_youtube_ids(course_url):
    """
    Extract YouTube video IDs from NPTEL course webpage.
    
    Args:
        course_url (str): URL of the NPTEL course
        
    Returns:
        list: List of unique YouTube video IDs
    """
    print(f"[*] Fetching course page: {course_url}")
    
    try:
        response = requests.get(course_url)
        response.raise_for_status()
        html = response.text
        
        # Extract YouTube IDs using regex
        youtube_ids = re.findall(r'youtube_id:"([A-Za-z0-9_-]{11})"', html)
        
        # Remove duplicates while preserving order
        youtube_ids = list(dict.fromkeys(youtube_ids))
        
        print(f"[OK] Found {len(youtube_ids)} unique video IDs")
        return youtube_ids
        
    except requests.RequestException as e:
        print(f"[ERROR] Error fetching course page: {e}")
        return []

def download_audio_and_subtitles(youtube_id, audio_dir, transcript_dir, use_cookies=False):
    """
    Download both audio and subtitles from YouTube video using yt-dlp.
    
    Args:
        youtube_id (str): YouTube video ID
        audio_dir (str): Directory to save audio file
        transcript_dir (str): Directory to save transcript/subtitle file
        use_cookies (bool): Whether to use cookies file for authentication
        
    Returns:
        tuple: (audio_success, subtitle_success)
    """
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    
    # Command to download audio
    audio_cmd = [
        "yt-dlp",
        "-x",  # Extract audio only
        "--audio-format", "wav",
        "-o", f"{audio_dir}/{youtube_id}.%(ext)s",
    ]
    
    # Command to download subtitles
    subtitle_cmd = [
        "yt-dlp",
        "--skip-download",  # Don't download video, only subtitles
        "--write-auto-sub",  # Download auto-generated subtitles
        "--write-sub",  # Download manual subtitles if available
        "--sub-lang", "en",  # English subtitles
        "--sub-format", "vtt",  # VTT format (we'll convert to plain text)
        "--convert-subs", "srt",  # Convert to SRT format
        "-o", f"{transcript_dir}/{youtube_id}.%(ext)s",
    ]
    
    # Add cookies if available
    if use_cookies and os.path.exists(COOKIES_FILE):
        audio_cmd.insert(1, "--cookies")
        audio_cmd.insert(2, COOKIES_FILE)
        subtitle_cmd.insert(1, "--cookies")
        subtitle_cmd.insert(2, COOKIES_FILE)
    
    # Add URL to both commands
    audio_cmd.append(url)
    subtitle_cmd.append(url)
    
    audio_success = False
    subtitle_success = False
    
    # Download audio
    try:
        subprocess.run(audio_cmd, check=True, capture_output=True, text=True)
        audio_success = True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Audio download failed for {youtube_id}: {e.stderr[:100]}")
    
    # Download subtitles
    try:
        subprocess.run(subtitle_cmd, check=True, capture_output=True, text=True)
        subtitle_success = True
    except subprocess.CalledProcessError as e:
        # Subtitles might not be available for all videos
        print(f"[WARN] Subtitle download failed for {youtube_id} (may not be available)")
    
    return (audio_success, subtitle_success)

def convert_srt_to_plain_text(srt_file, txt_file):
    """
    Convert SRT subtitle file to plain text.
    
    Args:
        srt_file (str): Path to SRT file
        txt_file (str): Path to output text file
    """
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract only the subtitle text (skip timestamps and numbers)
        text_lines = []
        skip_next = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip subtitle numbers (just digits)
            if line.isdigit():
                skip_next = True
                continue
            
            # Skip timestamp lines (contains -->)
            if '-->' in line:
                skip_next = False
                continue
            
            # Add text lines
            if not skip_next:
                text_lines.append(line)
        
        # Join all text
        full_text = ' '.join(text_lines)
        
        # Write to text file
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert {srt_file}: {e}")
        return False

def download_all_lectures(youtube_ids, use_cookies=False):
    """
    Download all lecture audio files and subtitles.
    
    Args:
        youtube_ids (list): List of YouTube video IDs
        use_cookies (bool): Whether to use cookies for authentication
    """
    print(f"\n[*] Starting download of {len(youtube_ids)} lectures (audio + subtitles)...")
    
    audio_successful = 0
    subtitle_successful = 0
    audio_failed = []
    subtitle_failed = []
    
    for i, video_id in enumerate(youtube_ids, 1):
        print(f"\n[{i}/{len(youtube_ids)}] Processing: {video_id}")
        
        # Check if files already exist
        audio_file = os.path.join(RAW_AUDIO_DIR, f"{video_id}.wav")
        txt_file = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.txt")
        
        skip_audio = os.path.exists(audio_file)
        skip_subtitle = os.path.exists(txt_file)
        
        if skip_audio and skip_subtitle:
            print(f"    [SKIP] Both audio and subtitle already exist")
            audio_successful += 1
            subtitle_successful += 1
            continue
        
        # Download
        if not skip_audio or not skip_subtitle:
            audio_ok, subtitle_ok = download_audio_and_subtitles(
                video_id, RAW_AUDIO_DIR, TRANSCRIPTS_DIR, use_cookies
            )
            
            if audio_ok or skip_audio:
                audio_successful += 1
                print(f"    [OK] Audio downloaded")
            else:
                audio_failed.append(video_id)
            
            # Convert SRT to plain text
            if subtitle_ok or skip_subtitle:
                # Find the SRT file (might be .en.srt or similar)
                srt_files = list(Path(TRANSCRIPTS_DIR).glob(f"{video_id}*.srt"))
                
                if srt_files:
                    srt_file = srt_files[0]
                    if convert_srt_to_plain_text(str(srt_file), txt_file):
                        subtitle_successful += 1
                        print(f"    [OK] Subtitle downloaded and converted")
                        # Remove SRT file after conversion
                        os.remove(srt_file)
                    else:
                        subtitle_failed.append(video_id)
                elif skip_subtitle:
                    subtitle_successful += 1
                else:
                    subtitle_failed.append(video_id)
                    print(f"    [WARN] No subtitle file found")
            else:
                subtitle_failed.append(video_id)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"[OK] Download Summary:")
    print(f"    Audio: {audio_successful}/{len(youtube_ids)} successful")
    print(f"    Subtitles: {subtitle_successful}/{len(youtube_ids)} successful")
    
    if audio_failed:
        print(f"\n[ERROR] Failed audio downloads ({len(audio_failed)}):")
        print(f"    {', '.join(audio_failed[:10])}{'...' if len(audio_failed) > 10 else ''}")
    
    if subtitle_failed:
        print(f"\n[WARN] Failed subtitle downloads ({len(subtitle_failed)}):")
        print(f"    {', '.join(subtitle_failed[:10])}{'...' if len(subtitle_failed) > 10 else ''}")
        print(f"    Note: Some videos may not have subtitles available")

def main():
    """Main execution function."""
    print("=" * 60)
    print("TASK 1: DOWNLOADING NPTEL LECTURES")
    print("Downloads: Audio (WAV) + Subtitles (TXT)")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Extract YouTube IDs
    youtube_ids = extract_youtube_ids(COURSE_URL)
    
    if not youtube_ids:
        print("[ERROR] No video IDs found. Exiting.")
        return
    
    # Display first few IDs
    print(f"\n[*] First 5 video IDs:")
    for i, vid in enumerate(youtube_ids[:5], 1):
        print(f"    {i}. {vid} - https://www.youtube.com/watch?v={vid}")
    
    # Check if yt-dlp is installed
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True, text=True)
        print(f"\n[OK] yt-dlp version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[ERROR] yt-dlp not found. Please install it:")
        print("    pip install yt-dlp")
        return
    
    # Check for cookies
    use_cookies = os.path.exists(COOKIES_FILE)
    if use_cookies:
        print(f"[OK] Using cookies from: {COOKIES_FILE}")
    else:
        print(f"[INFO] No cookies file found (optional)")
    
    # Download lectures
    download_all_lectures(youtube_ids, use_cookies)
    
    print("\n" + "=" * 60)
    print("[OK] TASK 1 COMPLETE")
    print("=" * 60)
    print(f"    Audio files saved to: {RAW_AUDIO_DIR}")
    print(f"    Transcripts saved to: {TRANSCRIPTS_DIR}")

if __name__ == "__main__":
    main()
