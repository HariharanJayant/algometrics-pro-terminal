import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import sqlite3
from sklearn.ensemble import RandomForestRegressor

# --- MODULE 1: ENTERPRISE IDENTITY SECURITY GATEHOUSE ---
# Universal fallback verification to see if the user object contains active credentials
is_authenticated = False
try:
    if hasattr(st, "user") and st.user.is_logged_in:
        is_authenticated = True
    elif hasattr(st, "experimental_user") and hasattr(st.experimental_user, "is_logged_in") and st.experimental_user.is_logged_in:
        is_authenticated = True
except Exception:
    pass

if not is_authenticated:
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1 style="color: #101828; font-size: 2.2rem; font-weight: 700;">⚡ AlgoMetrics Pro Workstation</h1>
            <p style="color: #475467; font-size: 1.1rem; margin-bottom: 30px;">Institutional Quantitative Trading & Position Architecture Suite</p>
            <div style="display: inline-block; padding: 24px; background: white; border: 1px solid #eaecf0; border-radius: 12px; box-shadow: 0 4px 6px rgba(16,24,40,0.03);">
                <p style="color: #667085; font-size: 0.9rem; margin-bottom: 20px;">🔒 Secure Access Control Layer Active</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("🔑 Log In to Workstation Terminal", on_click=st.login, use_container_width=True)
    st.stop()  # Aborts compilation immediately for unauthenticated traffic

# Extract user email safely based on available object structure
user_email = "Internal Staff"
try:
    if hasattr(st, "user") and hasattr(st.user, "email"):
        user_email = st.user.email
    elif hasattr(st, "experimental_user") and "email" in st.experimental_user:
        user_email = st.experimental_user["email"]
except Exception:
    pass

