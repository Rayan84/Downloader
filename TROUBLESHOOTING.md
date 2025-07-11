# How to Fix YouTube Download Issues

YouTube frequently blocks automated downloads to prevent bot activity. Here are several solutions:

## Method 1: Use Browser Cookies (Recommended)

1. **Install a browser extension:**
   - Chrome: "Get cookies.txt LOCALLY" or "cookies.txt"
   - Firefox: "cookies.txt" extension

2. **Export cookies:**
   - Go to YouTube in your browser and sign in
   - Navigate to any YouTube video
   - Click the extension icon
   - Export cookies as "cookies.txt"
   - Save the file in this project folder (replace the existing cookies.txt)

3. **Restart the Flask application**

## Method 2: Try Different Video URLs

Some videos work better than others. Try:
- Recently uploaded videos
- Videos from smaller channels
- Public videos (not age-restricted or private)
- Videos from different regions

## Method 3: Use VPN

YouTube blocks may be region-specific. Try:
- Connecting through a VPN
- Using different server locations
- US, UK, or Canada servers often work well

## Method 4: Wait and Retry

YouTube's anti-bot measures are temporary:
- Wait 15-30 minutes between attempts
- Don't make too many requests in a short time
- Try during off-peak hours

## Method 5: Alternative Video Sources

If YouTube continues to block:
- Try videos from other platforms that yt-dlp supports
- Test with non-YouTube URLs (Vimeo, Twitter, etc.)

## Troubleshooting Common Errors:

- **"Sign in to confirm you're not a bot"**: Use cookies method
- **"HTTP Error 403: Forbidden"**: Try VPN or wait
- **"Video unavailable"**: Video may be region-locked or removed
- **"Private video"**: Cannot download private videos

## Testing Your Setup:

Try these test URLs that often work:
- https://www.youtube.com/watch?v=jNQXAC9IVRw (famous "Me at the zoo" video)
- Any short, public YouTube video

If the test videos work, the issue is likely with the specific video you're trying to download.
