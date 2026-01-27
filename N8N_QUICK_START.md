# n8n Quick Start Guide

## Your API URL
```
https://audiencecleaner.onrender.com
```

## Quick n8n Setup

### Step 1: Add HTTP Request Node

1. **Add HTTP Request node** to your n8n workflow

2. **Configure:**
   - **Method**: `POST`
   - **URL**: `https://audiencecleaner.onrender.com/upload`
   - **Send Body**: Yes
   - **Body Content Type**: `Form-Data`
   - **Specify Body**: Yes

3. **Body Parameters:**
   - **Name**: `file`
   - **Type**: `File`
   - **Value**: `{{ $binary.data }}` (or your file input)

4. **Options:**
   - **Timeout**: `600000` (10 minutes for large files)

### Step 2: Save the Response

Add a **Set** node or **Write Binary File** node after HTTP Request:
- **File Name**: `cleaned_output.csv`
- **Data**: `{{ $binary.data }}`

## Test Your Setup

1. Upload a CSV file in n8n
2. The HTTP Request node will send it to your API
3. You'll get back the cleaned CSV file
4. Save it using Write Binary File node

## Example Workflow

```
[Webhook/Trigger] 
    ↓
[HTTP Request]
    Method: POST
    URL: https://audiencecleaner.onrender.com/upload
    Body: Form-Data
    file: {{ $binary.data }}
    ↓
[Write Binary File]
    File: cleaned_output.csv
    Data: {{ $binary.data }}
```

## Important Notes

- ✅ **Handles large files** (50MB+) without crashing
- ✅ **Free tier**: May take 30 seconds on first request (spin-up time)
- ✅ **No memory issues**: Uses streaming processing
- ⚠️ **Timeout**: Set to 600000ms (10 minutes) for large files

## Troubleshooting

**"Connection timeout"**
- Increase timeout in HTTP Request node to 600000ms
- Large files take time to process

**"Service unavailable"**
- Free tier spins down after 15 min inactivity
- First request may take 30 seconds to wake up
- Consider using a health check service to keep it alive

**Test API directly:**
```bash
curl https://audiencecleaner.onrender.com/health
```
Should return: `{"status":"healthy","service":"audience-cleaner-api"}`