# --- SYSTEM DATABASE INITIALIZATION (SQLite Layer) ---
def init_db():
    conn = sqlite3.connect("trading_workstation.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            direction TEXT,
            entry_price REAL,
            stop_loss REAL,
            target_price REAL,
            shares INTEGER,
            capital_deployed REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- PAGE INITIALIZATION ---
st.set_page_config(
    page_title="AlgoMetrics Pro Workstation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM LIGHT SYSTEM STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #fafbfc; color: #1d2939; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e4e7ec; }
    .premium-card { background-color: #ffffff; border: 1px solid #eaecf0; border-radius: 12px; padding: 20px 24px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05); }
    .stat-label { color: #667085; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.75px; margin-bottom: 4px; }
    .stat-value { color: #101828; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 1.75rem; font-weight: 700; }
    .alert-banner { padding: 12px 16px; border-radius: 8px; font-weight: 600; margin-bottom: 16px; border: 1px solid; }
    .alert-high { background-color: #fef3f2; color: #b42318; border-color: #fda29b; }
    input { background-color: #ffffff !important; border: 1px solid #d0d5dd !important; color: #101828 !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL NAVIGATION SEPARATION ---
app_mode = st.tabs(["📊 Individual Asset Terminal", "🌍 Macro Market Radar", "📋 Active Order Log"])

# ==============================================================================
# TAB 1: INDIVIDUAL ASSET TERMINAL
# ==============================================================================
with app_mode[0]:
    st.title("⚡ AlgoMetrics Pro Terminal")
    st.markdown(f"<p style='color: #475467; font-size: 1.05rem; margin-top:-15px;'>Enterprise Market Structure Mapping & Multi-Indicator Quant Suite</p>", unsafe_allow_html=True)
    st.divider()

    # --- SIDEBAR CONTROL INTERFACE ---
    st.sidebar.markdown(f"👤 **User Identity:** `{user_email}`")
    if st.sidebar.button("🚪 Secure System Sign Out"):
        st.logout()

    st.sidebar.divider()
    st.sidebar.markdown("### 🎛️ SYSTEM CONTROLS")
    ticker_input = st.sidebar.text_input("ASSET TICKER SYMBOL", value="NVDA").upper()

    if st.sidebar.button("🧹 Clear System Memory Cache"):
        st.cache_data.clear()
        st.toast("System cache purged successfully.")

    with st.sidebar.expander("💼 RISK ENGINE ASSIGNMENT", expanded=True):
        account_size = st.number_input("ACCOUNT BALANCE ($)", value=10000, step=1000)
        risk_method = st.selectbox("RISK MODEL", ["Percentage Basis", "Fixed Dollar Basis"])
        if risk_method == "Percentage Basis":
            risk_pct = st.slider("MAX TRADE RISK (%)", 0.25, 5.0, 1.0, 0.25)
            max_loss = account_size * (risk_pct / 100)
        else:
            max_loss = st.number_input("FIXED RISK AMOUNT ($)", value=100, step=25)

    with st.sidebar.expander("💸 COMMISSIONS & SLIPPAGE SCALER", expanded=False):
        per_share_fee = st.number_input("Broker Fee per Share ($)", value=0.005, format="%.3f")
        slippage_ticks = st.slider("Estimated Slippage (Ticks)", 0, 5, 1)

    with st.sidebar.expander("🔬 SIGNAL HORIZON TUNING", expanded=False):
        lookback = st.slider("LOOKBACK FRAME (DAYS)", 30, 365, 120)
        sensitivity = st.slider("PIVOT STRENGTH MATRIX", 3, 15, 5)

    st.sidebar.divider()
    st.sidebar.markdown("### 📸 CHART INGESTION PIPELINE")
    uploaded_screenshot = st.sidebar.file_uploader("DROP LIVE SCREENSHOT FILE HERE", type=["png", "jpg", "jpeg"])

    # --- MACHINE LEARNING VOLATILITY PREDICTION ENGINE ---
    def calculate_ml_volatility_prediction(df):
        try:
            df_ml = df.copy()
            df_ml['HL_Range'] = df_ml['High'] - df_ml['Low']
            df_ml['Target_Next_Vol'] = df_ml['HL_Range'].shift(-1)
            
            df_ml['Features_Lag1'] = df_ml['HL_Range'].shift(1)
            df_ml['Features_Lag2'] = df_ml['HL_Range'].shift(2)
            df_ml.dropna(inplace=True)
            
            X = df_ml[['Features_Lag1', 'Features_Lag2']].values
            y = df_ml['Target_Next_Vol'].values
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            latest_features = np.array([[df_ml['HL_Range'].iloc[-1], df_ml['HL_Range'].iloc[-2]]])
            predicted_range = model.predict(latest_features)[0]
            return float(predicted_range)
        except:
            return float(df['High'].iloc[-1] - df['Low'].iloc[-1])

    # --- MULTI-TIMEFRAME CONFLUENCE PROCESSOR ---
    @st.cache_data(ttl=60)
    def fetch_multi_timeframe_confluence(ticker):
        try:
            df_15m = yf.download(ticker, period="5d", interval="15m")
            if df_15m.empty: return "UNKNOWN"
            if isinstance(df_15m.columns, pd.MultiIndex): df_15m.columns = [col[0] for col in df_15m.columns]
            
            ema20_15m = df_15m['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            current_price = df_15m['Close'].iloc[-1]
            return "BULLISH" if current_price > ema20_15m else "BEARISH"
        except: return "UNKNOWN"

    @st.cache_data(ttl=60)
    def analyze_institutional_flow(ticker, days, window):
        try:
            start_date = datetime.now() - timedelta(days=days + 60)
            df = yf.download(ticker, start=start_date, end=datetime.now(), interval="1d")
            if df.empty: return None, "Asset Ticker Invalidation or no data found."
            if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
            else: df.columns = [str(col) for col in df.columns]
            
            df_full = df.copy()
            delta = df_full['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-9)
            df_full['RSI'] = 100 - (100 / (1 + rs))
            
            exp1 = df_full['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df_full['Close'].ewm(span=26, adjust=False).mean()
            df_full['MACD'] = exp1 - exp2
            df_full['Signal_Line'] = df_full['MACD'].ewm(span=9, adjust=False).mean()
            
            high_low = df_full['High'] - df_full['Low']
            high_cp = np.abs(df_full['High'] - df_full['Close'].shift())
            low_cp = np.abs(df_full['Low'] - df_full['Close'].shift())
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df_full['ATR'] = tr.rolling(window=14).mean()
            df_full['EMA20'] = df_full['Close'].ewm(span=20, adjust=False).mean()
            
            df = df_full.tail(days).copy()
            df['Is_Peak'] = 0
            df['Is_Valley'] = 0
            for i in range(window, len(df) - window):
                high_range = df['High'].iloc[i-window:i+window+1]
                low_range = df['Low'].iloc[i-window:i+window+1]
                if float(df['High'].iloc[i]) == float(high_range.max()): df.loc[df.index[i], 'Is_Peak'] = 1
                if float(df['Low'].iloc[i]) == float(low_range.min()): df.loc[df.index[i], 'Is_Valley'] = 1
            
            peaks = df[df['Is_Peak'] == 1]['High'].astype(float).tolist()
            valleys = df[df['Is_Valley'] == 1]['Low'].astype(float).tolist()
            
            cur_p = float(df['Close'].iloc[-1])
            trend = "BULLISH" if cur_p > float(df_full['EMA20'].iloc[-1]) else "BEARISH"
            
            formula_signal = "HOLD"
            if trend == "BULLISH" and float(df['RSI'].iloc[-1]) < 68 and float(df['MACD'].iloc[-1]) > float(df['Signal_Line'].iloc[-1]):
                formula_signal = "BUY TRIGGER"
            elif trend == "BEARISH" and float(df['RSI'].iloc[-1]) > 32 and float(df['MACD'].iloc[-1]) < float(df['Signal_Line'].iloc[-1]):
                formula_signal = "SELL TRIGGER"
                
            return {
                "df": df, "price": cur_p, "peaks": peaks, "valleys": valleys, 
                "trend": trend, "atr": float(df['ATR'].iloc[-1]), 
                "rsi": float(df['RSI'].iloc[-1]), "macd": float(df['MACD'].iloc[-1]), 
                "signal": formula_signal, "volume": float(df['Volume'].iloc[-1]),
                "avg_volume": float(df['Volume'].mean())
            }, None
        except Exception as e: return None, str(e)

    if uploaded_screenshot:
        if ticker_input:
            with st.status("Computing Advanced Models...", expanded=False):
                data, error = analyze_institutional_flow(ticker_input, lookback, sensitivity)
                short_term_trend = fetch_multi_timeframe_confluence(ticker_input)
            if error: st.error(f"Error: {error}")
            elif data:
                ml_predicted_range = calculate_ml_volatility_prediction(data["df"])
                
                if data["trend"] == short_term_trend:
                    st.success(f"⛓️ **MULTI-TIMEFRAME CONFLUENCE LOCKED:** Daily Trend and Intraday 15m Trend are both fully **{data['trend']}**.")
                else:
                    st.warning(f"⚠️ **TIMEFRAME DIVERGENCE DETECTED:** Daily Trend is {data['trend']}, but Intraday 15m Frame is shifting {short_term_trend}.")

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="premium-card"><p class="stat-label">Last Price</p><p class="stat-value">${data["price"]:,.2f}</p></div>', unsafe_allow_html=True)
                with c2:
                    sig_color = "color: #039855;" if "BUY" in data["signal"] else ("color: #d92d20;" if "SELL" in data["signal"] else "color: #667085;")
                    st.markdown(f'<div class="premium-card"><p class="stat-label">Formula Indicator</p><p class="stat-value" style="{sig_color}">{data["signal"]}</p></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="premium-card"><p class="stat-label">ML Predicted Range</p><p class="stat-value">${ml_predicted_range:.2f}</p></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="premium-card"><p class="stat-label">Volatility Noise (ATR)</p><p class="stat-value">${data["atr"]:.2f}</p></div>', unsafe_allow_html=True)

                st.write("##")
                left_col, right_col = st.columns([1.1, 0.9], gap="large")
                with left_col:
                    st.markdown("### 📈 Interactive Price Engine")
                    labels = [d.strftime('%Y-%m-%d') for d in data["df"].index]
                    close_prices = data["df"]['Close'].round(2).tolist()
                    ema20_values = data["df"]['EMA20'].round(2).tolist()

                    js_chart_html = f"""
                    <html>
                    <head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
                    <body style="margin:0; padding:0; background-color: #fafbfc;">
                        <canvas id="mainChart" style="width:100%; height:320px;"></canvas>
                        <script>
                            const ctx = document.getElementById('mainChart').getContext('2d');
                            new Chart(ctx, {{
                                type: 'line',
                                data: {{
                                    labels: {labels},
                                    datasets: [
                                        {{ label: 'Close Price ($)', data: {close_prices}, borderColor: '#101828', borderWidth: 2, pointRadius: 0, fill: false }},
                                        {{ label: 'EMA 20 Baseline', data: {ema20_values}, borderColor: '#2563eb', borderWidth: 1.5, borderDash: [5, 5], pointRadius: 0, fill: false }}
                                    ]
                                }},
                                options: {{ responsive: true, maintainAspectRatio: false, scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ color: '#eaecf0' }} }} }} }}
                            }});
                        </script>
                    </body>
                    </html>
                    """
                    components.html(js_chart_html, height=330)

                    st.markdown("### 📸 Image Engine Interface Reference")
                    st.image(Image.open(uploaded_screenshot), use_container_width=True)
                    
                    # --- PERFORMANCE BACKTESTER HUB ---
                    st.markdown("### 🔬 Quantitative Performance Backtester (1-Year Walk-Forward)")
                    with st.container(border=True):
                        df_bt = data["df"].copy()
                        initial_equity = float(account_size)
                        current_equity = initial_equity
                        equity_curve = [initial_equity]
                        total_trades = 0
                        winning_trades = 0
                        
                        for idx in range(15, len(df_bt)):
                            row_prev = df_bt.iloc[idx-1]
                            row_curr = df_bt.iloc[idx]
                            
                            if row_prev['Close'] > row_prev['EMA20'] and row_prev['RSI'] < 65:
                                trade_gain = (row_curr['Close'] - row_prev['Close']) / row_prev['Close']
                                current_equity *= (1 + trade_gain)
                                total_trades += 1
                                if trade_gain > 0: winning_trades += 1
                            equity_curve.append(round(current_equity, 2))
                        
                        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
                        
                        bt_c1, bt_c2, bt_c3 = st.columns(3)
                        bt_c1.metric("Simulated Win Rate", f"{win_rate:.1f}%")
                        bt_c2.metric("Total Executions", f"{total_trades} Trades")
                        bt_c3.metric("End Portfolio Value", f"${current_equity:,.2f}")
                        
                        bt_labels = list(range(len(equity_curve)))
                        js_bt_html = f"""
                        <html>
                        <head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
                        <body>
                            <canvas id="btChart" style="width:100%; height:140px;"></canvas>
                            <script>
                                const ctx2 = document.getElementById('btChart').getContext('2d');
                                new Chart(ctx2, {{
                                    type: 'line',
                                    data: {{
                                        labels: {bt_labels},
                                        datasets: [{{ label: 'Growth Vector ($)', data: {equity_curve}, borderColor: '#039855', borderWidth: 2, pointRadius: 0, fill: true, backgroundColor: 'rgba(3, 152, 85, 0.05)' }}]
                                    }},
                                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ grid: {{ color: '#eaecf0' }} }} }} }}
                                }});
                            </script>
                        </body>
                        </html>
                        """
                        components.html(js_bt_html, height=145)

                with right_col:
                    st.markdown("### 📋 Tactical Command Dashboard")
                    with st.container(border=True):
                        st.markdown("🛠️ **Dynamic Volatility Buffer Tuning**")
                        atr_multiplier = st.slider("Volatility Buffer Multiplier (ATR Scaler)", 1.0, 3.5, 1.5, 0.1)

                    resistances = [p for p in data["peaks"] if p > data["price"]]
                    supports = [v for v in data["valleys"] if v < data["price"]]
                    ceiling = min(resistances) if resistances else data["price"] * 1.05
                    floor = max(supports) if supports else data["price"] * 0.95
                    
                    entry = floor * 1.002 if data["trend"] == "BULLISH" else ceiling * 0.998
                    tp1 = ceiling if data["trend"] == "BULLISH" else floor
                    sl = entry - (data["atr"] * atr_multiplier) if data["trend"] == "BULLISH" else entry + (data["atr"] * atr_multiplier)
                    
                    risk_amt_per_share = abs(entry - sl)
                    shares = int(max_loss / risk_amt_per_share) if risk_amt_per_share > 0 else 0
                    total_fees = shares * per_share_fee
                    total_capital = (shares * entry) + total_fees
                    rr = abs(tp1 - entry) / risk_amt_per_share if risk_amt_per_share > 0 else 0

                    with st.container(border=True):
                        st.markdown(f"#### {data['trend']} LIMIT ALLOCATION")
                        st.write(f"🔹 **Entry Trigger:** `${entry:,.2f}`")
                        st.write(f"🎯 **Profit Target:** `${tp1:,.2f}` | 🛑 **Stop Loss:** `${sl:,.2f}`")
                        st.write(f"📦 **Volume Target:** `{shares}` Units | 📊 **Dynamic R:R:** `1 : {rr:.2f}`")
                        
                        st.divider()
                        # --- SQL DATABASE WRITER ---
                        if st.button("💾 Log Order Configuration to SQLite Database", use_container_width=True):
                            db_conn = sqlite3.connect("trading_workstation.db")
                            db_cursor = db_conn.cursor()
                            db_cursor.execute("""
                                INSERT INTO order_logs (timestamp, ticker, direction, entry_price, stop_loss, target_price, shares, capital_deployed)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ticker_input, data['trend'], entry, sl, tp1, shares, total_capital))
                            db_conn.commit()
                            db_conn.close()
                            st.toast("🎯 Trading plan appended to permanent local ledger!")
        else: st.info("Assign a specific asset ticker profile in the sidebar configs.")
    else:
        st.write("##")
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>Terminal Core Standby</h3>", unsafe_allow_html=True)

# ==============================================================================
# TAB 2: MACRO MARKET RADAR
# ==============================================================================
with app_mode[1]:
    st.title("🌍 Global Macro Market Radar")
    st.markdown("""
        <div class="alert-banner alert-high">
            ⚠️ <b>CRITICAL SYSTEM ALERT: HIGH VOLATILITY ECONOMIC RISK WINDOW ACTIVE</b><br>
            Federal Reserve FOMC Interest Rate Decision and Economic Projections release scheduled within this 24-hour cycle. 
        </div>
    """, unsafe_allow_html=True)
    
    major_markets = {"S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT"}

    @st.cache_data(ttl=60)
    def fetch_macro_radar_matrix():
        radar_results = {}
        for market_name, symbol in major_markets.items():
            try:
                df = yf.download(symbol, start=datetime.now() - timedelta(days=90), end=datetime.now(), interval="1d")
                if df.empty: continue
                if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
                
                cur_price = float(df['Close'].iloc[-1])
                prev_price = float(df['Close'].iloc[-2])
                session_change = ((cur_price - prev_price) / prev_price) * 100
                close_history = df['Close'].round(2).tolist()
                
                radar_results[market_name] = {"price": cur_price, "change": session_change, "history": close_history}
            except: continue
        return radar_results

    macro_matrix = fetch_macro_radar_matrix()
    if macro_matrix:
        grid_cols = st.columns(4)
        for i, (m_name, m_data) in enumerate(macro_matrix.items()):
            with grid_cols[i]:
                with st.container(border=True):
                    st.markdown(f"### {m_name}")
                    st.metric("Index Level", f"{m_data['price']:,.2f}", f"{m_data['change']:+.2f}%")
                    
                    line_color = '#039855' if m_data['change'] >= 0 else '#d92d20'
                    macro_js_html = f"""
                    <html>
                    <head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
                    <body style="margin:0; padding:0; background-color: transparent;">
                        <canvas id="miniChart_{i}" style="width:100%; height:100px;"></canvas>
                        <script>
                            const ctx = document.getElementById('miniChart_{i}').getContext('2d');
                            new Chart(ctx, {{
                                type: 'line',
                                data: {{
                                    labels: Array({len(m_data['history'])}).fill(''),
                                    datasets: [{{ data: {m_data['history']}, borderColor: '{line_color}', borderWidth: 1.5, pointRadius: 0, fill: false }}]
                                }},
                                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: false }} }} }}
                            }});
                        </script>
                    </body>
                    </html>
                    """
                    components.html(macro_js_html, height=110)

        # --- SECTOR CORRELATION HEATMAP MATRIX ---
        st.write("##")
        st.markdown("### 🧮 Technology & Sector Asset Inter-Correlation Matrix (Python 3.14 Safe Generation)")
        
        @st.cache_data(ttl=300)
        def generate_correlation_matrix_data():
            tickers = ["NVDA", "AMD", "AAPL", "MSFT", "QQQ", "SPY"]
            start_date = datetime.now() - timedelta(days=60)
            df_assets = yf.download(tickers, start=start_date, end=datetime.now())['Close']
            if isinstance(df_assets.columns, pd.MultiIndex):
                df_assets.columns = [col[0] for col in df_assets.columns]
            corr_df = df_assets.corr().round(2)
            return tickers, corr_df.values.tolist()

        try:
            corr_labels, corr_values = generate_correlation_matrix_data()
            
            html_table = "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; font-size: 0.9rem;'>"
            html_table += "<tr><th style='padding: 12px; border: 1px solid #eaecf0; background-color: #f9fafb;'>Asset</th>"
            for label in corr_labels:
                html_table += f"<th style='padding: 12px; border: 1px solid #eaecf0; background-color: #f9fafb;'>{label}</th>"
            html_table += "</tr>"
            
            for r_idx, row_name in enumerate(corr_labels):
                html_table += f"<tr><td style='padding: 12px; border: 1px solid #eaecf0; font-weight: 600; background-color: #f9fafb;'>{row_name}</td>"
                for c_idx, val in enumerate(corr_values[r_idx]):
                    alpha = abs(val)
                    bg_color = f"rgba(3, 152, 85, {alpha})" if val > 0 else f"rgba(217, 45, 32, {alpha})"
                    text_color = "#ffffff" if alpha > 0.5 else "#101828"
                    html_table += f"<td style='padding: 12px; border: 1px solid #eaecf0; background-color: {bg_color}; color: {text_color}; font-weight: bold;'>{val}</td>"
                html_table += "</tr>"
            html_table += "</table>"
            
            st.markdown(html_table, unsafe_allow_html=True)
        except Exception as ex:
            st.info("Computing sector network correlations... Please update system memory cache.")

# ==============================================================================
# TAB 3: ACTIVE ORDER LOG
# ==============================================================================
with app_mode[2]:
    st.title("📋 Active Order Log Ledger")
    st.markdown("<p style='color: #475467; font-size: 1.05rem; margin-top:-15px;'>Persistent SQL Audit Log of Structured Trade Configurations</p>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🧹 Flush Order Ledger Database History"):
        db_conn = sqlite3.connect("trading_workstation.db")
        db_cursor = db_conn.cursor()
        db_cursor.execute("DELETE FROM order_logs")
        db_conn.commit()
        db_conn.close()
        st.toast("Database ledger flushed successfully.")
        
    db_conn = sqlite3.connect("trading_workstation.db")
    try:
        df_logs = pd.read_sql_query("SELECT timestamp, ticker, direction, entry_price, stop_loss, target_price, shares, capital_deployed FROM order_logs ORDER BY id DESC", db_conn)
        if not df_logs.empty:
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("The persistent SQL database is currently empty. Log an order setup profile from Tab 1.")
    except Exception as db_err:
        st.error(f"Database Read Fault: {db_err}")
    finally:
        db_conn.close()
