# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v7.6 Complete Hybrid
# 修正：表示崩れ防止と、テストボタン・音量の完全動作を両立
# ==========================================

import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

# 1. 共通スタイル（外側の設定エリア用）
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem;}
    header, footer {visibility: hidden;}
    input[type="number"] { font-size: 2.2rem !important; font-weight: 700 !important; text-align: center !important; }
    .label-text { font-size: 1.1rem; font-weight: bold; color: #333; text-align: center; }
    div[data-testid="stNumberInput"] { max-width: 130px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. Python側の設定エリア
buf1, c1, c2, c3, buf2 = st.columns([1.5, 1, 1, 1, 2.5])
with c1:
    st.markdown('<div class="label-text">鈴1 (分)</div>', unsafe_allow_html=True)
    b1_m = st.number_input("b1", value=6, step=1, key="b1", label_visibility="collapsed")
with c2:
    st.markdown('<div class="label-text">鈴2 (分)</div>', unsafe_allow_html=True)
    b2_m = st.number_input("b2", value=7, step=1, key="b2", label_visibility="collapsed")
with c3:
    st.markdown('<div class="label-text">鈴3 (分)</div>', unsafe_allow_html=True)
    b3_m = st.number_input("b3", value=10, step=1, key="b3", label_visibility="collapsed")

# 3. メインコンテンツ（HTML/CSS/JSを一括でiframeに渡す）
b1_s, b2_s, b3_s = b1_m * 60, b2_m * 60, b3_m * 60

final_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ margin: 0; padding: 0; font-family: sans-serif; background: white; overflow: hidden; }}
    #main-wrapper {{ display: flex; flex-direction: column; align-items: center; width: 100%; padding: 0 10px; box-sizing: border-box; }}
    
    /* 音量・テストエリアをiframe内に配置して確実に動作させる */
    .top-controls {{ 
        display: flex; align-items: center; justify-content: flex-end; 
        width: 100%; gap: 15px; margin-bottom: 10px; padding-right: 20px; 
    }}
    .vol-box {{ display: flex; flex-direction: column; align-items: center; gap: 2px; }}
    .test-btn {{ background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 4px 10px; font-size: 0.75rem; cursor: pointer; }}

    #timer-container {{ 
        width: 100%; height: 50vh; background-color: #007BFF; color: white; 
        border-radius: 25px; display: flex; flex-direction: column; 
        justify-content: center; align-items: center; box-shadow: 0 6px 20px rgba(0,0,0,0.15); 
    }}
    #status {{ font-size: 8.5vw; font-weight: 700; margin-bottom: 3vw; }}
    #display {{ font-size: 14vw; font-weight: 700; font-variant-numeric: tabular-nums; }}

    .button-area {{ margin-top: 15px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; }}
    .btn {{ border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 140px; }}
    
    #help-modal {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; z-index: 100; justify-content: center; align-items: center; }}
    #help-content {{ background: white; color: #333; padding: 25px; border-radius: 20px; max-width: 550px; width: 85%; position: relative; }}
</style>
</head>
<body onclick="unlockAudio()">

<div id="main-wrapper">
    <div class="top-controls">
        <div class="vol-box">
            <span id="vol-label" style="font-size:0.7rem; font-weight:bold; color:#666;">鈴音量: 80%</span>
            <input type="range" min="0" max="100" value="80" oninput="updateVolume(this.value)" style="width:100px; cursor:pointer;">
        </div>
        <div style="display:flex; gap:5px;">
            <button class="test-btn" onclick="testBell('1')">🔔 1回</button>
            <button class="test-btn" onclick="testBell('2')">🔔 2回</button>
            <button class="test-btn" onclick="testBell('3')">🔔 3回</button>
        </div>
    </div>

    <div id="progress-outer-container" style="width: 100%; height: 35px; background: #e0e0e0; border-radius: 18px; overflow: hidden; position: relative; display: flex; border: 1px solid #bbb; margin-bottom:10px;">
        <div id="bar-done" style="height:100%; width:0%; background: transparent;"></div>
        <div id="bar-blue" style="height:100%; width:0%; background: linear-gradient(to bottom, #4facfe, #007BFF);"></div>
        <div id="bar-yellow" style="height:100%; width:0%; background: linear-gradient(to bottom, #fff3b0, #FFD700);"></div>
        <div id="bar-red" style="position: absolute; top:0; left:0; height:100%; width:0%; z-index:1; background: linear-gradient(to bottom, #ffcccc, #FF0000);"></div>
        <div id="progress-marks" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:2; pointer-events:none;"></div>
    </div>

    <div id="timer-container">
        <div id="status">発表時間</div>
        <div id="display">00:00</div>
    </div>
    
    <div class="button-area">
        <button class="btn" style="background-color: #87CEEB;" onclick="handleAction('start')">▶ START</button>
        <button class="btn" style="background-color: #FFB6C1;" onclick="handleAction('stop')">|| STOP</button>
        <button class="btn" style="background-color: #98FB98;" onclick="handleAction('reset')">🔄 RESET</button>
        <button class="btn" style="background-color: #6C757D; color: white;" onclick="handleAction('mode')">🔽 表示切替</button>
        <button id="mute-btn" class="btn" style="background-color: #E1F5FE; border: 1px solid #007BFF; color: #007BFF;" onclick="handleAction('mute')">🔔 鈴1,2：有効</button>
        <button class="btn" style="background-color: #343a40; color: white;" onclick="parent.location.reload();">🔄 同期</button>
        <button class="btn" style="background-color: #eee;" onclick="toggleHelp(true)">❓ 使い方</button>
    </div>
