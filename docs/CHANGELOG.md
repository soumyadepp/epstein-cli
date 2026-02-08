# Changelog

## [0.2.0] - 2026-02-08

### Added

- Comprehensive test suite with 24 tests covering client and CLI functionality
- GitHub Actions test workflow for automated testing on Python 3.9-3.12
- Test requirement for PyPI publishing (tests must pass before release)
- Coverage reporting with pytest-cov
- Test fixtures and conftest.py for pytest configuration
- Optional dev dependencies (pytest, pytest-cov)

### Improved

- Enhanced CI/CD pipeline with test-before-publish requirement
- Better code quality assurance for all releases

## [0.1.0] - 2026-02-08

### Added

- Initial release of Epstein DOJ Multimedia Search CLI
- `DOJMultimediaSearchClient` class for API access
- `search()` method for single-page searches
- `search_all()` method for paginated searches with automatic continuation
- `save_results()` method to export as JSON, CSV, and TXT
- CLI interface with argparse for command-line usage
- ASCII art banner when running `epstein` with no arguments
- Support for custom search queries, result limits, and output prefixes
- URL encoding to properly handle spaces and special characters
- Configurable delays between API requests for respectful scraping
- Backward compatibility with legacy `main.py` entry point
- Comprehensive documentation:
  - Installation guide
  - Usage examples
  - Python API documentation
  - FAQ and troubleshooting
  - Contributing guidelines

### Technical Details

- Python 3.9+ support
- Dependencies: requests, beautifulsoup4
- Package built with hatchling
- PyPI ready for distribution
- Git integration with .gitignore for lib_data/

## Future Roadmap

### Planned for v0.2.0

- [ ] Add caching to avoid redundant API calls
- [ ] Support for advanced search operators
- [ ] Bulk PDF download functionality
- [ ] Progress bar for large searches
- [ ] Configuration file support
- [ ] Export to additional formats (XLSX, Parquet)

### Planned for v0.3.0

- [ ] Full-text search indexing
- [ ] Document deduplication
- [ ] Metadata enrichment
- [ ] Export to databases (SQLite, PostgreSQL)

### Ideas for Future

- Desktop GUI
- Web interface
- Real-time document monitoring
- Document content search (OCR integration)
- Relationship mapping between documents
- Statistical analysis tools
