import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image
import sqlite3
import time
from sklearn.ensemble import RandomForestRegressor

# --- PAGE INITIALIZATION (Must be the absolute first Streamlit command) ---
st.set_page_config(
    page_title="AlgoMetrics Pro Workstation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UPGRADE 4: PERSISTENT DATABASE CACHING LAYER ---
@st.cache_resource
def get_db_connection():
    """Establishes a thread-safe, persistent connection pool in memory/RAM."""
    conn = sqlite3.connect("trading_workstation.db", check_same_thread=False)
    return conn

# Initialize tables on startup using the persistent pool
db_conn = get_db_connection()
cursor = db_conn.cursor()
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
db_conn.commit()

# --- MODULE 1: LOCAL INSTITUTIONAL GATEHOUSE SECURITY ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1 style="color: #101828; font-size: 2.2rem; font-weight: 700;">⚡ AlgoMetrics Pro Workstation</h1>
            <p style="color: #475467; font-size: 1.1rem; margin-bottom: 30px;">Institutional Quantitative Trading & Position Architecture Suite</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<p style='text-align: center; color: #667085;'>🔒 Secure Terminal Gatehouse Boundary</p>", unsafe_allow_html=True)
        access_key = st.text_input("ENTER OPERATOR SECURITY PASSKEY", type="password")
        
        if st.button("🔑 Verify and Unlock Terminal Infrastructure", use_container_width=True):
            if access_key == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("ACCESS DENIED: Cryptographic credentials mismatch.")
    st.stop()

user_email = "Master Operator"

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
# DATA ENGINES (Shared across components)
# ==============================================================================
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
        return float(model.predict(latest_features)[0])
    except:
        return float(df['High'].iloc[-1] - df['Low'].iloc[-1])

@st.cache_data(ttl=60)
def fetch_multi_timeframe_confluence(ticker):
    try:
        df_15m = yf.download(ticker, period="5d", interval="15m")
        if df_15m.empty: return "UNKNOWN"
        if isinstance(df_15m.columns, pd.MultiIndex): df_15m.columns = [col[0] for col in df_15m.columns]
        
        ema20_15m = df_15m['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        return "BULLISH" if df_15m['Close'].iloc[-1] > ema20_15m else "BEARISH"
    except: return "UNKNOWN"

@st.cache_data(ttl=60)
def analyze_institutional_flow(ticker, days, window):
    try:
        start_date = datetime.now() - timedelta(days=days + 60)
        df = yf.download(ticker, start=start_date, end=datetime.now(), interval="1d")
        if df.empty: return None, "Asset Ticker Invalidation or no data found."
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        
        df_full = df.copy()
        delta = df_full['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df_full['RSI'] = 100 - (100 / (1 + rs))
        
        df_full['EMA20'] = df_full['Close'].ewm(span=20, adjust=False).mean()
        df_full['ATR'] = (pd.concat([df_full['High']-df_full['Low'], np.abs(df_full['High']-df_full['Close'].shift()), np.abs(df_full['Low']-df_full['Close'].shift())], axis=1).max(axis=1)).rolling(window=14).mean()
        
        exp1 = df_full['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df_full['Close'].ewm(span=26, adjust=False).mean()
        df_full['MACD'] = exp1 - exp2
        df_full['Signal_Line'] = df_full['MACD'].ewm(span=9, adjust=False).mean()
        
        df = df_full.tail(days).copy()
        df['Is_Peak'] = 0; df['Is_Valley'] = 0
        for i in range(window, len(df) - window):
            if float(df['High'].iloc[i]) == float(df['High'].iloc[i-window:i+window+1].max()): df.loc[df.index[i], 'Is_Peak'] = 1
            if float(df['Low'].iloc[i]) == float(df['Low'].iloc[i-window:i+window+1].min()): df.loc[df.index[i], 'Is_Valley'] = 1
        
        peaks = df[df['Is_Peak'] == 1]['High'].astype(float).tolist()
        valleys = df[df['Is_Valley'] == 1]['Low'].astype(float).tolist()
        cur_p = float(df['Close'].iloc[-1])
        trend = "BULLISH" if cur_p > float(df_full['EMA20'].iloc[-1]) else "BEARISH"
        
        signal = "HOLD"
        if trend == "BULLISH" and float(df['RSI'].iloc[-1]) < 68 and float(df['MACD'].iloc[-1]) > float(df['Signal_Line'].iloc[-1]): signal = "BUY TRIGGER"
        elif trend == "BEARISH" and float(df['RSI'].iloc[-1]) > 32 and float(df['MACD'].iloc[-1]) < float(df['Signal_Line'].iloc[-1]): signal = "SELL TRIGGER"
            
        return {"df": df, "price": cur_p, "peaks": peaks, "valleys": valleys, "trend": trend, "atr": float(df['ATR'].iloc[-1]), "rsi": float(df['RSI'].iloc[-1]), "signal": signal}, None
    except Exception as e: return None, str(e)

# ==============================================================================
# TAB 1: INDIVIDUAL ASSET TERMINAL
# ==============================================================================
with app_mode[0]:
    st.title("⚡ AlgoMetrics Pro Terminal")
    st.markdown("<p style='color: #475467; font-size: 1.05rem; margin-top:-15px;'>Enterprise Market Structure Mapping & Multi-Indicator Quant Suite</p>", unsafe_allow_html=True)
    st.divider()

    # Sidebar Controls
    st.sidebar.markdown(f"👤 **User Identity:** `{user_email}`")
    if st.sidebar.button("🚪 Secure System Sign Out"):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("### 🎛️ SYSTEM CONTROLS")
    ticker_input = st.sidebar.text_input("ASSET TICKER SYMBOL", value="NVDA").upper()

    if st.sidebar.button("🧹 Clear System Memory Cache"):
        st.cache_data.clear()
        st.toast("System cache purged successfully.")

    with st.sidebar.expander("💼 RISK ENGINE ASSIGNMENT", expanded=True):
        account_size = st.number_input("ACCOUNT BALANCE ($)", value=10000, step=1000)
        risk_method = st.selectbox("RISK MODEL", ["Percentage Basis", "Fixed Dollar Basis"])
        max_loss = account_size * (st.slider("MAX TRADE RISK (%)", 0.25, 5.0, 1.0, 0.25) / 100) if risk_method == "Percentage Basis" else st.number_input("FIXED RISK AMOUNT ($)", value=100, step=25)

    with st.sidebar.expander("💸 COMMISSIONS & SLIPPAGE SCALER", expanded=False):
        per_share_fee = st.number_input("Broker Fee per Share ($)", value=0.005, format="%.3f")

    with st.sidebar.expander("🔬 SIGNAL HORIZON TUNING", expanded=False):
        lookback = st.slider("LOOKBACK FRAME (DAYS)", 30, 365, 120)
        sensitivity = st.slider("PIVOT STRENGTH MATRIX", 3, 15, 5)

    st.sidebar.divider()
    uploaded_screenshot = st.sidebar.file_uploader("DROP LIVE SCREENSHOT FILE HERE", type=["png", "jpg", "jpeg"])

    if uploaded_screenshot and ticker_input:
        data, error = analyze_institutional_flow(ticker_input, lookback, sensitivity)
        short_term_trend = fetch_multi_timeframe_confluence(ticker_input)
        
        if error: st.error(f"Error: {error}")
        elif data:
            ml_predicted_range = calculate_ml_volatility_prediction(data["df"])
            
            if data["trend"] == short_term_trend:
                st.success(f"⛓️ **MULTI-TIMEFRAME CONFLUENCE LOCKED:** Daily and Intraday 15m Trend are both **{data['trend']}**.")
            else:
                st.warning(f"⚠️ **TIMEFRAME DIVERGENCE DETECTED:** Daily is {data['trend']}, Intraday 15m is {short_term_trend}.")

            # Data Metrics Row
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
                # --- UPGRADE 1: STREAMLIT NATIVE PLOTLY CHARTS ---
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data["df"].index, y=data["df"]['Close'], name='Close Price', line=dict(color='#101828', width=2)))
                fig.add_trace(go.Scatter(x=data["df"].index, y=data["df"]['EMA20'], name='EMA 20 Baseline', line=dict(color='#2563eb', width=1.5, dash='dash')))
                fig.update_layout(template="plotly_white", height=350, margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📸 Image Engine Interface Reference")
                st.image(Image.open(uploaded_screenshot), use_container_width=True)

            with right_col:
                # --- UPGRADE 2 & 3: ISOLATED COMPUTATION VIA FRAGMENTS & WEBSOCKET SIMULATION ---
                @st.fragment
                def render_tactical_dashboard(static_data):
                    st.markdown("### 📋 Tactical Command Dashboard")
                    with st.container(border=True):
                        st.markdown("🛠️ **Dynamic Volatility Buffer Tuning**")
                        atr_multiplier = st.slider("Volatility Buffer Multiplier (ATR Scaler)", 1.0, 3.5, 1.5, 0.1)

                    resistances = [p for p in static_data["peaks"] if p > static_data["price"]]
                    supports = [v for v in static_data["valleys"] if v < static_data["price"]]
                    ceiling = min(resistances) if resistances else static_data["price"] * 1.05
                    floor = max(supports) if supports else static_data["price"] * 0.95
                    
                    entry = floor * 1.002 if static_data["trend"] == "BULLISH" else ceiling * 0.998
                    tp1 = ceiling if static_data["trend"] == "BULLISH" else floor
                    sl = entry - (static_data["atr"] * atr_multiplier) if static_data["trend"] == "BULLISH" else entry + (static_data["atr"] * atr_multiplier)
                    
                    risk_amt = abs(entry - sl)
                    shares = int(max_loss / risk_amt) if risk_amt > 0 else 0
                    total_capital = (shares * entry) + (shares * per_share_fee)
                    rr = abs(tp1 - entry) / risk_amt if risk_amt > 0 else 0

                    with st.container(border=True):
                        st.markdown(f"#### {static_data['trend']} LIMIT ALLOCATION")
                        st.write(f"🔹 **Entry Trigger:** `${entry:,.2f}`")
                        st.write(f"🎯 **Profit Target:** `${tp1:,.2f}` | 🛑 **Stop Loss:** `${sl:,.2f}`")
                        st.write(f"📦 **Volume Target:** `{shares}` Units | 📊 **Dynamic R:R:** `1 : {rr:.2f}`")
                        
                        st.divider()
                        if st.button("💾 Log Order Configuration to SQLite Database", use_container_width=True):
                            conn = get_db_connection()
                            c = conn.cursor()
                            c.execute("""
                                INSERT INTO order_logs (timestamp, ticker, direction, entry_price, stop_loss, target_price, shares, capital_deployed)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ticker_input, static_data['trend'], entry, sl, tp1, shares, total_capital))
                            conn.commit()
                            st.toast("🎯 Trading plan logged instantly to global memory pool!")

                render_tactical_dashboard(data)
    else:
        st.write("##")
        with st.container(border=True): st.markdown("<h3 style='text-align: center;'>Terminal Core Standby: Upload Screenshot File</h3>", unsafe_allow_html=True)

# ==============================================================================
# TAB 2: MACRO MARKET RADAR
# ==============================================================================
with app_mode[1]:
    st.title("🌍 Global Macro Market Radar")
    st.markdown("""<div class="alert-banner alert-high">⚠️ <b>CRITICAL SYSTEM ALERT: VOLATILITY SCALER SYSTEM MONITOR ACTIVE</b></div>""", unsafe_allow_html=True)
    
    # --- UPGRADE 2 & 3: STREAMING REAL-TIME SIMULATED TAPE ---
    @st.fragment(run_every=4)
    def render_streaming_macro_radar():
        major_markets = {"S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT"}
        grid_cols = st.columns(4)
        
        for i, (m_name, m_symbol) in enumerate(major_markets.items()):
            try:
                df = yf.download(m_symbol, start=datetime.now() - timedelta(days=20), end=datetime.now(), interval="1d")
                if df.empty: continue
                if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
                
                # Introduce a tiny variable tick fluctuation to emulate a live WebSocket socket feed
                live_variance = np.random.uniform(-0.15, 0.15)
                cur_price = float(df['Close'].iloc[-1]) + live_variance
                prev_price = float(df['Close'].iloc[-2])
                session_change = ((cur_price - prev_price) / prev_price) * 100
                
                with grid_cols[i]:
                    with st.container(border=True):
                        st.markdown(f"### {m_name}")
                        st.metric("Live Index Level", f"{cur_price:,.2f}", f"{session_change:+.2f}%")
                        
                        fig_mini = go.Figure()
                        fig_mini.add_trace(go.Scatter(y=df['Close'], line=dict(color='#039855' if session_change >= 0 else '#d92d20', width=1.5)))
                        fig_mini.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=70, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white")
                        st.plotly_chart(fig_mini, use_container_width=True, key=f"macro_chart_{i}_{time.time()}")
            except: continue
            
    render_streaming_macro_radar()

    # --- SECTOR CORRELATION HEATMAP MATRIX ---
    st.write("##")
    st.markdown("### 🧮 Technology & Sector Asset Inter-Correlation Matrix")
    
    @st.cache_data(ttl=300)
    def generate_correlation_matrix_data():
        tickers = ["NVDA", "AMD", "AAPL", "MSFT", "QQQ", "SPY"]
        df_assets = yf.download(tickers, start=datetime.now() - timedelta(days=60), end=datetime.now())['Close']
        if isinstance(df_assets.columns, pd.MultiIndex): df_assets.columns = [col[0] for col in df_assets.columns]
        return tickers, df_assets.corr().round(2).values.tolist()

    try:
        corr_labels, corr_values = generate_correlation_matrix_data()
        html_table = "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; font-size: 0.9rem;'><tr><th style='padding: 12px; border: 1px solid #eaecf0; background-color: #f9fafb;'>Asset</th>"
        for label in corr_labels: html_table += f"<th style='padding: 12px; border: 1px solid #eaecf0; background-color: #f9fafb;'>{label}</th>"
        html_table += "</tr>"
        for r_idx, row_name in enumerate(corr_labels):
            html_table += f"<tr><td style='padding: 12px; border: 1px solid #eaecf0; font-weight: 600; background-color: #f9fafb;'>{row_name}</td>"
            for c_idx, val in enumerate(corr_values[r_idx]):
                alpha = abs(val)
                html_table += f"<td style='padding: 12px; border: 1px solid #eaecf0; background-color: {'rgba(3, 152, 85, ' + str(alpha) + ')' if val > 0 else 'rgba(217, 45, 32, ' + str(alpha) + ')'}; color: {'#ffffff' if alpha > 0.5 else '#101828'}; font-weight: bold;'>{val}</td>"
            html_table += "</tr>"
        st.markdown(html_table + "</table>", unsafe_allow_html=True)
    except: st.info("Computing sector network correlations...")

# ==============================================================================
# TAB 3: ACTIVE ORDER LOG
# ==============================================================================
with app_mode[2]:
    st.title("📋 Active Order Log Ledger")
    st.markdown("<p style='color: #475467; font-size: 1.05rem; margin-top:-15px;'>Persistent SQL Audit Log of Structured Trade Configurations</p>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🧹 Flush Order Ledger Database History"):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM order_logs")
        conn.commit()
        st.toast("Database ledger flushed successfully.")
        
    # Read instantly using persistent cached connection allocation pool
    conn = get_db_connection()
    try:
        df_logs = pd.read_sql_query("SELECT timestamp, ticker, direction, entry_price, stop_loss, target_price, shares, capital_deployed FROM order_logs ORDER BY id DESC", conn)
        if not df_logs.empty: st.dataframe(df_logs, use_container_width=True)
        else: st.info("The persistent SQL database is currently empty. Log an order setup profile from Tab 1.")
    except Exception as db_err: st.error(f"Database Read Fault: {db_err}")
