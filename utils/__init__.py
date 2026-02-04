"""
Utils package initialization
"""

# Import functions from submodules
try:
    from .data_formatter import (
        parse_json_data,
        format_results_for_display,
        parse_uploaded_data,
        calculate_summary_stats
    )
except ImportError as e:
    print(f"Warning: Could not import from data_formatter: {e}")

try:
    from .file_handler import handle_file_upload, validate_file
except ImportError as e:
    print(f"Warning: Could not import from file_handler: {e}")

__all__ = [
    'parse_json_data',
    'format_results_for_display',
    'parse_uploaded_data',
    'calculate_summary_stats',
    'handle_file_upload',
    'validate_file'
]

