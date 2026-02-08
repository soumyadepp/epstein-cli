# Epstein DOJ Multimedia Search Client

CLI tool to query the DOJ Multimedia Search API and export document metadata.

## Installation

With `uv` installed:

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

## Usage

### Using the CLI module (recommended)

```bash
python3 -m epstein.cli --search "donald" --limit 50
```

### Using legacy main.py (backward compatible)

```bash
python3 main.py --search "artificial intelligence" --limit 100
```

### Basic search

```bash
python3 -m epstein.cli --search "donald" --limit 50
```

### Search and save results to files

```bash
python3 -m epstein.cli --search "artificial intelligence" --limit 100 --prefix ai_docs --output-path reports
```

This creates three files in the `reports` directory:

- `ai_docs_TIMESTAMP.json` - Full document metadata in JSON
- `ai_docs_TIMESTAMP.csv` - Comma-separated values for spreadsheet import
- `ai_docs_TIMESTAMP_urls.txt` - Plain text list of document URLs

### Preview results without saving

```bash
python3 -m epstein.cli --search "epstein" --limit 20 --no-save --head 5
```

### All options

```bash
python3 -m epstein.cli --help
```

**Common options:**

- `-s, --search TERM` - Search query (empty = all documents)
- `-l, --limit N` - Maximum number of results to fetch
- `-d, --delay SECONDS` - Delay between API requests (default: 0.5)
- `-o, --prefix NAME` - Output file prefix (default: epstein_library)
- `--output-path PATH` - Directory to save report files (default: lib_data)
- `--no-save` - Don't save to files, just display results
- `--head N` - Number of top results to display (default: 10)

## Examples

Search for documents mentioning "Trump":

```bash
python3 -m epstein.cli --search "Trump" --limit 50
```

Fetch 200 results with minimal delay:

```bash
python3 -m epstein.cli --search "banking" --limit 200 --delay 0.1
```

Get the first 5 results only, no file saving:

```bash
python3 -m epstein.cli --search "contacts" --limit 5 --no-save
```

## Project Structure

```
scrape-doj/
├── epstein/              # Main package
│   ├── __init__.py       # Package initialization
│   ├── client.py         # API client logic
│   └── cli.py            # CLI interface
├── main.py               # Legacy entry point (backward compatible)
├── README.md
├── pyproject.toml        # Project configuration with uv
├── requirements.txt      # pip-compatible requirements
└── uv.lock               # Lockfile for reproducible installs
```

## Output Format

Each result includes:

- **Title** - Document filename
- **File** - Actual filename
- **URL** - Direct link to the PDF (properly URL-encoded)
- **Document ID** - Unique identifier
- **Pages** - Page range in document
- **File Size** - Size in bytes
- **Words** - Total word count
- **Indexed** - When the document was indexed

## Requirements

- Python 3.9+
- `requests` - HTTP library
- `beautifulsoup4` - HTML/XML parsing

## API

You can also import and use the client directly:

```python
from epstein import DOJMultimediaSearchClient

client = DOJMultimediaSearchClient()
documents = client.search_all(query="donald", max_results=50)

# Save results
client.save_results(documents, prefix="my_search", output_path="my_reports")
```
