# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://localhost:5000)
python app.py
```

There are no lint or test scripts defined.

## Architecture

This is a Brazilian stock market dashboard built with Flask, tracking PETR4.SA, ITUB4.SA, and VALE3.SA via Yahoo Finance.

### Data flow

1. Routes in `app.py` call `get_data()`, which uses a module-level `_data_cache` dict to avoid repeated API calls.
2. `services/data_fetcher.py` downloads OHLCV data via yfinance and enriches it with `retorno_diario` (daily % return) and `retorno_acumulado` (YTD cumulative return).
3. `services/chart_builder.py` converts DataFrames to Plotly JSON via `_fig_to_json()`, which templates embed using Jinja2's `tojson` filter.

### Routes

| Route | Template | Description |
|-------|----------|-------------|
| `/` | `index.html` | Price cards + evolution chart |
| `/stock/<ticker>` | `stock_detail.html` | Candlestick + MA20 + volume |
| `/comparison` | `comparison.html` | Returns, heatmap, correlation tabs |
| `/api/chart/<chart_type>` | — | JSON API returning Plotly figure data |

### Configuration

`config.py` holds all tickers (`TICKERS` dict with name and color), `START_DATE`/`END_DATE`, and `CACHE_TTL` (1 hour). Add or remove tracked stocks here.

### Frontend

Templates extend `base.html`, which loads Bootstrap 5.3, Bootstrap Icons, and Plotly.js from CDN. `dashboard.js` handles responsive Plotly chart resizing on window resize.

## GitHub Repository

Repositório: https://github.com/Luizcruz75/stock-dashboard

### Sincronização automática

Todo arquivo editado ou criado pelo Claude Code é automaticamente commitado e enviado ao GitHub via hook `PostToolUse` configurado em `.claude/settings.json`.

O hook executa após cada operação de escrita (`Write|Edit`):
```bash
git add -A && git commit -m "Auto-update: <timestamp>" && git push
```

### Configuração inicial (se clonar em outra máquina)

```bash
git clone https://github.com/Luizcruz75/stock-dashboard.git
cd stock-dashboard
pip install -r requirements.txt
python app.py
```

O remote já está configurado com autenticação via token no repositório local. Se precisar reconfigurar:
```bash
git remote set-url origin https://<TOKEN>@github.com/Luizcruz75/stock-dashboard.git
```
