from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import threading
import time
from werkzeug.utils import secure_filename
import shutil
import subprocess
import glob
import glob
import sys

app = Flask(__name__)


# Configuration: Use system Downloads folder
import getpass
if os.name == 'nt':
    DOWNLOAD_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Downloads')
else:
    DOWNLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')

# Ensure the Downloads folder exists (should always exist, but just in case)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Configure ffmpeg path
def find_ffmpeg():
    """Find ffmpeg executable"""
    # Try common locations and PATH
    common_paths = [
        r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe",
        r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        "ffmpeg.exe",
        "ffmpeg"
    ]
    
    for path in common_paths:
        if shutil.which(path) or os.path.exists(path):
            return path
    
    # Try to find via winget
    try:
        result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

FFMPEG_PATH = find_ffmpeg()
if FFMPEG_PATH:
    print(f"✅ Found ffmpeg at: {FFMPEG_PATH}")
else:
    print("❌ ffmpeg not found!")

def cleanup_partial_files(url=None):
    """Clean up partial download files"""
    try:
        patterns = ["*.part", "*.ytdl", "*.temp.mp4"]
        for pattern in patterns:
            files = glob.glob(os.path.join(DOWNLOAD_FOLDER, pattern))
            for file_path in files:
                try:
                    os.remove(file_path)
                except:
                    pass  # Ignore if file is in use
    except:
        pass  # Ignore cleanup errors

# Store download progress
download_progress = {}

