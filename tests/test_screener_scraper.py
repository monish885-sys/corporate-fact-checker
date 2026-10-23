"""Tests for app.services.screener_scraper."""
import unittest
from unittest.mock import patch, MagicMock


class TestParseNumber(unittest.TestCase):
    def test_parse_number_cr(self):
        from app.services.screener_scraper import _parse_number
        self.assertIsNotNone(_parse_number("1,234 Cr"))
        self.assertEqual(_parse_number("10 Cr"), 10 * 1e7)

    def test_parse_number_percent(self):
        from app.services.screener_scraper import _parse_number
        self.assertEqual(_parse_number("15.5%"), 15.5)

    def test_parse_number_invalid(self):
        from app.services.screener_scraper import _parse_number
        self.assertIsNone(_parse_number(""))
        self.assertIsNone(_parse_number("N/A"))


class TestGet10YearTrends(unittest.TestCase):
    @patch("app.services.screener_scraper.requests.Session")
    def test_returns_error_when_connection_fails(self, mock_session):
        from app.services.screener_scraper import get_10_year_trends
        mock_session.return_value.get.side_effect = Exception("Connection refused")
        result = get_10_year_trends("RELIANCE")
        self.assertIn("error", result)
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
