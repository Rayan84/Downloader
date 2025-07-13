import os
import glob

def cleanup_partial_downloads():
    """Clean up incomplete download files"""
    print("🧹 CLEANING UP INCOMPLETE DOWNLOADS")
    print("=" * 50)
    
    # Use system Downloads folder
    if os.name == 'nt':
        downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(downloads_folder):
        print(f"❌ Downloads folder not found: {downloads_folder}")
        return
    
    # File patterns to clean up
    patterns = [
        "*.part",
        "*.part-*",
        "*.ytdl",
        "*.temp.mp4",
        "*.f*.mp4.part*"
    ]
    
    total_cleaned = 0
    total_size_cleaned = 0
    
    for pattern in patterns:
        files = glob.glob(os.path.join(downloads_folder, pattern))
        for file_path in files:
            try:
                file_size = os.path.getsize(file_path)
                total_size_cleaned += file_size
                os.remove(file_path)
                print(f"🗑️  Removed: {os.path.basename(file_path)} ({file_size/1024/1024:.1f} MB)")
                total_cleaned += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"📁 Files removed: {total_cleaned}")
    print(f"💾 Space freed: {total_size_cleaned/1024/1024:.1f} MB")
    
    # Show remaining files
    remaining_files = [f for f in os.listdir(downloads_folder) 
                      if os.path.isfile(os.path.join(downloads_folder, f)) and f.endswith('.mp4')]
    
    print(f"\n📼 Clean video files remaining: {len(remaining_files)}")
    for file in remaining_files[:5]:  # Show first 5
        file_path = os.path.join(downloads_folder, file)
        size = os.path.getsize(file_path)
        print(f"  ✅ {file} ({size/1024/1024:.1f} MB)")
    
    if len(remaining_files) > 5:
        print(f"  ... and {len(remaining_files) - 5} more files")

if __name__ == "__main__":
    cleanup_partial_downloads()
