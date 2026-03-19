# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v7.3 Debugged Edition
# 修正：CSS内の波括弧による NameError を修正
# ==========================================

import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

# 1. 共通CSSスタイルの定義（ここは変数展開しないので普通の文字列）
common_style = """
<style>
    .block-container {padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    input[type="number"] { font-size: 2.2rem !important; font-weight: 700 !important; text-align: center !important; }
    .label-text { font-size: 1.1rem; font-weight: bold; color: #333; text-align: center; }
    div[data-testid="stNumberInput"] { max-width: 130px; margin: 0 auto; }
    .test-area { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 5px; border-left: 1px solid #eee; padding-left: 10px; }
    .test-btn { background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 2px 8px; font-size: 0.75rem; cursor: pointer; width: 75px; transition: 0.2s; }
    .test-btn:hover { background: #e2e6ea; }
    .vol-container { display: flex; flex-direction: column; align-items: center; gap: 2px; }
    input[type=range] { width: 80px; cursor: pointer; }
    #vol-label { font-size: 0.7rem; color: #666; font-weight: bold; }
    
    #main-wrapper { display: flex; flex-direction: column; align-items: center; font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; width: 100%; background: white; padding: 0 30px; box-sizing: border-box; }
    .button-area { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; }
    .btn { border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 150px; transition: 0.1s; outline: none; }
    .btn:active { transform: scale(0.92); filter: brightness(0.9); }
    #footer-credit { margin-top: 25px; text-align: center; color: #aaa; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; width: 85%; line-height: 1.6; }
    #help-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); color: white; display: none; z-index: 9999; justify-content: center; align-items: center; }
    #help-content { background: #fff; color: #333; padding: 30px; border-radius: 20px; max-width: 650px; width: 90%; position: relative; }
    .close-btn { position: absolute; top: 10px; right: 15px; font-size: 1.5rem; cursor: pointer; color: #aaa; }
</style>
"""
st.markdown(common_style, unsafe_allow_html=True)

# 2. 設定エリア（Python側）
buf1, c1, c2, c3, c_test, buf2 = st.columns([1.5, 1, 1, 1, 1.8, 0.7])
with c1:
    st.markdown('<div class="label-text">鈴1 (分)</div>', unsafe_allow_html=True)
    b1_m = st.number_input("b1", value=6, step=1, key="b1", label_visibility="collapsed")
with c2:
    st.markdown('<div class="label-text">鈴2 (分)</div>', unsafe_allow_html=True)
    b2_m = st.number_input("b2", value=7, step=1, key="b2", label_visibility="collapsed")
with c3:
    st.markdown('<div class="label-text">鈴3 (分)</div>', unsafe_allow_html=True)
    b3_m = st.number_input("b3", value=10, step=1, key="b3", label_visibility="collapsed")

