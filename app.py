import streamlit as st
import yfinance as tf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

# --- 0. 页面基础配置 (Streamlit 铁律：必须作为绝对第一条命令执行) ---
st.set_page_config(page_title="FISHERMAN // TERMINAL", layout="centered")

# --- 1. 自动刷新配置（5分钟赛博发条） ---
st_autorefresh(interval=5 * 60 * 1000, key="cyber_refresh")

# --- 2. 赛博朋克 UI 视觉注入 (定制 CSS HUD) ---
cyber_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Ubuntu+Mono&display=swap');
    
    .stApp {
        background-color: #050505 !important;
        background-image: linear-gradient(rgba(0, 243, 255, 0.02) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 243, 255, 0.02) 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px !important;
    }
    
    .cyber-title {
        color: #00f3ff;
        text-shadow: 0 0 15px #00f3ff;
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .cyber-subtitle {
        color: #ff00ff;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        font-size: 14px;
        letter-spacing: 4px;
        margin-bottom: 30px;
        text-shadow: 0 0 8px #ff00ff;
    }

    .hud-container {
        display: flex;
        gap: 15px;
        justify-content: space-between;
        margin-bottom: 25px;
    }
    .hud-box {
        flex: 1;
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid #00f3ff;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
        padding: 15px;
        border-radius: 4px;
        text-align: center;
        position: relative;
    }
    .hud-box::before {
        content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 6px; border-top: 2px solid #ff00ff; border-left: 2px solid #ff00ff;
    }
    .hud-label {
        font-family: 'Orbitron', sans-serif;
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .hud-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 26px;
        font-weight: bold;
    }
    
    .advice-box {
        padding: 20px;
        border-radius: 4px;
        font-family: 'Ubuntu Mono', monospace;
        font-size: 16px;
        line-height: 1.5;
        margin-top: 20px;
        position: relative;
    }
    .advice-critical {
        border: 1px solid #ff00ff;
        background: rgba(255, 0, 255, 0.04);
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.25);
        color: #ff00ff;
    }
    .advice-success {
        border: 1px solid #00ff41;
        background: rgba(0, 255, 65, 0.04);
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.25);
        color: #00ff41;
    }
    .advice-warning {
        border: 1px solid #ffaa00;
        background: rgba(255, 170, 0, 0.04);
        box-shadow: 0 0 12px rgba(255, 170, 0, 0.15);
        color: #ffaa00;
    }
