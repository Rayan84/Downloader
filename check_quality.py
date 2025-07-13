import os
import subprocess
import json

def get_video_info(file_path):
    """Get video information using ffprobe (if available) or file size"""
    try:
        # Try to use ffprobe for detailed video info
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            if video_stream:
                return {
                    'resolution': f"{video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}",
                    'codec': video_stream.get('codec_name', 'N/A'),
                    'fps': video_stream.get('r_frame_rate', 'N/A'),
                    'bitrate': video_stream.get('bit_rate', 'N/A'),
                    'duration': float(data.get('format', {}).get('duration', 0)),
                    'audio_codec': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A'
                }
    except Exception as e:
        pass
    
    # Fallback to file size only
    return {
        'resolution': 'Unknown',
        'codec': 'Unknown',
        'fps': 'Unknown',
        'bitrate': 'Unknown',
        'duration': 0,
        'audio_codec': 'Unknown'
    }

def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def format_duration(seconds):
    """Format duration in MM:SS format"""
    if seconds <= 0:
        return "Unknown"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# Check videos in downloads folder
downloads_folder = "downloads"
if os.path.exists(downloads_folder):
    print("🎥 VIDEO QUALITY ANALYSIS")
    print("=" * 80)
    
    video_files = [f for f in os.listdir(downloads_folder) if f.endswith('.mp4')]
    
    # Sample a few videos to check quality
    sample_files = video_files[:10]  # Check first 10 videos
    
    for filename in sample_files:
        filepath = os.path.join(downloads_folder, filename)
        file_size = os.path.getsize(filepath)
        
        print(f"\n📹 {filename}")
        print(f"   Size: {format_size(file_size)}")
        
        video_info = get_video_info(filepath)
        print(f"   Resolution: {video_info['resolution']}")
        print(f"   Duration: {format_duration(video_info['duration'])}")
        print(f"   Video Codec: {video_info['codec']}")
        print(f"   Audio Codec: {video_info['audio_codec']}")
        
        if video_info['fps'] != 'Unknown':
            print(f"   FPS: {video_info['fps']}")
        if video_info['bitrate'] != 'Unknown' and video_info['bitrate'] != 'N/A':
            bitrate_mbps = int(video_info['bitrate']) / 1000000
            print(f"   Bitrate: {bitrate_mbps:.1f} Mbps")
        
        print("-" * 40)
    
    print(f"\n📊 SUMMARY:")
    print(f"Total videos: {len(video_files)}")
    print(f"Total size: {format_size(sum(os.path.getsize(os.path.join(downloads_folder, f)) for f in video_files))}")
    
    # Categorize by file size (rough quality estimation)
    small_files = [f for f in video_files if os.path.getsize(os.path.join(downloads_folder, f)) < 10*1024*1024]  # < 10MB
    medium_files = [f for f in video_files if 10*1024*1024 <= os.path.getsize(os.path.join(downloads_folder, f)) < 50*1024*1024]  # 10-50MB
    large_files = [f for f in video_files if os.path.getsize(os.path.join(downloads_folder, f)) >= 50*1024*1024]  # > 50MB
    
    print(f"\n📈 SIZE DISTRIBUTION (Quality estimation):")
    print(f"Small files (< 10MB, likely 360p or audio): {len(small_files)}")
    print(f"Medium files (10-50MB, likely 480p-720p): {len(medium_files)}")
    print(f"Large files (> 50MB, likely 720p+ or long videos): {len(large_files)}")

else:
    print("Downloads folder not found!")
