# WCAG Color Accessibility MCP Server

A FastAPI-based Model Context Protocol (MCP) server that analyzes WCAG color accessibility from ChatGPT Vision. Provides real-time color contrast analysis, WCAG compliance checking, and beautiful interactive HTML widgets.

## Author

**Rafael Areses Delgado-Brackenbury** ([@arebury](https://github.com/arebury))

## Features

✨ **Complete WCAG 2.1 Analysis**
- Accurate contrast ratio calculations
- Support for both normal and large text sizes
- AA and AAA compliance level detection

🎨 **Automatic Color Suggestions**
- Smart color adjustments for failed pairs
- Maintains visual harmony while meeting WCAG standards
- Before/after preview comparisons

📊 **Visual HTML Widgets**
- Beautiful, responsive design
- Summary statistics dashboard
- Detailed per-pair analysis with visual previews
- Embeds directly in ChatGPT conversations

🚀 **Production Ready**
- JSON-RPC 2.0 MCP protocol implementation
- CORS enabled for ChatGPT integration
- Health check endpoint for monitoring
- Render.com deployment configuration included

## Project Structure

```
.
├── main.py              # FastAPI MCP server
├── web/
│   └── ui-template.html # HTML widget template
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Requirements

- Python 3.9 or higher
- pip (Python package manager)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/arebury/accessibility-mcp-backend.git
   cd accessibility-mcp-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

   The server will start at `http://localhost:8000`

5. **Test the health endpoint**
   ```bash
   curl http://localhost:8000/health
   ```

## API Documentation

### MCP Endpoint: `POST /mcp`

Implements JSON-RPC 2.0 protocol for ChatGPT integration.

#### Method: `tools/list`

Returns available tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "analyze_color_accessibility",
        "description": "Analyze WCAG color accessibility from images",
        "inputSchema": { ... }
      }
    ]
  }
}
```

#### Method: `tools/call`

Executes the `analyze_color_accessibility` tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze_color_accessibility",
    "arguments": {
      "image_url": "https://example.com/image.png",
      "wcag_level": "AA"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...analysis results...}"
      },
      {
        "type": "resource",
        "resource": {
          "uri": "ui://widget/color-accessibility.html",
          "mimeType": "text/html",
          "text": "<html>...widget...</html>"
        }
      }
    ]
  }
}
```

### Health Check: `GET /health`

```json
{
  "status": "healthy",
  "service": "wcag-accessibility-mcp"
}
```

## WCAG Conformance Levels

The analyzer follows WCAG 2.1 Level AA/AAA standards:

| Text Size | AA Minimum | AAA Minimum |
|-----------|-----------|------------|
| Normal    | 4.5:1     | 7:1        |
| Large*    | 3:1       | 4.5:1      |

*Large text is defined as 18pt+ or 14pt+ bold

## Usage with ChatGPT

### Option 1: Developer Mode (Recommended)

1. **Deploy to Render.com** (see deployment section below)

2. **Enable Developer Mode in ChatGPT**
   - Settings → Apps → Advanced → Enable "Developer mode"

3. **Create App**
   - Settings → Apps → Create app
   - URL: `https://accessibility-mcp-backend.onrender.com`
   - Authentication: None

4. **Use in ChatGPT**
   ```
   Analyze the color accessibility of this image
   (attach screenshot)
   ```

   ChatGPT will extract colors and display an interactive widget!

### Option 2: Custom Connectors

1. **Deploy to Render.com**

2. **Add Connector**
   - Settings → Connectors → Add connector
   - URL: `https://accessibility-mcp-backend.onrender.com/mcp`
   - Authentication: None

3. **Use in ChatGPT**
   - Same as above

## Deployment to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/arebury/accessibility-mcp-backend.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and configure deployment
   - Click "Create Web Service"

3. **Get your URL**
   - After deployment, you'll get a URL like: `https://accessibility-mcp-backend.onrender.com`
   - Use this URL in your ChatGPT configuration

## Development

### Interactive API Documentation

When running locally, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Test

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | python -m json.tool
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pillow (PIL)**: Image processing for color extraction
- **pytesseract**: OCR for text detection in images
- **NumPy**: Numerical computations
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server

## License

MIT License

Copyright (c) 2026 Rafael Areses Delgado-Brackenbury

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/arebury/accessibility-mcp-backend/issues).

---

Created by **Rafael Areses Delgado-Brackenbury** ([@arebury](https://github.com/arebury))
