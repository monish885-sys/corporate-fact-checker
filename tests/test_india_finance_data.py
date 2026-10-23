"""Tests for app.services.india_finance_data (India market)."""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from app.services.india_finance_data import IndiaFinanceFetcher


class TestIndiaFinanceFetcherGetMetrics(unittest.TestCase):
    """Test IndiaFinanceFetcher.get_metrics (yfinance path)."""

    def test_symbol_normalized_strips_dot_ns(self):
        with patch.object(IndiaFinanceFetcher, "_get_metrics_yfinance") as mock_yf:
            mock_yf.return_value = {"Ticker": "RELIANCE", "Company Name": "Reliance", "Market": "India (NSE)"}
            fetcher = IndiaFinanceFetcher()
            fetcher.get_metrics("RELIANCE.NS")
            mock_yf.assert_called_once_with("RELIANCE")

    @patch("app.services.india_finance_data.yf.Ticker")
    def test_get_metrics_yfinance_returns_network_message_on_resolve_error(self, mock_ticker):
        from app.services.finance_data import NETWORK_ERROR_MESSAGE
        # Make accessing .info raise (so first line that touches network fails)
        class TickerRaise:
            @property
            def info(self):
                raise Exception("Could not resolve host: query1.finance.yahoo.com")
        mock_ticker.return_value = TickerRaise()
        fetcher = IndiaFinanceFetcher()
        result = fetcher._get_metrics_yfinance("RELIANCE")
        self.assertEqual(result["Error"], NETWORK_ERROR_MESSAGE)
        self.assertEqual(result["Market"], "India (NSE)")
        self.assertEqual(result["Ticker"], "RELIANCE")

    @patch("app.services.india_finance_data.yf.Ticker")
    def test_get_metrics_yfinance_returns_metrics_when_data_available(self, mock_ticker):
        mock_stock = MagicMock()
        mock_stock.info = {
            "longName": "Reliance Industries",
            "sector": "Energy",
            "industry": "Oil & Gas",
            "marketCap": 1e13,
            "trailingPE": 25.0,
            "trailingEps": 100.0,
            "dividendYield": 0.01,
        }
        mock_stock.financials = pd.DataFrame(
            {"2024-01-01": [1e12, 1e11, 5e10]},
            index=["Total Revenue", "Net Income", "EBITDA"],
        )
        mock_stock.balance_sheet = pd.DataFrame(
            {"2024-01-01": [2e12, 5e11]},
            index=["Total Assets", "Total Debt"],
        )
        mock_stock.cashflow = pd.DataFrame(
            {"2024-01-01": [8e10]},
            index=["Total Cash From Operating Activities"],
        )
        mock_ticker.return_value = mock_stock

        fetcher = IndiaFinanceFetcher()
        result = fetcher._get_metrics_yfinance("RELIANCE")
        self.assertEqual(result["Company Name"], "Reliance Industries")
        self.assertEqual(result["Ticker"], "RELIANCE")
        self.assertIn("Total Revenue", result)
        self.assertIn("Net Income", result)


if __name__ == "__main__":
    unittest.main()
