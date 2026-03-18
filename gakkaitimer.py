# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v2.8 (SE共同開発・カウント切替/キーボード操作対応)
# 作成日：2026年3月18日
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
    <div class="meta-info" style="font-size: 0.7rem; color: #888; text-align: right;">v2.8 Final with Countdown</div>
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
<div id="timer-container" style="display: flex; flex-direction: column; justify-content: center; align-items: center;
    height: 62vh; background-color: #007BFF; color: white; border-radius: 20px; font-family: sans-serif; transition: background-color 0.5s; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <div id="status" style="font-size: 12vw; font-weight: 800; line-height: 1.0; margin-bottom: 2vh;">発表時間</div>
    <div id="display" style="font-size: 15vw; font-weight: 900; line-height: 1.0;">00:00</div>
</div>

<div style="margin-top: 25px; display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; align-items: center; font-family: sans-serif;">
    <button onclick="playClick(); startTimer()" style="background-color: #87CEEB; border: none; padding: 15px 35px; font-size: 1.8rem; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px #6495ED;">▶ START</button>
    <button onclick="playClick(); stopTimer()" style="background-color: #FFB6C1; border: none; padding: 15px 35px; font-size: 1.8rem; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px #DB7093;">|| STOP</button>
    <button onclick="playClick(); resetTimer()" style="background-color: #98FB98; border: none; padding: 15px 35px; font-size: 1.8rem; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px #3CB371;">🔄 RESET</button>
    
    <button id="mode-btn" onclick="toggleMode()" style="background-color: #6C757D; color: white; border: none; padding: 15px 25px; font-size: 1.1rem; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px #5A6268; width: 220px;">
        🔽 カウントダウンへ切替
    </button>
    
    <button id="mute-btn" onclick="toggleMute()" style="background-color: #DC3545; color: white; border: none; padding: 15px 25px; font-size: 1.1rem; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px #A02030; width: 180px;">
        1,2鈴ミュート
    </button>
</div>

<script>
    let startTime = 0; let elapsed = 0; let running = false; let lastPlayed = -1; let isMuted = false;
    let isCountdown = false; // モード管理
    
    const b1 = {b1_m * 60}; const b2 = {b2_m * 60}; const b3 = {b3_m * 60};
    
    // SE様のpreload処理を採用
    const sounds = {{
        "1": new Audio("https://www.takedakenko.jp/bell1.mp3"),
        "2": new Audio("https://www.takedakenko.jp/bell2.mp3"),
        "3": new Audio("https://www.takedakenko.jp/bell3.mp3")
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
            btn.style.backgroundColor = "#17A2B8"; btn.innerText = "🔼 カウントアップへ切替"; btn.style.boxShadow = "0 4px #117A8B";
        }} else {{
            btn.style.backgroundColor = "#6C757D"; btn.innerText = "🔽 カウントダウンへ切替"; btn.style.boxShadow = "0 4px #5A6268";
        }}
        updateDisplay();
    }}

    function updateDisplay() {{
        const totalSec = Math.floor(elapsed / 1000);
        let displaySec = 0;
        const container = document.getElementById('timer-container');
        const status = document.getElementById('status');

        // 背景色と表示文言・計算ロジック
        if (totalSec < b2) {{ 
            container.style.backgroundColor = "#007BFF"; // 青
            status.innerText = isCountdown ? "発表残り時間" : "発表時間"; 
            displaySec = isCountdown ? (b2 - totalSec) : totalSec; // カウントダウン時は引く
        }}
        else if (totalSec < b3) {{ 
            container.style.backgroundColor = "#D4A017"; // くすんだ黄色
            status.innerText = "質疑応答"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec; // 質疑からは0からカウントアップ
        }}
        else {{ 
            container.style.backgroundColor = "#A52A2A"; // くすんだ赤
            status.innerText = "終了時間"; 
            displaySec = isCountdown ? (totalSec - b2) : totalSec;
        }}

        const mm = String(Math.floor(displaySec / 60)).padStart(2, '0');
        const ss = String(displaySec % 60).padStart(2, '0');
        document.getElementById('display').innerText = mm + ":" + ss;

        // 鈴の制御（内部時間は常に進むため、条件は統一でOK）
        if (totalSec !== lastPlayed) {{
            if (totalSec === b1 && !isMuted) sounds["1"].play().catch(e => {{}});
            if (totalSec === b2 && !isMuted) sounds["2"].play().catch(e => {{}});
            if (totalSec === b3) sounds["3"].play().catch(e => {{}});
            lastPlayed = totalSec;
        }}
    }}

    // SE様提案の requestAnimationFrame ループ
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
            requestAnimationFrame(loop); // setIntervalから変更
        }}
    }}
    
    function stopTimer() {{ running = false; }}
    
    function resetTimer() {{
        running = false; setPhysicalLock(false); elapsed = 0; lastPlayed = -1;
        updateDisplay(); // モードは維持したままリセット
    }}

    // SE様提案のキーボードショートカット
    document.addEventListener("keydown", (e) => {{
        if (e.code === "Space") {{ playClick(); startTimer(); e.preventDefault(); }}
        if (e.code === "KeyS") {{ playClick(); stopTimer(); }}
        if (e.code === "KeyR") {{ playClick(); resetTimer(); }}
    }});

    updateDisplay();
</script>
"""

st.components.v1.html(js_code, height=950)