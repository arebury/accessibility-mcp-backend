"""
FastAPI MCP Server for WCAG Color Accessibility Analysis
Implements JSON-RPC 2.0 protocol for ChatGPT integration
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import json

from color_analyzer import analyze_accessibility
from widget_generator import generate_widget


# Initialize FastAPI app
app = FastAPI(
    title="WCAG Color Accessibility MCP Server",
    description="MCP server for analyzing WCAG color accessibility with ChatGPT Vision",
    version="1.0.0"
)

# Enable CORS for ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ColorPair(BaseModel):
    background: str = Field(..., description="Background color (hex, rgb, etc.)")
    foreground: str = Field(..., description="Foreground/text color (hex, rgb, etc.)")
    text_size: str = Field(default="normal", description="Text size: 'normal' or 'large'")


class AnalyzeAccessibilityInput(BaseModel):
    color_pairs: List[ColorPair] = Field(..., description="Array of color pairs to analyze")


class JSONRPCRequest(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[Union[str, int]] = Field(default=None, description="Request ID")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")


class JSONRPCResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: Optional[Union[str, int]] = Field(default=None)
    result: Optional[Any] = Field(default=None)
    error: Optional[Dict[str, Any]] = Field(default=None)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "Color Accessibility MCP Server",
        "version": "1.0.0"
    }
    
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "Color Accessibility MCP Server",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "wcag-accessibility-mcp"}


# Main MCP endpoint
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Main MCP endpoint implementing JSON-RPC 2.0 protocol
    
    Supported methods:
    - tools/list: Returns available tools
    - tools/call: Executes the analyze_accessibility tool
    """
    try:
        # Parse JSON-RPC request
        body = await request.json()
        rpc_request = JSONRPCRequest(**body)
        
        # Handle different methods
        if rpc_request.method == "tools/list":
            return handle_tools_list(rpc_request.id)
        
        elif rpc_request.method == "tools/call":
            return await handle_tools_call(rpc_request.id, rpc_request.params)
        
        else:
            return JSONRPCResponse(
                id=rpc_request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {rpc_request.method}"
                }
            ).model_dump()
    
    except Exception as e:
        return JSONRPCResponse(
            id=None,
            error={
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        ).model_dump()


def handle_tools_list(request_id: Optional[Union[str, int]]) -> Dict[str, Any]:
    """
    Handle tools/list method
    Returns the list of available tools
    """
    return JSONRPCResponse(
        id=request_id,
        result={
            "tools": [
                {
                    "name": "analyze_accessibility",
                    "description": "Analyze WCAG color accessibility for multiple color pairs. Returns a visual HTML widget with contrast ratios, WCAG levels, and suggestions for failed pairs.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "color_pairs": {
                                "type": "array",
                                "description": "Array of color pairs to analyze",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "background": {
                                            "type": "string",
                                            "description": "Background color (hex, rgb, or CSS format)"
                                        },
                                        "foreground": {
                                            "type": "string",
                                            "description": "Foreground/text color (hex, rgb, or CSS format)"
                                        },
                                        "text_size": {
                                            "type": "string",
                                            "description": "Text size: 'normal' or 'large'",
                                            "enum": ["normal", "large"],
                                            "default": "normal"
                                        }
                                    },
                                    "required": ["background", "foreground"]
                                }
                            }
                        },
                        "required": ["color_pairs"]
                    }
                }
            ]
        }
    ).model_dump()


async def handle_tools_call(request_id: Optional[Union[str, int]], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle tools/call method
    Executes the requested tool and returns results
    """
    if not params:
        return JSONRPCResponse(
            id=request_id,
            error={
                "code": -32602,
                "message": "Invalid params: params object is required"
            }
        ).model_dump()
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name != "analyze_accessibility":
        return JSONRPCResponse(
            id=request_id,
            error={
                "code": -32602,
                "message": f"Unknown tool: {tool_name}"
            }
        ).model_dump()
    
    try:
        # Validate input
        input_data = AnalyzeAccessibilityInput(**arguments)
        
        # Convert to dict format for analyzer
        color_pairs = [pair.model_dump() for pair in input_data.color_pairs]
        
        # Perform analysis
        analysis_results = analyze_accessibility(color_pairs)
        
        # Generate HTML widget
        html_widget = generate_widget(analysis_results)
        
        # Return result in MCP format
        return JSONRPCResponse(
            id=request_id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": html_widget,
                        "mimeType": "text/html"
                    }
                ]
            }
        ).model_dump()
    
    except Exception as e:
        return JSONRPCResponse(
            id=request_id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        ).model_dump()


# Direct analysis endpoint (for testing/debugging)
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_direct(input_data: AnalyzeAccessibilityInput):
    """
    Direct analysis endpoint that returns HTML widget
    Useful for testing without JSON-RPC wrapper
    """
    try:
        # Convert to dict format
        color_pairs = [pair.model_dump() for pair in input_data.color_pairs]
        
        # Perform analysis
        analysis_results = analyze_accessibility(color_pairs)
        
        # Generate and return HTML widget
        html_widget = generate_widget(analysis_results)
        
        return HTMLResponse(content=html_widget)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
