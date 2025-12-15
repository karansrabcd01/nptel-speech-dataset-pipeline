"""
Main Setup Script
Runs all tasks sequentially to complete the entire pipeline.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def print_header(task_name):
    """Print formatted task header."""
    print("\n" + "=" * 70)
    print(f"  {task_name}")
    print("=" * 70 + "\n")

def run_task(task_number, task_name, module_name):
    """
    Run a specific task module.
    
    Args:
        task_number (int): Task number
        task_name (str): Task description
        module_name (str): Python module to import and run
    """
    print_header(f"TASK {task_number}: {task_name}")
    
    try:
        # Import and run the task module
        task_module = __import__(module_name)
        task_module.main()
        print(f"\n✅ Task {task_number} completed successfully!\n")
        return True
    except Exception as e:
        print(f"\n❌ Task {task_number} failed with error: {e}\n")
        return False

def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("  AI4BHARAT DATA ENGINEERING HIRING CHALLENGE")
    print("  Complete Pipeline Execution")
    print("=" * 70)
    
    print("\nThis script will run all tasks sequentially:")
    print("  1. Download NPTEL lectures")
    print("  2. Preprocess audio files")
    print("  3. Preprocess text transcripts")
    print("  4. Create training manifest")
    print("  5. Launch interactive dashboard")
    
    response = input("\nDo you want to continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Task 1: Download Lectures
    success = run_task(1, "DOWNLOADING LECTURES", "task1_download_lectures")
    if not success:
        print("⚠️  Task 1 failed. You may need to download lectures manually.")
        response = input("Continue to next task? (y/n): ").strip().lower()
        if response != 'y':
            return
    
    # Task 2: Preprocess Audio
    success = run_task(2, "PREPROCESSING AUDIO", "task2_preprocess_audio")
    if not success:
        print("❌ Task 2 failed. Cannot continue without processed audio.")
        return
    
    # Task 3: Preprocess Text
    success = run_task(3, "PREPROCESSING TEXT", "task3_preprocess_text")
    if not success:
        print("⚠️  Task 3 failed. You may need to download and process transcripts manually.")
        response = input("Continue to next task? (y/n): ").strip().lower()
        if response != 'y':
            return
    
    # Task 4: Create Manifest
    success = run_task(4, "CREATING TRAINING MANIFEST", "task4_create_manifest")
    if not success:
        print("❌ Task 4 failed. Cannot launch dashboard without manifest.")
        return
    
    # Task 5: Launch Dashboard
    print_header("TASK 5: LAUNCHING DASHBOARD")
    print("The dashboard will open in a new window.")
    print("To launch the dashboard manually later, run:")
    print("  python dashboard/app.py")
    
    response = input("\nLaunch dashboard now? (y/n): ").strip().lower()
    
    if response == 'y':
        os.chdir('dashboard')
        success = run_task(5, "INTERACTIVE DASHBOARD", "app")
    
    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE!")
    print("=" * 70)
    print("\n✅ All tasks completed successfully!")
    print("\nNext steps:")
    print("  1. Review the generated files in the output/ directory")
    print("  2. Launch the dashboard: python dashboard/app.py")
    print("  3. Explore the dataset statistics and visualizations")
    print("\nThank you for using the AI4Bharat Data Engineering Pipeline!")

if __name__ == "__main__":
    main()
