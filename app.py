from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import threading
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Store download progress
download_progress = {}

class ProgressHook:
    def __init__(self, download_id):
        self.download_id = download_id
    
    def __call__(self, d):
        if d['status'] == 'downloading':
            # Extract progress information
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
            download_progress[self.download_id] = {
                'status': 'finished',
                'filename': d['filename']
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
        
        # Configure yt-dlp for info extraction only
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            },
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'formats': len(info.get('formats', [])) if info.get('formats') else 0
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
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [ProgressHook(download_id)],
            # Add user agent and other headers to avoid bot detection
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '300',
                'Connection': 'keep-alive',
            },
            # Additional options to bypass restrictions
            'extractor_args': {
                'youtube': {
                    'skip': ['dash'],
                    'player_client': ['web', 'android'],
                    'player_skip': ['configs'],
                }
            },
            # Retry options
            'retries': 10,
            'fragment_retries': 10,
            # Sleep between requests to avoid rate limiting
            'sleep_interval': 2,
            'max_sleep_interval': 10,
            'sleep_interval_requests': 1,
            'sleep_interval_subtitles': 1,
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
        }
        
        # Set quality options
        if quality == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif quality == 'best':
            ydl_opts['format'] = 'best'
        elif quality == 'worst':
            ydl_opts['format'] = 'worst'
        else:
            ydl_opts['format'] = f'best[height<={quality}]'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
    except Exception as e:
        error_msg = str(e)
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            download_progress[download_id] = {
                'status': 'error',
                'error': 'YouTube blocked the request. Try using cookies or wait before trying again.'
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
        files = []
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        return jsonify(files)
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
