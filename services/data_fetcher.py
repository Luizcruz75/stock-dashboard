import pandas as pd
import yfinance as yf
from config import TICKERS, START_DATE, END_DATE

_cache = {}


def _fetch_raw():
    tickers = list(TICKERS.keys())
    raw = yf.download(tickers, start=START_DATE, end=END_DATE, group_by="ticker", auto_adjust=True)
    return raw


def get_stock_data():
    """Retorna dict {ticker: DataFrame} com colunas limpas e derivadas."""
    if _cache:
        return _cache

    try:
        raw = _fetch_raw()
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados: {e}")

    tickers = list(TICKERS.keys())

    for ticker in tickers:
        try:
            if len(tickers) == 1:
                df = raw.copy()
            else:
                df = raw[ticker].copy()

            df = df.dropna(subset=["Close"])
            df.index = pd.to_datetime(df.index)
            df["retorno_diario"] = df["Close"].pct_change() * 100
            first_close = df["Close"].iloc[0]
            df["retorno_acumulado"] = (df["Close"] / first_close - 1) * 100
            _cache[ticker] = df
        except Exception:
            _cache[ticker] = pd.DataFrame()

    return _cache


def get_ticker_data(ticker):
    """Retorna DataFrame de um único ticker."""
    data = get_stock_data()
    return data.get(ticker, pd.DataFrame())


def get_summary_cards():
    """Retorna lista de dicts com métricas resumidas para cada ação."""
    data = get_stock_data()
    cards = []
    for ticker, info in TICKERS.items():
        df = data.get(ticker, pd.DataFrame())
        if df.empty:
            cards.append({
                "ticker": ticker,
                "name": info["name"],
                "color": info["color"],
                "preco_atual": "N/D",
                "retorno_ytd": "N/D",
                "maxima": "N/D",
                "minima": "N/D",
            })
            continue

        cards.append({
            "ticker": ticker,
            "name": info["name"],
            "color": info["color"],
            "preco_atual": f"R$ {df['Close'].iloc[-1]:.2f}",
            "retorno_ytd": f"{df['retorno_acumulado'].iloc[-1]:+.2f}%",
            "maxima": f"R$ {df['Close'].max():.2f}",
            "minima": f"R$ {df['Close'].min():.2f}",
            "retorno_valor": df["retorno_acumulado"].iloc[-1],
        })
    return cards


def get_last_updated():
    """Retorna a data mais recente nos dados."""
    data = get_stock_data()
    for df in data.values():
        if not df.empty:
            return df.index[-1].strftime("%d/%m/%Y")
    return "N/D"
