"""
Template Inspection Utility

This script provides a command-line interface for inspecting data extraction
templates in both Word (.docx) and Excel (.xlsx) formats.

Usage:
    python inspect_template.py <template_file>
    
Example:
    python inspect_template.py GLP1_Meta_Analysis_Data_Extraction_Template.docx
    python inspect_template.py template.xlsx
"""

import argparse
import sys
from template_parser import parse_template, detect_template_format


def inspect_template(filepath: str, verbose: bool = False):
    """
    Inspect a template file and display its structure.
    
    Args:
        filepath: Path to template file
        verbose: If True, show detailed information including descriptions
    """
    try:
        print(f"Inspecting template: {filepath}")
        print(f"Format: {detect_template_format(filepath)}")
        print()
        
        fields = parse_template(filepath)
        
        print(f"Found {len(fields)} fields:")
        print("=" * 80)
        
        # Group fields by section
        sections = {}
        for field in fields:
            section = field.section if field.section else "General"
            if section not in sections:
                sections[section] = []
            sections[section].append(field)
        
        # Display fields grouped by section
        for section_name, section_fields in sections.items():
            print(f"\n[{section_name}] ({len(section_fields)} fields)")
            print("-" * 80)
            
            for field in section_fields:
                if verbose and field.description:
                    print(f"  • {field.name}")
                    print(f"    Description: {field.description}")
                else:
                    print(f"  • {field.name}")
        
        print("\n" + "=" * 80)
        print(f"Summary: {len(sections)} sections, {len(fields)} total fields")
        
        # Show field names as a list (useful for copying)
        if verbose:
            print("\nField names (for reference):")
            print("-" * 80)
            for field in fields:
                print(f"  '{field.name}',")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: Template file not found: {filepath}", file=sys.stderr)
        return False
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Inspect data extraction templates (Word or Excel format)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inspect_template.py template.docx
  python inspect_template.py template.xlsx --verbose
  python inspect_template.py "My Template (v2).docx" -v
        """
    )
    
    parser.add_argument(
        'template',
        help='Path to template file (.docx or .xlsx)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information including field descriptions'
    )
    
    args = parser.parse_args()
    
    success = inspect_template(args.template, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
