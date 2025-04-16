import re
from typing import Dict, List, Optional

def clean_response(text: str) -> str:
    """
    Clean and normalize a consultation response.
    
    Args:
        text: Raw response text
        
    Returns:
        Cleaned response text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove [comments]
    text = re.sub(r'\(.*?\)', '', text)  # Remove (parentheses)
    
    # Normalize punctuation
    text = re.sub(r'\.{2,}', '.', text)  # Replace multiple dots with single
    text = re.sub(r'!{2,}', '!', text)   # Replace multiple ! with single
    text = re.sub(r'\?{2,}', '?', text)  # Replace multiple ? with single
    
    return text

def extract_quotes(text: str) -> List[str]:
    """
    Extract quoted phrases from a response.
    
    Args:
        text: Response text
        
    Returns:
        List of quoted phrases
    """
    # Match text between quotes
    quotes = re.findall(r'["\'](.*?)["\']', text)
    
    # Also match text that might be intended as quotes without actual quotes
    potential_quotes = re.findall(r'\b(?:said|stated|mentioned|commented)\s+(?:that\s+)?([^.,!?]+)', text, re.IGNORECASE)
    
    return list(set(quotes + potential_quotes))

def split_compound_response(text: str) -> List[str]:
    """
    Split a compound response into individual statements.
    
    Args:
        text: Response text
        
    Returns:
        List of individual statements
    """
    # Split on common conjunctions and punctuation
    statements = re.split(r'\s*(?:but|however|although|though|and|or|;|\.)\s+', text)
    
    # Clean and filter empty statements
    statements = [clean_response(s) for s in statements if s.strip()]
    
    return statements

def validate_code_assignment(
    codes: List[str],
    codeframe: Dict
) -> Dict[str, List[str]]:
    """
    Validate code assignments against the codeframe.
    
    Args:
        codes: List of assigned codes
        codeframe: Codeframe dictionary
        
    Returns:
        Dictionary with valid and invalid codes
    """
    valid_codes = []
    invalid_codes = []
    
    # Flatten codeframe into list of all valid codes
    all_valid_codes = []
    for category in codeframe.get("categories", {}).values():
        all_valid_codes.extend(category.keys())
    
    # Check each assigned code
    for code in codes:
        if code in all_valid_codes:
            valid_codes.append(code)
        else:
            invalid_codes.append(code)
    
    return {
        "valid": valid_codes,
        "invalid": invalid_codes
    } 