import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import TICKERS


def _fig_to_json(fig):
    return json.loads(fig.to_json())


def build_price_evolution_chart(data):
    """Gráfico de linha: preço de fechamento das 3 ações."""
    fig = go.Figure()
    for ticker, info in TICKERS.items():
        df = data.get(ticker, pd.DataFrame())
        if df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            name=info["name"],
            line=dict(color=info["color"], width=2),
            hovertemplate=(
                f"<b>{info['name']}</b><br>"
                "Data: %{x|%d/%m/%Y}<br>"
                "Preço: R$ %{y:.2f}<extra></extra>"
            ),
        ))
    fig.update_layout(
        template="plotly_white",
        title="Evolução do Preço de Fechamento (2025)",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=60),
    )
    return _fig_to_json(fig)


def build_cumulative_return_chart(data):
    """Gráfico de retorno acumulado % das 3 ações (base 0% em jan/2025)."""
    fig = go.Figure()
    for ticker, info in TICKERS.items():
        df = data.get(ticker, pd.DataFrame())
        if df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["retorno_acumulado"],
            name=info["name"],
            line=dict(color=info["color"], width=2),
            fill="tozeroy",
            fillcolor=info["color"] + "22",
            hovertemplate=(
                f"<b>{info['name']}</b><br>"
                "Data: %{x|%d/%m/%Y}<br>"
                "Retorno: %{y:+.2f}%<extra></extra>"
            ),
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.update_layout(
        template="plotly_white",
        title="Retorno Acumulado % desde 01/01/2025",
        xaxis_title="Data",
        yaxis_title="Retorno (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=60),
    )
    return _fig_to_json(fig)


def build_candlestick_with_volume(df, ticker):
    """Candlestick OHLC + MA20 + volume para um único ticker."""
    info = TICKERS.get(ticker, {"name": ticker, "color": "#666666"})
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{info['name']} — Candlestick + MA20", "Volume"),
    )

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ), row=1, col=1)

    ma20 = df["Close"].rolling(window=20).mean()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=ma20,
        name="MA20",
        line=dict(color="#ff9800", width=1.5, dash="dot"),
        hovertemplate="MA20: R$ %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    colors = ["#26a69a" if c >= o else "#ef5350"
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume",
        marker_color=colors,
        showlegend=False,
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=80, b=60),
        height=600,
    )
    return _fig_to_json(fig)


def build_monthly_heatmap(data):
    """Heatmap de retorno mensal por ação."""
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    names = [TICKERS[t]["name"] for t in TICKERS]
    z = []
    text = []

    for ticker in TICKERS:
        df = data.get(ticker, pd.DataFrame())
        row = []
        row_text = []
        for month in range(1, 13):
            month_df = df[df.index.month == month] if not df.empty else pd.DataFrame()
            if month_df.empty or len(month_df) < 2:
                row.append(None)
                row_text.append("N/D")
            else:
                ret = (month_df["Close"].iloc[-1] / month_df["Close"].iloc[0] - 1) * 100
                row.append(ret)
                row_text.append(f"{ret:+.2f}%")
        z.append(row)
        text.append(row_text)

    fig = go.Figure(go.Heatmap(
        z=z,
        x=months,
        y=names,
        text=text,
        texttemplate="%{text}",
        colorscale="RdYlGn",
        zmid=0,
        colorbar=dict(title="Retorno %"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white",
        title="Retorno Mensal por Ação (2025)",
        margin=dict(l=100, r=20, t=60, b=60),
        height=300,
    )
    return _fig_to_json(fig)


def build_correlation_matrix(data):
    """Matriz de correlação dos retornos diários entre as 3 ações."""
    returns = {}
    for ticker, info in TICKERS.items():
        df = data.get(ticker, pd.DataFrame())
        if not df.empty:
            returns[info["name"]] = df["retorno_diario"].dropna()

    if len(returns) < 2:
        return {}

    ret_df = pd.DataFrame(returns).dropna()
    corr = ret_df.corr()

    names = list(corr.columns)
    z = corr.values.tolist()
    text = [[f"{v:.3f}" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=names,
        y=names,
        text=text,
        texttemplate="%{text}",
        colorscale="RdYlGn",
        zmin=-1, zmax=1, zmid=0,
        colorbar=dict(title="Correlação"),
        hovertemplate="<b>%{x} × %{y}</b><br>Correlação: %{text}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white",
        title="Correlação dos Retornos Diários",
        margin=dict(l=100, r=20, t=60, b=60),
        height=320,
    )
    return _fig_to_json(fig)
