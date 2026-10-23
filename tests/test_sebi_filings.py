"""Tests for app.services.sebi_filings."""
import unittest
from app.services.sebi_filings import get_filing_links, get_brsr_download_note


class TestGetFilingLinks(unittest.TestCase):
    """Test get_filing_links."""

    def test_returns_five_links(self):
        links = get_filing_links("RELIANCE")
        self.assertGreaterEqual(len(links), 5)
        self.assertIn("NSE Corporate Filings (All)", links)
        self.assertIn("NSE BRSR (Sustainability Reports)", links)
        self.assertIn("SEBI Corporate Filings", links)

    def test_symbol_uppercased(self):
        links = get_filing_links("reliance")
        self.assertIn("RELIANCE", links["NSE Company Tracking"])

    def test_symbol_strips_dot_ns(self):
        links = get_filing_links("TCS.NS")
        self.assertIn("TCS", links["NSE Company Tracking"])


class TestGetBrsrDownloadNote(unittest.TestCase):
    """Test get_brsr_download_note."""

    def test_contains_symbol(self):
        note = get_brsr_download_note("RELIANCE")
        self.assertIn("RELIANCE", note)
        self.assertIn("BRSR", note)
        self.assertIn("NSE", note)


if __name__ == "__main__":
    unittest.main()
