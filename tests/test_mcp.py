import sys
import os
import pytest

# Add finance and wiki MCP directories to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base_dir, ".agents", "mcp", "finance"))
sys.path.insert(0, os.path.join(base_dir, ".agents", "mcp", "wiki"))

import calc
import check_links

def test_calc_cagr():
    # Test CAGR calculation
    rate = calc.cagr(100, 121, 2)
    assert abs(rate - 0.1) < 1e-5

def test_calc_fv():
    # Test future value
    fv = calc.future_value(0.1, 2, 10, 100)
    # Year 1: 100 * 1.1 + 10 = 120
    # Year 2: 120 * 1.1 + 10 = 142
    assert abs(fv - 142) < 1e-5

def test_calc_dca():
    # Test DCA projection
    proj = calc.dca_projection(100, 0.08, 10)
    assert "total_contributed" in proj
    assert "projected_value" in proj
    assert "total_gain" in proj
    assert proj["total_contributed"] == 12000

def test_check_links_link_parsing():
    # Test internal helper in check_links if any
    assert hasattr(check_links, "check_file")
