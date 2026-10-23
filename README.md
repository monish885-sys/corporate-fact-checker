# The Corporate Fact-Checker

A Streamlit application that performs "Financial Grounding" by verifying claims in CEO transcripts and news articles against actual audited financial data.

## Features

- **Dual market support**: Global (US, Yahoo Finance) and **India (NSE/BSE)**
- Fetches real-time financial data (Yahoo Finance for US; NSEPython + yfinance for India)
- **India**: Corporate actions (dividends, splits), SEBI/BRSR filing links, Screener.in 10-year trends
- Analyzes text claims against actual financial metrics
- Fact-checking analysis and Truth Score (out of 10) via **Ollama** (local, free; no API key)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and run Ollama**
   - Install from [ollama.com](https://ollama.com)
   - Pull a model: `ollama run llama3.2` (or `ollama run mistral`)
   - Optional: set `OLLAMA_MODEL=mistral` in `.env` to use a different model (default: `llama3.2`)

3. **Run the Application**
   ```bash
   python run_app.py
   ```
   Or: `streamlit run app/main_ui.py`

## Usage

1. Choose **Market**: Global (US) or India in the sidebar
2. Enter a stock ticker (e.g. AAPL, TSLA for Global; RELIANCE, TCS, INFY for India)
3. Click "Fetch Financials" to load company data
4. For India: use **SEBI Filings** links for BRSR/Annual Reports; **Screener.in** for 10-year trends
5. Paste the earnings call transcript or news article
6. Click "Run Fact Check" to get the analysis and Truth Score (powered by Ollama)

## India Market Data Sources

- **NSEPython** (optional): Install `nsepython` or `nsepythonserver` for NSE API (corporate actions, live quote). Without it, India data uses yfinance with `.NS` suffix.
- **SEBI/BSE/NSE Filings**: Links to BRSR (Business Responsibility & Sustainability Reports), Annual Reports, and Investor Presentations
- **Screener.in**: 10-year revenue and profit trends (scraped when you click "Fetch Screener.in data")

## Financial Metrics Analyzed

- Net Income, Total Revenue, Operating Cash Flow, Total Debt
- Valuation (P/E, EPS), profitability (ROE, ROA, margins), liquidity and leverage ratios
- **Truth-Check Ratios** (critical for manufacturing/FMCG and Indian markets):
  - **Cash Conversion (CFO/EBITDA)**: High EBITDA with low CFO = profits on paper, not in the bank (red flag).
  - **Asset Turnover**: Revenue/Assets; falling ratio despite revenue growth = less efficient scaling.
  - **Interest Coverage**: Operating Income/Interest; low ratio = debt-servicing risk (e.g. in rate-sensitive India).
- India: Corporate actions (dividends, splits) when available

## Requirements

- Python 3.10+
- **Ollama** (local; install from [ollama.com](https://ollama.com), then `ollama run llama3.2`)
- Internet connection (for Yahoo Finance, NSE, Screener.in)
