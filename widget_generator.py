"""
HTML Widget Generator for WCAG Analysis Results
Uses static HTML template with data injection (Cristina's approach)
"""

from typing import Dict, Any
import json
import os


def generate_widget(analysis_results: Dict[str, Any]) -> str:
    """
    Generate HTML widget by injecting data into template
    """
    # Read HTML template
    template_path = os.path.join(os.path.dirname(__file__), 'ui-template.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Transform data to match template format
    transformed_data = {
        "summary": {
            "total_pairs": analysis_results["statistics"]["total_pairs"],
            "passing_pairs": analysis_results["statistics"]["passes"],
            "failing_pairs": analysis_results["statistics"]["failures"],
            "detected_texts": analysis_results["statistics"]["total_pairs"]
        },
        "color_pairs": []
    }
    
    # Transform each result
    for idx, result in enumerate(analysis_results["results"]):
        pair = {
            "id": f"pair-{idx}",
            "text": f"Color Pair {idx + 1}",
            "background": result["background"],
            "foreground": result["foreground"],
            "contrast_ratio": result["contrast_ratio"],
            "wcag_aa": {
                "normal_text": result["wcag_level"] in ["AA", "AAA"],
                "large_text": result["wcag_level"] in ["AA", "AAA"]
            },
            "wcag_aaa": {
                "normal_text": result["wcag_level"] == "AAA",
                "large_text": result["wcag_level"] == "AAA"
            },
            "status": "pass" if result["passes"] else "fail",
            "suggestions": []
        }
        
        transformed_data["color_pairs"].append(pair)
    
    # Inject data into template (Cristina's method)
    html_content = html_content.replace(
        'const sampleData = {',
        f'const sampleData = {json.dumps(transformed_data)}; \n const _ignored = {{'
    )
    
    return html_content