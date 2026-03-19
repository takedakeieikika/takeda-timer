# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v2.8 Final (Web & Mobile Optimized)
# 特徴：GitHub音源対応・レスポンシブ・物理ロック・キーボード操作
# ==========================================

import streamlit as st

# --- 1. ページ設定 ---
st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .label-text {
        font-size: 1.1rem; 
        font-weight: bold; 
        color: #333; 
        margin-bottom: 2px; 
        text-align: center;
        white-space: nowrap;
    }

    /* 入力数値のフォント（特大サイズ） */
    input[type="number"] {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        height: 60px !important;
        color: #000 !important;
    }

    div[data-testid="stNumberInput"] {
        max-width: 140px;
        margin: 0 auto;
    }

    /* ロック用オーバーレイ（透明な壁） */
    #lock-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 180px; 
        z-index: 999999; display: none; cursor: not-allowed;
    }
    </style>
    <div id="lock-overlay"></div>
    <div class="meta-info" style="font-size: 0.7rem; color: #888; text-align: right;">v2.8 Final with Responsive UI</div>
    """, unsafe_allow_html=True)

# --- 2. 設定エリア ---
buf1, c1, c2, c3, buf2 = st.columns([1.5, 1, 1, 1, 2.5])

with c1:
    st.markdown('<div class="label-text">鈴1 (分)</div>', unsafe_allow_html=True)
    b1_m = st.number_input("b1", value=6, step=1, label_visibility="collapsed")
with c2:
    st.markdown('<div class="label-text">鈴2 (分)</div>', unsafe_allow_html=True)
    b2_m = st.number_input("b2", value=7, step=1, label_visibility="collapsed")
with c3:
    st.markdown('<div class="label-text">鈴3 (分)</div>', unsafe_allow_html=True)
    b3_m = st.number_input("b3", value=10, step=1, label_visibility="collapsed")

# --- 3. JavaScriptによるメインロジック ---
js_code = f"""
<style>
    /* 全体コンテナ */
    #main-wrapper {{
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        font-family: sans-serif;
    }}

    /* タイマー本体：スマホ・PC両対応 */
    #timer-container {{
        width: 100%;
        height: 55vh; 
        background-color: #007BFF; 
        color: white; 
        border-radius: 20px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        transition: background-color 0.5s; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}

    /* ボタンエリア：折り返し対応 */
    .button-area {{
        margin-top: 20px; 
        display: flex; 
        flex-wrap: wrap; 
        gap: 12px; 
        justify-content: center; 
        width: 100%;
    }}

    /* ボタン共通スタイル */
    .btn {{
        border: none; 
        padding: 15px 20px; 
        font-size: 1.3rem; 
        font-weight: bold; 
        border-radius: 12px; 
        cursor: pointer; 
        min-width: 150px;
        flex: 1 1 150px;
        max-width: 280px;
    }}

    #status {{ font-size: 10vw; font-weight: 800; line-height: 1.0; margin-bottom: 2vh; }}
    #display {{ font-size: 15vw; font-weight: 900; line-height: 1.0; }}

    .btn-start {{ background-color: #87CEEB; box-shadow: 0 4px #6495ED; }}
    .btn-stop {{ background-color: #FFB6C1; box-shadow: 0 4px #DB7093; }}
    .btn-reset {{ background-color: #98FB98; box-shadow: 0 4px #3CB371; }}
    .btn-mode {{ background-color: #6C757D; color: white; box-shadow: 0 4px #5A6268; }}
    .btn-mute {{ background-color: #DC3545; color: white; box-shadow: 0 4px #A02030; }}
</style>

<div id="main-wrapper">
    <div id="timer-container">
        <div id="status">発表時間</div>
        <div id="display">00:00</div>
    </div>

    <div class="button-area">
        <button class="btn btn-start" onclick="playClick(); startTimer()">▶ START</button>
        <button class="btn btn-stop" onclick="playClick(); stopTimer()">|| STOP</button>
        <button class="btn btn-reset" onclick="playClick(); resetTimer()">🔄 RESET</button>
        <button id="mode-btn" class="btn btn-mode" onclick="toggleMode()">🔽 カウントダウン</button>
        <button id="mute-btn" class="btn btn-mute" onclick="toggleMute()">1,2鈴ミュート</button>
    </div>
</div>

<script>
    let startTime = 0; let elapsed = 0; let running = false; let lastPlayed = -1; let isMuted = false;
    let isCountdown = false;
    
    const b1 = {b1_m * 60}; const b2 = {b2_m * 60}; const b3 = {b3_m * 60};
    
    // GitHub音源URL（直リンク）
    const sounds = {{
         "1": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell1.mp3"),
         "2": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell2.mp3"),
         "3": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell3.mp3")
    }};
    Object.values(sounds).forEach(s => {{ s.preload = "auto"; }});
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function setPhysicalLock(lock) {{
        const overlay = window.parent.document.getElementById('lock-overlay');
        if (overlay) overlay.style.display = lock ? 'block' : 'none';
        const inputs = window.parent.document.querySelectorAll('div[data-testid="stNumberInput"]');
        inputs.forEach(div => {{
            div.style.opacity = lock ? "0.4" : "1.0";
            div.style.pointerEvents = lock ? "none" : "auto";
        }});
    }}

    function playClick() {{
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        osc.start(); osc.stop(audioCtx.currentTime + 0.05);
    }}

    function toggleMute() {{
        playClick(); isMuted = !isMuted;
        const btn = document.getElementById('mute-btn');
        if (isMuted) {{
            btn.style.backgroundColor = "#CCCCCC"; btn.innerText = "1,2鈴 消音中"; btn.style.boxShadow = "none";
        }} else {{
            btn.style.backgroundColor = "#DC3545"; btn.innerText = "1,2鈴ミュート"; btn.style.boxShadow = "0 4px #A02030";
        }}
    }}

    function toggleMode() {{
        playClick(); isCountdown = !isCountdown;
        const btn = document.getElementById('mode-btn');
        if (isCountdown) {{
            btn.style.backgroundColor = "#17A2B8"; btn.innerText = "🔼 カウントアップ"; btn.style.boxShadow = "0 4px #117A8B";
        }} else {{
            btn.style.backgroundColor = "#6C757D"; btn.innerText = "🔽 カウントダウン"; btn.style.boxShadow = "0 4px #5A6268";
        }}
        updateDisplay();
    }}

    function updateDisplay() {{
        const totalSec = Math.floor(elapsed / 1000);
        let displaySec = 0;
        const container = document.getElementById('timer-container');
        const status = document.getElementById('status');

        if (totalSec < b2) {{ 
            container.style.backgroundColor = "#007BFF";
            status.innerText = isCountdown ? "残り時間" : "発表時間"; 
            displaySec = isCountdown ? (b2 - totalSec) : totalSec;
        }}
        else if (totalSec < b3) {{ 
            container.style.backgroundColor = "#D4A017";
            status.innerText = "質疑応答"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec;
        }}
        else {{ 
            container.style.backgroundColor = "#A52A2A";
            status.innerText = "終了時間"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec;
        }}

        const mm = String(Math.floor(displaySec / 60)).padStart(2, '0');
        const ss = String(displaySec % 60).padStart(2, '0');
        document.getElementById('display').innerText = mm + ":" + ss;

        if (totalSec !== lastPlayed) {{
            if (totalSec === b1 && !isMuted) {{ sounds["1"].currentTime = 0; sounds["1"].play().catch(e => {{}}); }}
            if (totalSec === b2 && !isMuted) {{ sounds["2"].currentTime = 0; sounds["2"].play().catch(e => {{}}); }}
            if (totalSec === b3) {{ sounds["3"].currentTime = 0; sounds["3"].play().catch(e => {{}}); }}
            lastPlayed = totalSec;
        }}
    }}

    function loop() {{
        if (!running) return;
        elapsed = performance.now() - startTime;
        updateDisplay();
        requestAnimationFrame(loop);
    }}

    function startTimer() {{
        if (!running) {{ 
            running = true; setPhysicalLock(true);
            startTime = performance.now() - elapsed;
            requestAnimationFrame(loop);
        }}
    }}
    
    function stopTimer() {{ running = false; }}
    
    function resetTimer() {{
        running = false; setPhysicalLock(false); elapsed = 0; lastPlayed = -1;
        updateDisplay();
    }}

    document.addEventListener("keydown", (e) => {{
        if (e.code === "Space") {{ playClick(); startTimer(); e.preventDefault(); }}
        if (e.code === "KeyS") {{ playClick(); stopTimer(); }}
        if (e.code === "KeyR") {{ playClick(); resetTimer(); }}
    }});

    updateDisplay();
</script>
"""

st.components.v1.html(js_code, height=900)
