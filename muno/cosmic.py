import cv2
import numpy as np
import time
import datetime
import os
import json
import subprocess

# --- CONFIGURATION (NCBI + C922 OPTIMIZED) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_FILE = os.path.join(BASE_DIR, "dashboard.html")
IMAGE_DIR = os.path.join(BASE_DIR, "cosmic_images")
STATS_FILE = os.path.join(BASE_DIR, "stats.json")
LOG_FILE = os.path.join(BASE_DIR, "cosmic.log")

# Scientific Parameters
MIN_THETA = 95          # The "9 AM" sensitivity floor
HOT_PIXEL_SAMPLES = 60  # Initial calibration frames
NOISE_DECAY = 0.01      # Adaptive background speed
CAMERA_DEVICE = "/dev/video0"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted, flush=True)
    with open(LOG_FILE, "a") as f: f.write(formatted + "\n")

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(float(f.read()) / 1000.0, 1)
    except: return 0.0

def configure_c922():
    """Force C922 into raw, manual laboratory mode."""
    log("Configuring C922 Driver: Disabling 'Smart' features...")
    # These commands lock the exposure, gain, and disable auto-focus/auto-low-light
    cmds = [
        f"v4l2-ctl -d {CAMERA_DEVICE} -c focus_auto=0",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c focus_absolute=0",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c exposure_auto=1",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c exposure_absolute=2047",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c gain=255",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c sharpness=255",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c backlight_compensation=0",
        f"v4l2-ctl -d {CAMERA_DEVICE} -c exposure_dynamic_framerate=0"
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, capture_output=True)
        time.sleep(0.1)

def update_dashboard(stats, recent_images, current_temp):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    js_data = json.dumps(stats['chart_data'])
    gallery_html = ""
    for img in reversed(recent_images):
        snr = round(img[2] / MIN_THETA, 2)
        gallery_html += f"""
        <div class='card'><div class='hit-tag'>SNR: {snr}x</div>
        <img src='cosmic_images/{img[0]}'><div class='caption'>
        <b>TIME:</b> {img[1]} | <b>ENERGY:</b> {img[2]}<br><b>TEMP:</b> {img[3]}°C</div></div>"""

    html = f"""
    <!DOCTYPE html><html><head><title>C922 Muon Observatory</title><meta http-equiv="refresh" content="30">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script><script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        :root {{ --neon: #00e5ff; --bg: #050505; --card: #111; }}
        body {{ font-family: 'Courier New', monospace; background: var(--bg); color: var(--neon); padding: 20px; }}
        .grid {{ display: grid; grid-template-columns: 300px 1fr; gap: 20px; }}
        .stat-panel {{ background: var(--card); border: 1px solid #333; padding: 15px; border-radius: 4px; }}
        .stat-val {{ font-size: 2.2rem; color: #fff; font-weight: bold; }}
        .chart-box {{ background: var(--card); border: 1px solid #333; padding: 10px; height: 320px; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .card {{ background: var(--card); border: 1px solid #222; position: relative; }}
        .card img {{ width: 100%; height: 160px; image-rendering: pixelated; filter: contrast(300%) brightness(150%); }}
        .hit-tag {{ position: absolute; top: 5px; right: 5px; background: rgba(0,229,255,0.2); border: 1px solid var(--neon); padding: 2px 5px; font-size: 0.7rem; }}
        .caption {{ padding: 8px; font-size: 0.7rem; color: #aaa; }}
    </style></head><body><h1>Particle Detection Laboratory</h1>
    <div class="grid"><div class="stat-panel"><div style="color:#888;">TOTAL FLUX EVENTS</div><div class="stat-val">{stats['total_hits']}</div>
    <div style="color:#888; margin-top:10px;">CPU TEMP</div><div class="stat-val" style="color:#ff4444;">{current_temp}°C</div>
    <p><b>HB:</b> {now}</p></div><div class="chart-box"><canvas id="cChart"></canvas></div></div>
    <h3>DETECTION MORPHOLOGY (AUTO-CONTRAST)</h3><div class="gallery">{gallery_html}</div>
    <script>new Chart(document.getElementById('cChart'),{{type:'scatter',data:{{datasets:[{{label:'Energy',data:{js_data}.map(d=>({{x:d.x,y:d.y}})),backgroundColor:'#00e5ff',borderColor:'#00e5ff',showLine:true,tension:0.3}}]}},options:{{maintainAspectRatio:false,scales:{{x:{{type:'time',grid:{{color:'#222'}},ticks:{{color:'#888'}}}},y:{{min:80,max:255,grid:{{color:'#222'}},ticks:{{color:'#888'}}}}}},plugins:{{legend:{{display:false}}}}}}}});</script>
    </body></html>"""
    with open(DASHBOARD_FILE, "w") as f: f.write(html)

if __name__ == "__main__":
    if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
    
    configure_c922()
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
    cap.set(3, 640); cap.set(4, 480)
    
    # 1. NCBI Calibration Phase
    log("Phase 1: Sampling for hot pixels...")
    mask_acc = np.zeros((480, 640), dtype=np.float32)
    for _ in range(HOT_PIXEL_SAMPLES):
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask_acc = cv2.max(mask_acc, gray.astype(np.float32))
    _, hot_pixel_mask = cv2.threshold(mask_acc, 50, 255, cv2.THRESH_BINARY)
    hot_pixel_mask = hot_pixel_mask.astype(np.uint8)

    # 2. Setup
    ret, frame = cap.read()
    frame_avg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
    stats = {"total_hits": 10, "chart_data": [], "start_time": str(datetime.datetime.now())}
    recent_images = []; last_hbeat = time.time(); last_dash = time.time()
    log("Phase 2: Monitoring under-bed flux. Trap is set.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None: continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clean_gray = cv2.bitwise_and(gray, cv2.bitwise_not(hot_pixel_mask))
            
            diff = clean_gray.astype(np.float32) - frame_avg
            _, max_val, _, max_loc = cv2.minMaxLoc(diff)

            if max_val > 10 and clean_gray[max_loc[1], max_loc[0]] > MIN_THETA:
                ts_iso = datetime.datetime.now().isoformat()
                ts_p = datetime.datetime.now().strftime("%H:%M:%S")
                fname = f"hit_{int(time.time())}.png"
                energy = int(clean_gray[max_loc[1], max_loc[0]])
                cur_t = get_cpu_temp()
                
                cv2.imwrite(os.path.join(IMAGE_DIR, fname), frame)
                stats['total_hits'] += 1
                stats['chart_data'].append({'x': ts_iso, 'y': energy})
                if len(stats['chart_data']) > 100: stats['chart_data'].pop(0)
                recent_images.append((fname, ts_p, energy, cur_t))
                if len(recent_images) > 12: recent_images.pop(0)
                
                update_dashboard(stats, recent_images, cur_t)
                log(f"HIT! SNR: {round(energy/MIN_THETA,1)}x | Temp: {cur_t}C")
                time.sleep(0.4)

            cv2.accumulateWeighted(clean_gray, frame_avg, NOISE_DECAY)

            if time.time() - last_dash > 60:
                update_dashboard(stats, recent_images, get_cpu_temp())
                last_dash = time.time()
            if time.time() - last_hbeat > 300:
                log(f"HEARTBEAT: OK. Hits: {stats['total_hits']} | Temp: {get_cpu_temp()}C")
                last_hbeat = time.time()
    finally: cap.release()
