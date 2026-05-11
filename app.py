import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 每 15 分钟自动刷新一次页面
st_autorefresh(interval=15 * 60 * 1000, key="datarefresh")


# --- 仪表盘美学配置 ---
st.set_page_config(page_title="The Fisherman TSLA", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; }
    .stProgress > div > div > div > div { background-color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心计算引擎 ---
def calculate_kdj(df, n=9):
    low_list = df['Low'].rolling(window=n).min()
    high_list = df['High'].rolling(window=n).max()
    rsv = (df['Close'] - low_list) / (high_list - low_list) * 100
    df['K'] = rsv.ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df

@st.cache_data(ttl=900)
def get_market_data():
    tsla = yf.Ticker("TSLA")
    hist = tsla.history(period="1y")
    hist = calculate_kdj(hist)
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    # 模拟 IV Rank (基于20日历史波动率百分位)
    vol = hist['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
    iv_rank = (vol.iloc[-1] - vol.min()) / (vol.max() - vol.min()) * 100
    return hist.iloc[-1], vix, iv_rank

# --- 界面渲染 ---
st.title("🎣 The Fisherman")
st.caption("百万账户级 · TSLA 动态捕鱼仪表盘")

try:
    last_data, vix, iv_rank = get_market_data()
    j_val = last_data['J']
    price = last_data['Close']

    # 1. 3000股目标进度
    current_shares = 2440
    target_shares = 3000
    progress = current_shares / target_shares
    
    st.write(f"📊 **3,000 股目标进度: {current_shares} / {target_shares} ({progress*100:.1f}%)**")
    st.progress(progress)
    st.write(f"距离目标还差 **{target_shares - current_shares}** 股。")

    st.markdown("---")

    # 2. 核心指标展示
    col1, col2, col3 = st.columns(3)
    col1.metric("TSLA 现价", f"${price:.2f}")
    col2.metric("J-Value", f"{j_val:.1f}", delta="厚实" if j_val < 20 else "太薄", delta_color="normal" if j_val < 20 else "inverse")
    col3.metric("VIX 恐慌指数", f"{vix:.1f}")

    # 3. 收割指数计算 (J + VIX + IV Rank)
    j_score = max(0, (20 - j_val) * 2.5) if j_val < 20 else 0
    vix_score = min(100, (vix / 30) * 100)
    total_score = (j_score * 0.5) + (vix_score * 0.3) + (iv_rank * 0.2)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_score,
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00ffcc"},
            'steps' : [
                {'range': [0, 40], 'color': "#222"},
                {'range': [40, 75], 'color': "#444"},
                {'range': [75, 100], 'color': "#1a472a"}]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

    # 4. 自动决策提示
    if total_score > 75:
        st.success("🔥 **行动建议：全力收割！** 权利金极厚，J值已探底。")
    elif total_score > 40:
        st.warning("☕ **行动建议：继续喝咖啡等待。** 还没到时候，等J值跌破20。")
    else:
        st.info("🚫 **行动建议：不值得出手。** 市场太狂热，权利金太薄。")

except Exception as e:
    st.error("正在同步美股数据... 请稍后。")

st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')} | 策略：J值收割 v2.0")
