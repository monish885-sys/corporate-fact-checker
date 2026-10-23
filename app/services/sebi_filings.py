"""
SEBI / BSE / NSE filing integration.
Provides links to Annual Reports (BRSR), Investor Presentations, and corporate filings.
"""
from typing import Dict, List, Optional
import re

# Optional: fetch filing list from NSE/BSE pages (requires requests + BeautifulSoup)
try:
    import requests
    from urllib.parse import quote
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# NSE & BSE corporate filings base URLs (official)
NSE_CORPORATE_FILINGS = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
NSE_BRSR = "https://www.nseindia.com/companies-listing/corporate-filings-bussiness-sustainabilitiy-reports"
NSE_COMPANY_FILINGS_TEMPLATE = "https://www.nseindia.com/company-tracking?symbol={symbol}"
BSE_CORPORATE_ANNOUNCEMENTS = "https://www.bseindia.com/corporates/List_Forth_Results.aspx"
BSE_COMPANY_FILINGS = "https://www.bseindia.com/corporates/List_Company.aspx?scripcd={scrip_cd}"
SEBI_CORPORATE_FILINGS = "https://www.sebi.gov.in/curation/corporate_filings.html"


def get_filing_links(symbol: str, exchange: str = "NSE") -> Dict[str, str]:
    """
    Return direct links to BRSR, Annual Reports, and Investor Presentations for a company.
    Symbol should be NSE ticker (e.g. RELIANCE, TCS). BSE scrip code can be added later.
    """
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        symbol = symbol[:-3]

    links = {
        "NSE Corporate Filings (All)": NSE_CORPORATE_FILINGS,
        "NSE BRSR (Sustainability Reports)": NSE_BRSR,
        "NSE Company Tracking": NSE_COMPANY_FILINGS_TEMPLATE.format(symbol=symbol),
        "BSE Corporate Announcements": BSE_CORPORATE_ANNOUNCEMENTS,
        "SEBI Corporate Filings": SEBI_CORPORATE_FILINGS,
    }

    return links


def get_brsr_download_note(symbol: str) -> str:
    """Return user-facing note on how to access BRSR/Annual Report for the symbol."""
    symbol = symbol.upper().strip()
    return (
        f"For **{symbol}**: Open NSE BRSR page, search for the company, and download the latest "
        "Business Responsibility and Sustainability Report (BRSR). "
        "Investor presentations are often under 'Corporate Announcements' on NSE/BSE."
    )


def fetch_nse_company_filings_list(symbol: str) -> List[Dict[str, str]]:
    """
    Optionally fetch list of filings from NSE for the company.
    NSE requires session/cookies for many endpoints; this may return empty if blocked.
    """
    if not REQUESTS_AVAILABLE:
        return []

    symbol = symbol.upper().strip()
    if symbol.endswith(".NS"):
        symbol = symbol[:-3]

    results = []
    try:
        # NSE company tracking page - often requires Referer and cookies
        url = NSE_COMPANY_FILINGS_TEMPLATE.format(symbol=quote(symbol))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://www.nseindia.com/",
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and "Annual Report" in r.text or "BRSR" in r.text:
            # Minimal parse: just indicate that page was fetched
            results.append({"title": "NSE Company Filings", "url": url, "source": "NSE"})
    except Exception:
        pass
    return results
