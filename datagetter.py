import pypdf
import re
import json
from typing import Dict, List
from pathlib import Path


def load_fry_word_lists_from_pdf() -> Dict[str, List[str]]:
    """
    Extract Fry word lists from the PDF file (pages 3-13).
    Groups words by the "hundred" headers shown in the PDF (The First Hundred, The Second Hundred, etc.)
    Returns a dictionary with header names as keys and word lists as values.
    """
    pdf_path = Path(__file__).parent / "fry-word-list.pdf"
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        
        word_lists = {}
        processed_hundreds = set()  # Track which hundreds we've already processed
        
        # Process pages 3-13 (indices 2-12)
        # Each page has one header specifying which hundred it belongs to
        for page_num in range(2, 13):
            if page_num >= len(reader.pages):
                break
            
            page_text = reader.pages[page_num].extract_text()
            
            # Find the hundred header on this page
            header_match = re.search(r'Fry Words[^–]*–\s*The\s+(\w+)\s+Hundred', page_text)
            if not header_match:
                continue
            
            hundred_name = f"The {header_match.group(1)} Hundred"
            
            # Skip if we've already processed this hundred (duplicate pages)
            if hundred_name in processed_hundreds:
                continue
            
            processed_hundreds.add(hundred_name)
            if hundred_name not in word_lists:
                word_lists[hundred_name] = []
            
            # Extract all lists from this page
            list_pattern = r'List\s+(\d+)\s*\n((?:(?!List\s+\d+).)*?)(?=List\s+\d+|$)'
            list_matches = re.findall(list_pattern, page_text, re.DOTALL)
            
            for list_num_str, words_text in list_matches:
                # Extract individual words from this list
                lines = words_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Skip full footer/header lines (multiple words on one line)
                    if len(line.split()) > 1:
                        # Multi-word lines are headers/footers
                        if any(skip in line.lower() for skip in ('fry words', 'free for', 'copyright', 'anne gardner')):
                            continue
                    
                    # Skip single metadata words
                    if line.lower() in ('free', 'copyright', '–', '2014', 'anne', 'gardner'):
                        continue
                    if re.match(r'^(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+(hundred)?$', line.lower()):
                        continue
                    
                    # Extract just alphabetic characters and apostrophes
                    word = re.sub(r'[^a-z\']', '', line.lower())
                    
                    if word:
                        # Handle contractions: don't -> dont
                        word_clean = word.replace("'", "")
                        
                        # Skip single 't' from contractions
                        if word_clean and word_clean != 't' and len(word_clean) > 0:
                            # Avoid duplicates within the same hundred
                            if word_clean not in word_lists[hundred_name]:
                                word_lists[hundred_name].append(word_clean)
    
    return word_lists

# Load on module import
_FRY_LISTS = None


def get_fry_word_lists() -> Dict[str, List[str]]:
    """
    Returns a dictionary of Fry word lists organized by "hundred" headers.
    Loads from PDF on first call, then caches the result.
    """
    global _FRY_LISTS
    if _FRY_LISTS is None:
        _FRY_LISTS = load_fry_word_lists_from_pdf()
    return _FRY_LISTS


def get_list_names() -> List[str]:
    """Returns sorted list of available Fry hundred names."""
    lists = get_fry_word_lists()
    # Sort by the ordinal name (First, Second, Third, etc.)
    ordinal_order = {
        'First': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Fifth': 5,
        'Sixth': 6, 'Seventh': 7, 'Eighth': 8, 'Ninth': 9, 'Tenth': 10
    }
    return sorted(lists.keys(), key=lambda x: ordinal_order.get(x.split()[1], 999))


def get_words_from_list(list_name: str) -> List[str]:
    """
    Get all words from a specific hundred.
    
    Args:
        list_name: Name of the hundred (e.g., 'The First Hundred', 'The Second Hundred')
    
    Returns:
        List of words, or empty list if not found
    """
    lists = get_fry_word_lists()
    return lists.get(list_name, [])


def get_total_words_in_list(list_name: str) -> int:
    """Returns the number of words in a specific hundred."""
    return len(get_words_from_list(list_name))


def save_word_lists_to_json(filepath: str = None) -> str:
    """
    Save extracted word lists to JSON for review.
    
    Args:
        filepath: Optional path to save to. If not provided, saves to fry-word-lists.json in the same directory.
    
    Returns:
        Path to the saved file
    """
    if filepath is None:
        filepath = Path(__file__).parent / "fry-word-lists.json"
    
    lists = get_fry_word_lists()
    
    with open(filepath, 'w') as f:
        json.dump(lists, f, indent=2)
    
    return str(filepath)
