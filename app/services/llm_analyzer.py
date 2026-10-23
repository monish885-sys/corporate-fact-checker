"""
LLM analyzer using Ollama (local, free).
"""
from typing import Dict
import requests
from app.config import get_ollama_model


def _build_financial_context(financial_data: Dict[str, str]) -> str:
    return f"""
COMPANY INFORMATION:
Ticker: {financial_data.get('Ticker', 'N/A')}
Company: {financial_data.get('Company Name', 'N/A')}
Sector: {financial_data.get('Sector', 'N/A')}
Industry: {financial_data.get('Industry', 'N/A')}

INCOME STATEMENT METRICS:
Total Revenue: {financial_data.get('Total Revenue', 'N/A')}
Gross Profit: {financial_data.get('Gross Profit', 'N/A')}
Operating Income: {financial_data.get('Operating Income', 'N/A')}
EBITDA: {financial_data.get('EBITDA', 'N/A')}
Net Income: {financial_data.get('Net Income', 'N/A')}

BALANCE SHEET METRICS:
Total Assets: {financial_data.get('Total Assets', 'N/A')}
Total Debt: {financial_data.get('Total Debt', 'N/A')}
Total Equity: {financial_data.get('Total Equity', 'N/A')}
Current Assets: {financial_data.get('Current Assets', 'N/A')}
Current Liabilities: {financial_data.get('Current Liabilities', 'N/A')}
Cash and Cash Equivalents: {financial_data.get('Cash and Cash Equivalents', 'N/A')}

CASH FLOW METRICS:
Operating Cash Flow: {financial_data.get('Operating Cash Flow', 'N/A')}
Free Cash Flow: {financial_data.get('Free Cash Flow', 'N/A')}
Capital Expenditure: {financial_data.get('Capital Expenditure', 'N/A')}

VALUATION METRICS:
Market Cap: {financial_data.get('Market Cap', 'N/A')}
Enterprise Value: {financial_data.get('Enterprise Value', 'N/A')}
P/E Ratio: {financial_data.get('P/E Ratio', 'N/A')}
P/B Ratio: {financial_data.get('P/B Ratio', 'N/A')}
EPS: {financial_data.get('EPS', 'N/A')}

PROFITABILITY RATIOS:
ROE (Return on Equity): {financial_data.get('ROE', 'N/A')}
ROA (Return on Assets): {financial_data.get('ROA', 'N/A')}
Profit Margin: {financial_data.get('Profit Margin', 'N/A')}
Operating Margin: {financial_data.get('Operating Margin', 'N/A')}

LIQUIDITY RATIOS:
Current Ratio: {financial_data.get('Current Ratio', 'N/A')}
Quick Ratio: {financial_data.get('Quick Ratio', 'N/A')}

LEVERAGE RATIOS:
Debt-to-Equity: {financial_data.get('Debt-to-Equity', 'N/A')}
Debt-to-Assets: {financial_data.get('Debt-to-Assets', 'N/A')}

TRUTH-CHECK RATIOS (critical for manufacturing/FMCG and Indian markets):
Interest Expense: {financial_data.get('Interest Expense', 'N/A')}
Cash Conversion (CFO/EBITDA): {financial_data.get('Cash Conversion (CFO/EBITDA)', 'N/A')}  — Profits in bank vs on paper; low or negative CFO vs high EBITDA = red flag (accruals, not cash).
Asset Turnover: {financial_data.get('Asset Turnover', 'N/A')}  — Revenue/Assets; if revenue grows but ratio falls, company is scaling less efficiently.
Interest Coverage: {financial_data.get('Interest Coverage', 'N/A')}  — Operating Income/Interest; ability to service debt; crucial when interest rates fluctuate (e.g. India).
"""