</div>

<div id="help-modal">
    <div id="help-content">
        <span onclick="toggleHelp(false)" style="position:absolute; right:15px; top:10px; cursor:pointer; font-size:1.5rem; color:#aaa;">×</span>
        <h3 style="color:#007BFF; border-bottom:2px solid #007BFF; text-align:center; margin-top:0;">💡 学会タイマーたけださんの使い方</h3>
        <div style="font-size:0.9rem; line-height:1.7; color:#333;">
            <p>〇発表時間設定：鈴１回（発表終了１分前）、鈴２回（発表終了時間）、鈴３回（質疑終了）の各分数を設定できます。</p>
            <p>〇表示切替：経過時間と残り時間の表示を切り替えます。</p>
            <p>〇鈴１，２ミュートボタン：鈴１回と鈴２回を消音できます。</p>
            <div style="margin-top:15px; padding:10px; background:#f8f9fa; border-radius:10px; font-size:0.8rem;">
                <b>⌨️ キーボード:</b> [Space]開始/停止, [R]リセット, [M]ミュート
            </div>
        </div>
    </div>
</div>

<script>
    const B1_LIMIT = {b1_s}, B2_LIMIT = {b2_s}, B3_LIMIT = {b3_s};
    let currentVolume = 0.8;
    let startTime = 0, elapsed = 0, running = false, lastPlayed = -1;
    let isCountdown = false, isMuted = false;

    const bellSounds = {{
        "1": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        "2": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        "3": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    }};

    function updateVolume(val) {{
        currentVolume = val / 100;
        document.getElementById('vol-label').innerText = "鈴音量: " + val + "%";
        Object.values(bellSounds).forEach(s => s.volume = currentVolume);
    }}

    function testBell(num) {{
        const s = bellSounds[num]; s.currentTime = 0; s.play().catch(e=>{{}});
    }}

    function handleAction(type) {{
        if (type === 'start' && !running) {{ running = true; startTime = performance.now() - elapsed; requestAnimationFrame(loop); }}
        if (type === 'stop') running = false;
        if (type === 'reset') {{ running = false; elapsed = 0; lastPlayed = -1; updateDisplay(); }}
        if (type === 'mode') {{ isCountdown = !isCountdown; updateDisplay(); }}
        if (type === 'mute') {{ 
            isMuted = !isMuted; document.getElementById('mute-btn').innerText = isMuted ? "✕ 鈴1,2：消音" : "🔔 鈴1,2：有効";
        }}
    }}

    function updateDisplay() {{
        const totalSec = Math.floor(elapsed / 1000);
        const container = document.getElementById('timer-container'), displayEl = document.getElementById('display'), status = document.getElementById('status');
        const bDone = document.getElementById('bar-done'), bBlue = document.getElementById('bar-blue'), bYellow = document.getElementById('bar-yellow'), bRed = document.getElementById('bar-red');
        
        const minPct = 100 / (B3_LIMIT / 60);
        document.getElementById('progress-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) ${{minPct}}%)`;

        if (totalSec < B2_LIMIT) {{
            container.style.backgroundColor = "#007BFF"; status.innerText = isCountdown ? "残り時間" : "発表時間"; 
            let d = isCountdown ? (B2_LIMIT - totalSec) : totalSec;
            updateTimeStr(d);
            bDone.style.width = (totalSec / B3_LIMIT * 100) + "%"; 
            bBlue.style.width = ((B2_LIMIT - totalSec) / B3_LIMIT * 100) + "%"; 
            bYellow.style.width = ((B3_LIMIT - B2_LIMIT) / B3_LIMIT * 100) + "%";
        }} else if (totalSec < B3_LIMIT) {{
            container.style.backgroundColor = "#D4A017"; status.innerText = "質疑応答"; 
            let d = isCountdown ? (totalSec - B2_LIMIT) : totalSec;
            updateTimeStr(d);
            bDone.style.width = (totalSec / B3_LIMIT * 100) + "%"; bBlue.style.width = "0%";
            bYellow.style.width = ((B3_LIMIT - totalSec) / B3_LIMIT * 100) + "%";
        }} else {{
            container.style.backgroundColor = "#A52A2A"; status.innerText = "終了時間";
            updateTimeStr(totalSec - B2_LIMIT);
            bRed.style.width = "100%";
        }}

        if (totalSec !== lastPlayed) {{
            if (totalSec === B1_LIMIT && !isMuted) bellSounds["1"].play();
            if (totalSec === B2_LIMIT && !isMuted) bellSounds["2"].play();
            if (totalSec === B3_LIMIT) bellSounds["3"].play();
            lastPlayed = totalSec;
        }}
    }}
    function updateTimeStr(s) {{
        const mm = String(Math.floor(s / 60)).padStart(2, '0'), ss = String(s % 60).padStart(2, '0');
        document.getElementById('display').innerText = mm + ":" + ss;
    }}
    function loop() {{ if (running) {{ elapsed = performance.now() - startTime; updateDisplay(); requestAnimationFrame(loop); }} }}
    function toggleHelp(s) {{ document.getElementById('help-modal').style.display = s ? 'flex' : 'none'; }}
    document.addEventListener('keydown', (e) => {{
        if (e.code === "Space") handleAction(running ? 'stop' : 'start');
        if (e.key.toLowerCase() === "r") handleAction('reset');
        if (e.key.toLowerCase() === "m") handleAction('mute');
    }});
    updateDisplay();
</script>
</body>
</html>
"""

st.components.v1.html(final_content, height=850)
