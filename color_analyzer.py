"""
WCAG Color Accessibility Analyzer
Uses coloraide library for WCAG 2.1 contrast calculations
"""

from coloraide import Color
from typing import Dict, List, Any


def analyze_color_pair(background: str, foreground: str, text_size: str = "normal") -> Dict[str, Any]:
    """
    Analyze a single color pair for WCAG compliance
    
    Args:
        background: Background color (hex, rgb, or other CSS format)
        foreground: Foreground/text color (hex, rgb, or other CSS format)
        text_size: "normal" or "large" (large is 18pt+ or 14pt+ bold)
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Parse colors using coloraide
        bg_color = Color(background)
        fg_color = Color(foreground)
        
        # Calculate WCAG 2.1 contrast ratio
        contrast_ratio = fg_color.contrast(bg_color, method="wcag21")
        
        # Determine WCAG level
        wcag_level = get_wcag_level(contrast_ratio, text_size)
        
        # Generate suggestion if failed
        suggestion = None
        if wcag_level == "Fail":
            suggestion = suggest_better_color(bg_color, fg_color, text_size)
        
        return {
            "background": bg_color.to_string(hex=True),
            "foreground": fg_color.to_string(hex=True),
            "contrast_ratio": round(contrast_ratio, 2),
            "text_size": text_size,
            "wcag_level": wcag_level,
            "passes": wcag_level != "Fail",
            "suggestion": suggestion
        }
    except Exception as e:
        return {
            "background": background,
            "foreground": foreground,
            "contrast_ratio": 0,
            "text_size": text_size,
            "wcag_level": "Error",
            "passes": False,
            "error": str(e)
        }


def get_wcag_level(contrast_ratio: float, text_size: str) -> str:
    """
    Determine WCAG conformance level based on contrast ratio and text size
    
    WCAG 2.1 Requirements:
    - AAA: 7:1 for normal text, 4.5:1 for large text
    - AA: 4.5:1 for normal text, 3:1 for large text
    
    Args:
        contrast_ratio: Calculated contrast ratio
        text_size: "normal" or "large"
    
    Returns:
        "AAA", "AA", or "Fail"
    """
    if text_size == "large":
        if contrast_ratio >= 7.0:
            return "AAA"
        elif contrast_ratio >= 4.5:
            return "AA"
        else:
            return "Fail"
    else:  # normal text
        if contrast_ratio >= 7.0:
            return "AAA"
        elif contrast_ratio >= 4.5:
            return "AA"
        else:
            return "Fail"


def suggest_better_color(bg_color: Color, fg_color: Color, text_size: str) -> Dict[str, Any]:
    """
    Suggest a better foreground color that meets WCAG AA standards
    
    Strategy: Adjust the lightness of the foreground color to achieve
    the minimum required contrast ratio
    
    Args:
        bg_color: Background Color object
        fg_color: Foreground Color object
        text_size: "normal" or "large"
    
    Returns:
        Dictionary with suggested color and new contrast ratio
    """
    # Target ratio for AA compliance
    target_ratio = 4.5 if text_size == "normal" else 3.0
    
    # Convert to LAB color space for lightness adjustment
    fg_lab = fg_color.convert("lab")
    bg_lightness = bg_color.convert("lab")["lightness"]
    
    # Try making text darker or lighter based on background
    suggested_color = None
    best_ratio = 0
    
    # Try both directions (darker and lighter)
    for lightness in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
        test_color = fg_lab.clone().set("lightness", lightness)
        test_ratio = test_color.contrast(bg_color, method="wcag21")
        
        if test_ratio >= target_ratio and test_ratio > best_ratio:
            best_ratio = test_ratio
            suggested_color = test_color.convert("srgb")
    
    if suggested_color:
        return {
            "color": suggested_color.to_string(hex=True),
            "contrast_ratio": round(best_ratio, 2),
            "wcag_level": get_wcag_level(best_ratio, text_size)
        }
    
    # Fallback: suggest black or white based on background lightness
    if bg_lightness > 50:
        fallback = Color("#000000")
    else:
        fallback = Color("#FFFFFF")
    
    fallback_ratio = fallback.contrast(bg_color, method="wcag21")
    
    return {
        "color": fallback.to_string(hex=True),
        "contrast_ratio": round(fallback_ratio, 2),
        "wcag_level": get_wcag_level(fallback_ratio, text_size)
    }


def analyze_accessibility(color_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze multiple color pairs for WCAG compliance
    
    Args:
        color_pairs: List of dicts with 'background', 'foreground', 'text_size' keys
    
    Returns:
        Full analysis results with statistics
    """
    results = []
    total_pairs = len(color_pairs)
    failures = 0
    text_count = {"normal": 0, "large": 0}
    
    for pair in color_pairs:
        analysis = analyze_color_pair(
            background=pair.get("background", "#FFFFFF"),
            foreground=pair.get("foreground", "#000000"),
            text_size=pair.get("text_size", "normal")
        )
        results.append(analysis)
        
        if not analysis["passes"]:
            failures += 1
        
        text_count[analysis["text_size"]] += 1
    
    return {
        "results": results,
        "statistics": {
            "total_pairs": total_pairs,
            "failures": failures,
            "passes": total_pairs - failures,
            "text_count": text_count
        }
    }
