"""
CLI interface for DOJ Multimedia Search
"""

import argparse
import sys
from epstein import DOJMultimediaSearchClient


ASCII_ART = r"""
    ███████╗██████╗ ███████╗████████╗███████╗██╗███╗   ██╗
    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝██║████╗  ██║
    █████╗  ██████╔╝███████╗   ██║   █████╗  ██║██╔██╗ ██║
    ██╔══╝  ██╔═══╝ ╚════██║   ██║   ██╔══╝  ██║██║╚██╗██║
    ███████╗██║     ███████║   ██║   ███████╗██║██║ ╚████║
    ╚══════╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝╚═╝  ╚═══╝

    DOJ Multimedia Search Client
    Query and export classified document metadata
"""


def show_banner():
    """Display the ASCII art banner"""
    print(ASCII_ART)
    print("─" * 70)
    print("Use 'epstein --help' for command options")
    print("─" * 70 + "\n")


def main():
    """Main CLI entry point"""
    # Show banner if no arguments provided
    if len(sys.argv) == 1:
        show_banner()
        return

    parser = argparse.ArgumentParser(
        prog="epstein",
        description="DOJ Multimedia Search Client - Query and export document metadata",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--search",
        default="",
        help="Search query (empty = all documents)",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results to fetch",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "-o",
        "--prefix",
        default="epstein_library",
        help="Output file prefix",
    )
    parser.add_argument(
        "--output-path",
        default="lib_data",
        help="Directory to save report files",
    )
    parser.add_argument(
        "--base-url",
        default="https://www.justice.gov/multimedia-search",
        help="Base search endpoint URL",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save results to files (only print summary)",
    )
    parser.add_argument(
        "--head",
        type=int,
        default=10,
        help="Number of top results to display",
    )

    args = parser.parse_args()

    client = DOJMultimediaSearchClient(base_url=args.base_url)

    documents = client.search_all(
        query=args.search,
        max_results=args.limit,
        delay=args.delay,
    )

    print("\n" + "=" * 70)
    print(f"SUMMARY: Found {len(documents)} documents")
    print("=" * 70)

    if not documents:
        print("\n⚠ No documents found.")
        return

    if not args.no_save:
        json_file, csv_file, urls_file = client.save_results(
            documents, prefix=args.prefix, output_path=args.output_path
        )

    # Show first few results
    print(f"\nFirst {args.head} documents found:")
    print("-" * 70)
    for i, doc in enumerate(documents[: args.head], 1):
        print(f"\n{i}. {doc['title']}")
        print(f"   File: {doc['file_name']}")
        print(f"   URL: {doc['url']}")
        print(f"   Document ID: {doc.get('document_id', 'N/A')}")
        print(f"   Pages: {doc.get('start_page', 0)}-{doc.get('end_page', 0)}")
        print(f"   File Size: {doc.get('file_size', 0):,} bytes")
        print(f"   Words: {doc.get('total_words', 0):,}")
        if doc.get("is_chunked"):
            print(f"   Status: Chunked")
        print(f"   Indexed: {doc.get('indexed_at', 'N/A')}")


if __name__ == "__main__":
    main()
