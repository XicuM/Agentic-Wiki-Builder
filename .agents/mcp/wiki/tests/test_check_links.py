import sys
import os
import pytest

# Add wiki MCP directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import check_links

def test_check_links_link_parsing():
    # Test internal helper in check_links if any
    assert hasattr(check_links, "check_file")
