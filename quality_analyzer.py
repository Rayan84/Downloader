import os

def analyze_downloads():
    downloads_folder = "downloads"
    
    print("🎥 YOUTUBE DOWNLOADER - VIDEO QUALITY ANALYSIS")
    print("=" * 70)
    
    if not os.path.exists(downloads_folder):
        print("❌ Downloads folder not found!")
        return
    
    files = os.listdir(downloads_folder)
    video_files = [f for f in files if f.endswith('.mp4')]
    
    if not video_files:
        print("❌ No video files found!")
        return
    
    print(f"📊 FOUND {len(video_files)} VIDEO FILES\n")
    
    # Analyze by file size (quality estimation)
    quality_analysis = {
        'Low Quality (< 5MB)': [],
        'Medium Quality (5-15MB)': [],
        'Good Quality (15-50MB)': [],
        'High Quality (50MB+)': []
    }
    
    total_size = 0
    
    for filename in video_files:
        filepath = os.path.join(downloads_folder, filename)
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        total_size += size_bytes
        
        # Categorize by size
        if size_mb < 5:
            quality_analysis['Low Quality (< 5MB)'].append((filename, size_mb))
        elif size_mb < 15:
            quality_analysis['Medium Quality (5-15MB)'].append((filename, size_mb))
        elif size_mb < 50:
            quality_analysis['Good Quality (15-50MB)'].append((filename, size_mb))
        else:
            quality_analysis['High Quality (50MB+)'].append((filename, size_mb))
    
    # Display analysis
    for category, files in quality_analysis.items():
        if files:
            print(f"🎬 {category}: {len(files)} files")
            for filename, size_mb in sorted(files, key=lambda x: x[1], reverse=True)[:5]:  # Show top 5
                print(f"   • {filename[:50]}{'...' if len(filename) > 50 else ''} ({size_mb:.1f} MB)")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
            print()
    
    # Summary statistics
    total_gb = total_size / (1024 * 1024 * 1024)
    avg_size_mb = (total_size / len(video_files)) / (1024 * 1024)
    
    print("📈 SUMMARY STATISTICS:")
    print(f"   Total files: {len(video_files)}")
    print(f"   Total size: {total_gb:.2f} GB")
    print(f"   Average file size: {avg_size_mb:.1f} MB")
    
    # Quality estimation based on typical YouTube file sizes
    print(f"\n🎯 ESTIMATED QUALITY DISTRIBUTION:")
    low_q = len(quality_analysis['Low Quality (< 5MB)'])
    med_q = len(quality_analysis['Medium Quality (5-15MB)'])
    good_q = len(quality_analysis['Good Quality (15-50MB)'])
    high_q = len(quality_analysis['High Quality (50MB+)'])
    
    print(f"   360p/Audio Only: {low_q} files ({low_q/len(video_files)*100:.1f}%)")
    print(f"   480p: {med_q} files ({med_q/len(video_files)*100:.1f}%)")
    print(f"   720p: {good_q} files ({good_q/len(video_files)*100:.1f}%)")
    print(f"   1080p+/Long videos: {high_q} files ({high_q/len(video_files)*100:.1f}%)")
    
    # Find largest and smallest files
    sizes = [(f, os.path.getsize(os.path.join(downloads_folder, f))) for f in video_files]
    largest = max(sizes, key=lambda x: x[1])
    smallest = min(sizes, key=lambda x: x[1])
    
    print(f"\n🏆 LARGEST FILE: {largest[0][:50]} ({largest[1]/(1024*1024):.1f} MB)")
    print(f"🔹 SMALLEST FILE: {smallest[0][:50]} ({smallest[1]/(1024*1024):.1f} MB)")
    
    print(f"\n💡 QUALITY TIPS:")
    print("   • Files < 5MB are likely 360p or audio-only")
    print("   • Files 5-15MB are typically 480p")
    print("   • Files 15-50MB are usually 720p")
    print("   • Files > 50MB are either 1080p+ or very long videos")
    print("   • Use 'best' quality setting for highest available resolution")

if __name__ == "__main__":
    analyze_downloads()
