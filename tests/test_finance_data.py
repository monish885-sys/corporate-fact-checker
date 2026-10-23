"""Tests for app.services.finance_data (Global market)."""
import unittest
import pandas as pd
from unittest.mock import MagicMock, patch

from app.services.finance_data import (
    FinanceFetcher,
    _is_network_error,
    NETWORK_ERROR_MESSAGE,
)


class TestFormatNumber(unittest.TestCase):
    """Test FinanceFetcher.format_number."""

    def test_format_billions(self):
        self.assertEqual(FinanceFetcher.format_number(5_000_000_000), "$5.00B")
        # Negative billions: format_number uses value in f-string so we get $-1.20B
        self.assertIn("1.20B", FinanceFetcher.format_number(-1.2e9))

    def test_format_millions(self):
        self.assertEqual(FinanceFetcher.format_number(1_500_000), "$1.50M")

    def test_format_thousands(self):
        self.assertEqual(FinanceFetcher.format_number(5000), "$5.00K")

    def test_format_na_for_none(self):
        self.assertEqual(FinanceFetcher.format_number(None), "N/A")

    def test_format_na_for_nan(self):
        self.assertEqual(FinanceFetcher.format_number(pd.NA), "N/A")


class TestIsNetworkError(unittest.TestCase):
    """Test _is_network_error helper."""

    def test_resolve_host_detected(self):
        e = Exception("curl: (6) Could not resolve host: query1.finance.yahoo.com")
        self.assertTrue(_is_network_error(e))

    def test_nodename_servname_detected(self):
        e = Exception("nodename nor servname provided, or not known")
        self.assertTrue(_is_network_error(e))

    def test_connection_detected(self):
        e = Exception("Connection refused")
        self.assertTrue(_is_network_error(e))

    def test_generic_exception_not_network(self):
        e = Exception("Something else went wrong")
        self.assertFalse(_is_network_error(e))


class TestGetMetrics(unittest.TestCase):
    """Test FinanceFetcher.get_metrics with mocked yfinance."""

    @patch("app.services.finance_data.yf.Ticker")
    def test_get_metrics_returns_network_message_on_resolve_error(self, mock_ticker):
        mock_ticker.side_effect = Exception("Could not resolve host: query1.finance.yahoo.com")
        fetcher = FinanceFetcher()
        result = fetcher.get_metrics("AAPL")
        self.assertIn("Error", result)
        self.assertEqual(result["Error"], NETWORK_ERROR_MESSAGE)
        self.assertEqual(result["Ticker"], "AAPL")
        self.assertEqual(result["Company Name"], "Error")

    @patch("app.services.finance_data.yf.Ticker")
    def test_get_metrics_returns_error_dict_on_any_exception(self, mock_ticker):
        mock_ticker.side_effect = Exception("Random error")
        fetcher = FinanceFetcher()
        result = fetcher.get_metrics("INVALID")
        self.assertEqual(result["Ticker"], "INVALID")
        self.assertIn("Error", result)


class TestGetHistoricalData(unittest.TestCase):
    """Test get_historical_data."""

    @patch("app.services.finance_data.yf.Ticker")
    def test_get_historical_data_returns_empty_df_on_error(self, mock_ticker):
        mock_ticker.return_value.history.side_effect = Exception("Network error")
        fetcher = FinanceFetcher()
        df = fetcher.get_historical_data("AAPL", period="1y")
        self.assertTrue(df.empty)


if __name__ == "__main__":
    unittest.main()
