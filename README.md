# WCAG Color Accessibility MCP Server

A FastAPI-based Model Context Protocol (MCP) server that analyzes WCAG color accessibility from ChatGPT Vision. Uses the `coloraide` library for accurate WCAG 2.1 contrast calculations and generates beautiful, embeddable HTML widgets with analysis results and automatic color suggestions.

## Features

✨ **Complete WCAG 2.1 Analysis**
- Accurate contrast ratio calculations using coloraide
- Support for both normal and large text sizes
- AAA and AA compliance level detection

🎨 **Automatic Color Suggestions**
- Smart color adjustments for failed pairs
- Maintains visual harmony while meeting WCAG standards
- Before/after preview comparisons

📊 **Visual HTML Widgets**
- Beautiful, responsive design with Tailwind CSS
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
├── main.py              # FastAPI server with MCP endpoint
├── color_analyzer.py    # WCAG analysis logic using coloraide
├── widget_generator.py  # Generates visual HTML widget
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
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
        "name": "analyze_accessibility",
        "description": "Analyze WCAG color accessibility...",
        "inputSchema": { ... }
      }
    ]
  }
}
```

#### Method: `tools/call`

Executes the `analyze_accessibility` tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze_accessibility",
    "arguments": {
      "color_pairs": [
        {
          "background": "#FFFFFF",
          "foreground": "#767676",
          "text_size": "normal"
        },
        {
          "background": "#000000",
          "foreground": "#FFFFFF",
          "text_size": "large"
        }
      ]
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
        "text": "<html>...</html>",
        "mimeType": "text/html"
      }
    ]
  }
}
```

### Direct Analysis Endpoint: `POST /analyze`

Test endpoint that returns HTML widget directly (bypasses JSON-RPC).

**Request:**
```json
{
  "color_pairs": [
    {
      "background": "#FFFFFF",
      "foreground": "#767676",
      "text_size": "normal"
    }
  ]
}
```

**Response:** HTML widget (Content-Type: text/html)

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

1. **Deploy to Render.com** (see deployment section below)

2. **Add as ChatGPT Action**
   - Go to ChatGPT Settings → Actions
   - Add new action with your deployed URL
   - Import the schema from `/openapi.json`

3. **Use in ChatGPT**
   ```
   Analyze the color accessibility of:
   - White background (#FFFFFF) with gray text (#767676)
   - Black background (#000000) with white text (#FFFFFF)
   ```

   ChatGPT will use Vision to extract colors and call your MCP server to display the widget!

## Deployment to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and configure deployment
   - Click "Create Web Service"

3. **Get your URL**
   - After deployment, you'll get a URL like: `https://wcag-accessibility-mcp.onrender.com`
   - Use this URL in your ChatGPT Action configuration

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest httpx

# Run tests
pytest
```

### Interactive API Documentation

When running locally, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example cURL Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "color_pairs": [
      {
        "background": "#FFFFFF",
        "foreground": "#767676",
        "text_size": "normal"
      }
    ]
  }' > output.html

# Open the generated widget
open output.html
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **coloraide**: Advanced color science library with WCAG 2.1 support
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server
- **Tailwind CSS**: Utility-first CSS framework (via CDN in widget)

## License

MIT License - feel free to use this in your projects!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