class ProgressHook:
    def __init__(self, download_id):
        self.download_id = download_id
        self.finished_file = None

    def __call__(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            download_progress[self.download_id] = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta
            }
        elif d['status'] == 'finished':
            self.finished_file = d.get('filename')
            download_progress[self.download_id] = {
                'status': 'finished',
                'filename': d.get('filename')
            }
        elif d['status'] == 'error':
            download_progress[self.download_id] = {
                'status': 'error',
                'error': str(d.get('error', 'Unknown error'))
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video-info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Configure yt-dlp for info extraction with full format access
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'ios'],  # Multiple clients for better format access
                    'player_skip': ['configs'],
                }
            },
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract available qualities with proper 4K/8K detection including ultra-wide formats
            formats = info.get('formats', [])
            available_qualities = set()
            for f in formats:
                if f.get('height') and f.get('width'):
                    height = f.get('height')
                    width = f.get('width')
                    
                    # Calculate total pixels for ultra-wide format detection
                    total_pixels = height * width
                    
                    # Ultra-wide 4K detection (3840x1406 = ~5.4M pixels, standard 4K = ~8.3M pixels)
                    if total_pixels >= 16000000:  # 8K territory (7680x4320 = ~33M pixels)
                        available_qualities.add('8K/Ultra-wide 4K')
                    elif total_pixels >= 4000000 or width >= 3840:  # 4K territory (including ultra-wide)
                        available_qualities.add('4K/Ultra-wide 4K')
                    elif height >= 2160:  # Standard 4K by height
                        available_qualities.add('4K (2160p)')
                    elif height >= 1440 or total_pixels >= 2500000:  # 1440p or equivalent ultra-wide
                        available_qualities.add('1440p/Ultra-wide')
                    elif height >= 1080 or total_pixels >= 1800000:  # 1080p or equivalent ultra-wide
                        available_qualities.add('1080p/Ultra-wide')
                    elif height >= 720:
                        available_qualities.add('720p')
                    elif height >= 480:
                        available_qualities.add('480p')
                    elif height >= 360:
                        available_qualities.add('360p')
                    else:
                        available_qualities.add('240p')
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'available_qualities': sorted(list(available_qualities), reverse=True),
                'formats_count': len(formats)
            })
            
    except Exception as e:
        error_msg = str(e)
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            return jsonify({
                'error': 'YouTube is blocking the request. Please try with cookies or a different video.',
                'suggestion': 'Try using cookies.txt file or wait a few minutes before trying again.'
            }), 429
        else:
            return jsonify({'error': f'Could not extract video info: {error_msg}'}), 400

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Generate unique download ID
        download_id = str(int(time.time() * 1000))
        
        # Initialize progress
        download_progress[download_id] = {
            'status': 'starting',
            'percent': '0%',
            'speed': 'N/A',
            'eta': 'N/A'
        }
        
        # Start download in background thread
        thread = threading.Thread(target=download_video_async, args=(url, quality, download_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({'download_id': download_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def download_video_async(url, quality, download_id):
    try:
        # Clean up any existing partial downloads for this video first
        cleanup_partial_files(url)
        
        # Configure yt-dlp options with enhanced bypass strategies
        progress_hook = ProgressHook(download_id)
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            # Add ffmpeg path if found
            'ffmpeg_location': FFMPEG_PATH if FFMPEG_PATH else None,
            # Better error handling and recovery
            'ignoreerrors': False,
            'no_warnings': False,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            # Cleanup partial files on error
            'keepvideo': False,
            # Force cleanup of temporary files
            'nopart': False,  # Allow .part files for resume capability
            # Enhanced bypass options
            'force_generic_extractor': False,
            'extract_flat': False,
            # Add user agent and other headers to avoid bot detection
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            },
            # Additional options to bypass restrictions
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'ios', 'mweb'],  # Multiple clients for better format access
                    'player_skip': ['configs'],
                    'skip': ['hls', 'dash'],  # Skip problematic formats
                    'include_hls_manifest': False,
                    'include_dash_manifest': False,
                }
            },
            # Retry options
            'retries': 10,
            'fragment_retries': 10,
            # Sleep between requests to avoid rate limiting
            'sleep_interval': 3,
            'max_sleep_interval': 15,
            'sleep_interval_requests': 2,
            'sleep_interval_subtitles': 2,
            # Use cookies if available
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            # Additional bypass options
            'no_check_certificate': True,
            'prefer_insecure': False,
            'force_json': False,
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # More bypass options
            'age_limit': None,
            'match_filter': None,
            'no_color': True,
            'call_home': False,
        }

        # After download, create a marker file for tracking
        def mark_downloaded(filepath):
            marker = filepath + ".ytserver"
            try:
                with open(marker, 'w') as f:
                    f.write('downloaded by ytserver')
            except Exception as e:
                print(f"[DEBUG] Could not create marker for {filepath}: {e}")
        
        # Set quality options with 4K/8K support
        if quality == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif quality == 'best':
            # Best quality with ffmpeg support - merge best video and audio for highest quality
            ydl_opts['format'] = 'bestvideo[width>=3840]+bestaudio/bestvideo[height>=1080]+bestaudio/best'
        elif quality == '8K' or quality == '4320':
            # 8K with fallbacks
            ydl_opts['format'] = 'best[height<=4320][height>=2160]/best[height<=2160]/best[height<=1440]/best'
        elif quality == '4K' or quality == '2160':
            # 4K with ffmpeg support - merge ultra-wide 4K video with best audio
            ydl_opts['format'] = 'bestvideo[width>=3840]+bestaudio/bestvideo[height>=2160]+bestaudio/bestvideo[height>=1440]+bestaudio/best'
        elif quality == '1440':
            # 1440p with fallbacks
            ydl_opts['format'] = 'best[height<=1440][height>=1080]/best[height<=1440]/best[height<=1080]/best'
        elif quality == '1080':
            # 1080p with fallbacks
            ydl_opts['format'] = 'best[height<=1080][height>=720]/best[height<=1080]/best[height<=720]/best'
        elif quality == 'worst':
            ydl_opts['format'] = 'worst[height>=360]/worst'
        elif quality == '720':
            # 720p with fallbacks
            ydl_opts['format'] = 'best[height<=720][height>=480]/best[height<=720]/best[height<=480]/best'
        elif quality == '480':
            # 480p with fallbacks
            ydl_opts['format'] = 'best[height<=480][height>=360]/best[height<=480]/best'
        elif quality == '360':
            # 360p with fallbacks
            ydl_opts['format'] = 'best[height<=360]/worst[height>=240]/worst'
        else:
            # Custom resolution with fallbacks
            ydl_opts['format'] = f'best[height<={quality}][height>={int(quality)*0.75}]/best[height<={quality}]/best'
        
        # Try download with primary strategy first
        success = False
        strategies = [
            {
                'name': 'primary',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios', 'mweb'],
                        'player_skip': ['configs'],
                    }
                }
            },
            {
                'name': 'android_fallback',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                },
                'format_override': 'best[height<=720]/best'
            },
            {
                'name': 'web_simple',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                    }
                },
                'format_override': 'best[height<=480]/worst'
            }
        ]
        
        for strategy in strategies:
            try:
                # Update progress
                download_progress[download_id] = {
                    'status': 'downloading',
                    'percent': '0%',
                    'speed': 'Trying ' + strategy['name'],
                    'eta': 'N/A'
                }

                # Apply strategy-specific settings
                strategy_opts = ydl_opts.copy()
                strategy_opts['extractor_args'] = strategy['extractor_args']

                # Override format if specified
                if 'format_override' in strategy:
                    if quality == 'best' or quality == '4K':
                        strategy_opts['format'] = strategy['format_override']

                print(f"Trying strategy: {strategy['name']}")
                with yt_dlp.YoutubeDL(strategy_opts) as ydl:
                    result = ydl.download([url])

                # After download, mark the exact finished file (from progress hook), fallback to most recent .mp4 if needed
                try:
                    finished_file = progress_hook.finished_file
                    if finished_file and os.path.isfile(finished_file):
                        mark_downloaded(finished_file)
                        print(f"[DEBUG] Marked downloaded file: {finished_file}")
                    else:
                        # Fallback: mark the most recent .mp4 file in the Downloads folder
                        print(f"[DEBUG] No finished file to mark (progress_hook): {finished_file}")
                        mp4_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.lower().endswith('.mp4')]
                        if mp4_files:
                            mp4_files_full = [os.path.join(DOWNLOAD_FOLDER, f) for f in mp4_files]
                            most_recent_mp4 = max(mp4_files_full, key=os.path.getmtime)
                            mark_downloaded(most_recent_mp4)
                            print(f"[DEBUG] Fallback: Marked most recent mp4: {most_recent_mp4}")
                        else:
                            print(f"[DEBUG] No mp4 files found for fallback marker.")
                except Exception as e:
                    print(f"[DEBUG] Could not mark downloaded file: {e}")
                success = True
                break

            except Exception as e:
                print(f"Strategy {strategy['name']} failed: {e}")
                continue
        
        if not success:
            raise Exception("All download strategies failed")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Download error for {download_id}: {error_msg}")  # Debug logging
        
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            download_progress[download_id] = {
                'status': 'error',
                'error': 'YouTube blocked the request. Try using fresh cookies or wait before trying again.'
            }
        elif 'downloaded file is empty' in error_msg.lower():
            download_progress[download_id] = {
                'status': 'error',
                'error': 'Download blocked by YouTube. The video may be region-restricted or require sign-in. Try with different cookies or a VPN.'
            }
        elif 'Private video' in error_msg:
            download_progress[download_id] = {
                'status': 'error',
                'error': 'This video is private and cannot be downloaded.'
            }
        elif 'Video unavailable' in error_msg:
            download_progress[download_id] = {
                'status': 'error',
                'error': 'Video is unavailable or has been removed.'
            }
        elif 'HTTP Error 403' in error_msg or 'Forbidden' in error_msg:
            download_progress[download_id] = {
                'status': 'error',
                'error': 'Access forbidden. YouTube is blocking this request. Try refreshing cookies or using a VPN.'
            }
        elif 'HTTP Error 429' in error_msg or 'rate limit' in error_msg.lower():
            download_progress[download_id] = {
                'status': 'error',
                'error': 'Rate limited by YouTube. Please wait a few minutes before trying again.'
            }
        else:
            download_progress[download_id] = {
                'status': 'error',
                'error': f'Download failed: {error_msg}'
            }

