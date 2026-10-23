"""
Finance data fetching service using yfinance.
"""
import yfinance as yf
from typing import Dict, Optional
import pandas as pd

# User-friendly message when Yahoo Finance is unreachable (DNS/network)
NETWORK_ERROR_MESSAGE = (
    "Cannot reach Yahoo Finance (query1.finance.yahoo.com). "
    "Check your internet connection and DNS. If you use a VPN or corporate network, try disabling it or using another network."
)


def _is_network_error(exc: Exception) -> bool:
    """True if the exception is due to DNS/connection (e.g. could not resolve host)."""
    msg = (getattr(exc, "message", "") or str(exc)).lower()
    return (
        "could not resolve host" in msg
        or "resolve host" in msg
        or "name or service not known" in msg
        or "connection" in msg
        or "yahoo" in msg
        or "nodename nor servname" in msg
    )


class FinanceFetcher:
    """Class to fetch and process financial data from Yahoo Finance."""
    
    @staticmethod
    def format_number(value: float) -> str:
        """
        Format large numbers into readable strings.
        
        Args:
            value: Numeric value to format
            
        Returns:
            str: Formatted string (e.g., "$5.0B", "$1.2M")
        """
        if pd.isna(value) or value is None:
            return "N/A"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        elif abs_value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        elif abs_value >= 1_000:
            return f"${value / 1_000:.2f}K"
        else:
            return f"${value:.2f}"
    
    def get_metrics(self, ticker: str) -> Dict[str, str]:
        """
        Fetch comprehensive financial metrics for a given stock ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            Dict[str, str]: Dictionary containing formatted financial metrics
        """
        try:
            # Create ticker object
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            # Fetch financial statements
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            # Initialize result dictionary with all metrics
            result = {
                # Basic Info
                "Ticker": ticker.upper(),
                "Company Name": info.get("longName", "Unknown"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                
                # Income Statement Metrics
                "Total Revenue": "Data Unavailable",
                "Net Income": "Data Unavailable",
                "Gross Profit": "Data Unavailable",
                "Operating Income": "Data Unavailable",
                "EBITDA": "Data Unavailable",
                
                # Balance Sheet Metrics
                "Total Assets": "Data Unavailable",
                "Total Debt": "Data Unavailable",
                "Total Equity": "Data Unavailable",
                "Current Assets": "Data Unavailable",
                "Current Liabilities": "Data Unavailable",
                "Cash and Cash Equivalents": "Data Unavailable",
                
                # Cash Flow Metrics
                "Operating Cash Flow": "Data Unavailable",
                "Free Cash Flow": "Data Unavailable",
                "Capital Expenditure": "Data Unavailable",
                
                # Valuation Metrics
                "Market Cap": "Data Unavailable",
                "Enterprise Value": "Data Unavailable",
                "P/E Ratio": "N/A",
                "P/B Ratio": "N/A",
                "EPS": "N/A",
                
                # Profitability Ratios
                "ROE": "N/A",  # Return on Equity
                "ROA": "N/A",  # Return on Assets
                "Profit Margin": "N/A",
                "Operating Margin": "N/A",
                
                # Liquidity Ratios
                "Current Ratio": "N/A",
                "Quick Ratio": "N/A",
                
                # Leverage Ratios
                "Debt-to-Equity": "N/A",
                "Debt-to-Assets": "N/A",
                
                # Truth-Check Ratios (critical for manufacturing/FMCG and Indian markets)
                "Interest Expense": "Data Unavailable",
                "Cash Conversion (CFO/EBITDA)": "N/A",  # CFO to EBITDA – profits in bank vs on paper
                "Asset Turnover": "N/A",                 # Revenue/Assets – capital efficiency
                "Interest Coverage": "N/A",              # EBIT/Interest – ability to service debt
            }
            
            # Extract most recent year's data (first column is usually the most recent)
            if financials is not None and not financials.empty:
                # Net Income
                if "Net Income" in financials.index:
                    net_income = financials.loc["Net Income"].iloc[0]
                    if not pd.isna(net_income):
                        result["Net Income"] = self.format_number(net_income)
                
                # Total Revenue
                if "Total Revenue" in financials.index:
                    revenue = financials.loc["Total Revenue"].iloc[0]
                    if not pd.isna(revenue):
                        result["Total Revenue"] = self.format_number(revenue)
                elif "Revenue" in financials.index:
                    revenue = financials.loc["Revenue"].iloc[0]
                    if not pd.isna(revenue):
                        result["Total Revenue"] = self.format_number(revenue)
                
                # Gross Profit
                if "Gross Profit" in financials.index:
                    gross_profit = financials.loc["Gross Profit"].iloc[0]
                    if not pd.isna(gross_profit):
                        result["Gross Profit"] = self.format_number(gross_profit)
                
                # Operating Income
                if "Operating Income" in financials.index:
                    op_income = financials.loc["Operating Income"].iloc[0]
                    if not pd.isna(op_income):
                        result["Operating Income"] = self.format_number(op_income)
                
                # EBITDA
                if "EBITDA" in financials.index:
                    ebitda = financials.loc["EBITDA"].iloc[0]
                    if not pd.isna(ebitda):
                        result["EBITDA"] = self.format_number(ebitda)
                
                # Interest Expense (for Interest Coverage ratio)
                if "Interest Expense" in financials.index:
                    int_exp = financials.loc["Interest Expense"].iloc[0]
                    if not pd.isna(int_exp):
                        result["Interest Expense"] = self.format_number(abs(int_exp))
            
            # Balance Sheet Metrics
            if balance_sheet is not None and not balance_sheet.empty:
                # Total Assets
                if "Total Assets" in balance_sheet.index:
                    assets = balance_sheet.loc["Total Assets"].iloc[0]
                    if not pd.isna(assets):
                        result["Total Assets"] = self.format_number(assets)
                
                # Total Debt
                if "Total Debt" in balance_sheet.index:
                    debt = balance_sheet.loc["Total Debt"].iloc[0]
                    if not pd.isna(debt):
                        result["Total Debt"] = self.format_number(debt)
                elif "Long Term Debt" in balance_sheet.index:
                    debt = balance_sheet.loc["Long Term Debt"].iloc[0]
                    if not pd.isna(debt):
                        result["Total Debt"] = self.format_number(debt)
                
                # Total Equity
                if "Stockholders Equity" in balance_sheet.index:
                    equity = balance_sheet.loc["Stockholders Equity"].iloc[0]
                    if not pd.isna(equity):
                        result["Total Equity"] = self.format_number(equity)
                elif "Total Stockholder Equity" in balance_sheet.index:
                    equity = balance_sheet.loc["Total Stockholder Equity"].iloc[0]
                    if not pd.isna(equity):
                        result["Total Equity"] = self.format_number(equity)
                
                # Current Assets
                if "Current Assets" in balance_sheet.index:
                    curr_assets = balance_sheet.loc["Current Assets"].iloc[0]
                    if not pd.isna(curr_assets):
                        result["Current Assets"] = self.format_number(curr_assets)
                
                # Current Liabilities
                if "Current Liabilities" in balance_sheet.index:
                    curr_liab = balance_sheet.loc["Current Liabilities"].iloc[0]
                    if not pd.isna(curr_liab):
                        result["Current Liabilities"] = self.format_number(curr_liab)
                
                # Cash
                if "Cash And Cash Equivalents" in balance_sheet.index:
                    cash = balance_sheet.loc["Cash And Cash Equivalents"].iloc[0]
                    if not pd.isna(cash):
                        result["Cash and Cash Equivalents"] = self.format_number(cash)
            
            # Cash Flow Metrics
            if cashflow is not None and not cashflow.empty:
                # Operating Cash Flow
                if "Total Cash From Operating Activities" in cashflow.index:
                    ocf = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
                    if not pd.isna(ocf):
                        result["Operating Cash Flow"] = self.format_number(ocf)
                elif "Operating Cash Flow" in cashflow.index:
                    ocf = cashflow.loc["Operating Cash Flow"].iloc[0]
                    if not pd.isna(ocf):
                        result["Operating Cash Flow"] = self.format_number(ocf)
                
                # Capital Expenditure
                if "Capital Expenditure" in cashflow.index:
                    capex = cashflow.loc["Capital Expenditure"].iloc[0]
                    if not pd.isna(capex):
                        result["Capital Expenditure"] = self.format_number(abs(capex))
                
                # Calculate Free Cash Flow (Operating CF - CapEx)
                ocf_val = None
                if "Total Cash From Operating Activities" in cashflow.index:
                    ocf_val = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
                elif "Operating Cash Flow" in cashflow.index:
                    ocf_val = cashflow.loc["Operating Cash Flow"].iloc[0]
                
                if "Capital Expenditure" in cashflow.index:
                    capex_val = cashflow.loc["Capital Expenditure"].iloc[0]
                    if not pd.isna(ocf_val) and not pd.isna(capex_val):
                        fcf = ocf_val + capex_val  # CapEx is negative
                        result["Free Cash Flow"] = self.format_number(fcf)
            
            # Valuation Metrics from info
            if info:
                # Market Cap
                if "marketCap" in info and info["marketCap"]:
                    result["Market Cap"] = self.format_number(info["marketCap"])
                
                # Enterprise Value
                if "enterpriseValue" in info and info["enterpriseValue"]:
                    result["Enterprise Value"] = self.format_number(info["enterpriseValue"])
                
                # P/E Ratio
                if "trailingPE" in info and info["trailingPE"]:
                    result["P/E Ratio"] = f"{info['trailingPE']:.2f}"
                
                # P/B Ratio
                if "priceToBook" in info and info["priceToBook"]:
                    result["P/B Ratio"] = f"{info['priceToBook']:.2f}"
                
                # EPS
                if "trailingEps" in info and info["trailingEps"]:
                    result["EPS"] = f"${info['trailingEps']:.2f}"
            
            # Calculate Ratios
            try:
                # Get raw values for calculations
                net_income_raw = None
                revenue_raw = None
                assets_raw = None
                equity_raw = None
                debt_raw = None
                curr_assets_raw = None
                curr_liab_raw = None
                cash_raw = None
                
                ocf_raw = None
                ebitda_raw = None
                interest_expense_raw = None
                op_income_raw = None
                
                if financials is not None and not financials.empty:
                    if "Net Income" in financials.index:
                        net_income_raw = financials.loc["Net Income"].iloc[0]
                    if "Total Revenue" in financials.index:
                        revenue_raw = financials.loc["Total Revenue"].iloc[0]
                    elif "Revenue" in financials.index:
                        revenue_raw = financials.loc["Revenue"].iloc[0]
                    if "Operating Income" in financials.index:
                        op_income_raw = financials.loc["Operating Income"].iloc[0]
                    if "EBITDA" in financials.index:
                        ebitda_raw = financials.loc["EBITDA"].iloc[0]
                    if "Interest Expense" in financials.index:
                        interest_expense_raw = financials.loc["Interest Expense"].iloc[0]
                        if pd.isna(interest_expense_raw):
                            interest_expense_raw = None
                        elif interest_expense_raw != 0:
                            interest_expense_raw = abs(interest_expense_raw)
                
                if cashflow is not None and not cashflow.empty:
                    if "Total Cash From Operating Activities" in cashflow.index:
                        ocf_raw = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
                    elif "Operating Cash Flow" in cashflow.index:
                        ocf_raw = cashflow.loc["Operating Cash Flow"].iloc[0]
                
                if balance_sheet is not None and not balance_sheet.empty:
                    if "Total Assets" in balance_sheet.index:
                        assets_raw = balance_sheet.loc["Total Assets"].iloc[0]
                    if "Stockholders Equity" in balance_sheet.index:
                        equity_raw = balance_sheet.loc["Stockholders Equity"].iloc[0]
                    elif "Total Stockholder Equity" in balance_sheet.index:
                        equity_raw = balance_sheet.loc["Total Stockholder Equity"].iloc[0]
                    if "Total Debt" in balance_sheet.index:
                        debt_raw = balance_sheet.loc["Total Debt"].iloc[0]
                    elif "Long Term Debt" in balance_sheet.index:
                        debt_raw = balance_sheet.loc["Long Term Debt"].iloc[0]
                    if "Current Assets" in balance_sheet.index:
                        curr_assets_raw = balance_sheet.loc["Current Assets"].iloc[0]
                    if "Current Liabilities" in balance_sheet.index:
                        curr_liab_raw = balance_sheet.loc["Current Liabilities"].iloc[0]
                    if "Cash And Cash Equivalents" in balance_sheet.index:
                        cash_raw = balance_sheet.loc["Cash And Cash Equivalents"].iloc[0]
                
                # ROE (Return on Equity)
                if net_income_raw and equity_raw and not pd.isna(net_income_raw) and not pd.isna(equity_raw) and equity_raw != 0:
                    roe = (net_income_raw / equity_raw) * 100
                    result["ROE"] = f"{roe:.2f}%"
                
                # ROA (Return on Assets)
                if net_income_raw and assets_raw and not pd.isna(net_income_raw) and not pd.isna(assets_raw) and assets_raw != 0:
                    roa = (net_income_raw / assets_raw) * 100
                    result["ROA"] = f"{roa:.2f}%"
                
                # Profit Margin
                if net_income_raw and revenue_raw and not pd.isna(net_income_raw) and not pd.isna(revenue_raw) and revenue_raw != 0:
                    profit_margin = (net_income_raw / revenue_raw) * 100
                    result["Profit Margin"] = f"{profit_margin:.2f}%"
                
                # Operating Margin (if Operating Income available)
                if financials is not None and not financials.empty:
                    if "Operating Income" in financials.index:
                        op_income_raw = financials.loc["Operating Income"].iloc[0]
                        if revenue_raw and not pd.isna(op_income_raw) and not pd.isna(revenue_raw) and revenue_raw != 0:
                            op_margin = (op_income_raw / revenue_raw) * 100
                            result["Operating Margin"] = f"{op_margin:.2f}%"
                
                # Current Ratio
                if curr_assets_raw and curr_liab_raw and not pd.isna(curr_assets_raw) and not pd.isna(curr_liab_raw) and curr_liab_raw != 0:
                    current_ratio = curr_assets_raw / curr_liab_raw
                    result["Current Ratio"] = f"{current_ratio:.2f}"
                
                # Quick Ratio (Current Assets - Cash) / Current Liabilities
                if curr_assets_raw and cash_raw and curr_liab_raw:
                    if not pd.isna(curr_assets_raw) and not pd.isna(cash_raw) and not pd.isna(curr_liab_raw) and curr_liab_raw != 0:
                        quick_ratio = (curr_assets_raw - cash_raw) / curr_liab_raw
                        result["Quick Ratio"] = f"{quick_ratio:.2f}"
                
                # Debt-to-Equity
                if debt_raw and equity_raw and not pd.isna(debt_raw) and not pd.isna(equity_raw) and equity_raw != 0:
                    debt_to_equity = debt_raw / equity_raw
                    result["Debt-to-Equity"] = f"{debt_to_equity:.2f}"
                
                # Debt-to-Assets
                if debt_raw and assets_raw and not pd.isna(debt_raw) and not pd.isna(assets_raw) and assets_raw != 0:
                    debt_to_assets = (debt_raw / assets_raw) * 100
                    result["Debt-to-Assets"] = f"{debt_to_assets:.2f}%"
                
                # Cash Conversion Ratio (CFO / EBITDA) – key truth-check: profits in bank vs on paper
                if ocf_raw is not None and ebitda_raw is not None and not pd.isna(ocf_raw) and not pd.isna(ebitda_raw) and ebitda_raw != 0:
                    cash_conversion = (ocf_raw / ebitda_raw)
                    result["Cash Conversion (CFO/EBITDA)"] = f"{cash_conversion:.2f}x"
                
                # Asset Turnover (Revenue / Total Assets) – capital efficiency; falling = less efficient "scaling"
                if revenue_raw and assets_raw and not pd.isna(revenue_raw) and not pd.isna(assets_raw) and assets_raw != 0:
                    asset_turnover = revenue_raw / assets_raw
                    result["Asset Turnover"] = f"{asset_turnover:.2f}x"
                
                # Interest Coverage (Operating Income / Interest Expense) – ability to service debt
                if op_income_raw is not None and interest_expense_raw is not None and interest_expense_raw != 0:
                    if not pd.isna(op_income_raw):
                        interest_coverage = op_income_raw / interest_expense_raw
                        result["Interest Coverage"] = f"{interest_coverage:.2f}x"
                    
            except Exception as calc_error:
                # If ratio calculation fails, continue with available data
                pass
            
            return result
            
        except Exception as e:
            # Return error state with a clear message for network/DNS failures
            err_msg = str(e)
            if _is_network_error(e):
                err_msg = NETWORK_ERROR_MESSAGE
            return {
                "Ticker": ticker.upper(),
                "Company Name": "Error",
                "Error": err_msg,
            }
    
    def get_historical_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical stock price data for charting.
        
        Args:
            ticker: Stock ticker symbol
            period: Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            pd.DataFrame: Historical price data with Date, Open, High, Low, Close, Volume
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=period)
            return hist
        except Exception:
            return pd.DataFrame()
    
    def get_financial_history(self, ticker: str, metric: str = "revenue", years: int = 5) -> Dict:
        """
        Get historical financial data for a specific metric.
        
        Args:
            ticker: Stock ticker symbol
            metric: Metric to track ('revenue', 'net_income', 'cash_flow')
            years: Number of years of history
            
        Returns:
            Dict with years and values
        """
        try:
            stock = yf.Ticker(ticker.upper())
            financials = stock.financials
            
            if financials is None or financials.empty:
                return {}
            
            history = {}
            
            # Get data for last N years (columns are years, most recent first)
            num_years = min(years, len(financials.columns))
            
            for i in range(num_years):
                year = financials.columns[i]
                if metric == "revenue":
                    if "Total Revenue" in financials.index:
                        value = financials.loc["Total Revenue", year]
                    elif "Revenue" in financials.index:
                        value = financials.loc["Revenue", year]
                    else:
                        continue
                elif metric == "net_income":
                    if "Net Income" in financials.index:
                        value = financials.loc["Net Income", year]
                    else:
                        continue
                else:
                    continue
                
                if not pd.isna(value):
                    history[str(year)[:4]] = float(value)
            
            return history
            
        except Exception as e:
            return {}