with c_test:
    st.markdown("""
    <div class="test-area">
        <div style="display:flex; gap:10px; align-items:center;">
            <div class="vol-container">
                <div id="vol-label">鈴音量: --%</div>
                <input type="range" id="volume-slider" min="0" max="100" value="80" oninput="updateVolume(this.value)">
            </div>
            <div style="display:flex; flex-direction:column; gap:3px;">
                <button class="test-btn" onclick="testBell('1')">🔔 1回</button>
                <button class="test-btn" onclick="testBell('2')">🔔 2回</button>
                <button class="test-btn" onclick="testBell('3')">🔔 3回</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 3. メインJavaScript & HTML（動的な値だけ f-string で埋め込み、他は {{ }} でエスケープ）
b1_s, b2_s, b3_s = b1_m * 60, b2_m * 60, b3_m * 60

js_html_content = f"""
<script>
    const B1_LIMIT = {b1_s}, B2_LIMIT = {b2_s}, B3_LIMIT = {b3_s};
    
    if (typeof window.currentVolume === 'undefined') {{
        window.currentVolume = parseFloat(localStorage.getItem("takeda_timer_volume")) || 0.8;
        window.startTime = 0; window.elapsed = 0; window.running = false; window.lastPlayed = -1;
        window.isCountdown = false; window.isMuted = false;
    }}

    const bellSounds = {{
        "1": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        "2": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        "3": new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    }};

    function syncUI() {{
        const volSlider = document.getElementById('volume-slider');
        const volLabel = document.getElementById('vol-label');
        if (volSlider && volLabel) {{
            volSlider.value = window.currentVolume * 100;
            volLabel.innerText = "鈴音量: " + Math.round(window.currentVolume * 100) + "%";
        }}
    }}
    setTimeout(syncUI, 100);

    window.updateVolume = function(val) {{
        window.currentVolume = val / 100;
        document.getElementById('vol-label').innerText = "鈴音量: " + val + "%";
        Object.values(bellSounds).forEach(s => s.volume = window.currentVolume);
        localStorage.setItem("takeda_timer_volume", window.currentVolume);
    }};

    function unlockAudio() {{
        if (!window.audioCtx) {{
            window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            Object.values(bellSounds).forEach(s => {{ s.volume = window.currentVolume; s.load(); }});
        }}
        if (window.audioCtx.state === 'suspended') window.audioCtx.resume();
    }}

    function synthClick() {{
        if (!window.audioCtx) return;
        const osc = window.audioCtx.createOscillator(), gain = window.audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(1200, window.audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, window.audioCtx.currentTime + 0.05);
        gain.gain.setValueAtTime(0.1, window.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, window.audioCtx.currentTime + 0.05);
        osc.connect(gain); gain.connect(window.audioCtx.destination);
        osc.start(); osc.stop(window.audioCtx.currentTime + 0.05);
    }}

    window.testBell = function(num) {{ unlockAudio(); synthClick(); const s = bellSounds[num]; s.volume = window.currentVolume; s.currentTime = 0; s.play().catch(e => {{}}); }};

    document.addEventListener('keydown', (e) => {{
        if (e.target.tagName === 'INPUT') return;
        if (e.code === "Space") {{ e.preventDefault(); handleAction(window.running ? 'stop' : 'start'); }}
        if (e.key.toLowerCase() === "r") handleAction('reset');
        if (e.key.toLowerCase() === "m") handleAction('mute');
    }});

    function toggleHelp(show) {{ synthClick(); document.getElementById('help-modal').style.display = show ? 'flex' : 'none'; }}

    function handleAction(type) {{
        unlockAudio(); synthClick();
        if (type === 'start' && !window.running) {{ window.running = true; window.startTime = performance.now() - window.elapsed; requestAnimationFrame(loop); }}
        if (type === 'stop') window.running = false;
        if (type === 'reset') {{ window.running = false; window.elapsed = 0; window.lastPlayed = -1; updateDisplay(); }}
        if (type === 'mode') {{ window.isCountdown = !window.isCountdown; updateDisplay(); }}
        if (type === 'mute') {{ 
            window.isMuted = !window.isMuted; const mbtn = document.getElementById('mute-btn');
            mbtn.innerHTML = window.isMuted ? '<span style="color:#ff4b4b;">✕</span> 鈴1,2：消音中' : '🔔 鈴1,2：有効 (M)';
            mbtn.style.backgroundColor = window.isMuted ? "#f5f5f5" : "#E1F5FE";
        }}
    }}
    
    function toggleFullscreen() {{
        synthClick(); let elem = document.getElementById("main-wrapper");
        if (!document.fullscreenElement) elem.requestFullscreen().catch(e => {{}});
        else document.exitFullscreen();
    }}
    
    function updateDisplay() {{
        const totalSec = Math.floor(window.elapsed / 1000);
        let displaySec = 0;
        const container = document.getElementById('timer-container'), status = document.getElementById('status'), displayEl = document.getElementById('display');
        const barDone = document.getElementById('bar-done'), barBlue = document.getElementById('bar-blue'), barYellow = document.getElementById('bar-yellow'), barRed = document.getElementById('bar-red');
        
        const totalMinutes = B3_LIMIT / 60;
        const minPct = 100 / totalMinutes;
        document.getElementById('progress-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${{minPct}}% - 1px), rgba(0,0,0,0.15) calc(${{minPct}}% - 1px), rgba(0,0,0,0.15) ${{minPct}}%)`;
        
        if (totalSec < B2_LIMIT) {{
            container.style.backgroundColor = "#007BFF"; status.innerText = window.isCountdown ? "残り時間" : "発表時間"; displaySec = window.isCountdown ? (B2_LIMIT - totalSec) : totalSec;
            barDone.style.width = (totalSec / B3_LIMIT * 100) + "%";
            barBlue.style.width = ((B2_LIMIT - totalSec) / B3_LIMIT * 100) + "%";
            barYellow.style.width = ((B3_LIMIT - B2_LIMIT) / B3_LIMIT * 100) + "%";
            barRed.style.width = "0%";
        }} else if (totalSec < B3_LIMIT) {{
            container.style.backgroundColor = "#D4A017"; status.innerText = "質疑応答"; displaySec = window.isCountdown ? (totalSec - B2_LIMIT) : totalSec;
            barDone.style.width = (totalSec / B3_LIMIT * 100) + "%";
            barBlue.style.width = "0%";
            barYellow.style.width = ((B3_LIMIT - totalSec) / B3_LIMIT * 100) + "%";
            barRed.style.width = "0%";
        }} else {{
            container.style.backgroundColor = "#A52A2A"; status.innerText = "終了時間"; displaySec = window.isCountdown ? (totalSec - B2_LIMIT) : totalSec;
            barDone.style.width = "0%"; barBlue.style.width = "0%"; barYellow.style.width = "0%";
            barRed.style.width = "100%";
        }}
        
        const mm = String(Math.floor(displaySec / 60)).padStart(2, '0'), ss = String(displaySec % 60).padStart(2, '0');
        displayEl.innerHTML = mm + '<span class="colon">:</span>' + ss;
        
        if (totalSec !== window.lastPlayed) {{
            if (totalSec === B1_LIMIT && !window.isMuted) bellSounds["1"].play().catch(e=>{{}});
            if (totalSec === B2_LIMIT && !window.isMuted) bellSounds["2"].play().catch(e=>{{}});
            if (totalSec === B3_LIMIT) bellSounds["3"].play().catch(e=>{{}});
            window.lastPlayed = totalSec;
        }}
    }}
    function loop() {{ if (window.running) {{ window.elapsed = performance.now() - window.startTime; updateDisplay(); requestAnimationFrame(loop); }} }}
    updateDisplay();
</script>

<div id="main-wrapper" onclick="unlockAudio()">
    <div id="progress-outer-container" style="width: 100%; height: 40px; background: #e0e0e0; border-radius: 20px; margin: 5px 0 10px 0; box-shadow: inset 0 3px 8px rgba(0,0,0,0.2); overflow: hidden; position: relative; display: flex; border: 1px solid #bbb;">
        <div id="bar-done" style="height:100%; width:0%; background: transparent; transition: width 0.1s linear;"></div>
        <div id="bar-blue" style="height:100%; width:0%; background: linear-gradient(to bottom, #4facfe 0%, #007BFF 50%, #0056b3 100%); transition: width 0.1s linear;"></div>
        <div id="bar-yellow" style="height:100%; width:0%; background: linear-gradient(to bottom, #fff3b0 0%, #FFD700 50%, #b89b00 100%); transition: width 0.1s linear;"></div>
        <div id="bar-red" style="position: absolute; top:0; left:0; height:100%; width:0%; z-index:1; background: linear-gradient(to bottom, #ffcccc 0%, #FF0000 50%, #b30000 100%); transition: width 0.3s;"></div>
        <div id="progress-marks" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none;"></div>
        <div id="progress-highlight" style="position: absolute; top: 2px; left: 10px; right: 10px; height: 35%; background: linear-gradient(to bottom, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0) 100%); border-radius: 20px; filter: blur(1px); z-index: 3; pointer-events: none;"></div>
    </div>

    <div id="timer-container" style="width: 100%; height: 52vh; background-color: #007BFF; color: white; border-radius: 25px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 6px 20px rgba(0,0,0,0.15); padding-top: 1vh; padding-bottom: 1vh;">
        <div id="status" style="font-size: 8.5vw; font-weight: 700; line-height: 1.0; margin-bottom: 4vw; opacity: 0.95; letter-spacing: 0.05em;">発表時間</div>
        <div id="display" style="font-size: 14vw; font-weight: 700; line-height: 0.8; font-variant-numeric: tabular-nums; letter-spacing: -0.02em;">00<span class="colon">:</span>00</div>
    </div>
    
    <div class="button-area">
        <button class="btn" style="background-color: #87CEEB;" onclick="handleAction('start')">▶ START (Space)</button>
        <button class="btn" style="background-color: #FFB6C1;" onclick="handleAction('stop')">|| STOP (Space)</button>
        <button class="btn" style="background-color: #98FB98;" onclick="handleAction('reset')">🔄 RESET (R)</button>
        <button class="btn" style="background-color: #6C757D; color: white;" onclick="handleAction('mode')">🔽 表示切替</button>
        <button id="mute-btn" class="btn" style="background-color: #E1F5FE; border: 1px solid #007BFF; color: #007BFF;" onclick="handleAction('mute')">🔔 鈴1,2：有効 (M)</button>
        <button class="btn" style="background-color: #343a40; color: white;" onclick="toggleFullscreen()">🔳 全画面</button>
        <button class="btn" style="background-color: #eee;" onclick="toggleHelp(true)">❓ 使い方</button>
    </div>
    <div id="footer-credit">
        <div>学会タイマーたけださん v7.3</div>
        <div>&copy; 2026 <b>Takeda Healthcare Foundation</b>. All Rights Reserved.</div>
    </div>
</div>

<div id="help-modal">
    <div id="help-content">
        <span class="close-btn" onclick="toggleHelp(false)">×</span>
        <h3 style="color:#007BFF; border-bottom:2px solid #007BFF; margin-top:0; padding-bottom:10px; text-align:center;">💡 学会タイマーたけださんの使い方</h3>
        <div style="font-size:0.95rem; line-height:1.8; color:#333; text-align:left;">
            <p style="margin: 15px 0;">〇発表時間設定：鈴１回（発表終了１分前）、鈴２回（発表終了時間）、鈴３回（質疑終了）の各分数を設定できます。</p>
            <p style="margin: 15px 0;">〇表示切替：発表経過時間（カウントアップ）と発表残り時間（カウントダウン）の表示を切り替えます。</p>
            <p style="margin: 15px 0;">〇鈴１，２ミュートボタン：鈴１回と鈴２回を消音できます。</p>
            <div style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 10px; font-size: 0.85rem;">
                <b>⌨️ キーボードショートカット:</b><br>
                ・[Space] 開始 / 停止<br>
                ・[R] リセット<br>
                ・[M] 鈴1,2のミュート切替
            </div>
        </div>
    </div>
</div>
"""
st.components.v1.html(js_html_content, height=920)
