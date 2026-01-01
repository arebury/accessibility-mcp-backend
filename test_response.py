#!/usr/bin/env python3
import sys
import json

data = json.load(sys.stdin)
print('✅ Response structure:')
content = data.get('result', {}).get('content', [])
print(f'  - Number of content items: {len(content)}')
for i, item in enumerate(content):
    print(f'  - Item {i}: type="{item.get("type")}"')
    if item.get('type') == 'resource':
        res = item.get('resource', {})
        print(f'    URI: {res.get("uri")}')
        print(f'    mimeType: {res.get("mimeType")}')
        print(f'    HTML length: {len(res.get("text", ""))} chars')
