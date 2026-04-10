# ShadowTag v2 Examples

This directory contains example scripts demonstrating various features of ShadowTag v2.

## Examples

### 1. Basic Watermarking (`basic_watermarking.py`)

Demonstrates the basic watermarking workflow:
- Loading a preset configuration
- Watermarking video and audio content
- Verifying watermarked content
- Extracting payload information

```bash
python examples/basic_watermarking.py
```

### 2. Platform Optimization (`platform_optimization.py`)

Shows how to use platform-specific presets:
- YouTube optimization
- TikTok optimization
- Instagram optimization
- Twitter optimization

```bash
python examples/platform_optimization.py
```

### 3. Quality Testing (`quality_testing.py`)

Demonstrates quality metric evaluation:
- Video quality (PSNR, SSIM)
- Audio quality (SNR)
- Watermark robustness (BER)
- Overall quality grading

```bash
python examples/quality_testing.py
```

### 4. Robustness Testing (`robustness_testing.py`)

Comprehensive robustness testing:
- H.264/H.265/VP9 compression attacks
- Platform simulation (YouTube, TikTok, Instagram)
- MP3/AAC/Opus audio encoding attacks
- Survival rate calculation

```bash
python examples/robustness_testing.py
```

## Prerequisites

Before running the examples, ensure you have:

1. Installed ShadowTag v2 and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. FFmpeg installed for video processing:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg
   ```

3. Sample input files (replace paths in examples):
   - `input_video.mp4`: Sample video file
   - `input_audio.wav`: Sample audio file

## Notes

- Examples use placeholder file paths (`input_video.mp4`, `input_audio.wav`)
- Replace with actual file paths before running
- Some examples require FFmpeg to be installed
- Blockchain features require additional configuration (see main README)
- GCP integration requires Google Cloud credentials (optional)

## Expected Output

Each example will:
1. Display configuration information
2. Process the watermarking/testing task
3. Show detailed results and metrics
4. Provide a summary of success/failure

## Troubleshooting

**FFmpeg not found:**
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

**File not found errors:**
- Update file paths in examples to point to your actual media files

**Import errors:**
- Ensure ShadowTag v2 is installed: `pip install -e .`
- Or add to PYTHONPATH: `export PYTHONPATH=/path/to/aiyou-fastapi-services:$PYTHONPATH`

## License

MIT License - See main LICENSE file for details.
