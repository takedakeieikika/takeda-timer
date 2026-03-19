import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

# Streamlit側の余白を消す
st.markdown("""
    <style>
    .block-container {padding: 0px;}
    header, footer {visibility: hidden;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

# すべてを一つのHTMLに統合
final_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin: 0; padding: 10px; font-family: 'Hiragino Kaku Gothic ProN', sans-serif; background: white; text-align: center; overflow-x: hidden; }
    
    /* 設定エリア：中央寄せ */
    .setup-row { display: flex; justify-content: center; align-items: flex-end; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
    .input-group { display: flex; flex-direction: column; align-items: center; }
    .label-text { font-size: 0.85rem; font-weight: bold; color: #444; margin-bottom: 4px; }
    
    /* ＋/－ボタン付き入力窓の自作 */
    .number-ctrl { display: flex; align-items: center; border: 2px solid #ddd; border-radius: 8px; overflow: hidden; background: #fff; }
    .num-btn { background: #eee; border: none; width: 30px; height: 38px; font-size: 1.2rem; cursor: pointer; font-weight: bold; }
    .num-btn:hover { background: #ddd; }
    .num-input { width: 45px; height: 38px; border: none; text-align: center; font-size: 1.3rem; font-weight: bold; -moz-appearance: textfield; }
    .num-input::-webkit-inner-spin-button { -webkit-appearance: none; }

    /* 音量・テストエリア */
    .control-divider { width: 1px; height: 40px; background: #eee; margin: 0 5px; }
    .vol-section { display: flex; flex-direction: column; align-items: center; gap: 2px; }
    .test-group { display: flex; gap: 5px; }
    .test-btn { background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 6px 10px; font-size: 0.75rem; cursor: pointer; }

    /* プログレスバー */
    #progress-outer { width: 100%; height: 32px; background: #e0e0e0; border-radius: 16px; overflow: hidden; position: relative; display: flex; border: 1px solid #bbb; margin: 10px 0; }
    
    /* タイマー本体 */
    #timer-box { width: 100%; height: 48vh; background-color: #007BFF; color: white; border-radius: 25px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    #status { font-size: 6vw; font-weight: bold; margin-bottom: 5px; line-height: 1.0; }
    #display { font-size: 15vw; font-weight: bold; line-height: 0.9; font-variant-numeric: tabular-nums; }

    /* 操作ボタン */
    .button-area { margin-top: 15px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
    .btn { border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 140px; transition: 0.1s; }
    .btn:active { transform: scale(0.95); }
    
    #footer-credit { margin-top: 25px; text-align: center; color: #aaa; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; line-height: 1.6; }

    /* モーダル */
    #help-modal { position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); display:none; z-index:1000; justify-content:center; align-items:center; }
    #help-content { background:white; color:#333; padding:25px; border-radius:20px; max-width:500px; width:85%; position:relative; text-align:left; }
</style>
</head>
<body>

<div class="setup-row">
    <div class="input-group">
        <span class="label-text">鈴1(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="step('b1', -1)">−</button>
            <input type="number" id="b1" class="num-input" value="6">
            <button class="num-btn" onclick="step('b1', 1)">＋</button>
        </div>
    </div>
    <div class="input-group">
        <span class="label-text">鈴2(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="step('b2', -1)">−</button>
            <input type="number" id="b2" class="num-input" value="7">
            <button class="num-btn" onclick="step('b2', 1)">＋</button>
        </div>
    </div>
    <div class="input-group">
        <span class="label-text">鈴3(分)</span>
        <div class="number-ctrl">
            <button class="num-btn" onclick="step('b3', -1)">−</button>
            <input type="number" id="b3" class="num-input" value="10">
            <button class="num-btn" onclick="step('b3', 1)">＋</button>
        </div>
    </div>
    
    <div class="control-divider"></div>

    <div class="vol-section">
        <span id="vol-txt" style="font-size:0.7rem; font-weight:bold; color:#666;">音量: 80%</span>
        <input type="range" id="vol-range" min="0" max="100" value="80" style="width:100px; cursor:pointer;" oninput="changeVol(this.value)">
    </div>
    <div class="test-group">
        <button class="test-btn" onclick="playBell(1)">🔔 1回</button>
        <button class="test-btn" onclick="playBell(2)">🔔 2回</button>
        <button class="test-btn" onclick="playBell(3)">🔔 3回</button>
    </div>
</div>

<div id="progress-outer">
    <div id="bar-done" style="width:0%; background:transparent;"></div>
    <div id="bar-blue" style="width:0%; background:linear-gradient(to bottom, #4facfe, #007BFF);"></div>
    <div id="bar-yellow" style="width:0%; background:linear-gradient(to bottom, #fff3b0, #FFD700);"></div>
    <div id="bar-red" style="position:absolute; top:0; left:0; width:0%; height:100%; background:linear-gradient(to bottom, #ffcccc, #FF0000); z-index:1;"></div>
    <div id="p-marks" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:2; pointer-events:none;"></div>
</div>

<div id="timer-box">
    <div id="status">発表時間</div>
    <div id="display">00:00</div>
</div>

<div class="button-area">
    <button class="btn" style="background-color: #87CEEB;" onclick="act('start')">▶ START</button>
    <button class="btn" style="background-color: #FFB6C1;" onclick="act('stop')">|| STOP</button>
    <button class="btn" style="background-color: #98FB98;" onclick="act('reset')">🔄 RESET</button>
    <button class="btn" style="background-color: #6C757D; color: white;" onclick="act('mode')">🔽 表示切替</button>
    <button id="mute-btn" class="btn" style="background-color: #E1F5FE; border: 1px solid #007BFF; color: #007BFF;" onclick="act('mute')">🔔 鈴1,2：有効</button>
    <button class="btn" style="background-color: #eee;" onclick="toggleHelp(true)">❓ 使い方</button>
</div>

<div id="footer-credit">
    <div>学会タイマーたけださん v8.0</div>
    <div>&copy; 2026 <b>Takeda Healthcare Foundation</b>. All Rights Reserved.</div>
</div>

<div id="help-modal">
    <div id="help-content">
        <span onclick="toggleHelp(false)" style="position:absolute; right:15px; top:10px; cursor:pointer; font-size:1.5rem; color:#aaa;">×</span>
        <h3 style="color:#007BFF; border-bottom:2px solid #007BFF; text-align:center; margin-top:0; padding-bottom:10px;">💡 学会タイマーたけださんの使い方</h3>
        <p>〇発表時間設定：鈴１回（終了１分前）、鈴２回（終了）、鈴３回（質疑終了）を設定できます。</p>
        <p>〇表示切替：経過時間と残り時間の表示を切り替えます。</p>
        <p>〇鈴１，２ミュート：鈴１回と鈴２回を消音できます。</p>
        <div style="margin-top:20px; padding:10px; background:#f8f9fa; border-radius:10px; font-size:0.8rem;">
            <b>⌨️ キーボード:</b> [Space]開始/停止, [R]リセット, [M]ミュート
        </div>
    </div>
</div>

<script>
    let vol = 0.8;
    let start = 0, elapsed = 0, running = false, lastS = -1, isCD = false, muted = false;
    const bells = {
        1: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell1.mp3"),
        2: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell2.mp3"),
        3: new Audio("https://raw.githubusercontent.com/takedakeieikika/takeda-timer/main/bell3.mp3")
    };

    function step(id, n) { 
        const el = document.getElementById(id);
        el.value = Math.max(0, parseInt(el.value) + n);
        updateDisplay();
    }
    function changeVol(v) { 
        vol = v/100; document.getElementById('vol-txt').innerText = "音量: "+v+"%"; 
        Object.values(bells).forEach(b => b.volume = vol);
    }
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

        // 目盛り描画
        const minPct = 100 / (b3/60 || 1);
        document.getElementById('p-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${minPct}% - 1px), rgba(0,0,0,0.1) calc(${minPct}% - 1px), rgba(0,0,0,0.1) ${minPct}%)`;

        let d = 0;
        if(s < b2) {
            box.style.backgroundColor="#007BFF"; status.innerText=isCD?"残り時間":"発表時間"; d=isCD?(b2-s):s;
            bd.style.width=(s/b3*100)+"%"; bb.style.width=((b2-s)/b3*100)+"%"; by.style.width=((b3-b2)/b3*100)+"%"; br.style.width="0%";
        } else if(s < b3) {
            box.style.backgroundColor="#D4A017"; status.innerText="質疑応答"; d=isCD?(s-b2):s;
            bd.style.width=(s/b3*100)+"%"; bb.style.width="0%"; by.style.width=((b3-s)/b3*100)+"%"; br.style.width="0%";
        } else {
            box.style.backgroundColor="#A52A2A"; status.innerText="終了時間"; d=s-b2;
            bd.style.width="0%"; bb.style.width="0%"; by.style.width="0%"; br.style.width="100%";
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
    function toggleHelp(s) { document.getElementById('help-modal').style.display = s?'flex':'none'; }
    document.addEventListener('keydown', e => {
        if(e.code==='Space') { e.preventDefault(); act(running?'stop':'start'); }
        if(e.key.toLowerCase()==='r') act('reset');
        if(e.key.toLowerCase()==='m') act('mute');
    });
    updateDisplay();
</script>
</body>
</html>
"""

st.components.v1.html(final_content, height=900)
