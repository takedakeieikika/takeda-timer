# ==========================================
# システム名：学会タイマーたけださん
# バージョン：v7.3 Full Feature Edition
# 修正：使い方ボタン(モーダル)とクレジット表示を復活。
#       テストボタンのクリック音なし、設定保存機能も継続。
# ==========================================

import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container {padding: 0 !important;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

html_code = """
<div id="app-container">
    <div class="config-bar">
        <div class="input-group">
            <span class="label">鈴1(分)</span>
            <input type="number" id="m1" value="6" min="0" onchange="saveSettings()">
        </div>
        <div class="input-group">
            <span class="label">鈴2(分)</span>
            <input type="number" id="m2" value="7" min="0" onchange="saveSettings()">
        </div>
        <div class="input-group">
            <span class="label">鈴3(分)</span>
            <input type="number" id="m3" value="10" min="0" onchange="saveSettings()">
        </div>
        
        <div class="vol-section">
            <div id="vol-label">鈴音量: 80%</div>
            <input type="range" id="vol-slider" min="0" max="100" value="80">
        </div>
        
        <div class="test-bell-group">
            <button onclick="testBell(1)">🔔1</button>
            <button onclick="testBell(2)">🔔2</button>
            <button onclick="testBell(3)">🔔3</button>
        </div>
    </div>

    <div id="progress-container">
        <div id="bar-blue" class="bar"></div>
        <div id="bar-yellow" class="bar"></div>
        <div id="bar-red" class="bar"></div>
        <div id="progress-marks"></div>
    </div>

    <div id="timer-panel">
        <div id="status-text">発表時間</div>
        <div id="time-display">00:00</div>
    </div>

    <div class="controls">
        <button class="btn btn-start" onclick="handleAction('start')">▶ START (Space)</button>
        <button class="btn btn-stop" onclick="handleAction('stop')">|| STOP</button>
        <button class="btn btn-reset" onclick="handleAction('reset')">🔄 RESET (R)</button>
        <button class="btn btn-mode" onclick="handleAction('mode')">表示切替</button>
        <button id="mute-btn" class="btn btn-mute" onclick="handleAction('mute')">🔔 鈴1,2：有効 (M)</button>
        <button class="btn btn-fs" onclick="toggleFS()">🔳 全画面</button>
        <button class="btn btn-help" onclick="toggleHelp(true)">❓ 使い方</button>
    </div>

    <div id="footer-credit">
        <div>学会タイマーたけださん v7.3</div>
        <div>&copy; 2026 <b>Takeda Healthcare Foundation</b>. All Rights Reserved.</div>
    </div>
</div>

<div id="help-modal">
    <div id="help-content">
        <span class="close-btn" onclick="toggleHelp(false)">×</span>
        <h3 style="color:#007BFF; border-bottom:2px solid #007BFF; margin:0 0 15px 0; padding-bottom:5px;">💡 使い方</h3>
        <div style="font-size:0.9rem; line-height:1.6; text-align:left; color:#333;">
            <p><b>⌨️ ショートカット:</b><br>
               ・[Space] 開始/停止<br>
               ・[R] リセット / [M] 消音切替</p>
            <p><b>〇時間設定:</b> 数値を変更すると自動保存されます。</p>
            <p><b>〇音量:</b> スライダーで調整。テストボタンは操作音なしで確認できます。</p>
        </div>
    </div>
</div>

<style>
    :root { --blue: #007BFF; --yellow: #D4A017; --red: #A52A2A; }
    body { margin: 0; font-family: 'Helvetica Neue', Arial, sans-serif; background: #fff; overflow: hidden; }
    #app-container { display: flex; flex-direction: column; align-items: center; padding: 10px 20px; box-sizing: border-box; width: 100vw; }
    
    .config-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; padding: 5px; border-bottom: 1px solid #eee; width: 100%; justify-content: center; }
    .input-group input { width: 60px; font-size: 1.3rem; text-align: center; font-weight: bold; border: 1px solid #ccc; border-radius: 5px; }
    .vol-section { display: flex; flex-direction: column; align-items: center; border-left: 1px solid #ddd; padding-left: 12px; }
    
    #progress-container { width: 100%; height: 32px; background: #eee; border-radius: 16px; position: relative; overflow: hidden; border: 1px solid #bbb; margin-bottom: 8px; display: flex; }
    .bar { height: 100%; transition: width 0.1s linear; }
    #bar-blue { background: linear-gradient(to bottom, #4facfe, #007BFF); }
    #bar-yellow { background: linear-gradient(to bottom, #fff3b0, #FFD700); }
    #bar-red { position: absolute; left: 0; top: 0; background: linear-gradient(to bottom, #ffcccc, #FF0000); width: 0%; z-index: 2; }
    
    #timer-panel { width: 100%; height: 52vh; background: var(--blue); color: white; border-radius: 25px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    #status-text { font-size: 7vw; font-weight: bold; }
    #time-display { font-size: 14vw; font-weight: bold; font-variant-numeric: tabular-nums; }
    
    .controls { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; width: 100%; justify-content: center; }
    .btn { border: none; padding: 10px 12px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 0.8rem; flex: 1 1 100px; max-width: 140px; }
    .btn-start { background: #87CEEB; }
    .btn-stop { background: #FFB6C1; }
    .btn-reset { background: #98FB98; }
    .btn-mode { background: #6C757D; color: white; }
    .btn-mute { background: #E1F5FE; color: var(--blue); border: 1px solid var(--blue); }
    .btn-help { background: #f0f0f0; }
    .btn-fs { background: #333; color: white; }

    #footer-credit { margin-top: 15px; text-align: center; color: #aaa; font-size: 0.75rem; border-top: 1px solid #eee; padding-top: 8px; width: 80%; }
    
    /* モーダルCSS */
    #help-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: none; z-index: 1000; justify-content: center; align-items: center; }
    #help-content { background: #fff; padding: 25px; border-radius: 15px; width: 85%; max-width: 450px; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
    .close-btn { position: absolute; top: 10px; right: 15px; font-size: 1.4rem; cursor: pointer; color: #999; }
</style>

<script>
    let running = false, startTime = 0, elapsed = 0, lastSec = -1, isCountdown = false, isMuted = false, audioCtx = null;
    let currentVol = parseFloat(localStorage.getItem("takeda_vol")) || 0.8;

    const bells = {
        1: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        2: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        3: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    };

    window.onload = () => {
        document.getElementById('m1').value = localStorage.getItem("takeda_m1") || 6;
        document.getElementById('m2').value = localStorage.getItem("takeda_m2") || 7;
        document.getElementById('m3').value = localStorage.getItem("takeda_m3") || 10;
        const s = document.getElementById('vol-slider');
        s.value = currentVol * 100;
        document.getElementById('vol-label').innerText = "鈴音量: " + s.value + "%";
        update();
    };

    function saveSettings() {
        localStorage.setItem("takeda_m1", document.getElementById('m1').value);
        localStorage.setItem("takeda_m2", document.getElementById('m2').value);
        localStorage.setItem("takeda_m3", document.getElementById('m3').value);
        update();
    }

    document.getElementById('vol-slider').oninput = function() {
        currentVol = this.value / 100;
        document.getElementById('vol-label').innerText = "鈴音量: " + this.value + "%";
        localStorage.setItem("takeda_vol", currentVol);
        Object.values(bells).forEach(b => b.volume = currentVol);
    };

    function unlock() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            Object.values(bells).forEach(b => { b.volume = currentVol; b.load(); });
        }
        if (audioCtx.state === 'suspended') audioCtx.resume();
    }

    function click() {
        if(!audioCtx) return;
        const o = audioCtx.createOscillator(), g = audioCtx.createGain();
        o.type='sine'; o.frequency.setValueAtTime(1200, audioCtx.currentTime);
        g.gain.setValueAtTime(0.05, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
        o.connect(g); g.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + 0.05);
    }

    window.testBell = (n) => { unlock(); bells[n].currentTime=0; bells[n].play().catch(e=>{}); };
    window.toggleHelp = (show) => { click(); document.getElementById('help-modal').style.display = show ? 'flex' : 'none'; };

    window.handleAction = (type) => {
        unlock(); click();
        if (type === 'start' && !running) { running = true; startTime = performance.now() - elapsed; requestAnimationFrame(loop); }
        if (type === 'stop') running = false;
        if (type === 'reset') { running = false; elapsed = 0; lastSec = -1; update(); }
        if (type === 'mode') { isCountdown = !isCountdown; update(); }
        if (type === 'mute') {
            isMuted = !isMuted;
            document.getElementById('mute-btn').innerHTML = isMuted ? '<span style="color:red">✕</span> 消音中' : '🔔 鈴1,2：有効 (M)';
        }
    };

    function toggleFS() {
        click();
        if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(e=>{});
        else document.exitFullscreen();
    }

    function update() {
        const b1 = (document.getElementById('m1').value || 0) * 60;
        const b2 = (document.getElementById('m2').value || 0) * 60;
        const b3 = (document.getElementById('m3').value || 0) * 60;
        const sec = Math.floor(elapsed / 1000);
        let disp = isCountdown ? (sec < b2 ? b2 - sec : sec - b2) : sec;
        
        const panel = document.getElementById('timer-panel'), stat = document.getElementById('status-text');
        const bBlue = document.getElementById('bar-blue'), bYellow = document.getElementById('bar-yellow'), bRed = document.getElementById('bar-red');

        const step = 100 / (b3 / 60 || 1);
        document.getElementById('progress-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${step}% - 1px), rgba(0,0,0,0.1) calc(${step}% - 1px), rgba(0,0,0,0.1) ${step}%)`;

        if (sec < b2) {
            panel.style.background = 'var(--blue)'; stat.innerText = isCountdown ? "残り時間" : "発表時間";
            bBlue.style.width = ((b2 - sec) / b3 * 100) + "%"; bYellow.style.width = ((b3 - b2) / b3 * 100) + "%"; bRed.style.width = "0%";
        } else if (sec < b3) {
            panel.style.background = 'var(--yellow)'; stat.innerText = "質疑応答";
            bBlue.style.width = "0%"; bYellow.style.width = ((b3 - sec) / b3 * 100) + "%"; bRed.style.width = "0%";
        } else {
            panel.style.background = 'var(--red)'; stat.innerText = "終了時間";
            bRed.style.width = "100%";
        }

        const mm = String(Math.floor(disp / 60)).padStart(2, '0'), ss = String(disp % 60).padStart(2, '0');
        document.getElementById('time-display').innerText = mm + ":" + ss;

        if (sec !== lastSec) {
            if (sec === b1 && !isMuted) bells[1].play().catch(e=>{});
            if (sec === b2 && !isMuted) bells[2].play().catch(e=>{});
            if (sec === b3) bells[3].play().catch(e=>{});
            lastSec = sec;
        }
    }

    function loop() { if (running) { elapsed = performance.now() - startTime; update(); requestAnimationFrame(loop); } }
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;
        if (e.code === "Space") { e.preventDefault(); handleAction(running ? 'stop' : 'start'); }
        if (e.key.toLowerCase() === "r") handleAction('reset');
        if (e.key.toLowerCase() === "m") handleAction('mute');
    });
    update();
</script>
"""

st.components.v1.html(html_code, height=920, scrolling=False)
