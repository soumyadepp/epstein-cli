"""
DOJ Multimedia Search API Client
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime
import os


class DOJMultimediaSearchClient:
    """Client for querying DOJ Multimedia Search API"""

    def __init__(self, base_url="https://www.justice.gov/multimedia-search"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )

    def search(self, query="", page=0):
        """Query the multimedia search endpoint for documents"""
        print(f"Searching for: '{query}' (page={page})... ", end="", flush=True)

        try:
            params = {"keys": query, "page": page}
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            # Try to parse as JSON first (Elasticsearch response)
            try:
                data = response.json()

                # Parse Elasticsearch response format
                hits = data.get("hits", {}).get("hits", [])
                total_count = data.get("hits", {}).get("total", {}).get("value", 0)

                documents = []
                for hit in hits:
                    source = hit.get("_source", {})
                    # URL encode the URI to handle spaces and special characters
                    raw_url = source.get("ORIGIN_FILE_URI", "")
                    # Replace spaces with %20 in the URL
                    encoded_url = raw_url.replace(" ", "%20")

                    documents.append(
                        {
                            "title": source.get("ORIGIN_FILE_NAME", "Untitled"),
                            "file_name": source.get("ORIGIN_FILE_NAME", ""),
                            "url": encoded_url,
                            "document_id": source.get("documentId", ""),
                            "file_size": source.get("fileSize", 0),
                            "total_words": source.get("totalWords", 0),
                            "start_page": source.get("startPage", 0),
                            "end_page": source.get("endPage", 0),
                            "is_chunked": source.get("isChunked", False),
                            "indexed_at": source.get("indexedAt", ""),
                            "page": page,
                        }
                    )

                # Check if there are more pages
                has_next = (
                    len(documents) > 0 and len(documents) == 10
                )  # Assume 10 per page

                print(f"Found {len(documents)} documents (Total: {total_count})")
                return documents, has_next

            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, try HTML parsing
                soup = BeautifulSoup(response.content, "html.parser")

                # Parse search results from HTML
                documents = []

                # Find result containers (adjust selectors based on actual HTML structure)
                results = soup.find_all(
                    ["article", "div"],
                    class_=lambda x: (
                        bool(x and "result" in str(x).lower()) if x else False
                    ),
                )

                if not results:
                    # Try alternative selectors
                    results = soup.find_all(
                        "div",
                        class_=lambda x: (
                            bool(x and "item" in str(x).lower()) if x else False
                        ),
                    )

                for result in results:
                    # Extract URL
                    link = result.find("a", href=True)
                    if not link:
                        continue

                    href_val = link.get("href", "")
                    if isinstance(href_val, list):
                        href_val = href_val[0] if href_val else ""
                    url = str(href_val) if href_val else ""

                    # Extract filename from URL
                    file_name = url.split("/")[-1] if url else ""

                    # Extract title
                    title_elem = result.find(["h2", "h3", "h4", "a"])
                    title = (
                        title_elem.get_text(strip=True) if title_elem else "Untitled"
                    )

                    documents.append(
                        {
                            "title": title,
                            "file_name": file_name,
                            "url": url,
                            "page": page,
                        }
                    )

                # Check for next page
                has_next = False
                next_link = soup.find("a", rel="next")
                if next_link:
                    has_next = True
                else:
                    # Try to find "Next" button
                    pagination = soup.find(
                        "nav",
                        class_=lambda x: (
                            bool(x and "pag" in str(x).lower()) if x else False
                        ),
                    )
                    if pagination:
                        next_btn = pagination.find(
                            "a",
                            text=lambda x: (
                                bool(x and "next" in str(x).lower()) if x else False
                            ),
                        )
                        has_next = next_btn is not None

                print(f"Found {len(documents)} documents")
                return documents, has_next

        except requests.exceptions.RequestException as e:
            print(f"ERROR: {e}")
            return [], False
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()
            return [], False

    def search_all(self, query="", max_results=None, page_size=100, delay=0.5):
        """Fetch all search results with pagination"""
        print("=" * 70)
        print("DOJ Multimedia Search Client")
        print("=" * 70)
        print(f"Search term: '{query}' (empty = all documents)")
        print(f"Max results: {max_results or 'unlimited'}")
        print()

        all_documents = []
        page = 0
        has_next = True

        while has_next:
            if max_results and len(all_documents) >= max_results:
                print(f"\nReached max results limit: {max_results}")
                break

            documents, has_next = self.search(query=query, page=page)

            if not documents:
                print("\nNo more documents found")
                break

            all_documents.extend(documents)

            if has_next:
                page += 1
                print(f"Waiting {delay} seconds before next page...")
                time.sleep(delay)
            else:
                print(f"\nFetched all documents")

        return all_documents

    def save_results(self, documents, prefix="epstein_library", output_path="lib_data"):
        """Save results in multiple formats to the specified output folder"""
        # Create output folder if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON file
        json_file = os.path.join(output_path, f"{prefix}_{timestamp}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved JSON: {json_file}")

        # CSV file
        csv_file = os.path.join(output_path, f"{prefix}_{timestamp}.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if documents:
                writer = csv.DictWriter(f, fieldnames=documents[0].keys())
                writer.writeheader()
                writer.writerows(documents)
        print(f"✓ Saved CSV: {csv_file}")

        # Simple URL list
        urls_file = os.path.join(output_path, f"{prefix}_{timestamp}_urls.txt")
        with open(urls_file, "w", encoding="utf-8") as f:
            for doc in documents:
                f.write(f"{doc['url']}\n")
        print(f"✓ Saved URL list: {urls_file}")

        return json_file, csv_file, urls_file
