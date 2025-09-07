"""
Utilities for parsing search queries into facets (creature types, CR values).
"""

import re
from typing import Optional, Tuple
from foe_foundry.creature_types import CreatureType


def parse_cr_from_query(query: str) -> Optional[float]:
    """
    Parse a CR value from a search query.
    
    Supports formats like:
    - "CR 5", "cr 5"
    - "Challenge Rating 10", "challenge rating 10"
    - "5" (if it looks like a standalone number that could be CR)
    - "1/2", "1/4", "1/8" (fractional CRs)
    
    Args:
        query: The search query string
        
    Returns:
        The parsed CR value as a float, or None if no CR is detected
    """
    query = query.strip().lower()
    
    # Pattern 1: "CR X" or "cr X"
    cr_pattern = r'\bcr\s+(\d+/\d+|\d+(?:\.\d+)?)\b'
    match = re.search(cr_pattern, query, re.IGNORECASE)
    if match:
        return _parse_cr_value(match.group(1))
    
    # Pattern 2: "challenge rating X" or "challenge rating X"
    cr_long_pattern = r'\bchallenge\s+rating\s+(\d+/\d+|\d+(?:\.\d+)?)\b'
    match = re.search(cr_long_pattern, query, re.IGNORECASE)
    if match:
        return _parse_cr_value(match.group(1))
    
    # Pattern 3: Standalone number that could be a CR (only if the entire query is just the number)
    if re.match(r'^(\d+/\d+|\d+(?:\.\d+)?)$', query):
        return _parse_cr_value(query)
    
    return None


def _parse_cr_value(cr_str: str) -> float:
    """Parse a CR value string into a float."""
    if '/' in cr_str:
        # Handle fractions like "1/2", "1/4", "1/8"
        numerator, denominator = cr_str.split('/')
        return float(numerator) / float(denominator)
    else:
        return float(cr_str)


def parse_creature_type_from_query(query: str) -> Optional[CreatureType]:
    """
    Parse a creature type from a search query.
    
    Args:
        query: The search query string
        
    Returns:
        The parsed CreatureType, or None if no creature type is detected
    """
    query = query.strip().lower()
    
    # Try to parse the entire query as a creature type
    try:
        return CreatureType.parse(query)
    except ValueError:
        pass
    
    # Try to find creature type words within the query
    for creature_type in CreatureType:
        if creature_type.lower() in query:
            return creature_type
    
    return None


def detect_facet_query(query: str) -> Tuple[Optional[CreatureType], Optional[float]]:
    """
    Detect if a search query is primarily a facet query (creature type or CR).
    
    Args:
        query: The search query string
        
    Returns:
        A tuple of (creature_type, cr_value) where either could be None
    """
    creature_type = parse_creature_type_from_query(query)
    cr_value = parse_cr_from_query(query)
    
    return creature_type, cr_value


def is_facet_only_query(query: str) -> bool:
    """
    Determine if a query should be handled as facet-only (no text search).
    
    A query is considered facet-only if:
    1. It contains a recognizable CR pattern, OR
    2. It's exactly a creature type name, OR
    3. It's a simple number that could be a CR
    
    Args:
        query: The search query string
        
    Returns:
        True if this should be handled as a facet-only query
    """
    creature_type, cr_value = detect_facet_query(query)
    
    # If we found a CR value, it's definitely a facet query
    if cr_value is not None:
        return True
    
    # If the entire query is just a creature type, it's a facet query
    query_clean = query.strip().lower()
    if creature_type is not None and creature_type.lower() == query_clean:
        return True
    
    return False