"""
Main Streamlit UI for The Corporate Fact-Checker.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.services.finance_data import FinanceFetcher
from app.services.llm_analyzer import FactChecker
from app.config import validate_config


def main():
    """Main Streamlit application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="The Corporate Fact-Checker",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title
    st.title("🔍 The Corporate Fact-Checker")
    st.markdown("### Financial Grounding Tool")
    st.markdown("Verify claims in CEO transcripts and news articles against actual financial data.")
    
    # Initialize session state
    if "financial_data" not in st.session_state:
        st.session_state.financial_data = None
    if "ticker" not in st.session_state:
        st.session_state.ticker = "TSLA"
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Financial Data")
        
        # Ticker input
        ticker_input = st.text_input(
            "Stock Ticker",
            value=st.session_state.ticker,
            placeholder="e.g., AAPL, TSLA, MSFT",
            help="Enter a valid stock ticker symbol"
        )
        
        # Fetch button
        if st.button("Fetch Financials", type="primary"):
            if ticker_input:
                st.session_state.ticker = ticker_input.upper()
                with st.spinner(f"Fetching financial data for {ticker_input.upper()}..."):
                    fetcher = FinanceFetcher()
                    st.session_state.financial_data = fetcher.get_metrics(ticker_input)
                st.success("Financial data fetched!")
            else:
                st.error("Please enter a stock ticker.")
        
        # Display financial metrics
        if st.session_state.financial_data:
            # Company info
            company_name = st.session_state.financial_data.get("Company Name", "Unknown")
            ticker = st.session_state.financial_data.get("Ticker", "N/A")
            sector = st.session_state.financial_data.get("Sector", "N/A")
            industry = st.session_state.financial_data.get("Industry", "N/A")
            
            st.markdown(f"### **{company_name}** ({ticker})")
            if sector != "N/A":
                st.caption(f"{sector} • {industry}")
            
            # Check for errors
            if "Error" in st.session_state.financial_data:
                st.error(f"⚠️ Error: {st.session_state.financial_data['Error']}")
            else:
                # Create tabs for different metric categories
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "💰 Income", "🏦 Balance Sheet", "💵 Cash Flow", "📈 Valuation"])
                
                with tab1:
                    st.subheader("Key Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Market Cap", st.session_state.financial_data.get("Market Cap", "N/A"))
                    with col2:
                        st.metric("P/E Ratio", st.session_state.financial_data.get("P/E Ratio", "N/A"))
                    with col3:
                        st.metric("EPS", st.session_state.financial_data.get("EPS", "N/A"))
                    with col4:
                        st.metric("ROE", st.session_state.financial_data.get("ROE", "N/A"))
                    
                    # Profitability Ratios Chart
                    st.subheader("Profitability Ratios")
                    profitability_data = {
                        "Metric": ["ROE", "ROA", "Profit Margin", "Operating Margin"],
                        "Value": [
                            float(st.session_state.financial_data.get("ROE", "0%").replace("%", "")) if st.session_state.financial_data.get("ROE", "N/A") != "N/A" and "%" in st.session_state.financial_data.get("ROE", "") else 0,
                            float(st.session_state.financial_data.get("ROA", "0%").replace("%", "")) if st.session_state.financial_data.get("ROA", "N/A") != "N/A" and "%" in st.session_state.financial_data.get("ROA", "") else 0,
                            float(st.session_state.financial_data.get("Profit Margin", "0%").replace("%", "")) if st.session_state.financial_data.get("Profit Margin", "N/A") != "N/A" and "%" in st.session_state.financial_data.get("Profit Margin", "") else 0,
                            float(st.session_state.financial_data.get("Operating Margin", "0%").replace("%", "")) if st.session_state.financial_data.get("Operating Margin", "N/A") != "N/A" and "%" in st.session_state.financial_data.get("Operating Margin", "") else 0,
                        ]
                    }
                    if any(v != 0 for v in profitability_data["Value"]):
                        fig = px.bar(
                            profitability_data,
                            x="Metric",
                            y="Value",
                            title="Profitability Ratios (%)",
                            color="Value",
                            color_continuous_scale="Greens"
                        )
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Stock Price Chart
                    st.subheader("Stock Price History (1 Year)")
                    try:
                        fetcher = FinanceFetcher()
                        hist_data = fetcher.get_historical_data(ticker, period="1y")
                        if not hist_data.empty:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=hist_data.index,
                                y=hist_data['Close'],
                                mode='lines',
                                name='Close Price',
                                line=dict(color='#1f77b4', width=2)
                            ))
                            fig.update_layout(
                                title="Stock Price Over Time",
                                xaxis_title="Date",
                                yaxis_title="Price ($)",
                                height=400,
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Historical price data not available")
                    except Exception as e:
                        st.warning(f"Could not load price chart: {str(e)}")
                
                with tab2:
                    st.subheader("Income Statement Metrics")
                    income_metrics = {
                        "Total Revenue": st.session_state.financial_data.get("Total Revenue", "N/A"),
                        "Gross Profit": st.session_state.financial_data.get("Gross Profit", "N/A"),
                        "Operating Income": st.session_state.financial_data.get("Operating Income", "N/A"),
                        "EBITDA": st.session_state.financial_data.get("EBITDA", "N/A"),
                        "Net Income": st.session_state.financial_data.get("Net Income", "N/A"),
                    }
                    
                    income_df = pd.DataFrame(list(income_metrics.items()), columns=["Metric", "Value"])
                    st.dataframe(income_df, use_container_width=True, hide_index=True)
                    
                    # Revenue vs Net Income Chart
                    try:
                        revenue_val = st.session_state.financial_data.get("Total Revenue", "N/A")
                        net_income_val = st.session_state.financial_data.get("Net Income", "N/A")
                        
                        if revenue_val != "N/A" and net_income_val != "N/A":
                            # Try to extract numeric values for comparison
                            comparison_data = {
                                "Metric": ["Total Revenue", "Net Income"],
                                "Value": [1, 0.1]  # Placeholder - would need to parse formatted strings
                            }
                            st.info("💡 Revenue and Net Income comparison available when numeric values are parsed")
                    except:
                        pass
                
                with tab3:
                    st.subheader("Balance Sheet Metrics")
                    balance_metrics = {
                        "Total Assets": st.session_state.financial_data.get("Total Assets", "N/A"),
                        "Total Debt": st.session_state.financial_data.get("Total Debt", "N/A"),
                        "Total Equity": st.session_state.financial_data.get("Total Equity", "N/A"),
                        "Current Assets": st.session_state.financial_data.get("Current Assets", "N/A"),
                        "Current Liabilities": st.session_state.financial_data.get("Current Liabilities", "N/A"),
                        "Cash and Cash Equivalents": st.session_state.financial_data.get("Cash and Cash Equivalents", "N/A"),
                    }
                    
                    balance_df = pd.DataFrame(list(balance_metrics.items()), columns=["Metric", "Value"])
                    st.dataframe(balance_df, use_container_width=True, hide_index=True)
                    
                    # Liquidity Ratios
                    st.subheader("Liquidity & Leverage Ratios")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Ratio", st.session_state.financial_data.get("Current Ratio", "N/A"))
                        st.metric("Quick Ratio", st.session_state.financial_data.get("Quick Ratio", "N/A"))
                    with col2:
                        st.metric("Debt-to-Equity", st.session_state.financial_data.get("Debt-to-Equity", "N/A"))
                        st.metric("Debt-to-Assets", st.session_state.financial_data.get("Debt-to-Assets", "N/A"))
                
                with tab4:
                    st.subheader("Cash Flow Metrics")
                    cashflow_metrics = {
                        "Operating Cash Flow": st.session_state.financial_data.get("Operating Cash Flow", "N/A"),
                        "Free Cash Flow": st.session_state.financial_data.get("Free Cash Flow", "N/A"),
                        "Capital Expenditure": st.session_state.financial_data.get("Capital Expenditure", "N/A"),
                    }
                    
                    cashflow_df = pd.DataFrame(list(cashflow_metrics.items()), columns=["Metric", "Value"])
                    st.dataframe(cashflow_df, use_container_width=True, hide_index=True)
                
                with tab5:
                    st.subheader("Valuation Metrics")
                    valuation_metrics = {
                        "Market Cap": st.session_state.financial_data.get("Market Cap", "N/A"),
                        "Enterprise Value": st.session_state.financial_data.get("Enterprise Value", "N/A"),
                        "P/E Ratio": st.session_state.financial_data.get("P/E Ratio", "N/A"),
                        "P/B Ratio": st.session_state.financial_data.get("P/B Ratio", "N/A"),
                        "EPS": st.session_state.financial_data.get("EPS", "N/A"),
                    }
                    
                    valuation_df = pd.DataFrame(list(valuation_metrics.items()), columns=["Metric", "Value"])
                    st.dataframe(valuation_df, use_container_width=True, hide_index=True)
    
    # Main content area
    st.header("📝 Transcript / News Analysis")
    
    # Text area for transcript
    transcript_text = st.text_area(
        "Paste Earnings Call Transcript / News Article",
        height=300,
        placeholder="Paste the text containing financial claims here...",
        help="Enter the CEO transcript, news article, or any text containing financial claims"
    )
    
    # Fact check button
    if st.button("Run Fact Check", type="primary"):
        # Validate inputs
        if not transcript_text.strip():
            st.error("Please enter some text to analyze.")
        elif not st.session_state.financial_data:
            st.error("Please fetch financial data first using the sidebar.")
        elif not validate_config():
            st.error("⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file.")
        else:
            # Run analysis
            with st.spinner("🔍 Analyzing claims against financial data..."):
                try:
                    fact_checker = FactChecker()
                    analysis = fact_checker.analyze_claims(
                        st.session_state.financial_data,
                        transcript_text
                    )
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📊 Analysis Results")
                    st.markdown(analysis)
                    
                except ValueError as e:
                    st.error(f"⚠️ Configuration Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "The Corporate Fact-Checker | Financial Grounding Tool"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

