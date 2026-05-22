import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add the scripts directory to sys.path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "research", "scripts"))
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import ingest_paper

def test_sanitize():
    """Test PDF text sanitization logic."""
    assert ingest_paper._sanitize("  hello   world  ") == "hello world"
    assert ingest_paper._sanitize("line1\n\n\n\nline2") == "line1\n\nline2"
    assert ingest_paper._sanitize("\t tab \t space \t") == "tab space"

@patch("urllib.request.urlopen")
@patch("ingest_paper.MarkItDown")
@patch("os.makedirs")
@patch("os.unlink")
@patch("builtins.open")
def test_ingest_paper_logic(mock_file_open, mock_unlink, mock_makedirs, mock_markitdown_cls, mock_urlopen):
    """Test the main ingest_paper flow with mocks."""

    def urlopen_side_effect(req, *args, **kwargs):
        # req can be a Request object or a string
        url = req.full_url if hasattr(req, "full_url") else str(req)

        mock_resp = MagicMock()
        if "semanticscholar.org" in url or "arxiv.org/api" in url:
            # Metadata API request
            sample_metadata = {
                "title": "Test Paper Title",
                "abstract": "This is a test abstract.",
                "year": 2026,
                "authors": [{"name": "Test Author"}],
                "publicationTypes": ["JournalArticle"],
                "openAccessPdf": {"url": "https://arxiv.org/pdf/1234.5678.pdf"}
            }
            mock_resp.read.return_value = json.dumps(sample_metadata).encode("utf-8")
        else:
            # PDF file request
            mock_resp.read.return_value = b"%PDF-1.4 fake content"

        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    mock_urlopen.side_effect = urlopen_side_effect

    # Mock MarkItDown: md.convert(pdf_path).text_content
    mock_result = MagicMock()
    mock_result.text_content = "This is the extracted text from the PDF."
    mock_md_instance = MagicMock()
    mock_md_instance.convert.return_value = mock_result
    mock_markitdown_cls.return_value = mock_md_instance

    # Mock file writing
    mock_file = MagicMock()
    mock_file_open.return_value.__enter__.return_value = mock_file

    # Execute
    ingest_paper.ingest_paper("https://arxiv.org/pdf/1234.5678.pdf", "test_paper.md")

    # Verify MarkItDown was instantiated and convert was called
    mock_markitdown_cls.assert_called_once()
    mock_md_instance.convert.assert_called_once()
    called_path = mock_md_instance.convert.call_args[0][0]
    assert called_path.endswith("original.pdf")

    # Check if the correct content was written (handling potential mix of bytes and str write args)
    written_texts = []
    for call in mock_file.write.call_args_list:
        arg = call.args[0]
        if isinstance(arg, bytes):
            written_texts.append(arg.decode("utf-8", errors="ignore"))
        else:
            written_texts.append(arg)
    written_content = "".join(written_texts)

    assert "source_url: https://arxiv.org/pdf/1234.5678.pdf" in written_content
    assert "status: raw" in written_content
    assert "This is the extracted text from the PDF." in written_content
