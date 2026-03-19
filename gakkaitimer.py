# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v5.7 Hybrid Sound Edition
# 方式：クリック音(Web Audio合成) / ベル音(GitHub mp3)
# Created by Takeda Healthcare Foundation
# 2026/3/19  
# ==========================================

import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    input[type="number"] { font-size: 2.2rem !important; font-weight: 700 !important; text-align: center !important; }
    .label-text { font-size: 1.1rem; font-weight: bold; color: #333; text-align: center; }
    div[data-testid="stNumberInput"] { max-width: 130px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 設定エリア ---
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

b1_s, b2_s, b3_s = b1_m * 60, b2_m * 60, b3_m * 60

js_code = f"""
<style>
    #main-wrapper {{ display: flex; flex-direction: column; align-items: center; font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; width: 100%; background: white; }}
    #progress-outer-container {{ width: 100%; height: 40px; background: #e0e0e0; border-radius: 20px; margin: 5px 0 10px 0; box-shadow: inset 0 3px 8px rgba(0,0,0,0.2); overflow: hidden; position: relative; display: flex; border: 1px solid #bbb; }}
    .liquid-segment {{ height: 100%; transition: width 0.1s linear; }}
    #bar-empty {{ width: 0%; background: transparent; }}
    #bar-blue {{ background: linear-gradient(to bottom, #4facfe 0%, #007BFF 50%, #0056b3 100%); }}
    #bar-yellow {{ background: linear-gradient(to bottom, #fff3b0 0%, #FFD700 50%, #b89b00 100%); }}
    #bar-red {{ position: absolute; top:0; left:0; height:100%; width:0%; z-index:1; background: linear-gradient(to bottom, #ffcccc 0%, #FF0000 50%, #b30000 100%); transition: width 0.3s; }}
    #progress-marks {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }}
    #progress-highlight {{ position: absolute; top: 2px; left: 10px; right: 10px; height: 35%; background: linear-gradient(to bottom, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0) 100%); border-radius: 20px; filter: blur(1px); z-index: 3; pointer-events: none; }}
    #timer-container {{ width: 100%; height: 52vh; background-color: #007BFF; color: white; border-radius: 25px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 6px 20px rgba(0,0,0,0.15); padding-top: 1vh; padding-bottom: 1vh; }}
    #status {{ font-size: 9vw; font-weight: 700; line-height: 0.8; margin-bottom: 1.5vw; opacity: 0.95; }}
    #display {{ font-size: 14vw; font-weight: 700; line-height: 0.8; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }}
    .colon {{ vertical-align: middle; position: relative; top: -0.05em; }}
    .button-area {{ margin-top: 20px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; }}
    .btn {{ border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 150px; transition: 0.1s; }}
    .btn:active {{ transform: scale(0.92); filter: brightness(0.9); }}
</style>

<div id="main-wrapper" onclick="unlockAudio()">
    <div id="progress-outer-container">
        <div id="bar-empty" class="liquid-segment"></div>
        <div id="bar-blue" class="liquid-segment"></div>
        <div id="bar-yellow" class="liquid-segment"></div>
        <div id="bar-red"></div>
        <div id="progress-marks"></div>
        <div id="progress-highlight"></div>
    </div>
    <div id="timer-container">
        <div id="status">発表時間</div>
        <div id="display">00<span class="colon">:</span>00</div>
    </div>
    <div class="button-area">
        <button class="btn" style="background-color: #87CEEB;" onclick="handleAction('start')">▶ START</button>
        <button class="btn" style="background-color: #FFB6C1;" onclick="handleAction('stop')">|| STOP</button>
        <button class="btn" style="background-color: #98FB98;" onclick="handleAction('reset')">🔄 RESET</button>
        <button class="btn" style="background-color: #6C757D; color: white;" onclick="handleAction('mode')">🔽 表示切替</button>
        <button id="mute-btn" class="btn" style="background-color: #E1F5FE; border: 1px solid #007BFF; color: #007BFF;" onclick="handleAction('mute')">🔔 鈴1,2：有効</button>
        <button class="btn" style="background-color: #343a40; color: white;" onclick="toggleFullscreen()">🔳 全画面</button>
    </div>
</div>

<script>
    let startTime = 0, elapsed = 0, running = false, lastPlayed = -1, isCountdown = false, isMuted = false;
    let audioCtx = null;
    const b1 = {b1_s}, b2 = {b2_s}, b3 = {b3_s};
    
    // 【ベル音】GitHubからの外部読み込み
    const bellSounds = {{
        "1": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        "2": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        "3": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    }};

    // オーディオ初期化とアンロック
    function unlockAudio() {{
        if (!audioCtx) {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            Object.values(bellSounds).forEach(s => {{ 
                s.play().then(()=>{{s.pause(); s.currentTime=0;}}).catch(e=>{{}}); 
            }});
        }}
        if (audioCtx.state === 'suspended') audioCtx.resume();
    }}

    // 【クリック音】Web Audio APIによる合成（ポッという短い音）
    function synthClick() {{
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.05);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.05);
    }}

    function handleAction(type) {{
        unlockAudio();
        synthClick();
        if (type === 'start' && !running) {{ running = true; startTime = performance.now() - elapsed; requestAnimationFrame(loop); }}
        if (type === 'stop') running = false;
        if (type === 'reset') {{ running = false; elapsed = 0; lastPlayed = -1; updateDisplay(); }}
        if (type === 'mode') {{ isCountdown = !isCountdown; updateDisplay(); }}
        if (type === 'mute') {{ 
            isMuted = !isMuted; 
            const mbtn = document.getElementById('mute-btn');
            mbtn.innerHTML = isMuted ? '<span style="color:#ff4b4b;">✕</span> 鈴1,2：消音中' : '🔔 鈴1,2：有効';
            mbtn.style.backgroundColor = isMuted ? "#f5f5f5" : "#E1F5FE";
        }}
    }}

    function toggleFullscreen() {{
        synthClick();
        let elem = document.getElementById("main-wrapper");
        if (!document.fullscreenElement) elem.requestFullscreen().catch(e => {{}});
        else document.exitFullscreen();
    }}

    function updateDisplay() {{
        const totalSec = Math.floor(elapsed / 1000);
        let displaySec = 0;
        const container = document.getElementById('timer-container'), status = document.getElementById('status'), displayEl = document.getElementById('display');
        const minPct = 100 / (b3 / 60);
        document.getElementById('progress-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) ${{minPct}}%)`;

        if (totalSec < b2) {{
            container.style.backgroundColor = "#007BFF"; status.innerText = isCountdown ? "残り時間" : "発表時間"; displaySec = isCountdown ? (b2 - totalSec) : totalSec;
            document.getElementById('bar-empty').style.width = (totalSec / b3 * 100) + "%";
            document.getElementById('bar-blue').style.width = ((b2 - totalSec) / b3 * 100) + "%";
            document.getElementById('bar-yellow').style.width = ((b3 - b2) / b3 * 100) + "%";
        }} else if (totalSec < b3) {{
            container.style.backgroundColor = "#D4A017"; status.innerText = "質疑応答"; displaySec = isCountdown ? (totalSec - b2) : totalSec;
            document.getElementById('bar-empty').style.width = (totalSec / b3 * 100) + "%";
            document.getElementById('bar-blue').style.width = "0%";
            document.getElementById('bar-yellow').style.width = ((b3 - totalSec) / b3 * 100) + "%";
        }} else {{
            container.style.backgroundColor = "#A52A2A"; status.innerText = "終了時間"; displaySec = isCountdown ? (totalSec - b2) : totalSec;
            document.getElementById('bar-red').style.width = "100%";
        }}

        const mm = String(Math.floor(displaySec / 60)).padStart(2, '0'), ss = String(displaySec % 60).padStart(2, '0');
        displayEl.innerHTML = mm + '<span class="colon">:</span>' + ss;

        if (totalSec !== lastPlayed) {{
            if (totalSec === b1 && !isMuted) bellSounds["1"].play().catch(e=>{{}});
            if (totalSec === b2 && !isMuted) bellSounds["2"].play().catch(e=>{{}});
            if (totalSec === b3) bellSounds["3"].play().catch(e=>{{}});
            lastPlayed = totalSec;
        }}
    }}
    function loop() {{ if (running) {{ elapsed = performance.now() - startTime; updateDisplay(); requestAnimationFrame(loop); }} }}
    updateDisplay();
</script>
"""

st.components.v1.html(js_code, height=900)
