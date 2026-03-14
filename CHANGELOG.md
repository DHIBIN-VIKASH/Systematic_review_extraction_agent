# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-14

### Added
- **Template System**: Flexible template-based extraction supporting both Word (.docx) and Excel (.xlsx) formats
- **Template Parser Module** (`template_parser.py`): Unified parser with auto-detection of template format
- **Template Inspection Utility** (`inspect_template.py`): Command-line tool for examining template structure
- **Dynamic Field Loading**: Extraction fields loaded from templates instead of hardcoded
- **Command-Line Arguments**: `--template` flag to specify custom templates
- **Word Template Support**: Parse field definitions from Word documents with section grouping
- **Excel Template Support**: Parse column headers from Excel spreadsheets
- **Comprehensive Documentation**: Enhanced README with installation, usage, and troubleshooting
- **Contributing Guidelines**: CONTRIBUTING.md with development setup and PR process
- **MIT License**: Open-source license for public use
- **Git Ignore**: Proper exclusion of browser profiles, output files, and PDFs
- **Requirements File**: Pinned dependencies for reproducible installations

### Changed
- **gemini_extractor.py**: Refactored to use template parser instead of hardcoded fields
- **README.md**: Complete rewrite with badges, examples, and comprehensive documentation
- **Project Structure**: Organized for open-source distribution

### Features
- AI-powered data extraction using Google Gemini
- Browser automation with Playwright
- Incremental saving with resume capability
- Persistent browser sessions for authentication
- Support for multiple PDF processing
- Structured Excel output

## [Unreleased]

### Planned
- CSV template format support
- Unit tests and integration tests
- GitHub Actions CI/CD pipeline
- Optional GUI interface
- Batch processing improvements
- Template validation and error checking

---

[1.0.0]: https://github.com/DHIBIN-VIKASH/Systematic_review_extraction_agent/releases/tag/v1.0.0
