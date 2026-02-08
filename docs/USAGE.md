# Usage Guide

## Quick Start

Show the CLI banner:

```bash
epstein
```

Basic search:

```bash
epstein --search "donald" --limit 50
```

## Command Syntax

```bash
epstein [options]
```

## Options

| Flag         | Long Form  | Type   | Default           | Description                          |
| ------------ | ---------- | ------ | ----------------- | ------------------------------------ |
| `-s`         | `--search` | string | `""`              | Search query (empty = all documents) |
| `-l`         | `--limit`  | int    | `None`            | Maximum number of results to fetch   |
| `-d`         | `--delay`  | float  | `0.5`             | Delay between API requests (seconds) |
| `-o`         | `--prefix` | string | `epstein_library` | Output file prefix                   |
|              |`--output-path`| string | `lib_data`        | Directory to save report files      |
| `--base-url` | -          | string | DOJ URL           | Base search endpoint                 |
| `--no-save`  | -          | flag   | `false`           | Don't save to files, just display    |
| `--head`     | -          | int    | `10`              | Number of top results to display     |
| `-h`         | `--help`   | flag   | -                 | Show help message                    |

## Common Examples

### 1. Search and Save Results

```bash
epstein --search "artificial intelligence" --limit 100
```

Creates three files in the `lib_data/` directory (or your custom `--output-path`):

- `epstein_library_TIMESTAMP.json` - Full metadata
- `epstein_library_TIMESTAMP.csv` - Spreadsheet format
- `epstein_library_TIMESTAMP_urls.txt` - Just URLs

### 2. Preview Without Saving

```bash
epstein --search "epstein" --limit 20 --no-save
```

Displays results in terminal without creating files.

### 3. Show Only Top Results

```bash
epstein --search "trump" --limit 100 --head 5 --no-save
```

Fetch 100 results but only display the first 5.

### 4. Custom Output Prefix

```bash
epstein --search "banking" --limit 50 --prefix "banking_docs"
```

Files will be named `banking_docs_TIMESTAMP.*`

### 5. Save to a Custom Directory

```bash
epstein --search "finance" --limit 20 --output-path "reports/finance"
```

Files will be saved in the `reports/finance` directory.

### 6. Slow Down Requests

```bash
epstein --search "contacts" --limit 200 --delay 1.0
```

Wait 1 second between API calls (useful if getting rate limited).

### 7. Quick Search (No Pagination)

```bash
epstein --search "documents" --limit 10 --no-save --head 10
```

Just get the first page of results.

## Output Format

Each document in the results includes:

```
1. FILENAME.pdf
   File: EFTA00796097.pdf
   URL: https://www.justice.gov/epstein/files/DataSet%209/EFTA00796097.pdf
   Document ID: d92d2de6
   Pages: 14-16
   File Size: 1,321,323 bytes
   Words: 8,004
   Status: Chunked
   Indexed: 2026-01-30T18:04:12Z
```

## CSV Output

When saved to CSV, you can open in Excel, Google Sheets, or process programmatically:

| title            | file_name        | url         | document_id | file_size | total_words | start_page | end_page | is_chunked | indexed_at           | page |
| ---------------- | ---------------- | ----------- | ----------- | --------- | ----------- | ---------- | -------- | ---------- | -------------------- | ---- |
| EFTA00796097.pdf | EFTA00796097.pdf | https://... | d92d2de6    | 1321323   | 8004        | 14         | 16       | True       | 2026-01-30T18:04:12Z | 0    |

## JSON Output

Complete metadata in JSON format for programmatic processing:

```json
[
  {
    "title": "EFTA00796097.pdf",
    "file_name": "EFTA00796097.pdf",
    "url": "https://www.justice.gov/epstein/files/DataSet%209/EFTA00796097.pdf",
    "document_id": "d92d2de6",
    "file_size": 1321323,
    "total_words": 8004,
    "start_page": 14,
    "end_page": 16,
    "is_chunked": true,
    "indexed_at": "2026-01-30T18:04:12Z",
    "page": 0
  }
]
```

## Tips & Tricks

### Download All Results

```bash
# Get ALL documents (this may take a while!)
epstein --search "" --limit 50000 --delay 0.2
```

### Search Multiple Terms

Run separate searches and combine results:

```bash
epstein --search "trump" --prefix trump_docs
epstein --search "clinton" --prefix clinton_docs
```

### Filter Results in Excel

Export to CSV and use Excel's filter feature to find specific documents:

1. Run: `epstein --search "query" --limit 1000`
2. Open the `epstein_library_*.csv` file in your output directory (default: `lib_data/`) in Excel
3. Use AutoFilter to search by file size, date, pages, etc.

### Download PDFs in Bulk

Extract URLs from text file and download:

```bash
# Get URLs
epstein --search "query" --limit 100 --no-save > urls.txt

# Download with curl
cat urls.txt | xargs -I {} curl -O {}
```

Or with Python:

```python
from epstein import DOJMultimediaSearchClient

client = DOJMultimediaSearchClient()
docs = client.search_all(query="query", max_results=100)
urls = [doc['url'] for doc in docs]

import urllib.request
for url in urls:
    urllib.request.urlretrieve(url, url.split('/')[-1])
```

## Performance Notes

- Default delay is 0.5 seconds between requests
- Each API call returns ~10 documents
- Fetching 1000 documents takes ~50 seconds with 0.5s delay
- Reducing delay speeds up collection but may overload the server
- Recommended: keep delay ≥ 0.2 seconds for large queries

## Limitations

- API returns maximum 10 documents per request
- Some document URLs may have expired
- Large queries (>5000 documents) take significant time
- Search queries are case-insensitive
