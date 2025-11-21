#!/usr/bin/env python3
"""
Ariane-XML Error Lookup Utility

This utility allows you to look up error codes from the Ariane-XML error catalog.
It can search by error code, category, or keywords in the message/description.

Usage:
    python error_lookup.py ARX-01004
    python error_lookup.py --category "SELECT Clause"
    python error_lookup.py --search "duplicate"
    python error_lookup.py --list-categories
"""

import yaml
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class ErrorLookup:
    def __init__(self, catalog_path: str):
        """Initialize the error lookup with the catalog file path."""
        self.catalog_path = Path(catalog_path)
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict:
        """Load the error catalog from YAML file."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Error catalog not found: {self.catalog_path}")

        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def lookup_code(self, code: str) -> Optional[Dict]:
        """Look up a specific error code."""
        # Normalize code format
        code = code.upper()
        if not code.startswith('ARX-'):
            code = f'ARX-{code}'

        return self.catalog.get(code)

    def search_by_category(self, category: str) -> List[tuple]:
        """Find all errors in a specific category."""
        results = []
        category_lower = category.lower()

        for code, details in self.catalog.items():
            if details and details.get('category', '').lower() == category_lower:
                results.append((code, details))

        return results

    def search_by_keyword(self, keyword: str) -> List[tuple]:
        """Search for errors containing a keyword in message or description."""
        results = []
        keyword_lower = keyword.lower()

        for code, details in self.catalog.items():
            if not details:
                continue

            message = details.get('message', '').lower()
            description = details.get('description', '').lower()

            if keyword_lower in message or keyword_lower in description:
                results.append((code, details))

        return results

    def list_categories(self) -> List[str]:
        """Get a list of all unique categories."""
        categories = set()

        for details in self.catalog.values():
            if details and 'category' in details:
                categories.add(details['category'])

        return sorted(categories)

    def format_error_details(self, code: str, details: Dict, verbose: bool = False) -> str:
        """Format error details for display."""
        if not details:
            return f"{code}: No details available"

        output = []
        output.append(f"\n{'=' * 70}")
        output.append(f"Error Code: {code}")
        output.append(f"Category:   {details.get('category', 'Unknown')}")
        output.append(f"Severity:   {details.get('severity', 'Unknown')}")
        output.append(f"{'=' * 70}")

        output.append(f"\nMessage:")
        output.append(f"  {details.get('message', 'N/A')}")

        if verbose or details.get('description'):
            output.append(f"\nDescription:")
            output.append(f"  {details.get('description', 'N/A')}")

        if details.get('suggestion'):
            output.append(f"\nSuggestion:")
            output.append(f"  {details.get('suggestion')}")

        if verbose and details.get('example'):
            output.append(f"\nExample:")
            output.append(f"  {details.get('example')}")

        output.append("")
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Ariane-XML Error Lookup Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ARX-01004                    # Look up a specific error code
  %(prog)s 01004                        # Code without ARX- prefix also works
  %(prog)s --category "SELECT Clause"   # List all SELECT clause errors
  %(prog)s --search duplicate           # Search for errors about duplicates
  %(prog)s --list-categories            # Show all error categories
  %(prog)s ARX-05001 -v                 # Verbose output with examples
        """
    )

    parser.add_argument('code', nargs='?', help='Error code to look up (e.g., ARX-01004)')
    parser.add_argument('--category', '-c', help='List errors in this category')
    parser.add_argument('--search', '-s', help='Search for keyword in messages')
    parser.add_argument('--list-categories', '-l', action='store_true',
                        help='List all error categories')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed information including examples')
    parser.add_argument('--catalog', default='error_catalog.yaml',
                        help='Path to error catalog file (default: error_catalog.yaml)')

    args = parser.parse_args()

    # Find catalog file (look in parent directory if not found)
    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        # Try parent directory (if running from scripts/)
        parent_catalog = Path(__file__).parent.parent / args.catalog
        if parent_catalog.exists():
            catalog_path = parent_catalog

    try:
        lookup = ErrorLookup(str(catalog_path))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"Please run from the ariane-xml directory or specify --catalog path",
              file=sys.stderr)
        sys.exit(1)

    # Handle different command types
    if args.list_categories:
        print("\nAriane-XML Error Categories:")
        print("=" * 70)
        for category in lookup.list_categories():
            print(f"  - {category}")
        print()
        return

    if args.category:
        results = lookup.search_by_category(args.category)
        if not results:
            print(f"No errors found in category: {args.category}", file=sys.stderr)
            sys.exit(1)

        print(f"\nErrors in category '{args.category}':")
        for code, details in results:
            print(lookup.format_error_details(code, details, args.verbose))
        return

    if args.search:
        results = lookup.search_by_keyword(args.search)
        if not results:
            print(f"No errors found matching: {args.search}", file=sys.stderr)
            sys.exit(1)

        print(f"\nErrors matching '{args.search}':")
        for code, details in results:
            print(lookup.format_error_details(code, details, args.verbose))
        return

    if args.code:
        details = lookup.lookup_code(args.code)
        if not details:
            print(f"Error code not found: {args.code}", file=sys.stderr)
            sys.exit(1)

        print(lookup.format_error_details(args.code, details, args.verbose))
        return

    # No arguments provided
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
