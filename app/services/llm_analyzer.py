"""
LLM analyzer service using Google Gemini API.
"""
from typing import Dict
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import get_gemini_api_key, validate_config


class FactChecker:
    """Class to analyze financial claims using Google Gemini."""
    
    def __init__(self):
        """Initialize the FactChecker with Gemini client."""
        api_key = get_gemini_api_key()
        if not api_key or not validate_config():
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY in your .env file."
            )
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash for fast, reliable responses
        # Alternative: gemini-2.5-pro for better quality, gemini-flash-latest for latest version
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_claims(self, financial_data: Dict[str, str], transcript_text: str) -> str:
        """
        Analyze claims in the transcript against financial data.
        
        Args:
            financial_data: Dictionary containing financial metrics
            transcript_text: Text containing claims to verify
            
        Returns:
            str: Markdown-formatted analysis report
        """
        # Format comprehensive financial data for the prompt
        financial_context = f"""
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
"""
        
        system_prompt = """You are an expert forensic financial analyst with deep expertise in corporate financial analysis. Your job is to perform a comprehensive fact-check by comparing a company's actual audited financial data against claims made in earnings calls, press releases, or news articles.

ANALYSIS FRAMEWORK:
1. **Revenue & Growth Claims**: Verify claims about revenue growth, market share, sales performance against actual Total Revenue, Gross Profit, and Operating Income.

2. **Profitability Claims**: Check claims about profitability, margins, and earnings against Net Income, Profit Margin, ROE, ROA, and Operating Margin.

3. **Financial Health Claims**: Validate claims about financial strength, liquidity, and stability using Current Ratio, Quick Ratio, Cash position, and Free Cash Flow.

4. **Debt & Leverage Claims**: Fact-check debt-related claims using Total Debt, Debt-to-Equity ratio, Debt-to-Assets ratio, and compare against Equity.

5. **Valuation Claims**: Verify market cap, P/E ratio, and valuation claims against provided metrics.

6. **Cash Flow Claims**: Validate cash flow statements using Operating Cash Flow, Free Cash Flow, and Capital Expenditure data.

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

        user_prompt = f"""CONTEXT (THE TRUTH):
{financial_context}

USER INPUT (THE CLAIM):
{transcript_text}

Please analyze the claims in the text above against the financial data provided. Flag any contradictions and provide a Truth Score out of 10."""

        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Configure generation parameters for more detailed analysis
            generation_config = {
                "temperature": 0.2,  # Lower temperature for more factual, consistent analysis
                "max_output_tokens": 2500,  # Increased for comprehensive analysis
            }
            
            # Remove safety filters completely for financial content analysis
            # Financial transcripts should not be blocked
            safety_settings = [
                {
                    "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": HarmBlockThreshold.BLOCK_NONE
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE
                }
            ]
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.finish_reason == 2:  # SAFETY
                    return "## Error in Analysis\n\n⚠️ **Response Blocked:** The content was blocked by safety filters. This may happen if the transcript contains sensitive content. Please try with a different transcript or contact support if this persists."
                elif candidate.finish_reason == 3:  # RECITATION
                    return "## Error in Analysis\n\n⚠️ **Response Blocked:** The content was blocked due to potential recitation concerns. Please try with a different transcript."
                elif candidate.finish_reason == 4:  # OTHER
                    return "## Error in Analysis\n\n⚠️ **Response Blocked:** The content was blocked for other reasons. Please try again or use a different transcript."
            
            # Check if response has text content
            if hasattr(response, 'text') and response.text:
                return response.text
            elif response.candidates and len(response.candidates) > 0:
                # Try to get text from parts
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return ''.join(text_parts)
            
            return "## Error in Analysis\n\n⚠️ **No Response:** The API did not return any content. Please try again."
            
        except Exception as e:
            error_msg = str(e)
            if "finish_reason" in error_msg or "response.text" in error_msg:
                return "## Error in Analysis\n\n⚠️ **Response Blocked:** The content was filtered by safety settings. This can happen with certain financial terminology or content. Please try:\n\n1. Simplifying the transcript text\n2. Removing any potentially sensitive content\n3. Trying again with a different transcript"
            return f"## Error in Analysis\n\n❌ **Error:** {error_msg}\n\nPlease check your Gemini API key and try again."

