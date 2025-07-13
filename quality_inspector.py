import os
import subprocess
import json
import time
from datetime import datetime

def monitor_downloads():
    """Monitor the downloads folder for new files"""
    print("🔍 MONITORING DOWNLOADS FOLDER FOR NEW 4K VIDEOS")
    print("=" * 70)
    
    downloads_folder = "downloads"
    if not os.path.exists(downloads_folder):
        print("❌ Downloads folder not found!")
        return
    
    # Get initial file list
    initial_files = set(os.listdir(downloads_folder))
    print(f"📁 Initial files: {len(initial_files)} videos")
    
    print("👀 Watching for new downloads... (Press Ctrl+C to stop)")
    
    try:
        while True:
            current_files = set(os.listdir(downloads_folder))
            new_files = current_files - initial_files
            
            if new_files:
                print(f"\n🎉 NEW DOWNLOAD DETECTED: {len(new_files)} new file(s)")
                for new_file in new_files:
                    if new_file.endswith('.mp4'):
                        print(f"   📺 {new_file}")
                        analyze_new_video(os.path.join(downloads_folder, new_file))
                initial_files = current_files
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")

def analyze_new_video(filepath):
    """Analyze a newly downloaded video for quality"""
    print(f"\n🔍 ANALYZING NEW VIDEO QUALITY")
    print("=" * 60)
    
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    print(f"📹 File: {filename}")
    print(f"📊 Size: {format_size(file_size)}")
    print(f"⏰ Downloaded: {datetime.now().strftime('%H:%M:%S')}")
    
    # Try to get technical details with ffprobe
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            analyze_video_streams(data)
        else:
            print("⚠️  ffprobe not available - using file size analysis")
            analyze_by_size(file_size)
            
    except Exception as e:
        print(f"⚠️  Technical analysis failed: {e}")
        analyze_by_size(file_size)
    
    print("=" * 60)

def analyze_video_streams(data):
    """Analyze video streams from ffprobe data"""
    video_stream = None
    audio_stream = None
    
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_stream = stream
        elif stream.get('codec_type') == 'audio':
            audio_stream = stream
    
    if video_stream:
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        fps = video_stream.get('r_frame_rate', 'N/A')
        codec = video_stream.get('codec_name', 'N/A')
        bitrate = video_stream.get('bit_rate')
        
        print(f"🎬 VIDEO DETAILS:")
        print(f"   Resolution: {width}x{height}")
        print(f"   Quality: {get_quality_name(height)}")
        print(f"   Codec: {codec}")
        print(f"   FPS: {fps}")
        
        if bitrate:
            bitrate_mbps = int(bitrate) / 1000000
            print(f"   Bitrate: {bitrate_mbps:.1f} Mbps")
        
        # Quality assessment
        if height >= 2160:
            print("🌟 EXCELLENT! This is 4K Ultra HD quality!")
        elif height >= 1440:
            print("🎥 GREAT! This is 1440p Quad HD quality!")
        elif height >= 1080:
            print("🟣 GOOD! This is 1080p Full HD quality!")
        elif height >= 720:
            print("🟠 DECENT! This is 720p HD quality!")
        else:
            print("🟡 BASIC! This is standard definition quality!")
    
    if audio_stream:
        audio_codec = audio_stream.get('codec_name', 'N/A')
        audio_bitrate = audio_stream.get('bit_rate')
        print(f"🎵 AUDIO DETAILS:")
        print(f"   Codec: {audio_codec}")
        if audio_bitrate:
            audio_bitrate_kbps = int(audio_bitrate) / 1000
            print(f"   Bitrate: {audio_bitrate_kbps:.0f} kbps")
    
    # Overall file info
    duration = float(data.get('format', {}).get('duration', 0))
    if duration > 0:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"⏱️  Duration: {minutes}:{seconds:02d}")

def analyze_by_size(file_size):
    """Analyze quality based on file size"""
    size_mb = file_size / (1024 * 1024)
    
    print(f"📊 QUALITY ESTIMATION (based on file size):")
    
    if size_mb >= 100:
        print("🌟 LIKELY 4K+ or very long video! (>100MB)")
    elif size_mb >= 50:
        print("🎬 LIKELY 4K or long 1080p+ video! (50-100MB)")
    elif size_mb >= 20:
        print("🎥 LIKELY 1080p or short 4K video! (20-50MB)")
    elif size_mb >= 10:
        print("🟣 LIKELY 720p-1080p quality! (10-20MB)")
    elif size_mb >= 5:
        print("🟠 LIKELY 480p-720p quality! (5-10MB)")
    else:
        print("🟡 LIKELY 360p or audio-only! (<5MB)")

def get_quality_name(height):
    """Get quality name from height"""
    if height >= 4320:
        return "8K (4320p)"
    elif height >= 2160:
        return "4K (2160p)"
    elif height >= 1440:
        return "1440p"
    elif height >= 1080:
        return "1080p"
    elif height >= 720:
        return "720p"
    elif height >= 480:
        return "480p"
    elif height >= 360:
        return "360p"
    else:
        return "240p"

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def analyze_latest_download():
    """Analyze the most recently downloaded video"""
    print("🔍 ANALYZING LATEST DOWNLOAD")
    print("=" * 60)
    
    downloads_folder = "downloads"
    if not os.path.exists(downloads_folder):
        print("❌ Downloads folder not found!")
        return
    
    # Get the most recent file
    files = [(f, os.path.getmtime(os.path.join(downloads_folder, f))) 
             for f in os.listdir(downloads_folder) if f.endswith('.mp4')]
    
    if not files:
        print("❌ No video files found!")
        return
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    latest_file = files[0][0]
    
    print(f"📺 Latest download: {latest_file}")
    analyze_new_video(os.path.join(downloads_folder, latest_file))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_downloads()
    else:
        analyze_latest_download()
