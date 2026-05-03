# 📈 Indian Stock Market Analytics Dashboard

Live dashboard for real-time Indian stock market analysis with AI-powered assistant.

## 🔗 Live App
[View on Streamlit Cloud](https://stock-market-analysis-lenykycpapfun5vdr5wzfw.streamlit.app/)

## 📊 Dashboard Features

### Pages
1. **Overview** — Live price, candlestick chart, volume, KPI cards (52W high/low, market cap)
2. **Technical Analysis** — Moving Averages (MA20/50/200), RSI, Bollinger Bands
3. **Price Prediction** — 30-day forecast using Facebook Prophet with confidence intervals
4. **Portfolio Tracker** — Multi-stock normalized returns comparison
5. **AI Stock Assistant** — Groq AI (Llama 3.3 70B) with real-time market context
6. **Price Alerts** — Set target prices and check if stocks have crossed them

## 🤖 AI Assistant
- Powered by Groq API (Llama 3.3 70B)
- Injected with live stock data at query time
- Answers questions like "Which stocks are oversold?" or "Compare Reliance and TCS"
- Disclaimer: Not financial advice

## 📦 Data
- Source: Yahoo Finance API (yfinance)
- Market: NSE India (National Stock Exchange)
- Stocks: Reliance, TCS, Infosys, HDFC Bank, Wipro, ICICI Bank, Bajaj Finance, Adani, Tata Motors, Asian Paints

## 🛠️ Tech Stack
- Python, Pandas, NumPy
- yfinance, Prophet, Scikit-learn
- Streamlit, Plotly
- Groq API (Llama 3.3 70B)

## ⚙️ Run Locally

```bash
git clone https://github.com/vedantmishra12/stock-market-analysis.git
cd stock-market-analysis
pip install -r requirements.txt
```

Create a `.env` file:
