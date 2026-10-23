"""
Screener.in scraper for historical 10-year fundamental data.
Indian investors rely on long-term fundamental consistency from Screener.
"""
from typing import Dict, List, Optional, Any
import re

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

BASE_URL = "https://www.screener.in/company/{symbol}/"
CONSOLIDATED_URL = "https://www.screener.in/company/{symbol}/consolidated/"

# Rate limit: avoid too many requests
_session = None

def _get_session() -> "requests.Session":
    global _session
    if _session is None and SCRAPER_AVAILABLE:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
    return _session


def _parse_number(s: str) -> Optional[float]:
    """Parse Screener number: 1,234 Cr -> 1234e7 (in Crores), 1.2% -> 1.2."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip().replace(",", "")
    mult = 1
    if "Cr" in s or "cr" in s:
        s = s.replace("Cr", "").replace("cr", "").strip()
        mult = 1e7  # 1 Crore = 10^7
    if "%" in s:
        s = s.replace("%", "").strip()
    try:
        return float(re.sub(r"[^\d.\-]", "", s)) * mult if mult != 1 else float(re.sub(r"[^\d.\-]", "", s))
    except (ValueError, TypeError):
        return None


def fetch_screener_company(symbol: str, consolidated: bool = False) -> Dict[str, Any]:
    """
    Fetch company page from Screener.in and extract key financials.
    Returns dict with:
      - company_name
      - revenue_years: list of {year, revenue, ...}
      - profit_years: list of {year, net_profit, ...}
      - ratios: dict of latest ratios
      - raw_tables: optional raw table data
    """
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        symbol = symbol[:-3]

    out = {
        "company_name": symbol,
        "revenue_years": [],
        "profit_years": [],
        "ratios": {},
        "error": None,
        "source": "Screener.in",
    }

    if not SCRAPER_AVAILABLE:
        out["error"] = "requests and beautifulsoup4 required for Screener.in"
        return out

    url = CONSOLIDATED_URL.format(symbol=symbol) if consolidated else BASE_URL.format(symbol=symbol)
    try:
        sess = _get_session()
        r = sess.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        out["error"] = str(e)
        return out

    soup = BeautifulSoup(r.text, "html.parser")

    # Company name
    title = soup.find("h1")
    if title:
        out["company_name"] = title.get_text(strip=True)

    # Key ratios (often in a top section)
    for el in soup.select("[class*='ratio'], [class*='indicator']"):
        text = el.get_text(strip=True)
        if ":" in text:
            k, v = text.split(":", 1)
            out["ratios"][k.strip()] = v.strip()

    # Tables: Screener uses table with headers like "Sales", "Net Profit", "Years"
    tables = soup.find_all("table")
    for table in tables:
        headers = []
        thead = table.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all("th")]

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if not cells:
                continue
            row_label = cells[0].get_text(strip=True)
            values = [c.get_text(strip=True) for c in cells[1:]]

            # Map years from header (e.g. "Mar '24", "Mar '23", ...)
            if "Sales" in row_label or "Revenue" in row_label:
                for i, val in enumerate(values):
                    if i < len(headers) and val:
                        yr = headers[i] if i < len(headers) else str(i)
                        num = _parse_number(val)
                        out["revenue_years"].append({"period": yr, "value": num, "label": val})
            if "Net Profit" in row_label or "Profit" in row_label:
                for i, val in enumerate(values):
                    if i < len(headers) and val:
                        yr = headers[i] if i < len(headers) else str(i)
                        num = _parse_number(val)
                        out["profit_years"].append({"period": yr, "value": num, "label": val})

    # Dedupe and sort by period (most recent first often)
    def dedupe_by_period(items: List[Dict]) -> List[Dict]:
        seen = set()
        out_list = []
        for x in items:
            p = x.get("period")
            if p and p not in seen:
                seen.add(p)
                out_list.append(x)
        return out_list[:15]  # up to 15 years

    out["revenue_years"] = dedupe_by_period(out["revenue_years"])
    out["profit_years"] = dedupe_by_period(out["profit_years"])

    out["screener_url"] = url
    return out


def get_10_year_trends(symbol: str) -> Dict[str, Any]:
    """
    Convenience: fetch Screener data and return structure suitable for charts/tables.
    """
    data = fetch_screener_company(symbol, consolidated=False)
    if data.get("error"):
        return data

    # Build a simple table: Period | Revenue | Net Profit
    periods = set()
    rev_by_period = {p["period"]: p for p in data["revenue_years"]}
    profit_by_period = {p["period"]: p for p in data["profit_years"]}
    periods = sorted(set(rev_by_period) | set(profit_by_period), reverse=True)[:10]

    trends = []
    for p in periods:
        trends.append({
            "period": p,
            "revenue": rev_by_period.get(p, {}).get("label", "—"),
            "revenue_value": rev_by_period.get(p, {}).get("value"),
            "net_profit": profit_by_period.get(p, {}).get("label", "—"),
            "net_profit_value": profit_by_period.get(p, {}).get("value"),
        })

    data["trends_10y"] = trends
    return data
