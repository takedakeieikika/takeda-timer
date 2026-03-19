import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container {padding: 0px;}
    header, footer {visibility: hidden;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

final_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin: 0; padding: 10px; font-family: 'Hiragino Kaku Gothic ProN', sans-serif; background: white; text-align: center; overflow-x: hidden; }
    
    /* 設定エリア */
    .setup-row { display: flex; justify-content: center; align-items: flex-end; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
    .input-group { display: flex; flex-direction: column; align-items: center; }
    .label-text { font-size: 0.85rem; font-weight: bold; color: #444; margin-bottom: 4px; }
    .number-ctrl { display: flex; align-items: center; border: 2px solid #ddd; border-radius: 8px; overflow: hidden; background: #fff; }
    .num-btn { background: #eee; border: none; width: 30px; height: 38px; font-size: 1.2rem; cursor: pointer; font-weight: bold; }
    .num-input { width: 45px; height: 38px; border: none; text-align: center; font-size: 1.3rem; font-weight: bold; -moz-appearance: textfield; }
    
    /* 液体風プログレスバーのデザイン */
    #progress-outer { 
        width: 100%; height: 35px; background: #ebebeb; border-radius: 20px; 
        overflow: hidden; position: relative; display: flex; 
        border: 1px solid #ccc; margin: 10px 0; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .liquid-bar {
        height: 100%;
        transition: width 0.3s ease;
        position: relative;
        /* 液体のような光沢アニメーション */
        background-image: linear-gradient(
            45deg, 
            rgba(255,255,255,0.15) 25%, 
            transparent 25%, 
            transparent 50%, 
            rgba(255,255,255,0.15) 50%, 
            rgba(255,255,255,0.15) 75%, 
            transparent 75%, 
            transparent
        );
        background-size: 40px 40px;
        animation: move-liquid 2s linear infinite;
    }

    @keyframes move-liquid {
        from { background-position: 0 0; }
        to { background-position: 40px 0; }
    }

    /* 各色のグラデーション（液体感） */
    #bar-blue { background-color: #007BFF; background-image: linear-gradient(to bottom, #4facfe 0%, #007BFF 100%); }
    #bar-yellow { background-color: #FFD700; background-image: linear-gradient(to bottom, #fff3b0 0%, #FFD700 100%); }
    #bar-red { 
        position: absolute; top:0; left:0; height:100%; z-index:1;
        background-color: #FF0000; background-image: linear-gradient(to bottom, #ffcccc 0%, #FF0000 100%); 
    }

    /* タイマー本体 */
    #timer-box { width: 100%; height: 48vh; background-color: #007BFF; color: white; border-radius: 25px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    #status { font-size: 6vw; font-weight: bold; margin-bottom: 5px; }
    #display { font-size: 15vw; font-weight: bold; font-variant-numeric: tabular-nums; }

    .button-area { margin-top: 15px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
    .btn { border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 140px; }
    
    #footer-credit { margin-top: 25px; text-align: center; color: #aaa; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; }
</style>
</head>
<body>

<div class="setup-row">
    <div class="input-group">
        <span class="label-text">鈴1(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="clickSound(); step('b1', -1)">−</button>
            <input type="number" id="b1" class="num-input" value="6">
            <button class="num-btn" onclick="clickSound(); step('b1', 1)">＋</button>
        </div>
    </div>
    <div class="input-group">
        <span class="label-text">鈴2(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="clickSound(); step('b2', -1)">−</button>
            <input type="number" id="b2" class="num-input" value="7">
            <button class="num-btn" onclick="clickSound(); step('b2', 1)">＋</button>
        </div>
    </div>
    <div class="input-group">
        <span class="label-text">鈴3(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="clickSound(); step('b3', -1)">−</button>
            <input type="number" id="b3" class="num-input" value="10">
            <button class="num-btn" onclick="clickSound(); step('b3', 1)">＋</button>
        </div>
    </div>
    
    <div style="width:1px; height:40px; background:#eee; margin:0 5px;"></div>

    <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
        <span id="vol-txt" style="font-size:0.7rem; font-weight:bold; color:#666;">音量: 80%</span>
        <input type="range" id="vol-range" min="0" max="100" value="80" style="width:100px; cursor:pointer;" oninput="changeVol(this.value)">
    </div>
    <div style="display:flex; gap:5px;">
        <button class="test-btn" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.75rem; cursor:pointer;" onclick="playBell(1)">🔔 1回</button>
        <button class="test-btn" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.75rem; cursor:pointer;" onclick="playBell(2)">🔔 2回</button>
        <button class="test-btn" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.75rem; cursor:pointer;" onclick="playBell(3)">🔔 3回</button>
    </div>
</div>

<div id="progress-outer">
    <div id="bar-done" style="width:0%; background:transparent;"></div>
    <div id="bar-blue" class="liquid-bar" style="width:0%;"></div>
    <div id="bar-yellow" class="liquid-bar" style="width:0%;"></div>
    <div id="bar-red" class="liquid-bar" style="width:0%; display:none;"></div>
    <div id="p-marks" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:2; pointer-events:none;"></div>
</div>

<div id="timer-box">
    <div id="status">発表時間</div>
    <div id="display">00:00</div>
</div>

<div class="button-area">
    <button class="btn" style="background-color: #87CEEB;" onclick="clickSound(); act('start')">▶ START</button>
    <button class="btn" style="background-color: #FFB6C1;" onclick="clickSound(); act('stop')">|| STOP</button>
    <button class="btn" style="background-color: #98FB98;" onclick="clickSound(); act('reset')">🔄 RESET</button>
    <button class="btn" style="background-color: #6C757D; color: white;" onclick="clickSound(); act('mode')">🔽 表示切替</button>
    <button id="mute-btn" class="btn" style="background-color: #E1F5FE; border: 1px solid #007BFF; color: #007BFF;" onclick="clickSound(); act('mute')">🔔 鈴1,2：有効</button>
</div>

<div id="footer-credit">
    <div>学会タイマーたけださん v8.2</div>
    <div>&copy; 2026 <b>Takeda Healthcare Foundation</b>. All Rights Reserved.</div>
</div>

<script>
    let vol = 0.8;
    let start = 0, elapsed = 0, running = false, lastS = -1, isCD = false, muted = false;
    const clickAudio = new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/click.mp3");
    const bells = {
        1: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        2: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        3: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    };

    function clickSound() { clickAudio.volume = vol * 0.3; clickAudio.currentTime = 0; clickAudio.play().catch(e=>{}); }
    function step(id, n) { 
        const el = document.getElementById(id);
        el.value = Math.max(0, parseInt(el.value) + n);
        updateDisplay();
    }
    function changeVol(v) { vol = v/100; document.getElementById('vol-txt').innerText = "音量: "+v+"%"; Object.values(bells).forEach(b => b.volume = vol); }
    function playBell(n) { const b = bells[n]; b.volume = vol; b.currentTime = 0; b.play().catch(e=>{}); }

    function act(type) {
        if(type==='start' && !running) { running=true; start=performance.now()-elapsed; loop(); }
        if(type==='stop') running=false;
        if(type==='reset') { running=false; elapsed=0; lastS=-1; updateDisplay(); }
        if(type==='mode') { isCD=!isCD; updateDisplay(); }
        if(type==='mute') { muted=!muted; document.getElementById('mute-btn').innerText = muted ? "✕ 鈴1,2：消音" : "🔔 鈴1,2：有効"; }
    }

    function updateDisplay() {
        const b1 = parseInt(document.getElementById('b1').value)*60;
        const b2 = parseInt(document.getElementById('b2').value)*60;
        const b3 = parseInt(document.getElementById('b3').value)*60;
        const s = Math.floor(elapsed/1000);
        
        const box = document.getElementById('timer-box'), status = document.getElementById('status'), disp = document.getElementById('display');
        const bd = document.getElementById('bar-done'), bb = document.getElementById('bar-blue'), by = document.getElementById('bar-yellow'), br = document.getElementById('bar-red');

        const minPct = 100 / (b3/60 || 1);
        document.getElementById('p-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${minPct}% - 1px), rgba(0,0,0,0.1) calc(${minPct}% - 1px), rgba(0,0,0,0.1) ${minPct}%)`;

        let d = 0;
        if(s < b2) {
            box.style.backgroundColor="#007BFF"; status.innerText=isCD?"残り時間":"発表時間"; d=isCD?(b2-s):s;
            bd.style.width=(s/b3*100)+"%"; bb.style.width=((b2-s)/b3*100)+"%"; by.style.width=((b3-b2)/b3*100)+"%"; br.style.display="none";
        } else if(s < b3) {
            box.style.backgroundColor="#D4A017"; status.innerText="質疑応答"; d=isCD?(s-b2):s;
            bd.style.width=(s/b3*100)+"%"; bb.style.width="0%"; by.style.width=((b3-s)/b3*100)+"%"; br.style.display="none";
        } else {
            box.style.backgroundColor="#A52A2A"; status.innerText="終了時間"; d=s-b2;
            bd.style.width="0%"; bb.style.width="0%"; by.style.width="0%"; br.style.display="block"; br.style.width="100%";
        }
        const mm = String(Math.floor(d/60)).padStart(2,'0'), ss = String(d%60).padStart(2,'0');
        disp.innerText = mm+":"+ss;

        if(s !== lastS) {
            if(s===b1 && !muted) playBell(1);
            if(s===b2 && !muted) playBell(2);
            if(s===b3) playBell(3);
            lastS = s;
        }
    }
    function loop() { if(running) { elapsed=performance.now()-start; updateDisplay(); requestAnimationFrame(loop); } }
    updateDisplay();
</script>
</body>
</html>
"""

st.components.v1.html(final_content, height=850)
