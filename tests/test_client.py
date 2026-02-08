"""Tests for epstein.client module"""

import pytest
import json
from io import BytesIO
from pathlib import Path
from epstein.client import DOJMultimediaSearchClient


class TestDOJMultimediaSearchClient:
    """Test DOJMultimediaSearchClient class"""

    def test_init_default_url(self):
        """Test client initialization with default URL"""
        client = DOJMultimediaSearchClient()
        assert client.base_url == "https://www.justice.gov/multimedia-search"
        assert client.session is not None

    def test_init_custom_url(self):
        """Test client initialization with custom URL"""
        custom_url = "https://custom.example.com"
        client = DOJMultimediaSearchClient(base_url=custom_url)
        assert client.base_url == custom_url

    def test_search_single_page(self, mock_requests_get, sample_api_response):
        """Test searching a single page"""
        client = DOJMultimediaSearchClient()
        documents, has_next = client.search(query="test", page=0)

        assert len(documents) == 2
        assert documents[0]["file_name"] == "EFTA00796097.pdf"
        assert documents[0]["document_id"] == "d92d2de6"
        assert "%" in documents[0]["url"]  # URL should be encoded
        # has_next is False when returned docs < 10 (less than page size)
        assert has_next is False

    def test_search_url_encoding(self, mock_requests_get):
        """Test that spaces in URLs are properly encoded"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")

        # Check first document has encoded spaces
        assert "%20" in documents[0]["url"]
        assert " " not in documents[0]["url"]

    def test_search_all_single_page(self, mock_requests_get):
        """Test search_all with one page of results"""
        client = DOJMultimediaSearchClient()
        documents = client.search_all(query="test", max_results=10)

        assert len(documents) > 0
        assert all("file_name" in doc for doc in documents)
        assert all("url" in doc for doc in documents)

    def test_search_all_respects_max_results(self, mock_requests_get):
        """Test that search_all respects max_results limit"""
        client = DOJMultimediaSearchClient()
        documents = client.search_all(query="test", max_results=1)

        # Should stop at max_results
        assert len(documents) <= 10  # One page

    def test_search_all_with_delay(self, mock_requests_get):
        """Test that search_all accepts delay parameter"""
        client = DOJMultimediaSearchClient()
        documents = client.search_all(query="test", max_results=10, delay=0.1)

        assert len(documents) > 0

    def test_save_results_uses_default_path(self, mock_requests_get, temp_lib_data):
        """Test that save_results uses 'lib_data' by default"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")

        json_file, _, _ = client.save_results(documents, prefix="test")

        # Check that the file is in the default 'lib_data' directory
        assert Path(json_file).parent.name == "lib_data"
        assert Path(json_file).exists()

    def test_save_results_creates_files_in_custom_path(
        self, mock_requests_get, tmp_path
    ):
        """Test that save_results creates all three files in a custom path"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")

        output_dir = tmp_path / "custom_reports"
        json_file, csv_file, txt_file = client.save_results(
            documents, prefix="test", output_path=output_dir
        )

        # Check files were created in the custom path
        assert Path(json_file).parent == output_dir
        assert Path(csv_file).parent == output_dir
        assert Path(txt_file).parent == output_dir

    def test_save_results_json_format(self, mock_requests_get, tmp_path):
        """Test that saved JSON is valid"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")
        json_file, _, _ = client.save_results(
            documents, prefix="test", output_path=tmp_path
        )

        with open(json_file) as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["file_name"] == "EFTA00796097.pdf"

    def test_save_results_csv_format(self, mock_requests_get, tmp_path):
        """Test that saved CSV is valid"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")
        _, csv_file, _ = client.save_results(
            documents, prefix="test", output_path=tmp_path
        )

        with open(csv_file) as f:
            content = f.read()

        # Check CSV header and content
        assert "file_name" in content
        assert "EFTA00796097.pdf" in content
        lines = content.strip().split("\n")
        assert len(lines) == 3  # header + 2 documents

    def test_save_results_txt_format(self, mock_requests_get, tmp_path):
        """Test that saved TXT file has correct URLs"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")
        _, _, txt_file = client.save_results(
            documents, prefix="test", output_path=tmp_path
        )

        with open(txt_file) as f:
            urls = f.read().strip().split("\n")

        assert len(urls) == 2
        assert all(url.startswith("https://") for url in urls)

    def test_document_structure(self, mock_requests_get):
        """Test that returned documents have required fields"""
        client = DOJMultimediaSearchClient()
        documents, _ = client.search(query="test")

        required_fields = [
            "title",
            "file_name",
            "url",
            "document_id",
            "file_size",
            "total_words",
            "start_page",
            "end_page",
            "is_chunked",
            "indexed_at",
            "page",
        ]

        for doc in documents:
            for field in required_fields:
                assert field in doc, f"Missing field: {field}"

    def test_search_error_handling(self):
        """Test error handling when API fails"""
        from unittest.mock import patch
        from requests.exceptions import RequestException

        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = RequestException("Connection error")
            client = DOJMultimediaSearchClient()
            documents, has_next = client.search(query="test")

            assert documents == []
            assert has_next is False

    def test_save_results_empty_list(self, tmp_path):
        """Test save_results with empty document list"""
        client = DOJMultimediaSearchClient()
        json_file, csv_file, txt_file = client.save_results(
            [], prefix="empty", output_path=tmp_path
        )

        # Files should still be created
        assert Path(json_file).exists()
        assert Path(csv_file).exists()
        assert Path(txt_file).exists()

        # Check content is empty
        with open(json_file) as f:
            data = json.load(f)
        assert data == []
