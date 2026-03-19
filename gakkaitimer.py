import streamlit as st

st.set_page_config(page_title="学会タイマーたけださん", layout="wide", initial_sidebar_state="collapsed")

# 1. スタイル設定（入力窓を以前の方式に適したサイズに調整）
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0px;}
    header, footer {visibility: hidden;}
    
    /* 入力窓のスタイル：＋/－ボタンを表示させるため幅を少し広めに */
    div[data-testid="stNumberInput"] {
        max-width: 120px; 
        margin: 0 auto;
    }
    /* 入力窓内の数字サイズ */
    input[type="number"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    .label-text {
        font-size: 0.9rem;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-bottom: 2px;
    }
    /* カラム内を中央寄せ */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 設定・コントロールエリア（中央寄せレイアウト）
# 以前の方式（＋/－ボタンあり）にするため、step=1 を明示
buf_l, c1, c2, c3, c_vol, buf_r = st.columns([1.2, 1, 1, 1, 3, 0.8])

with c1:
    st.markdown('<div class="label-text">鈴1 (分)</div>', unsafe_allow_html=True)
    b1_m = st.number_input("b1", value=6, min_value=0, max_value=99, step=1, key="b1", label_visibility="collapsed")
with c2:
    st.markdown('<div class="label-text">鈴2 (分)</div>', unsafe_allow_html=True)
    b2_m = st.number_input("b2", value=7, min_value=0, max_value=99, step=1, key="b2", label_visibility="collapsed")
with c3:
    st.markdown('<div class="label-text">鈴3 (分)</div>', unsafe_allow_html=True)
    b3_m = st.number_input("b3", value=10, min_value=0, max_value=99, step=1, key="b3", label_visibility="collapsed")

with c_vol:
    # 垂直位置の微調整
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 1px solid #eee; padding-left: 15px;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <span id="vol-label-ext" style="font-size:0.7rem; font-weight:bold; color:#666; margin-bottom:2px;">鈴音量: 80%</span>
                <input type="range" id="vol-slider-ext" min="0" max="100" value="80" style="width:100px; cursor:pointer;" oninput="syncVolume(this.value)">
            </div>
            <div style="display:flex; gap:5px;">
                <button onclick="triggerTest('1')" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.8rem; cursor:pointer;">🔔 1回</button>
                <button onclick="triggerTest('2')" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.8rem; cursor:pointer;">🔔 2回</button>
                <button onclick="triggerTest('3')" style="background:#f8f9fa; border:1px solid #ddd; border-radius:5px; padding:6px 10px; font-size:0.8rem; cursor:pointer;">🔔 3回</button>
            </div>
        </div>
        <script>
            function syncVolume(v) {
                document.getElementById('vol-label-ext').innerText = "鈴音量: " + v + "%";
                const ifr = document.querySelector('iframe');
                if(ifr) ifr.contentWindow.postMessage({type: 'VOLUME', value: v}, '*');
            }
            function triggerTest(n) {
                const ifr = document.querySelector('iframe');
                if(ifr) ifr.contentWindow.postMessage({type: 'TEST', value: n}, '*');
            }
        </script>
    """, unsafe_allow_html=True)

# 3. タイマー表示（iframe）
b1_s, b2_s, b3_s = b1_m * 60, b2_m * 60, b3_m * 60

final_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ margin: 0; padding: 0; font-family: 'Hiragino Kaku Gothic ProN', sans-serif; background: white; overflow: hidden; }}
    #main-wrapper {{ display: flex; flex-direction: column; align-items: center; width: 100%; box-sizing: border-box; padding: 0 10px; }}
    
    #progress-outer-container {{ width: 100%; height: 32px; background: #e0e0e0; border-radius: 16px; overflow: hidden; position: relative; display: flex; border: 1px solid #bbb; margin: 8px 0; }}
    
    #timer-container {{ 
        width: 100%; height: 50vh; background-color: #007BFF; color: white; 
        border-radius: 25px; display: flex; flex-direction: column; 
        justify-content: center; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
    }}
    #status {{ font-size: 6.5vw; font-weight: 700; margin-bottom: 5px; line-height: 1.0; }}
    #display {{ font-size: 15vw; font-weight: 700; line-height: 0.9; font-variant-numeric: tabular-nums; }}

    .button-area {{ margin-top: 15px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; }}
    .btn {{ border: none; padding: 12px; font-size: 0.9rem; font-weight: bold; border-radius: 10px; cursor: pointer; flex: 1 1 110px; max-width: 140px; }}
    
    #help-modal {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; z-index: 100; justify-content: center; align-items: center; }}
    #help-content {{ background: white; color: #333; padding: 25px; border-radius: 20px; max-width: 550px; width: 85%; position: relative; }}
    
    #footer-credit {{ margin-top: 20px; text-align: center; color: #aaa; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; width: 100%; line-height: 1.5; }}
</style>
</head>
<body>
<div id="main-wrapper">
    <div id="progress-outer-container">
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
        <button class="btn" style="background-color: #eee;" onclick="toggleHelp(true)">❓ 使い方</button>
    </div>

    <div id="footer-credit">
        <div>学会タイマーたけださん v7.9</div>
        <div>&copy; 2026 <b>Takeda Healthcare Foundation</b>. All Rights Reserved.</div>
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

    window.addEventListener('message', function(e) {{
        if(e.data.type === 'VOLUME') {{
            currentVolume = e.data.value / 100;
            Object.values(bellSounds).forEach(s => s.volume = currentVolume);
        }}
        if(e.data.type === 'TEST') {{
            const s = bellSounds[e.data.value];
            s.volume = currentVolume; s.currentTime = 0; s.play().catch(err=>{{}});
        }}
    }});

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
        
        const minPct = 100 / (B3_LIMIT / 60 || 1);
        document.getElementById('progress-marks').style.background = `repeating-linear-gradient(to right, transparent 0, transparent calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) calc(${{minPct}}% - 1px), rgba(0,0,0,0.1) ${{minPct}}%)`;

        let disp = 0;
        if (totalSec < B2_LIMIT) {{
            container.style.backgroundColor = "#007BFF"; status.innerText = isCountdown ? "残り時間" : "発表時間"; 
            disp = isCountdown ? (B2_LIMIT - totalSec) : totalSec;
            bDone.style.width = (totalSec / B3_LIMIT * 100) + "%"; bBlue.style.width = ((B2_LIMIT - totalSec) / B3_LIMIT * 100) + "%"; bYellow.style.width = ((B3_LIMIT - B2_LIMIT) / B3_LIMIT * 100) + "%"; bRed.style.width = "0%";
        }} else if (totalSec < B3_LIMIT) {{
            container.style.backgroundColor = "#D4A017"; status.innerText = "質疑応答"; 
            disp = isCountdown ? (totalSec - B2_LIMIT) : totalSec;
            bDone.style.width = (totalSec / B3_LIMIT * 100) + "%"; bBlue.style.width = "0%"; bYellow.style.width = ((B3_LIMIT - totalSec) / B3_LIMIT * 100) + "%"; bRed.style.width = "0%";
        }} else {{
            container.style.backgroundColor = "#A52A2A"; status.innerText = "終了時間";
            disp = totalSec - B2_LIMIT;
            bRed.style.width = "100%";
        }}
        const mm = String(Math.floor(disp / 60)).padStart(2, '0'), ss = String(disp % 60).padStart(2, '0');
        displayEl.innerText = mm + ":" + ss;

        if (totalSec !== lastPlayed) {{
            if (totalSec === B1_LIMIT && !isMuted) bellSounds["1"].play();
            if (totalSec === B2_LIMIT && !isMuted) bellSounds["2"].play();
            if (totalSec === B3_LIMIT) bellSounds["3"].play();
            lastPlayed = totalSec;
        }}
    }}
    function loop() {{ if (running) {{ elapsed = performance.now() - startTime; updateDisplay(); requestAnimationFrame(loop); }} }}
    function toggleHelp(s) {{ document.getElementById('help-modal').style.display = s ? 'flex' : 'none'; }}
    document.addEventListener('keydown', (e) => {{
        if (e.code === "Space") {{ e.preventDefault(); handleAction(running ? 'stop' : 'start'); }}
        if (e.key.toLowerCase() === "r") handleAction('reset');
        if (e.key.toLowerCase() === "m") handleAction('mute');
    }});
    updateDisplay();
</script>

<div id="help-modal">
    <div id="help-content">
        <span onclick="toggleHelp(false)" style="position:absolute; right:15px; top:10px; cursor:pointer; font-size:1.5rem; color:#aaa;">×</span>
        <h3 style="color:#007BFF; border-bottom:2px solid #007BFF; text-align:center; margin-top:0; padding-bottom:10px;">💡 学会タイマーたけださんの使い方</h3>
        <div style="font-size:0.95rem; line-height:1.8; color:#333;">
            <p style="margin: 10px 0;">〇発表時間設定：鈴１回（発表終了１分前）、鈴２回（発表終了時間）、鈴３回（質疑終了）の各分数を設定できます。</p>
            <p style="margin: 10px 0;">〇表示切替：発表経過時間（カウントアップ）と発表残り時間（カウントダウン）の表示を切り替えます。</p>
            <p style="margin: 10px 0;">〇鈴１，２ミュートボタン：鈴１回と鈴２回を消音できます。</p>
            <div style="margin-top:20px; padding:10px; background:#f8f9fa; border-radius:10px; font-size:0.85rem;">
                <b>⌨️ キーボードショートカット:</b> [Space]開始/停止, [R]リセット, [M]ミュート
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

st.components.v1.html(final_content, height=880)
