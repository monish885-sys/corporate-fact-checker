"""
Indian market financial data using NSEPython and yfinance (.NS/.BO).
Includes corporate actions (dividends, splits) that CEOs often highlight.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

# Optional: NSEPython for NSE data (pip install nsepython or nsepythonserver on cloud)
_nse_equity_history = None
_nse_eq = None
_nse_corporate_actions = None
try:
    from nsepython import equity_history as _nse_equity_history
except ImportError:
    pass
try:
    from nsepython import nse_eq as _nse_eq
except ImportError:
    pass
try:
    from nsepython import nse_corporate_actions as _nse_corporate_actions
except ImportError:
    pass
NSEPYTHON_AVAILABLE = _nse_equity_history is not None

import yfinance as yf
from app.services.finance_data import NETWORK_ERROR_MESSAGE, _is_network_error


def _format_number(value: float) -> str:
    """Format large numbers (Cr = Crore, L = Lakh for India)."""
    if pd.isna(value) or value is None:
        return "N/A"
    abs_val = abs(value)
    if abs_val >= 1_00_00_00_00_00_00:  # 1 Lakh Crore
        return f"₹{value / 1_00_00_00_00_00_00:.2f}L Cr"
    if abs_val >= 1_00_00_00_00:  # 1 Crore
        return f"₹{value / 1_00_00_00_00:.2f} Cr"
    if abs_val >= 1_00_00_00:  # 1 Lakh
        return f"₹{value / 1_00_00_00:.2f} L"
    if abs_val >= 1_000:
        return f"₹{value / 1_000:.2f} K"
    return f"₹{value:.2f}"


class IndiaFinanceFetcher:
    """Fetch Indian stock data from NSE (NSEPython) with yfinance fallback."""

    def __init__(self):
        self._yf_suffix = ".NS"  # NSE

    def get_metrics(self, symbol: str) -> Dict[str, str]:
        """
        Get comprehensive metrics for an NSE/BSE symbol.
        Uses NSEPython if available, else yfinance with .NS suffix.
        """
        symbol = symbol.upper().strip()
        # Remove exchange suffix if user passed RELIANCE.NS
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            symbol = symbol[:-3]

        if NSEPYTHON_AVAILABLE:
            try:
                return self._get_metrics_nsepython(symbol)
            except Exception as e:
                pass  # Fall through to yfinance

        return self._get_metrics_yfinance(symbol)

    def _get_metrics_nsepython(self, symbol: str) -> Dict[str, str]:
        """Fetch using NSEPython (NSE India API)."""
        result = {
            "Ticker": symbol,
            "Company Name": "N/A",
            "Sector": "N/A",
            "Industry": "N/A",
            "Market": "India (NSE)",
            "Total Revenue": "Data Unavailable",
            "Net Income": "Data Unavailable",
            "Operating Cash Flow": "Data Unavailable",
            "Total Debt": "Data Unavailable",
            "Total Equity": "Data Unavailable",
            "Market Cap": "Data Unavailable",
            "P/E Ratio": "N/A",
            "EPS": "N/A",
            "Dividend Yield": "N/A",
            "Corporate Actions": "N/A",
            "Cash Conversion (CFO/EBITDA)": "N/A",
            "Asset Turnover": "N/A",
            "Interest Coverage": "N/A",
            "Interest Expense": "Data Unavailable",
        }

        try:
            if _nse_eq is None:
                raise ImportError("nse_eq not available")
            quote = _nse_eq(symbol)
            if isinstance(quote, dict):
                result["Company Name"] = quote.get("companyName", quote.get("symbol", symbol))
                result["Market Cap"] = _format_number(float(quote.get("marketCap", 0) or 0))
                result["P/E Ratio"] = str(round(float(quote.get("pe", 0) or 0), 2))
                result["EPS"] = f"₹{round(float(quote.get('eps', 0) or 0), 2)}"
                # Dividend yield if available
                dy = quote.get("dividendYield") or quote.get("divYield")
                if dy is not None:
                    result["Dividend Yield"] = f"{float(dy):.2f}%"
        except Exception:
            pass

        # Corporate actions (dividends, splits)
        try:
            if _nse_corporate_actions is None:
                raise ImportError("nse_corporate_actions not available")
            actions = _nse_corporate_actions(symbol)
            if actions and isinstance(actions, (list, dict)):
                if isinstance(actions, list) and len(actions) > 0:
                    result["Corporate Actions"] = f"{len(actions)} event(s) (see details)"
                elif isinstance(actions, dict):
                    result["Corporate Actions"] = "Available"
            else:
                result["Corporate Actions"] = "None recent"
        except Exception:
            result["Corporate Actions"] = "Unavailable"

        # Enrich with yfinance for financials and truth-check ratios (NSE doesn't provide all in one call)
        yf_data = self._get_metrics_yfinance(symbol)
        merge_keys = (
            "Total Revenue", "Net Income", "Operating Cash Flow", "Total Debt",
            "Total Equity", "Sector", "Industry",
            "EBITDA", "Operating Income", "Interest Expense", "Total Assets",
            "Cash Conversion (CFO/EBITDA)", "Asset Turnover", "Interest Coverage",
        )
        for key in merge_keys:
            if yf_data.get(key) and yf_data.get(key) not in ("N/A", "Data Unavailable"):
                result[key] = yf_data[key]
        if yf_data.get("Company Name") and result["Company Name"] == "N/A":
            result["Company Name"] = yf_data["Company Name"]

        return result

    def _get_metrics_yfinance(self, symbol: str) -> Dict[str, str]:
        """Fallback: use yfinance with .NS (NSE) suffix for Indian stocks."""
        ticker_str = f"{symbol}.NS"
        try:
            stock = yf.Ticker(ticker_str)
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
        except Exception as e:
            err_msg = str(e)
            if _is_network_error(e):
                err_msg = NETWORK_ERROR_MESSAGE
            return {
                "Ticker": symbol,
                "Company Name": "Error",
                "Market": "India (NSE)",
                "Error": err_msg,
            }

        result = {
            "Ticker": symbol,
            "Company Name": info.get("longName", symbol),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Market": "India (NSE)",
            "Total Revenue": "Data Unavailable",
            "Net Income": "Data Unavailable",
            "Operating Cash Flow": "Data Unavailable",
            "Total Debt": "Data Unavailable",
            "Total Equity": "Data Unavailable",
            "Total Assets": "Data Unavailable",
            "EBITDA": "Data Unavailable",
            "Operating Income": "Data Unavailable",
            "Interest Expense": "Data Unavailable",
            "Market Cap": "Data Unavailable",
            "P/E Ratio": "N/A",
            "EPS": "N/A",
            "Dividend Yield": "N/A",
            "Corporate Actions": "N/A",
            "Cash Conversion (CFO/EBITDA)": "N/A",
            "Asset Turnover": "N/A",
            "Interest Coverage": "N/A",
        }

        # Format in Crores/Lakhs for India
        def fmt_cr(val):
            if val is None or pd.isna(val):
                return "N/A"
            return _format_number(val)

        ocf_raw = None
        ebitda_raw = None
        revenue_raw = None
        assets_raw = None
        op_income_raw = None
        interest_expense_raw = None

        if financials is not None and not financials.empty:
            if "Total Revenue" in financials.index:
                v = financials.loc["Total Revenue"].iloc[0]
                if not pd.isna(v):
                    result["Total Revenue"] = fmt_cr(v)
                    revenue_raw = v
            if "Net Income" in financials.index:
                result["Net Income"] = fmt_cr(financials.loc["Net Income"].iloc[0])
            if "EBITDA" in financials.index:
                v = financials.loc["EBITDA"].iloc[0]
                if not pd.isna(v):
                    result["EBITDA"] = fmt_cr(v)
                    ebitda_raw = v
            if "Operating Income" in financials.index:
                v = financials.loc["Operating Income"].iloc[0]
                if not pd.isna(v):
                    result["Operating Income"] = fmt_cr(v)
                    op_income_raw = v
            if "Interest Expense" in financials.index:
                v = financials.loc["Interest Expense"].iloc[0]
                if not pd.isna(v) and v != 0:
                    result["Interest Expense"] = fmt_cr(abs(v))
                    interest_expense_raw = abs(v)

        if balance_sheet is not None and not balance_sheet.empty:
            if "Total Debt" in balance_sheet.index:
                result["Total Debt"] = fmt_cr(balance_sheet.loc["Total Debt"].iloc[0])
            elif "Long Term Debt" in balance_sheet.index:
                result["Total Debt"] = fmt_cr(balance_sheet.loc["Long Term Debt"].iloc[0])
            if "Stockholders Equity" in balance_sheet.index:
                result["Total Equity"] = fmt_cr(balance_sheet.loc["Stockholders Equity"].iloc[0])
            elif "Total Stockholder Equity" in balance_sheet.index:
                result["Total Equity"] = fmt_cr(balance_sheet.loc["Total Stockholder Equity"].iloc[0])
            if "Total Assets" in balance_sheet.index:
                v = balance_sheet.loc["Total Assets"].iloc[0]
                if not pd.isna(v):
                    result["Total Assets"] = fmt_cr(v)
                    assets_raw = v

        if cashflow is not None and not cashflow.empty:
            if "Total Cash From Operating Activities" in cashflow.index:
                v = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
                if not pd.isna(v):
                    result["Operating Cash Flow"] = fmt_cr(v)
                    ocf_raw = v

        if info.get("marketCap"):
            result["Market Cap"] = fmt_cr(info["marketCap"])
        if info.get("trailingPE"):
            result["P/E Ratio"] = f"{info['trailingPE']:.2f}"
        if info.get("trailingEps"):
            result["EPS"] = f"₹{info['trailingEps']:.2f}"
        if info.get("dividendYield") is not None:
            result["Dividend Yield"] = f"{info['dividendYield'] * 100:.2f}%"

        # Truth-check ratios (critical for Indian manufacturing/FMCG)
        if ocf_raw is not None and ebitda_raw is not None and ebitda_raw != 0:
            result["Cash Conversion (CFO/EBITDA)"] = f"{(ocf_raw / ebitda_raw):.2f}x"
        if revenue_raw is not None and assets_raw is not None and assets_raw != 0:
            result["Asset Turnover"] = f"{(revenue_raw / assets_raw):.2f}x"
        if op_income_raw is not None and interest_expense_raw is not None and interest_expense_raw != 0:
            result["Interest Coverage"] = f"{(op_income_raw / interest_expense_raw):.2f}x"

        return result

    def get_corporate_actions(self, symbol: str) -> List[Dict[str, Any]]:
        """Return list of corporate actions (dividends, splits) for the symbol."""
        symbol = symbol.upper().strip()
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            symbol = symbol[:-3]

        if NSEPYTHON_AVAILABLE and _nse_corporate_actions is not None:
            try:
                actions = _nse_corporate_actions(symbol)
                if isinstance(actions, list):
                    return actions[:20]  # Last 20
                if isinstance(actions, dict):
                    return [actions]
            except Exception:
                pass

        # yfinance dividends
        try:
            stock = yf.Ticker(f"{symbol}.NS")
            divs = stock.dividends
            if divs is not None and len(divs) > 0:
                return [
                    {"date": str(d), "value": v, "type": "Dividend"}
                    for d, v in divs.tail(10).items()
                ]
        except Exception:
            pass
        return []

    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Historical price data. Uses NSEPython if available, else yfinance."""
        symbol = symbol.upper().strip()
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            symbol = symbol[:-3]

        if NSEPYTHON_AVAILABLE:
            try:
                end = datetime.now()
                start = end - timedelta(days=365 if period == "1y" else 180)
                df = _nse_equity_history(symbol, "EQ", start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y"))
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass

        try:
            return yf.Ticker(f"{symbol}.NS").history(period=period)
        except Exception:
            return pd.DataFrame()
