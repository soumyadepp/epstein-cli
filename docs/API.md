# Python API Documentation

## Overview

The `epstein` package can be used as a Python library in your own projects. The main class is `DOJMultimediaSearchClient`.

## Installation

```bash
pip install doj-multimedia-search
```

## Basic Usage

```python
from epstein import DOJMultimediaSearchClient

# Create a client
client = DOJMultimediaSearchClient()

# Search for documents
documents = client.search_all(query="donald", max_results=50)

# Save results
client.save_results(documents, prefix="my_search")
```

## API Reference

### DOJMultimediaSearchClient

Main client class for querying the DOJ Multimedia Search API.

#### Constructor

```python
client = DOJMultimediaSearchClient(base_url="https://www.justice.gov/multimedia-search")
```

**Parameters:**

- `base_url` (str, optional): The DOJ search endpoint. Defaults to the official URL.

#### Methods

### search()

Fetch a single page of search results.

```python
documents, has_next = client.search(query="", page=0)
```

**Parameters:**

- `query` (str): Search term. Empty string returns all documents.
- `page` (int): Page number (0-indexed). Default: 0

**Returns:**

- `documents` (list): List of document dictionaries
- `has_next` (bool): Whether more pages are available

**Example:**

```python
docs, more = client.search(query="epstein", page=0)
for doc in docs:
    print(f"{doc['title']}: {doc['url']}")
```

### search_all()

Fetch all search results with automatic pagination.

```python
documents = client.search_all(
    query="",
    max_results=None,
    page_size=100,
    delay=0.5
)
```

**Parameters:**

- `query` (str): Search term. Default: "" (all documents)
- `max_results` (int, optional): Maximum results to fetch. None = unlimited
- `page_size` (int): Maximum results to fetch per API call. Default: 100
- `delay` (float): Seconds to wait between API calls. Default: 0.5

**Returns:**

- `documents` (list): All matching document dictionaries

**Example:**

```python
# Fetch first 100 documents matching "trump"
documents = client.search_all(
    query="trump",
    max_results=100,
    delay=0.3  # Fast, but respectful
)

print(f"Found {len(documents)} documents")
for doc in documents:
    print(f"  - {doc['file_name']}: {doc['file_size']} bytes")
```

### save_results()

Save search results to JSON, CSV, and TXT files.

```python
json_file, csv_file, urls_file = client.save_results(
    documents,
    prefix="epstein_library",
    output_path="lib_data"
)
```

**Parameters:**

- `documents` (list): List of document dictionaries
- `prefix` (str): File prefix. Default: "epstein_library"
- `output_path` (str): Directory to save files. Default: "lib_data"


**Returns:**

- `json_file` (str): Path to saved JSON file
- `csv_file` (str): Path to saved CSV file
- `urls_file` (str): Path to saved URLs text file

**Note:** Files are saved to the specified `output_path`, which defaults to `lib_data/`.

**Example:**

```python
documents = client.search_all(query="banking", max_results=200)
json_path, csv_path, urls_path = client.save_results(
    documents,
    prefix="banking_records",
    output_path="reports/banking"
)

print(f"Results saved to:")
print(f"  JSON: {json_path}")
print(f"  CSV:  {csv_path}")
print(f"  URLs: {urls_path}")
```

## Document Structure

Each document returned is a dictionary with the following keys:

```python
{
    "title": str,           # Document filename
    "file_name": str,       # Actual filename
    "url": str,             # Direct download URL
    "document_id": str,     # Unique document ID
    "file_size": int,       # Size in bytes
    "total_words": int,     # Word count
    "start_page": int,      # Starting page number
    "end_page": int,        # Ending page number
    "is_chunked": bool,     # Whether document is chunked
    "indexed_at": str,      # ISO 8601 timestamp
    "page": int             # Result page number
}
```

## Advanced Examples

### Filter Results

```python
from epstein import DOJMultimediaSearchClient

client = DOJMultimediaSearchClient()
documents = client.search_all(query="documents", max_results=500)

# Find large documents
large_docs = [d for d in documents if d['file_size'] > 5000000]
print(f"Found {len(large_docs)} documents over 5MB")

# Find recently indexed
recent_docs = [d for d in documents if d['indexed_at'] > '2026-01-01']
print(f"Found {len(recent_docs)} documents indexed in January 2026")
```

### Export to Different Formats

```python
import json
import csv
from epstein import DOJMultimediaSearchClient

client = DOJMultimediaSearchClient()
documents = client.search_all(query="query", max_results=100)

# XML format
import xml.etree.ElementTree as ET
root = ET.Element("documents")
for doc in documents:
    doc_elem = ET.SubElement(root, "document")
    for key, value in doc.items():
        child = ET.SubElement(doc_elem, key)
        child.text = str(value)
ET.ElementTree(root).write("documents.xml")

# Markdown table
with open("documents.md", "w") as f:
    f.write("| Title | File Size | Pages |\n")
    f.write("|-------|-----------|-------|\n")
    for doc in documents:
        f.write(f"| {doc['title']} | {doc['file_size']:,} | {doc['start_page']}-{doc['end_page']} |\n")
```

### Batch Processing

```python
from epstein import DOJMultimediaSearchClient
import urllib.request
import os

client = DOJMultimediaSearchClient()
documents = client.search_all(query="query", max_results=50)

# Download first 10 PDFs
os.makedirs("downloaded_pdfs", exist_ok=True)
for i, doc in enumerate(documents[:10], 1):
    try:
        url = doc['url']
        filename = os.path.join("downloaded_pdfs", doc['file_name'])
        print(f"Downloading {i}/10: {doc['file_name']}...", end="", flush=True)
        urllib.request.urlretrieve(url, filename)
        print(" ✓")
    except Exception as e:
        print(f" ✗ ({e})")
```

### Search with Progress Tracking

```python
from epstein import DOJMultimediaSearchClient

client = DOJMultimediaSearchClient()

# Manual pagination with progress
all_docs = []
page = 0
total_fetched = 0
max_results = 200

while total_fetched < max_results:
    docs, has_next = client.search(query="documents", page=page)

    if not docs:
        break

    all_docs.extend(docs)
    total_fetched += len(docs)

    print(f"Page {page}: {len(docs)} docs ({total_fetched}/{max_results})")

    if not has_next:
        break

    page += 1

print(f"\nFetched {len(all_docs)} total documents")
```

## Error Handling

```python
from epstein import DOJMultimediaSearchClient
import requests

client = DOJMultimediaSearchClient()

try:
    documents = client.search_all(query="query", max_results=100)
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Tips

1. **Batch Operations**: Fetch many documents once rather than multiple small requests
2. **Adjust Delay**: Reduce `delay` parameter for faster results (but be respectful)
3. **Limit Results**: Use `max_results` to avoid unnecessary API calls
4. **Reuse Client**: Create one client instance and reuse it for multiple queries
5. **Stream Processing**: For very large datasets, process documents as they arrive rather than storing all in memory

## Rate Limiting

The DOJ API doesn't have strict rate limiting, but:

- Default delay is 0.5 seconds between pages (respectful)
- Each page returns ~10 documents
- Minimum recommended delay: 0.1 seconds
- Maximum recommended delay: 2.0 seconds

## Troubleshooting

**No results returned?**

```python
# Try without search term
docs = client.search_all(query="")
print(f"Total documents available: {len(docs)}")
```

**Connection timeout?**

```python
# Increase delay
docs = client.search_all(query="query", delay=2.0)
```

**Want to see API responses?**

```python
docs, has_next = client.search(query="query", page=0)
print(f"Got {len(docs)} documents")
print(f"Has more pages: {has_next}")
```
