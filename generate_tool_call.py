#!/usr/bin/env python3
import json

# Test data for tool call
test_request = {
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

print(json.dumps(test_request))
