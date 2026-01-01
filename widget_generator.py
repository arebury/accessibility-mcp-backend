"""
HTML Widget Generator for WCAG Analysis Results
Generates embeddable HTML with inline Tailwind CSS
"""

from typing import Dict, Any


def generate_widget(analysis_results: Dict[str, Any]) -> str:
    """
    Generate HTML widget displaying WCAG analysis results
    
    Args:
        analysis_results: Output from analyze_accessibility()
    
    Returns:
        Complete HTML string with inline Tailwind CSS
    """
    stats = analysis_results["statistics"]
    results = analysis_results["results"]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WCAG Color Accessibility Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }}
    </style>
</head>
<body class="bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-6 mb-6 text-white">
            <h1 class="text-3xl font-bold mb-2">WCAG Color Accessibility Analysis</h1>
            <p class="text-blue-100">Comprehensive contrast ratio evaluation based on WCAG 2.1 guidelines</p>
        </div>
        
        <!-- Statistics Card -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Summary Statistics</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
                    <div class="text-2xl font-bold text-blue-700">{stats['total_pairs']}</div>
                    <div class="text-sm text-gray-600">Total Color Pairs</div>
                </div>
                <div class="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
                    <div class="text-2xl font-bold text-green-700">{stats['passes']}</div>
                    <div class="text-sm text-gray-600">Passes</div>
                </div>
                <div class="bg-red-50 rounded-lg p-4 border-l-4 border-red-500">
                    <div class="text-2xl font-bold text-red-700">{stats['failures']}</div>
                    <div class="text-sm text-gray-600">Failures</div>
                </div>
                <div class="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
                    <div class="text-2xl font-bold text-purple-700">{stats['text_count']['normal']}/{stats['text_count']['large']}</div>
                    <div class="text-sm text-gray-600">Normal/Large Text</div>
                </div>
            </div>
        </div>
        
        <!-- Color Pairs Results -->
        <div class="space-y-4">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Detailed Analysis</h2>
"""
    
    # Generate individual color pair cards
    for idx, result in enumerate(results, 1):
        passes = result["passes"]
        wcag_level = result["wcag_level"]
        
        # Determine badge color
        if wcag_level == "AAA":
            badge_class = "bg-green-100 text-green-800 border-green-300"
        elif wcag_level == "AA":
            badge_class = "bg-yellow-100 text-yellow-800 border-yellow-300"
        elif wcag_level == "Error":
            badge_class = "bg-gray-100 text-gray-800 border-gray-300"
        else:
            badge_class = "bg-red-100 text-red-800 border-red-300"
        
        card_border = "border-green-200" if passes else "border-red-200"
        
        html += f"""
            <div class="bg-white rounded-lg shadow-md p-6 border-2 {card_border}">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <span class="text-lg font-semibold text-gray-700">Pair #{idx}</span>
                        <span class="px-3 py-1 rounded-full text-xs font-semibold border {badge_class}">
                            {wcag_level}
                        </span>
                        <span class="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                            {result['text_size'].capitalize()} Text
                        </span>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold text-gray-800">{result['contrast_ratio']}:1</div>
                        <div class="text-xs text-gray-500">Contrast Ratio</div>
                    </div>
                </div>
                
                <!-- Color Chips -->
                <div class="flex items-center gap-4 mb-4">
                    <div class="flex-1">
                        <div class="text-xs text-gray-600 mb-2 font-medium">Background</div>
                        <div class="flex items-center gap-3">
                            <div class="w-16 h-16 rounded-lg shadow-inner border-2 border-gray-300" 
                                 style="background-color: {result['background']}"></div>
                            <code class="bg-gray-100 px-3 py-1 rounded text-sm font-mono">{result['background']}</code>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="text-xs text-gray-600 mb-2 font-medium">Foreground</div>
                        <div class="flex items-center gap-3">
                            <div class="w-16 h-16 rounded-lg shadow-inner border-2 border-gray-300" 
                                 style="background-color: {result['foreground']}"></div>
                            <code class="bg-gray-100 px-3 py-1 rounded text-sm font-mono">{result['foreground']}</code>
                        </div>
                    </div>
                </div>
                
                <!-- Preview -->
                <div class="mb-4">
                    <div class="text-xs text-gray-600 mb-2 font-medium">Preview</div>
                    <div class="p-4 rounded-lg border-2 border-gray-200" 
                         style="background-color: {result['background']}; color: {result['foreground']}">
                        <p class="{'text-lg' if result['text_size'] == 'large' else 'text-sm'}">
                            The quick brown fox jumps over the lazy dog
                        </p>
                    </div>
                </div>
"""
        
        # Add suggestion section if failed
        if not passes and result.get("suggestion"):
            suggestion = result["suggestion"]
            html += f"""
                <!-- Suggestion -->
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                    <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                        </svg>
                        <div class="flex-1">
                            <h4 class="font-semibold text-blue-900 mb-2">Suggested Fix</h4>
                            <div class="flex items-center gap-4 mb-3">
                                <div>
                                    <div class="text-xs text-blue-700 mb-1">Better Foreground</div>
                                    <div class="flex items-center gap-2">
                                        <div class="w-12 h-12 rounded-lg shadow-inner border-2 border-blue-300" 
                                             style="background-color: {suggestion['color']}"></div>
                                        <code class="bg-white px-2 py-1 rounded text-xs font-mono">{suggestion['color']}</code>
                                    </div>
                                </div>
                                <div>
                                    <div class="text-xs text-blue-700 mb-1">New Ratio</div>
                                    <div class="text-xl font-bold text-blue-900">{suggestion['contrast_ratio']}:1</div>
                                    <div class="text-xs text-blue-700">{suggestion['wcag_level']} Level</div>
                                </div>
                            </div>
                            <div class="p-3 rounded-lg bg-white border border-blue-200" 
                                 style="background-color: {result['background']}; color: {suggestion['color']}">
                                <p class="{'text-lg' if result['text_size'] == 'large' else 'text-sm'}">
                                    The quick brown fox jumps over the lazy dog
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
"""
        
        html += """
            </div>
"""
    
    # Footer
    html += """
        </div>
        
        <!-- Footer -->
        <div class="mt-8 text-center text-sm text-gray-500">
            <p>Based on WCAG 2.1 Level AA/AAA Guidelines</p>
            <p class="mt-1">
                <span class="font-medium">AA:</span> 4.5:1 (normal) / 3:1 (large) &nbsp;|&nbsp; 
                <span class="font-medium">AAA:</span> 7:1 (normal) / 4.5:1 (large)
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html
