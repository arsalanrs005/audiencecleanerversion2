# Performance Estimate for Large Files

## Your File
- **Size**: 541MB
- **Records**: 600,000 rows

## Time Breakdown

### 1. Render Spin-Up (if idle)
- **Time**: 30-60 seconds
- **When**: First request after 15 minutes of inactivity
- **Solution**: Keep the service alive with periodic health checks

### 2. File Upload
- **Depends on your upload speed:**
  - 10 Mbps: ~7 minutes
  - 50 Mbps: ~1.4 minutes
  - 100 Mbps: ~43 seconds
  - 500 Mbps: ~9 seconds

### 3. Processing Time
- **Processing speed**: ~10,000 rows/second
- **Your file**: 600,000 rows
- **Processing time**: ~60 seconds (1 minute)

### 4. File Download
- **Depends on your download speed:**
  - 10 Mbps: ~7 minutes
  - 50 Mbps: ~1.4 minutes
  - 100 Mbps: ~43 seconds
  - 500 Mbps: ~9 seconds

## Total Time Estimate

**Best case** (fast internet, service already running):
- Upload: 43 seconds
- Processing: 60 seconds
- Download: 43 seconds
- **Total: ~2.5 minutes**

**Average case** (moderate internet):
- Upload: 2-3 minutes
- Processing: 60 seconds
- Download: 2-3 minutes
- **Total: ~5-7 minutes**

**Worst case** (slow internet + spin-up):
- Spin-up: 60 seconds
- Upload: 7 minutes
- Processing: 60 seconds
- Download: 7 minutes
- **Total: ~15-16 minutes**

## Important Notes

1. **Timeout**: Make sure your HTTP client timeout is set to at least **600 seconds (10 minutes)** or more

2. **Render Free Tier**: 
   - May spin down after 15 min inactivity
   - First request takes 30-60 seconds to wake up
   - Consider using a health check service

3. **Progress**: The API doesn't show progress during processing, but it's working. Be patient!

4. **Memory**: Uses streaming, so memory stays constant regardless of file size

## Testing Recommendation

Test with a smaller file first (like your 22MB test2.csv) to verify everything works, then try the large file.

## Using curl

```bash
# Test with large file (set long timeout)
curl -X POST \
  -F "file=@your_large_file.csv" \
  https://audiencecleaner.onrender.com/upload \
  -o cleaned_output.csv \
  --max-time 1200
```

The `--max-time 1200` sets a 20-minute timeout.


