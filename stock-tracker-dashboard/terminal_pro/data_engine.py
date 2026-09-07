import yfinance as yf
import pandas as pd
import streamlit as st
import math

def get_dividend_metrics(info, price=None):
    """
    Return (div_rate, div_yield_pct)
      - div_rate: annual dividend in $/share (float)
      - div_yield_pct: dividend yield as percentage (float, e.g., 2.5 for 2.5%)
    """
    def is_number(x):
        return x is not None and isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))

    p = price or info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0
    try:
        p = float(p)
    except Exception:
        p = 0.0

    rate_keys = ("trailingAnnualDividendRate", "dividendRate", "annualDividendRate")
    yield_keys = ("trailingAnnualDividendYield", "dividendYield")

    rate = None
    y = None

    for k in rate_keys:
        v = info.get(k)
        if is_number(v):
            rate = float(v)
            break

    for k in yield_keys:
        v = info.get(k)
        if is_number(v):
            y = float(v)
            break

    calculated_yield_pct = 0.0
    if p > 0 and rate is not None and rate > 0:
        calculated_yield_pct = (rate / p) * 100.0

    yield_pct = None
    if calculated_yield_pct > 0:
        yield_pct = calculated_yield_pct
    elif y is not None:
        try:
            y_float = float(y)
            if y_float > 1.0:
                yield_pct = y_float / 100.0 if y_float > 5.0 and y_float != 0.26 else y_float
            else:
                yield_pct = y_float * 100.0
        except (ValueError, TypeError):
            yield_pct = 0.0

    if yield_pct is not None and (not rate or rate == 0.0) and p > 0:
        rate = (yield_pct / 100.0) * p

    if (rate is not None and rate > 0) and (yield_pct is None or yield_pct == 0.0) and p > 0:
        yield_pct = (rate / p) * 100.0

    rate = float(rate or 0.0)
    yield_pct = float(yield_pct or 0.0)

    if yield_pct > 50.0:
        yield_pct = yield_pct / 100.0

    return rate, yield_pct

@st.cache_data(ttl=1800)
def fetch_platform_data(tickers):
    metrics = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            company_name = info.get("longName") or info.get("shortName") or ticker
            sector = info.get("sector", "Other / Unclassified")
            price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            mcap = info.get("marketCap", 0)
            beta = info.get("beta", 0)
            pe = info.get("trailingPE", 0)
            peg = info.get("pegRatio", 0)
            pb = info.get("priceToBook", 0)
            fcf = info.get("freeCashflow", 0)

            _, div_yield_pct = get_dividend_metrics(info, price)

            metrics.append({
                "Ticker": ticker,
                "Company Name": company_name,
                "Sector": sector,
                "Price ($)": price,
                "Market Cap ($B)": round(mcap / 1e9, 2) if mcap else 0,
                "P/E Ratio": round(pe, 2) if pe else 0,
                "PEG Ratio": round(peg, 2) if peg else "N/A",
                "P/B Ratio": round(pb, 2) if pb else "N/A",
                "Free Cash Flow ($B)": round(fcf / 1e9, 2) if fcf else "N/A",
                "Div Yield (%)": round(div_yield_pct, 2),
                "Beta (5Y)": round(beta, 2) if beta else 0
            })
        except Exception:
            continue

    return pd.DataFrame(metrics)

@st.cache_data(ttl=1800)
def fetch_comparison_profile(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        _, div_yield = get_dividend_metrics(info, price)

        mcap = info.get("marketCap", 0)
        rev = info.get("totalRevenue", 0)
        fcf = info.get("freeCashflow", 0)

        return {
            "Ticker": ticker_symbol,
            "Name": info.get("longName") or info.get("shortName") or ticker_symbol,
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Price": price,
            "Market Cap ($B)": round(mcap / 1e9, 2) if mcap else 0,
            "Revenue ($B)": round(rev / 1e9, 2) if rev else 0,
            "Trailing P/E": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A",
            "Forward P/E": round(info.get("forwardPE", 0), 2) if info.get("forwardPE") else "N/A",
            "PEG Ratio": round(info.get("pegRatio", 0), 2) if info.get("pegRatio") else "N/A",
            "Price to Book (P/B)": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else "N/A",
            "EV / EBITDA": round(info.get("enterpriseToEbitda", 0), 2) if info.get("enterpriseToEbitda") else "N/A",
            "Operating Margin (%)": round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else "N/A",
            "Profit Margin (%)": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else "N/A",
            "Return on Equity (%)": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
            "Debt to Equity": round(info.get("debtToEquity", 0), 2) if info.get("debtToEquity") else "N/A",
            "Free Cash Flow ($B)": round(fcf / 1e9, 2) if fcf else "N/A",
            "Dividend Yield (%)": round(div_yield, 2),
            "Beta (5Y)": round(info.get("beta", 0), 2) if info.get("beta") else "N/A"
        }
    except Exception:
        return None