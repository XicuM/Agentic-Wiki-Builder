import sys
import os
from unittest.mock import MagicMock, patch

# Mock fitz (PyMuPDF) before importing the script that uses it
sys.modules["fitz"] = MagicMock()

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
@patch("urllib.request.Request")
@patch("fitz.open")
@patch("os.makedirs")
@patch("os.unlink")
@patch("builtins.open")
def test_ingest_paper_logic(mock_file_open, mock_unlink, mock_makedirs, mock_fitz_open, mock_request, mock_urlopen):
    """Test the main ingest_paper flow with mocks."""
    # Mock URL response
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"%PDF-1.4 fake content"
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp
    
    # Mock PDF extraction
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "This is the extracted text from the PDF."
    # Simulate fitz.open(path) returning a doc that can be iterated for pages
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc
    # In the script, it does: doc = fitz.open(pdf_path); pages = [page.get_text() for page in doc]
    # So we need to make sure mock_fitz_open.return_value behaves like a list or has __iter__
    
    # Mock file writing
    mock_file = MagicMock()
    mock_file_open.return_value.__enter__.return_value = mock_file
    
    # Execute
    ingest_paper.ingest_paper("https://arxiv.org/pdf/1234.5678.pdf", "test_paper.md")
    
    # Verify
    mock_urlopen.assert_called()
    mock_fitz_open.assert_called()
    
    # Check if the correct content was written
    written_content = "".join(call.args[0] for call in mock_file.write.call_args_list)
    assert "source_url: https://arxiv.org/pdf/1234.5678.pdf" in written_content
    assert "status: raw" in written_content
    assert "This is the extracted text from the PDF." in written_content
