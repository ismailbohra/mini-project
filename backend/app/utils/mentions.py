"""Utility module for handling @mentions in posts and comments."""

import re
from typing import List, Set


def extract_mentions(content: str) -> List[str]:
    """
    Extract unique usernames mentioned in the content.

    Pattern: @username where username contains only alphanumeric, underscore, and hyphen.
    No whitespace allowed.

    Args:
        content: The text content containing mentions

    Returns:
        List of unique usernames (without @ symbol)
    """
    # Match @username pattern (alphanumeric, underscore, hyphen only)
    # Username must start with alphanumeric or underscore
    pattern = r"@([a-zA-Z0-9_][a-zA-Z0-9_-]*)"

    # Find all matches and deduplicate
    mentions = re.findall(pattern, content)

    # Return unique mentions preserving order
    seen: Set[str] = set()
    unique_mentions: List[str] = []

    for mention in mentions:
        mention_lower = mention.lower()
        if mention_lower not in seen:
            seen.add(mention_lower)
            unique_mentions.append(mention)

    return unique_mentions


def validate_username_format(username: str) -> bool:
    """
    Validate that username follows the required format.

    Rules:
    - No whitespace or blank spaces
    - Only alphanumeric, underscore, and hyphen
    - Must start with alphanumeric or underscore
    - Minimum 3 characters, maximum 30 characters

    Args:
        username: The username to validate

    Returns:
        True if valid, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 30:
        return False

    # Check for whitespace
    if " " in username or "\t" in username or "\n" in username:
        return False

    # Check pattern
    pattern = r"^[a-zA-Z0-9_][a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, username))