@app.route('/progress/<download_id>')
def get_progress(download_id):
    progress = download_progress.get(download_id, {'status': 'not_found'})
    return jsonify(progress)

@app.route('/downloads')
def list_downloads():
    try:
        print("[DEBUG] Listing files in:", DOWNLOAD_FOLDER)
        all_files = os.listdir(DOWNLOAD_FOLDER)
        print("[DEBUG] All files:", all_files)
        files = []
        for filename in all_files:
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            # Only include files with a .ytserver marker
            marker = filepath + ".ytserver"
            if os.path.isfile(filepath) and os.path.exists(marker):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        print("[DEBUG] Files returned to frontend:", [f['name'] for f in files])
        # Sort files by modification time descending
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify(files)
    except Exception as e:
        print("[DEBUG] Exception in /downloads:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/download-file/<filename>')
def download_file(filename):
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(DOWNLOAD_FOLDER, safe_filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/show-in-explorer/<filename>')
def show_in_explorer(filename):
    from flask import abort
    print(f"[ShowInExplorer] Requested filename: {filename}")
    # Always resolve to Downloads folder, ignore any path in filename, but keep original filename (with spaces)
    real_filename = os.path.basename(filename)
    print(f"[ShowInExplorer] Using real filename: {real_filename}")
    filepath = os.path.abspath(os.path.join(DOWNLOAD_FOLDER, real_filename))
    print(f"[ShowInExplorer] Full file path: {filepath}")
    if not os.path.exists(filepath):
        print(f"[ShowInExplorer] File not found: {filepath}")
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    try:
        print(f"[ShowInExplorer] Platform: {sys.platform}")
        if sys.platform.startswith('win'):
            # Use explorer to select the file
            print(f"[ShowInExplorer] Running: explorer /select,\"{filepath}\"")
            subprocess.Popen(['explorer', f'/select,{filepath}'])
        elif sys.platform == 'darwin':
            print(f"[ShowInExplorer] Running: open -R {filepath}")
            subprocess.Popen(['open', '-R', filepath])
        else:
            print(f"[ShowInExplorer] Running: xdg-open {os.path.dirname(filepath)}")
            subprocess.Popen(['xdg-open', os.path.dirname(filepath)])
        print(f"[ShowInExplorer] Success!")
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"[ShowInExplorer] Exception: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
