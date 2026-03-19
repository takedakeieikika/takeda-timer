# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v3.2 Final (MP3 Edition)
# 特徴：GitHub音源対応・iPhoneアンロック機能・クレジット表記
# Created by Takeda Health Foundation
# 2026/3/19  
# ==========================================

import streamlit as st

# --- 1. ページ設定 ---
st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

# クレジットとカスタムCSS
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 左上のクレジット表記 */
    .credit {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 0.7rem;
        color: #aaaaaa;
        font-family: sans-serif;
    }

    .label-text {
        font-size: 1.1rem; font-weight: bold; color: #333; 
        margin-bottom: 2px; text-align: center;
    }

    input[type="number"] {
        font-size: 2.5rem !important; font-weight: 900 !important;
        text-align: center !important; height: 60px !important; color: #000 !important;
    }

    div[data-testid="stNumberInput"] { max-width: 140px; margin: 0 auto; }

    #lock-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 180px; 
        z-index: 999999; display: none; cursor: not-allowed;
    }
    </style>
    <div class="credit">Created by Takeda Healthcare Foundation</div>
    <div id="lock-overlay"></div>
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
    #main-wrapper {{ display: flex; flex-direction: column; align-items: center; font-family: sans-serif; }}
    #timer-container {{
        width: 100%; height: 50vh; background-color: #007BFF; color: white; 
        border-radius: 20px; display: flex; flex-direction: column; 
        justify-content: center; align-items: center; transition: background-color 0.5s; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .button-area {{ margin-top: 15px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; width: 100%; }}
    .btn {{
        border: none; padding: 12px 15px; font-size: 1.2rem; font-weight: bold; 
        border-radius: 12px; cursor: pointer; flex: 1 1 130px; max-width: 220px;
    }}
    #status {{ font-size: 8vw; font-weight: 800; line-height: 1.0; margin-bottom: 2vh; }}
    #display {{ font-size: 15vw; font-weight: 900; line-height: 1.0; }}

    .btn-start {{ background-color: #87CEEB; box-shadow: 0 4px #6495ED; }}
    .btn-stop {{ background-color: #FFB6C1; box-shadow: 0 4px #DB7093; }}
    .btn-reset {{ background-color: #98FB98; box-shadow: 0 4px #3CB371; }}
    .btn-mode {{ background-color: #6C757D; color: white; }}
    .btn-mute {{ background-color: #DC3545; color: white; }}
</style>

<div id="main-wrapper">
    <div id="timer-container">
        <div id="status">発表時間</div>
        <div id="display">00:00</div>
    </div>
    <div class="button-area">
        <button class="btn btn-start" onclick="handleAction('start')">▶ START</button>
        <button class="btn btn-stop" onclick="handleAction('stop')">|| STOP</button>
        <button class="btn btn-reset" onclick="handleAction('reset')">🔄 RESET</button>
        <button id="mode-btn" class="btn btn-mode" onclick="handleAction('mode')">🔽 カウントダウン</button>
        <button id="mute-btn" class="btn btn-mute" onclick="handleAction('mute')">1,2鈴ミュート</button>
    </div>
</div>

<script>
    let startTime = 0; let elapsed = 0; let running = false; let lastPlayed = -1; 
    let isMuted = false; let isCountdown = false; let audioUnlocked = false;
    
    const b1 = {b1_m * 60}; const b2 = {b2_m * 60}; const b3 = {b3_m * 60};
    
    // GitHub音源
    const sounds = {{
         "1": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell1.mp3"),
         "2": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell2.mp3"),
         "3": new Audio("https://github.com/takedakeieikika/takeda-timer/raw/main/bell3.mp3")
    }};

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    // iPhone用アンロック: 最初のクリックで全ファイルを「空再生」して許可を得る
    function unlockAudio() {{
        if (audioUnlocked) return;
        Object.values(sounds).forEach(s => {{
            s.play().then(() => {{ s.pause(); s.currentTime = 0; }}).catch(e => {{}});
        }});
        if (!audioCtx) audioCtx = new AudioContext();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        audioUnlocked = true;
    }}

    function playClick() {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + 0.05);
    }}

    function handleAction(type) {{
        unlockAudio(); // 全ボタンでアンロックを試みる
        if (type === 'start') {{ playClick(); startTimer(); }}
        if (type === 'stop') {{ playClick(); stopTimer(); }}
        if (type === 'reset') {{ playClick(); resetTimer(); }}
        if (type === 'mode') {{ playClick(); toggleMode(); }}
        if (type === 'mute') {{ playClick(); toggleMute(); }}
    }}

    function toggleMute() {{
        isMuted = !isMuted;
        const btn = document.getElementById('mute-btn');
        btn.style.backgroundColor = isMuted ? "#CCCCCC" : "#DC3545";
        btn.innerText = isMuted ? "1,2鈴 消音中" : "1,2鈴ミュート";
    }}

    function toggleMode() {{
        isCountdown = !isCountdown;
        const btn = document.getElementById('mode-btn');
        btn.innerText = isCountdown ? "🔼 カウントアップ" : "🔽 カウントダウン";
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
        }} else if (totalSec < b3) {{ 
            container.style.backgroundColor = "#D4A017";
            status.innerText = "質疑応答"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec;
        }} else {{ 
            container.style.backgroundColor = "#A52A2A";
            status.innerText = "終了時間"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec;
        }}

        const mm = String(Math.floor(displaySec / 60)).padStart(2, '0');
        const ss = String(displaySec % 60).padStart(2, '0');
        document.getElementById('display').innerText = mm + ":" + ss;

        if (totalSec !== lastPlayed) {{
            if (totalSec === b1 && !isMuted) {{ sounds["1"].currentTime = 0; sounds["1"].play().catch(e=>{{}}); }}
            if (totalSec === b2 && !isMuted) {{ sounds["2"].currentTime = 0; sounds["2"].play().catch(e=>{{}}); }}
            if (totalSec === b3) {{ sounds["3"].currentTime = 0; sounds["3"].play().catch(e=>{{}}); }}
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
            running = true; startTime = performance.now() - elapsed;
            requestAnimationFrame(loop);
        }}
    }}
    function stopTimer() {{ running = false; }}
    function resetTimer() {{ running = false; elapsed = 0; lastPlayed = -1; updateDisplay(); }}

    updateDisplay();
</script>
"""

st.components.v1.html(js_code, height=850)
