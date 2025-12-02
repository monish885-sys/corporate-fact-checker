# The Corporate Fact-Checker

A Streamlit application that performs "Financial Grounding" by verifying claims in CEO transcripts and news articles against actual audited financial data.

## Features

- Fetches real-time financial data from Yahoo Finance using `yfinance`
- Analyzes text claims against actual financial metrics
- Uses OpenAI GPT to provide intelligent fact-checking analysis
- Provides a Truth Score (out of 10) for the claims made

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

3. **Run the Application**
   ```bash
   python run_app.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run app/main_ui.py
   ```

## Usage

1. Enter a stock ticker (e.g., AAPL, TSLA, MSFT) in the sidebar
2. Click "Fetch Financials" to retrieve the company's financial data
3. Paste the earnings call transcript or news article in the main text area
4. Click "Run Fact Check" to analyze the claims against the financial data
5. Review the analysis and Truth Score provided by the AI

## Financial Metrics Analyzed

- Net Income
- Total Revenue
- Operating Cash Flow
- Total Debt

## Requirements

- Python 3.10+
- OpenAI API key
- Internet connection (for fetching financial data)

