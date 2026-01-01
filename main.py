"""
FastAPI MCP Server with SSE Transport for ChatGPT
Implements Server-Sent Events to match Cristina's Node.js implementation
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import json
import asyncio
import uuid
from datetime import datetime

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


# Store for SSE connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, asyncio.Queue] = {}
    
    async def connect(self, connection_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.active_connections[connection_id] = queue
        return queue
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].put(message)


manager = ConnectionManager()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "Color Accessibility MCP Server",
        "version": "1.0.0",
        "message": "WCAG Color Accessibility Checker - Ready",
        "endpoints": {
            "mcp": "/mcp (POST) - Traditional MCP endpoint",
            "sse": "/mcp/sse (GET) - Server-Sent Events for streaming",
            "messages": "/mcp/messages (POST) - SSE messages endpoint",
            "health": "/health (GET) - Health check"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "wcag-accessibility-mcp"}


# Traditional MCP endpoint (POST) - For ChatGPT Custom Actions
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Traditional JSON-RPC 2.0 endpoint for MCP protocol
    Works with ChatGPT Custom Actions (no SSE required)
    
    Supported methods:
    - initialize: Protocol handshake
    - tools/list: Returns available tools
    - tools/call: Executes the analyze_accessibility tool
    """
    try:
        body = await request.json()
        
        method = body.get("method")
        request_id = body.get("id")
        params = body.get("params", {})
        
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "Color Accessibility MCP Server",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
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
            })
        
        elif method == "tools/call":
            result = await handle_tool_call_sync(request_id, params)
            return JSONResponse(content=result)
        
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except Exception as e:
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }, status_code=500)


async def handle_tool_call_sync(request_id: Optional[Union[str, int]], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle tools/call method synchronously (for traditional POST /mcp)
    """
    if not params:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "Invalid params: params object is required"
            }
        }
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name != "analyze_accessibility":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": f"Unknown tool: {tool_name}"
            }
        }
    
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
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(analysis_results, indent=2)
                    },
                    {
                        "type": "resource",
                        "resource": {
                            "uri": "ui://widget/color-accessibility.html",
                            "mimeType": "text/html+skybridge",
                            "text": html_widget
                        }
                    }
                ]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }



# SSE endpoint for ChatGPT
@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    """
    Server-Sent Events endpoint for MCP protocol
    ChatGPT connects here to receive responses
    """
    connection_id = str(uuid.uuid4())
    queue = await manager.connect(connection_id)
    
    async def event_generator():
        try:
            # Send initial connection event
            yield f"event: endpoint\ndata: /mcp/messages\n\n"
            
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # Send message as SSE event
                    data = json.dumps(message)
                    yield f"event: message\ndata: {data}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"
                    continue
                    
        finally:
            manager.disconnect(connection_id)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Messages endpoint for ChatGPT to send requests
@app.post("/mcp/messages")
async def mcp_messages(request: Request):
    """
    POST endpoint for receiving messages from ChatGPT
    Processes JSON-RPC requests and sends responses via SSE
    """
    try:
        body = await request.json()
        
        # Extract connection ID from headers or generate new one
        connection_id = request.headers.get("X-Connection-Id", str(uuid.uuid4()))
        
        # Process JSON-RPC request
        method = body.get("method")
        request_id = body.get("id")
        params = body.get("params")
        
        response = None
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "Color Accessibility MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
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
                            },
                            # CRITICAL: Tell ChatGPT to render HTML widget
                            "annotations": {
                                "readOnlyHint": True
                            },
                            "_meta": {
                                "openai/outputTemplate": "html"
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            response = await handle_tool_call(request_id, params)
        
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        # Send response via SSE
        if connection_id in manager.active_connections:
            await manager.send_message(connection_id, response)
        
        # Also return response directly for synchronous clients
        return JSONResponse(content=response)
        
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }
        return JSONResponse(content=error_response, status_code=500)


async def handle_tool_call(request_id: Optional[Union[str, int]], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle tools/call method
    Executes the requested tool and returns results
    """
    if not params:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "Invalid params: params object is required"
            }
        }
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name != "analyze_accessibility":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": f"Unknown tool: {tool_name}"
            }
        }
    
    try:
        # Validate input
        input_data = AnalyzeAccessibilityInput(**arguments)
        
        # Convert to dict format for analyzer
        color_pairs = [pair.model_dump() for pair in input_data.color_pairs]
        
        # Perform analysis
        analysis_results = analyze_accessibility(color_pairs)
        
        # Generate HTML widget
        html_widget = generate_widget(analysis_results)
        
        # Return result in MCP format (IDENTICAL to Node.js)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(analysis_results, indent=2)
                    },
                    {
                        "type": "resource",
                        "resource": {
                            "uri": "ui://widget/color-accessibility.html",
                            "mimeType": "text/html+skybridge",
                            "text": html_widget
                        }
                    }
                ]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)