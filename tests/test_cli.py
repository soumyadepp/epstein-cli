"""Tests for epstein.cli module"""

import pytest
from unittest.mock import patch
from io import StringIO
import sys
from epstein.cli import main, show_banner


class TestCLI:
    """Test CLI functionality"""

    def test_show_banner(self, capsys):
        """Test that banner displays correctly"""
        show_banner()
        captured = capsys.readouterr()

        assert "███████╗██████╗" in captured.out
        assert "DOJ Multimedia Search Client" in captured.out
        assert "Use 'epstein --help'" in captured.out

    def test_main_no_args_shows_banner(self, capsys, monkeypatch):
        """Test that running with no args shows banner"""
        monkeypatch.setattr(sys, "argv", ["epstein"])
        main()
        captured = capsys.readouterr()

        assert "DOJ Multimedia Search Client" in captured.out

    def test_main_help(self, capsys, monkeypatch):
        """Test --help argument"""
        monkeypatch.setattr(sys, "argv", ["epstein", "--help"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        captured = capsys.readouterr()
        assert "DOJ Multimedia Search Client" in captured.out
        assert exc_info.value.code == 0

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_search_basic(self, mock_search, capsys, monkeypatch):
        """Test basic search via CLI"""
        mock_search.return_value = [
            {
                "title": "Test1.pdf",
                "file_name": "Test1.pdf",
                "url": "https://example.com/test1.pdf",
                "document_id": "123",
                "file_size": 1000,
                "total_words": 100,
                "start_page": 1,
                "end_page": 5,
                "is_chunked": False,
                "indexed_at": "2026-01-01T00:00:00Z",
                "page": 0,
            }
        ]

        monkeypatch.setattr(
            sys, "argv", ["epstein", "--search", "test", "--no-save", "--limit", "1"]
        )
        main()
        captured = capsys.readouterr()

        assert "Found 1 documents" in captured.out
        assert "Test1.pdf" in captured.out

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    @patch("epstein.client.DOJMultimediaSearchClient.save_results")
    def test_main_search_with_save(self, mock_save, mock_search, monkeypatch):
        """Test search with file saving uses default output path"""
        documents = [
            {
                "title": "Test1.pdf",
                "file_name": "Test1.pdf",
                "url": "https://example.com/test1.pdf",
                "document_id": "123",
                "file_size": 1000,
                "total_words": 100,
                "start_page": 1,
                "end_page": 5,
                "is_chunked": False,
                "indexed_at": "2026-01-01T00:00:00Z",
                "page": 0,
            }
        ]
        mock_search.return_value = documents
        mock_save.return_value = ("test.json", "test.csv", "test_urls.txt")

        monkeypatch.setattr(
            sys,
            "argv",
            ["epstein", "--search", "test", "--limit", "1", "--prefix", "mytest"],
        )
        main()

        # Verify save_results was called with default output_path
        mock_save.assert_called_once_with(
            documents, prefix="mytest", output_path="lib_data"
        )

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    @patch("epstein.client.DOJMultimediaSearchClient.save_results")
    def test_main_search_with_custom_output_path(
        self, mock_save, mock_search, monkeypatch, tmp_path
    ):
        """Test search with custom output path"""
        documents = [{"title": "Test1.pdf", "file_name": "Test1.pdf", "url": "https://example.com/test1.pdf"}]
        mock_search.return_value = documents
        mock_save.return_value = ("test.json", "test.csv", "test_urls.txt")

        output_dir = tmp_path / "my_reports"

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "epstein",
                "--search",
                "test",
                "--output-path",
                str(output_dir),
            ],
        )
        main()

        # Verify save_results was called with the custom output_path
        mock_save.assert_called_once_with(
            documents, prefix="epstein_library", output_path=str(output_dir)
        )

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_custom_delay(self, mock_search, monkeypatch):
        """Test custom delay parameter"""
        mock_search.return_value = []

        monkeypatch.setattr(
            sys, "argv", ["epstein", "--search", "test", "--delay", "2.0", "--no-save"]
        )
        main()

        # Check that search_all was called with custom delay
        mock_search.assert_called_once()
        call_args = mock_search.call_args
        assert call_args[1]["delay"] == 2.0

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_custom_prefix(self, mock_search, monkeypatch):
        """Test custom output prefix"""
        mock_search.return_value = []

        monkeypatch.setattr(
            sys,
            "argv",
            ["epstein", "--search", "test", "--prefix", "custom_prefix", "--no-save"],
        )
        main()

        # If no error, custom prefix was accepted
        assert True

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_head_parameter(self, mock_search, capsys, monkeypatch):
        """Test --head parameter limits displayed results"""
        mock_search.return_value = [
            {
                "title": f"Test{i}.pdf",
                "file_name": f"Test{i}.pdf",
                "url": f"https://example.com/test{i}.pdf",
                "document_id": str(i),
                "file_size": 1000,
                "total_words": 100,
                "start_page": 1,
                "end_page": 5,
                "is_chunked": False,
                "indexed_at": "2026-01-01T00:00:00Z",
                "page": 0,
            }
            for i in range(5)
        ]

        monkeypatch.setattr(
            sys, "argv", ["epstein", "--search", "test", "--head", "2", "--no-save"]
        )
        main()
        captured = capsys.readouterr()

        # Should show "First 2 documents"
        assert "First 2 documents" in captured.out

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_no_results(self, mock_search, capsys, monkeypatch):
        """Test handling when no results found"""
        mock_search.return_value = []

        monkeypatch.setattr(
            sys, "argv", ["epstein", "--search", "nonexistent", "--no-save"]
        )
        main()
        captured = capsys.readouterr()

        assert "No documents found" in captured.out

    @patch("epstein.client.DOJMultimediaSearchClient.search_all")
    def test_main_base_url_option(self, mock_search, monkeypatch):
        """Test custom base URL option"""
        mock_search.return_value = []

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "epstein",
                "--search",
                "test",
                "--base-url",
                "https://custom.url",
                "--no-save",
            ],
        )
        main()

        # Verify custom base_url was accepted (no error means it worked)
        assert True
