# app.py — Stock Market Analytics Dashboard
import streamlit as st

st.set_page_config(
    page_title="Indian Stock Analytics",
    page_icon="📈",
    layout="wide"
)

# ── Animated Background ───────────────────────────────────
st.markdown("""
<style>
.stApp {
    background-image: url("https://raw.githubusercontent.com/vedantmishra12/stock-market-analysis/main/assets/background.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.85);
    z-index: 0;
}

.main .block-container {
    position: relative;
    z-index: 1;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/NSE-Logo.svg/2560px-NSE-Logo.svg.png", width=200)
st.sidebar.title("📈 Stock Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Overview",
    "📊 Technical Analysis",
    "🔮 Price Prediction",
    "💼 Portfolio Tracker",
    "🤖 AI Stock Assistant",
    "🔔 Price Alerts",
    "🧠 ML Price Predictor"
])

# ── Stock selector ─────────────────────────────────────────
POPULAR_STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Wipro": "WIPRO.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Asian Paints": "ASIANPAINT.NS"
}

selected_name = st.sidebar.selectbox("Select Stock", list(POPULAR_STOCKS.keys()))
ticker = POPULAR_STOCKS[selected_name]

period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# ── Load data ──────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_stock_data(ticker, period):
    import time
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            info = dict(stock.info)
            return df, info
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                return pd.DataFrame(), {}

df, info = load_stock_data(ticker, period)

if df is None or len(df) == 0:
    st.error("⚠️ Could not fetch stock data. Yahoo Finance rate limit reached. Please wait a few minutes and refresh.")
    st.stop()

# ── Helper ─────────────────────────────────────────────────
def dark_layout(fig):
    fig.update_layout(
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font_color='white'
    )
    return fig

# ══════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title(f"📈 {selected_name} ({ticker})")
    st.markdown("---")

    # KPI cards
    current_price = info.get('currentPrice', df['Close'].iloc[-1])
    prev_close    = info.get('previousClose', df['Close'].iloc[-2])
    change        = current_price - prev_close
    change_pct    = (change / prev_close) * 100
    market_cap    = info.get('marketCap', 0)
    volume        = info.get('volume', 0)
    week_high     = info.get('fiftyTwoWeekHigh', 0)
    week_low      = info.get('fiftyTwoWeekLow', 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"₹{current_price:,.2f}", f"{change_pct:+.2f}%")
    col2.metric("Market Cap", f"₹{market_cap/1e9:.1f}B")
    col3.metric("52W High", f"₹{week_high:,.2f}")
    col4.metric("52W Low", f"₹{week_low:,.2f}")

    st.markdown("---")

    # Price chart
    st.subheader("📉 Price History")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(dark_layout(fig), use_container_width=True)

    # Volume chart
    st.subheader("📊 Volume")
    fig2 = px.bar(df, x=df.index, y='Volume', color_discrete_sequence=['#00b4d8'])
    st.plotly_chart(dark_layout(fig2), use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — TECHNICAL ANALYSIS
# ══════════════════════════════════════════════════════════
elif page == "📊 Technical Analysis":
    st.title(f"📊 Technical Analysis — {selected_name}")
    st.markdown("---")

    # Moving averages
    df['MA20']  = df['Close'].rolling(20).mean()
    df['MA50']  = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='white')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'],  name='MA20',  line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'],  name='MA50',  line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200', line=dict(color='red')))
    fig.update_layout(title='Moving Averages')
    st.plotly_chart(dark_layout(fig), use_container_width=True)

    # RSI
    delta     = df['Close'].diff()
    gain      = delta.where(delta > 0, 0).rolling(14).mean()
    loss      = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs        = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')))
    fig3.add_hline(y=70, line_dash='dash', line_color='red',   annotation_text='Overbought')
    fig3.add_hline(y=30, line_dash='dash', line_color='green', annotation_text='Oversold')
    fig3.update_layout(title='RSI (14)', yaxis_range=[0, 100])
    st.plotly_chart(dark_layout(fig3), use_container_width=True)

    # Bollinger Bands
    df['BB_mid']   = df['Close'].rolling(20).mean()
    df['BB_upper'] = df['BB_mid'] + 2 * df['Close'].rolling(20).std()
    df['BB_lower'] = df['BB_mid'] - 2 * df['Close'].rolling(20).std()

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df.index, y=df['Close'],    name='Price',      line=dict(color='white')))
    fig4.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='Upper Band', line=dict(color='red',   dash='dash')))
    fig4.add_trace(go.Scatter(x=df.index, y=df['BB_mid'],   name='Mid Band',   line=dict(color='orange',dash='dash')))
    fig4.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='Lower Band', line=dict(color='green', dash='dash')))
    fig4.update_layout(title='Bollinger Bands')
    st.plotly_chart(dark_layout(fig4), use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — PRICE PREDICTION
# ══════════════════════════════════════════════════════════
elif page == "🔮 Price Prediction":
    st.title(f"🔮 Price Prediction — {selected_name}")
    st.markdown("---")
    st.info("Using Facebook Prophet for 30-day price forecast")

    try:
        from prophet import Prophet

        prophet_df = df[['Close']].reset_index()[['Date', 'Close']]
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)

        model = Prophet(daily_seasonality=True)
        model.fit(prophet_df)

        future   = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'],       name='Actual',   line=dict(color='white')))
        fig5.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat'],      name='Forecast', line=dict(color='cyan')))
        fig5.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat_upper'],name='Upper',    line=dict(color='green', dash='dash')))
        fig5.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat_lower'],name='Lower',    line=dict(color='red',   dash='dash')))
        fig5.update_layout(title='30-Day Price Forecast')
        st.plotly_chart(dark_layout(fig5), use_container_width=True)

        st.subheader("📋 Forecast Table (Next 30 Days)")
        forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)
        forecast_display.columns = ['Date', 'Predicted Price', 'Lower Bound', 'Upper Bound']
        forecast_display = forecast_display.round(2)
        st.dataframe(forecast_display, use_container_width=True)

    except Exception as e:
        st.error(f"Prediction error: {e}")

# ══════════════════════════════════════════════════════════
# PAGE 4 — PORTFOLIO TRACKER
# ══════════════════════════════════════════════════════════
elif page == "💼 Portfolio Tracker":
    st.title("💼 Portfolio Tracker")
    st.markdown("---")

    selected_stocks = st.multiselect(
        "Select stocks to compare",
        list(POPULAR_STOCKS.keys()),
        default=["Reliance Industries", "TCS", "Infosys"]
    )

    if selected_stocks:
        @st.cache_data(ttl=300)
        def load_multiple(tickers, period):
            dfs = {}
            for name, t in tickers.items():
                d = yf.Ticker(t).history(period=period)
                dfs[name] = d['Close']
            return pd.DataFrame(dfs)

        selected_tickers = {k: POPULAR_STOCKS[k] for k in selected_stocks}
        portfolio_df = load_multiple(selected_tickers, period)

        # Normalized returns
        normalized = (portfolio_df / portfolio_df.iloc[0]) * 100

        st.subheader("📈 Normalized Price Performance (Base 100)")
        fig6 = px.line(normalized, x=normalized.index, y=normalized.columns)
        st.plotly_chart(dark_layout(fig6), use_container_width=True)

        # Returns
        st.subheader("📊 Total Returns (%)")
        returns = ((portfolio_df.iloc[-1] - portfolio_df.iloc[0]) / portfolio_df.iloc[0] * 100).round(2)
        returns_df = returns.reset_index()
        returns_df.columns = ['Stock', 'Return (%)']
        fig7 = px.bar(returns_df, x='Stock', y='Return (%)',
                      color='Return (%)', color_continuous_scale='RdYlGn')
        st.plotly_chart(dark_layout(fig7), use_container_width=True)

        st.subheader("📋 Summary Table")
        st.dataframe(returns_df, use_container_width=True)
# ══════════════════════════════════════════════════════════
# PAGE 5 — AI STOCK ASSISTANT
# ══════════════════════════════════════════════════════════
elif page == "🤖 AI Stock Assistant":
    st.title("🤖 AI Stock Assistant")
    st.markdown("### Powered by Groq AI")
    st.markdown("---")
    st.warning("⚠️ This is for educational purposes only. Not financial advice.")

    from groq import Groq
    from dotenv import load_dotenv
    import os
    load_dotenv()

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Load current stock context
    @st.cache_data(ttl=300)
    def get_market_context():
        context = {}
        for name, t in POPULAR_STOCKS.items():
            try:
                stock = yf.Ticker(t)
                info  = stock.info
                hist  = stock.history(period='1mo')

                current = info.get('currentPrice', hist['Close'].iloc[-1])
                prev    = info.get('previousClose', hist['Close'].iloc[-2])
                change  = ((current - prev) / prev * 100)

                delta = hist['Close'].diff()
                gain  = delta.where(delta > 0, 0).rolling(14).mean()
                loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi   = (100 - (100 / (1 + gain/loss))).iloc[-1]

                context[name] = {
                    'price': current,
                    'change_pct': change,
                    'rsi': round(rsi, 1),
                    'week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                    'week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                    'market_cap': info.get('marketCap', 0)
                }
            except:
                pass
        return context

    market_context = get_market_context()

    context_str = "Current Indian Stock Market Data:\n"
    for name, data in market_context.items():
        context_str += f"{name}: Price ₹{data['price']:,.2f} ({data['change_pct']:+.2f}%), RSI {data['rsi']}, 52W High ₹{data['week_high']}, 52W Low ₹{data['week_low']}\n"

    # Chat history
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []

    # Chat input
    user_input = st.chat_input("Ask anything about Indian stocks...")

    if user_input:
        st.session_state.ai_chat_history.append({
            "role": "user",
            "content": user_input
        })

        messages = [
            {
                "role": "system",
                "content": f"""You are a knowledgeable Indian stock market assistant. 
You have access to real-time data for major NSE stocks.
Always clarify you are not a SEBI registered advisor and cannot give financial advice.
Keep responses concise and data-driven.

{context_str}"""
            }
        ] + st.session_state.ai_chat_history

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=500
            )
            reply = response.choices[0].message.content

        st.session_state.ai_chat_history.append({
            "role": "assistant",
            "content": reply
        })

    # Display chat
    for msg in st.session_state.ai_chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    if not st.session_state.ai_chat_history:
        st.info("👋 Try asking:\n- 'Which stock has the highest RSI right now?'\n- 'Compare Reliance and TCS'\n- 'What does RSI mean?'\n- 'Which stocks are oversold?'")

# ══════════════════════════════════════════════════════════
# PAGE 6 — PRICE ALERTS
# ══════════════════════════════════════════════════════════
elif page == "🔔 Price Alerts":
    st.title("🔔 Price Alerts")
    st.markdown("### Set target prices and get notified")
    st.markdown("---")

    # Initialize alerts in session state
    if 'alerts' not in st.session_state:
        st.session_state.alerts = {}

    # Add new alert
    st.subheader("➕ Add New Alert")
    col1, col2, col3 = st.columns(3)

    with col1:
        alert_stock = st.selectbox("Select Stock", list(POPULAR_STOCKS.keys()), key="alert_stock")
    with col2:
        alert_type = st.selectbox("Alert Type", ["Above", "Below"], key="alert_type")
    with col3:
        alert_price = st.number_input("Target Price (₹)", min_value=0.0, value=1000.0, step=10.0)

    if st.button("🔔 Set Alert", use_container_width=True):
        alert_key = f"{alert_stock}_{alert_type}_{alert_price}"
        st.session_state.alerts[alert_key] = {
            "stock": alert_stock,
            "ticker": POPULAR_STOCKS[alert_stock],
            "type": alert_type,
            "target": alert_price
        }
        st.success(f"Alert set: {alert_stock} {alert_type} ₹{alert_price:,.2f}")

    st.markdown("---")

    # Check and display alerts
    if st.session_state.alerts:
        st.subheader("📋 Your Alerts")

        if st.button("🔄 Check All Alerts", use_container_width=True):
            for key, alert in st.session_state.alerts.items():
                try:
                    stock     = yf.Ticker(alert['ticker'])
                    current   = stock.info.get('currentPrice', 0)
                    target    = alert['target']
                    triggered = (alert['type'] == 'Above' and current >= target) or \
                                (alert['type'] == 'Below' and current <= target)

                    if triggered:
                        st.error(f"🚨 **ALERT TRIGGERED** — {alert['stock']} is at ₹{current:,.2f} ({alert['type']} target ₹{target:,.2f})")
                    else:
                        diff = current - target if alert['type'] == 'Above' else target - current
                        st.info(f"⏳ {alert['stock']} — Current ₹{current:,.2f} | Target {alert['type']} ₹{target:,.2f} | ₹{diff:,.2f} away")

                except:
                    st.warning(f"Could not fetch data for {alert['stock']}")

        # Show alert table
        alerts_data = []
        for key, alert in st.session_state.alerts.items():
            alerts_data.append({
                "Stock": alert['stock'],
                "Type": alert['type'],
                "Target (₹)": alert['target']
            })

        st.dataframe(pd.DataFrame(alerts_data), use_container_width=True)

        # Clear alerts
        if st.button("🗑️ Clear All Alerts", use_container_width=True):
            st.session_state.alerts = {}
            st.success("All alerts cleared.")
    else:
        st.info("No alerts set yet. Add one above.")

# ══════════════════════════════════════════════════════════
# PAGE 7 — ML PRICE PREDICTOR
# ══════════════════════════════════════════════════════════
elif page == "🧠 ML Price Predictor":
    st.title("🧠 Live ML Price Direction Predictor")
    st.markdown("### Model trains on live data every time you run a prediction")
    st.markdown("---")
    st.warning("⚠️ For educational purposes only. Not financial advice.")

    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.preprocessing import StandardScaler
    import warnings
    warnings.filterwarnings('ignore')

    predict_stock = st.selectbox("Select Stock to Predict", list(POPULAR_STOCKS.keys()), key="predict_stock")
    predict_ticker = POPULAR_STOCKS[predict_stock]

    if st.button("🚀 Train Model & Predict", use_container_width=True):
        with st.spinner("Fetching live data and training model..."):

            # ── 1. Fetch live data ─────────────────────────────
            raw = yf.Ticker(predict_ticker).history(period="2y")
            raw = raw.dropna()

            # ── 2. Feature Engineering ─────────────────────────
            df_ml = raw.copy()

            # Price features
            df_ml['return_1d']  = df_ml['Close'].pct_change(1)
            df_ml['return_5d']  = df_ml['Close'].pct_change(5)
            df_ml['return_10d'] = df_ml['Close'].pct_change(10)

            # Moving averages
            df_ml['MA10']  = df_ml['Close'].rolling(10).mean()
            df_ml['MA20']  = df_ml['Close'].rolling(20).mean()
            df_ml['MA50']  = df_ml['Close'].rolling(50).mean()
            df_ml['MA_cross_10_20'] = df_ml['MA10'] - df_ml['MA20']
            df_ml['MA_cross_20_50'] = df_ml['MA20'] - df_ml['MA50']

            # RSI
            delta = df_ml['Close'].diff()
            gain  = delta.where(delta > 0, 0).rolling(14).mean()
            loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df_ml['RSI'] = 100 - (100 / (1 + gain / loss))

            # Volatility
            df_ml['volatility'] = df_ml['Close'].rolling(10).std()

            # Volume change
            df_ml['volume_change'] = df_ml['Volume'].pct_change()

            # Bollinger Band position
            bb_mid   = df_ml['Close'].rolling(20).mean()
            bb_std   = df_ml['Close'].rolling(20).std()
            df_ml['bb_position'] = (df_ml['Close'] - bb_mid) / (2 * bb_std)

            # High/Low range
            df_ml['hl_range'] = (df_ml['High'] - df_ml['Low']) / df_ml['Close']

            # ── 3. Target: will price go up tomorrow? ──────────
            df_ml['target'] = (df_ml['Close'].shift(-1) > df_ml['Close']).astype(int)

            # ── 4. Clean ───────────────────────────────────────
            features = [
                'return_1d', 'return_5d', 'return_10d',
                'MA_cross_10_20', 'MA_cross_20_50',
                'RSI', 'volatility', 'volume_change',
                'bb_position', 'hl_range'
            ]
            df_ml = df_ml.dropna()
            X = df_ml[features]
            y = df_ml['target']

            # ── 5. Train/test split (time-aware) ───────────────
            split = int(len(df_ml) * 0.8)
            X_train, X_test = X.iloc[:split], X.iloc[split:]
            y_train, y_test = y.iloc[:split], y.iloc[split:]

            # ── 6. Scale ───────────────────────────────────────
            scaler = StandardScaler()
            X_train_sc = scaler.fit_transform(X_train)
            X_test_sc  = scaler.transform(X_test)

            # ── 7. Train ───────────────────────────────────────
            model_ml = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                random_state=42
            )
            model_ml.fit(X_train_sc, y_train)

            # ── 8. Evaluate ────────────────────────────────────
            preds    = model_ml.predict(X_test_sc)
            accuracy = accuracy_score(y_test, preds)

            # ── 9. Predict tomorrow ────────────────────────────
            latest_features = scaler.transform(X.iloc[[-1]])
            tomorrow_pred   = model_ml.predict(latest_features)[0]
            tomorrow_proba  = model_ml.predict_proba(latest_features)[0]

        # ── Display Results ────────────────────────────────────
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Model Accuracy", f"{accuracy*100:.1f}%")
        col2.metric("Training Samples", f"{len(X_train)}")
        col3.metric("Test Samples", f"{len(X_test)}")

        st.markdown("---")
        st.subheader("🔮 Tomorrow's Prediction")

        if tomorrow_pred == 1:
            st.success(f"📈 **{predict_stock} is predicted to go UP tomorrow**")
        else:
            st.error(f"📉 **{predict_stock} is predicted to go DOWN tomorrow**")

        up_prob   = tomorrow_proba[1] * 100
        down_prob = tomorrow_proba[0] * 100

        col4, col5 = st.columns(2)
        col4.metric("Probability UP ↑", f"{up_prob:.1f}%")
        col5.metric("Probability DOWN ↓", f"{down_prob:.1f}%")

        # Probability bar
        proba_df = pd.DataFrame({
            'Direction': ['UP ↑', 'DOWN ↓'],
            'Probability': [up_prob, down_prob]
        })
        fig_proba = px.bar(
            proba_df, x='Direction', y='Probability',
            color='Direction',
            color_discrete_map={'UP ↑': '#00b894', 'DOWN ↓': '#d63031'},
            title='Prediction Confidence'
        )
        st.plotly_chart(dark_layout(fig_proba), use_container_width=True)

        # Feature importance
        st.subheader("📊 Feature Importance")
        importance_df = pd.DataFrame({
            'Feature': features,
            'Importance': model_ml.feature_importances_
        }).sort_values('Importance', ascending=False)

        fig_imp = px.bar(
            importance_df, x='Feature', y='Importance',
            color='Importance', color_continuous_scale='Blues',
            title='What drove this prediction'
        )
        st.plotly_chart(dark_layout(fig_imp), use_container_width=True)

        # Recent price context
        st.subheader("📉 Recent Price Context")
        fig_ctx = go.Figure()
        fig_ctx.add_trace(go.Candlestick(
            x=raw.index[-60:],
            open=raw['Open'][-60:],
            high=raw['High'][-60:],
            low=raw['Low'][-60:],
            close=raw['Close'][-60:],
            name='Price'
        ))
        fig_ctx.update_layout(
            xaxis_rangeslider_visible=False,
            title='Last 60 Days'
        )
        st.plotly_chart(dark_layout(fig_ctx), use_container_width=True)

        st.markdown("---")
        st.caption("Model trained fresh on live yfinance data. Accuracy reflects historical test set performance only.")

# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit & Yahoo Finance | Data is delayed")