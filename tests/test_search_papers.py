import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add the scripts directory to sys.path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "research", "scripts"))
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import search_papers

@patch("urllib.request.urlopen")
@patch("urllib.request.Request")
def test_search_papers_logic(mock_request, mock_urlopen):
    """Test the search_papers flow with mocks."""
    # Mock API response
    sample_data = {
        "total": 1,
        "data": [
            {
                "title": "Science Paper",
                "authors": [{"name": "Dr. Huberman"}],
                "year": 2023,
                "url": "https://example.com/paper",
                "openAccessPdf": {"url": "https://example.com/paper.pdf"}
            }
        ]
    }
    
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(sample_data).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp
    
    # Capture print output
    with patch("builtins.print") as mock_print:
        search_papers.search_papers("melatonin dosage", limit=1)
        
        # Verify URL construction (partial check)
        args, _ = mock_request.call_args
        assert "api.semanticscholar.org" in args[0]
        assert "query=melatonin+dosage" in args[0]
        assert "limit=1" in args[0]
        
        # Verify print was called with the JSON data
        mock_print.assert_called()
        printed_data = json.loads(mock_print.call_args[0][0])
        assert printed_data["total"] == 1
        assert printed_data["data"][0]["title"] == "Science Paper"