</style>
"""
st.markdown(cyber_css, unsafe_allow_html=True)

# --- 3. 实时北京时间校准 ---
beijing_tz = pytz.timezone('Asia/Shanghai')
beijing_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')

# 终端主标题渲染
st.markdown('<div class="cyber-title">FISHERMAN // MAINNET 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">// TSLA QUANTUM RADAR //</div>', unsafe_allow_html=True)

# --- 4. 侧边栏多维控制台 (北京时间 + 2.0 货舱控制器) ---
st.sidebar.markdown("### 📡 TERMINAL STATUS")
st.sidebar.markdown(f"⏱️ **BEIJING TIME**:\n`{beijing_time}`")
st.sidebar.markdown("⚡ **REFRESH RATE**: `5 MINS`")
st.sidebar.markdown("---")

# 🎛️ 2.0 货舱控制器
st.sidebar.markdown("### 🎛️ CARGO CONTROLLER")
current_shares = st.sidebar.number_input(
    "CURRENT SHARES (TSLA)",
    min_value=0,
    max_value=5000,
    value=2440,  
    step=10,     
    key="cyber_cargo_shares"
)

# --- 5. 高速并行数据抓取管道 ---
@st.cache_data(ttl=300)
def fetch_cyber_market_data_fast():
    df = tf.download("TSLA ^VIX", period="3mo", interval="1d", group_by='ticker', progress=False)
    
    if df.empty:
        raise ValueError("Data pipeline returned empty data matrix.")
        
    tsla_df = df['TSLA'].copy()
    vix_df = df['^VIX'].copy()
    
    # KDJ 核心算法
    low_list = tsla_df['Low'].rolling(9, min_periods=9).min()
    high_list = tsla_df['High'].rolling(9, min_periods=9).max()
    rsv = (tsla_df['Close'] - low_list) / (high_list - low_list) * 100
    
    tsla_df['K'] = rsv.ewm(com=2).mean()
    tsla_df['D'] = tsla_df['K'].ewm(com=2).mean()
    tsla_df['J'] = 3 * tsla_df['K'] - 2 * tsla_df['D']
    
    return tsla_df.iloc[-1], vix_df.iloc[-1]

try:
    with st.spinner("📡 CYBER LINK COUPLING // 正在接入量子网络解算密匙..."):
        last_tsla, last_vix = fetch_cyber_market_data_fast()
    
    tsla_price = float(last_tsla['Close'].values[0] if isinstance(last_tsla['Close'], pd.Series) else last_tsla['Close'])
    j_val = float(last_tsla['J'].values[0] if isinstance(last_tsla['J'], pd.Series) else last_tsla['J'])
    vix_val = float(last_vix['Close'].values[0] if isinstance(last_vix['Close'], pd.Series) else last_vix['Close'])
    
    # --- 6. 赛博 HUD 仪表板渲染 ---
    hud_html = f"""
    <div class="hud-container">
        <div class="hud-box">
            <div class="hud-label">TSLA PRICE</div>
            <div class="hud-value" style="color: #00f3ff; text-shadow: 0 0 10px #00f3ff;">${tsla_price:.2f}</div>
        </div>
        <div class="hud-box">
            <div class="hud-label">CURRENT J-VAL</div>
            <div class="hud-value" style="color: {'#ff00ff' if j_val > 80 or j_val < 0 else '#00ff41'}; text-shadow: 0 0 10px {'#ff00ff' if j_val > 80 or j_val < 0 else '#00ff41'};">{j_val:.1f}</div>
        </div>
        <div class="hud-box">
            <div class="hud-label">VIX INDEX</div>
            <div class="hud-value" style="color: #ffaa00; text-shadow: 0 0 10px #ffaa00;">{vix_val:.2f}</div>
        </div>
    </div>
    """
    st.markdown(hud_html, unsafe_allow_html=True)
    
    # --- 7. OPTIMUS 进度条 ---
    st.markdown("<h4 style='color:#e0e0e0; margin-bottom:10px;'>🤖 OPTIMUS ACCUMULATION PROFILE</h4>", unsafe_allow_html=True)
    target_shares = 3000
    
    safe_shares = min(current_shares, target_shares)
    progress_percent = (safe_shares / target_shares) * 100
    shares_left = max(target_shares - current_shares, 0)
    
    progress_html = f"""
    <div style="background: #111; border: 1px solid #00ff41; height: 26px; border-radius: 4px; overflow: hidden; position: relative; margin-bottom: 10px;">
        <div style="width: {progress_percent:.1f}%; background: linear-gradient(90deg, #00ff41, #00f3ff); height: 100%; box-shadow: 0 0 12px #00ff41;"></div>
        <div style="position: absolute; width: 100%; text-align: center; top: 0; line-height: 26px; font-family: 'Orbitron'; font-size: 13px; color: #fff; font-weight: bold; text-shadow: 0 0 4px #000;">
            {progress_percent:.1f}% NETWORK DEPLOYED
        </div>
    </div>
    <div style="font-family: 'Ubuntu Mono'; color: #888; font-size: 14px; margin-bottom: 25px;">
        📊 HOLDING: <strong style="color:#00ff41;">{current_shares}</strong> SHARES | TARGET: <strong style="color:#00f3ff;">{target_shares}</strong> SHARES | CAP GAP: <strong style="color:#ff00ff;">{shares_left}</strong> SHARES UNIT
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # --- 8. 综合收割指数半表盘 ---
    st.markdown("<h4 style='color:#e0e0e0; margin-bottom:5px;'>🌊 INTEGRATED HARVEST INDEX</h4>", unsafe_allow_html=True)
    j_score = np.clip((100 - j_val) / 1.2, 0, 60)
    vix_score = np.clip(vix_val * 2, 0, 40)
    harvest_index = j_score + vix_score
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=harvest_index,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "#00f3ff"},
            'bar': {'color': "#00f3ff"},
            'steps': [
                {'range': [0, 40], 'color': "#111"},
                {'range': [40, 70], 'color': "#1a1f2c"},
                {'range': [70, 100], 'color': "#0a2f30"}
            ],
        }
    ))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 9. 动态战术建议 ---
    if j_val < 0:
        advice_html = f"""
        <div class="advice-box advice-critical">
            ⚡ <strong>[CRITICAL PROTOCOL // 深水炸弹触发]</strong><br>
            J值已彻底击穿0轴底线（当前实时精确值: <strong>{j_val:.1f}</strong>），市场情绪陷入极端恐慌冰点，深水水位极其“厚实”！核心仓位防御圈完全打开。建议立刻执行收割，在 Moomoo/Firstrade 坚决挂单高溢价 Sell Put，全速抢夺权利金肥肉！
        </div>
        """
    elif j_val <= 20:
        advice_html = f"""
        <div class="advice-box advice-success">
            🐟 <strong>[TACTICAL SIGNAL // 鱼群大量进窝]</strong><br>
            J值已成功杀入20以下的“安全厚实区间”（当前实时精确值: <strong>{j_val:.1f}</strong>）。水流深度符合捕鱼指标，期权隐波处于优势期。下网时机完全成熟，适合分批次、多节点部署阶梯式 Put 防御拦截网，稳步向 3000 股终极目标靠拢。
        </div>
        """
    else:
        advice_html = f"""
        <div class="advice-box advice-warning">
            ☕ <strong>[STANDBY MODE // 静默喝咖啡等待]</strong><br>
            当前J值依然飘在空中（当前实时精确值: <strong>{j_val:.1f}</strong>），高于20临界值，水流太薄，多头仍在高位拉扯。长线猎手请保持克制，切勿抢跑接飞刀。将看盘权限全权移交 Fisherman 定时系统，静候指标落地。
        </div>
        """
    st.markdown(advice_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"📡 终端核心网元连接超时。ERROR CODES: {e}")
