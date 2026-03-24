from flask import Flask, render_template, jsonify, abort
from flask_caching import Cache
from config import TICKERS, CACHE_TTL
from services import data_fetcher, chart_builder

app = Flask(__name__)
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = CACHE_TTL
cache = Cache(app)

# Injeta o cache do Flask no data_fetcher para evitar chamadas repetidas ao yfinance
_data_cache = {}


def get_data():
    global _data_cache
    if not _data_cache:
        _data_cache = data_fetcher.get_stock_data()
    return _data_cache


@app.route("/")
def index():
    try:
        data = get_data()
        price_chart = chart_builder.build_price_evolution_chart(data)
        cards = data_fetcher.get_summary_cards()
        last_updated = data_fetcher.get_last_updated()
    except Exception as e:
        return render_template("error.html", message=str(e)), 500

    return render_template(
        "index.html",
        cards=cards,
        price_chart=price_chart,
        last_updated=last_updated,
        tickers=TICKERS,
    )


@app.route("/stock/<ticker>")
def stock_detail(ticker):
    if ticker not in TICKERS:
        abort(404)
    try:
        data = get_data()
        df = data_fetcher.get_ticker_data(ticker)
        if df.empty:
            return render_template("error.html", message=f"Dados indisponíveis para {ticker}."), 500
        chart = chart_builder.build_candlestick_with_volume(df, ticker)
        cards = data_fetcher.get_summary_cards()
        card = next((c for c in cards if c["ticker"] == ticker), None)
        last_updated = data_fetcher.get_last_updated()
    except Exception as e:
        return render_template("error.html", message=str(e)), 500

    return render_template(
        "stock_detail.html",
        ticker=ticker,
        info=TICKERS[ticker],
        chart=chart,
        card=card,
        last_updated=last_updated,
        tickers=TICKERS,
    )


@app.route("/comparison")
def comparison():
    try:
        data = get_data()
        return_chart = chart_builder.build_cumulative_return_chart(data)
        heatmap = chart_builder.build_monthly_heatmap(data)
        correlation = chart_builder.build_correlation_matrix(data)
        last_updated = data_fetcher.get_last_updated()
    except Exception as e:
        return render_template("error.html", message=str(e)), 500

    return render_template(
        "comparison.html",
        return_chart=return_chart,
        heatmap=heatmap,
        correlation=correlation,
        last_updated=last_updated,
        tickers=TICKERS,
    )


@app.route("/api/chart/<chart_type>")
def api_chart(chart_type):
    try:
        data = get_data()
        if chart_type == "price":
            fig = chart_builder.build_price_evolution_chart(data)
        elif chart_type == "return":
            fig = chart_builder.build_cumulative_return_chart(data)
        elif chart_type == "heatmap":
            fig = chart_builder.build_monthly_heatmap(data)
        elif chart_type == "correlation":
            fig = chart_builder.build_correlation_matrix(data)
        else:
            return jsonify({"error": "chart_type inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(fig)


if __name__ == "__main__":
    app.run(debug=True)
