"""
Custom validators for input sanitization and validation.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach


def sanitize_html_input(value):
    """
    Sanitize HTML input to prevent XSS attacks.
    Strips all HTML tags except safe ones.
    """
    if not value:
        return value

    # Allow only basic formatting tags
    allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li']
    allowed_attrs = {}

    return bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def sanitize_text_input(value):
    """
    Completely strip all HTML tags from input.
    Use for fields that should be plain text only.
    """
    if not value:
        return value

    return strip_tags(value).strip()


def validate_no_sql_injection(value):
    """
    Basic SQL injection pattern detection.
    Raises ValidationError if suspicious patterns found.
    """
    if not value:
        return value

    # Common SQL injection patterns
    sql_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--)",
        r"(;.*DROP)",
        r"(;.*DELETE)",
        r"(1=1)",
        r"(OR.*1.*=.*1)",
    ]

    value_upper = str(value).upper()

    for pattern in sql_patterns:
        if re.search(pattern, value_upper, re.IGNORECASE):
            raise ValidationError(
                'Input contains potentially malicious content.',
                code='sql_injection'
            )

    return value


def validate_no_javascript(value):
    """
    Detect JavaScript in input.
    Raises ValidationError if suspicious patterns found.
    """
    if not value:
        return value

    # JavaScript patterns
    js_patterns = [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"onload=",
        r"onfocus=",
        r"onmouseover=",
        r"eval\(",
        r"alert\(",
    ]

    value_lower = str(value).lower()

    for pattern in js_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            raise ValidationError(
                'Input contains potentially malicious JavaScript.',
                code='xss_attempt'
            )

    return value


def validate_safe_filename(value):
    """
    Validate filename to prevent directory traversal attacks.
    """
    if not value:
        return value

    # Check for directory traversal attempts
    dangerous_patterns = ['../', '..\\', '~/', '/etc/', 'c:\\']

    value_lower = str(value).lower()

    for pattern in dangerous_patterns:
        if pattern in value_lower:
            raise ValidationError(
                'Filename contains invalid characters.',
                code='invalid_filename'
            )

    # Ensure filename only contains safe characters
    if not re.match(r'^[\w\s\-\.]+$', value):
        raise ValidationError(
            'Filename can only contain letters, numbers, spaces, hyphens, and periods.',
            code='invalid_filename_chars'
        )

    return value


def validate_price_range(value):
    """
    Validate property price is within reasonable range.
    """
    if value is None:
        return value

    min_price = 0
    max_price = 1_000_000_000  # 1 billion

    if value < min_price or value > max_price:
        raise ValidationError(
            f'Price must be between ${min_price} and ${max_price}.',
            code='invalid_price_range'
        )

    return value


def validate_square_feet(value):
    """
    Validate square footage is reasonable.
    """
    if value is None:
        return value

    min_sqft = 1
    max_sqft = 100_000_000  # 100 million sqft

    if value < min_sqft or value > max_sqft:
        raise ValidationError(
            f'Square footage must be between {min_sqft} and {max_sqft}.',
            code='invalid_sqft'
        )

    return value


def clean_user_input(data):
    """
    Comprehensive input cleaning for user-submitted data.
    Returns cleaned dictionary.
    """
    if not isinstance(data, dict):
        return data

    cleaned = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Strip HTML tags
            value = sanitize_text_input(value)
            # Validate no SQL injection
            try:
                value = validate_no_sql_injection(value)
                value = validate_no_javascript(value)
            except ValidationError:
                # Skip malicious inputs
                continue

        cleaned[key] = value

    return cleaned