SYSTEM_PROMPT = """You are an expert forensic financial analyst with deep expertise in corporate financial analysis. Your job is to perform a comprehensive fact-check by comparing a company's actual audited financial data against claims made in earnings calls, press releases, or news articles.

ANALYSIS FRAMEWORK:
1. **Revenue & Growth Claims**: Verify claims about revenue growth, market share, sales performance against actual Total Revenue, Gross Profit, and Operating Income.

2. **Profitability Claims**: Check claims about profitability, margins, and earnings against Net Income, Profit Margin, ROE, ROA, and Operating Margin.

3. **Financial Health Claims**: Validate claims about financial strength, liquidity, and stability using Current Ratio, Quick Ratio, Cash position, and Free Cash Flow.

4. **Debt & Leverage Claims**: Fact-check debt-related claims using Total Debt, Debt-to-Equity ratio, Debt-to-Assets ratio, and compare against Equity.

5. **Valuation Claims**: Verify market cap, P/E ratio, and valuation claims against provided metrics.

6. **Cash Flow Claims**: Validate cash flow statements using Operating Cash Flow, Free Cash Flow, and Capital Expenditure data.

7. **TRUTH-CHECK RATIOS (especially for Indian manufacturing/FMCG)**:
   - **CFO to EBITDA (Cash Conversion Ratio)**: If the CEO claims "record EBITDA" or "strong profitability" but Cash Conversion (CFO/EBITDA) is low, below 1x, or negative, FLAG this as a major red flag—profits may be on paper (accruals) and not in the bank. High EBITDA with low/negative CFO suggests quality-of-earnings risk.
   - **Asset Turnover (Revenue/Assets)**: If the CEO claims "scaling efficiently" or "capital efficiency" but Asset Turnover is declining (or low) while revenue is growing, FLAG it—the company may be adding assets faster than revenue, i.e. becoming less efficient.
   - **Interest Coverage (Operating Income/Interest Expense)**: If the CEO downplays debt or interest risk but Interest Coverage is low (e.g. below 2–3x) or falling, FLAG it—this is a leading indicator of default risk, especially important in rate-sensitive markets like India.

INSTRUCTIONS:
- Analyze ALL financial claims in the text systematically
- Compare each claim against the relevant financial metrics provided
- Flag ANY contradictions, exaggerations, or misleading statements
- Provide specific evidence (quote the metric and value) for each flag
- Calculate a comprehensive "Truth Score" out of 10 based on:
  * Number of accurate claims (positive points)
  * Number of false/misleading claims (negative points)
  * Severity of false claims (major vs minor discrepancies)
- Identify patterns of misleading communication
- Provide actionable insights about the company's actual financial position

OUTPUT FORMAT:
- Use Markdown formatting
- Use emojis for visual clarity (✅ for accurate, ⚠️ for questionable, ❌ for false)
- Structure: Executive Summary → Detailed Analysis → Truth Score → Key Findings
- Be thorough, professional, and evidence-based"""


def _error_msg(generic: str, detail: str = "") -> str:
    return f"## Error in Analysis\n\n❌ **Error:** {detail or generic}\n\nEnsure Ollama is running (ollama run llama3.2) and try again."


class FactChecker:
    """Analyze financial claims using Ollama (local)."""

    def __init__(self):
        pass

    def analyze_claims(self, financial_data: Dict[str, str], transcript_text: str) -> str:
        """
        Analyze claims in the transcript against financial data.

        Returns:
            str: Markdown-formatted analysis report
        """
        financial_context = _build_financial_context(financial_data)
        user_prompt = f"""CONTEXT (THE TRUTH):
{financial_context}

USER INPUT (THE CLAIM):
{transcript_text}

Please analyze the claims in the text above against the financial data provided. Flag any contradictions and provide a Truth Score out of 10."""

        try:
            return _call_ollama(user_prompt)
        except Exception as e:
            return _error_msg("LLM request failed.", str(e))


def _call_ollama(user_prompt: str) -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    model = get_ollama_model()
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 2500},
    }
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        return _error_msg(
            "Cannot reach Ollama.",
            "Is Ollama running? Install from ollama.com and run: ollama run " + model,
        )
    except requests.exceptions.Timeout:
        return _error_msg("Ollama request timed out. Try a smaller model or shorter transcript.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return _error_msg("Ollama model not found.", f"Run: ollama run {model}")
        return _error_msg("Ollama error.", str(e))
    data = r.json()
    text = (data.get("response") or "").strip()
    if not text:
        return "## Error in Analysis\n\n⚠️ **No Response:** Ollama returned empty text. Try another model (e.g. ollama run mistral)."
    return text
