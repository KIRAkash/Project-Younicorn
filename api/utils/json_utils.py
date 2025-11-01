"""JSON utility functions for Project Younicorn API."""

import json
import re
from typing import Optional, Dict, Any

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text that may be wrapped in markdown code blocks."""
    if not text:
        return None
    
    text = text.strip()
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # Try each match until we find valid JSON
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Try to extract JSON from plain code blocks
    code_pattern = r'```\s*\n?(.*?)\n?```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def safe_json_loads(val, default):
    """Safely load JSON values with fallback."""
    if val is None:
        return default
    
    if isinstance(val, str):
        if not val.strip():  # Empty string
            return default
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return default
    
    # If it's already a dict/list (parsed JSON), return as-is
    if isinstance(val, (dict, list)):
        return val
    
    return default
