import streamlit as st
import cv2
import time
import base64

from detector import detect
from alerts.play_voice import play_voice

# =========================================
# CONFIG
# =========================================
st.set_page_config(
    page_title="Smart AI CCTV",
    layout="wide"
)

st.title("🧠 Smart AI CCTV Surveillance")

# =========================================
# SESSION STATE
# =========================================
if "run" not in st.session_state:
    st.session_state.run = False

if "camera" not in st.session_state:
    st.session_state.camera = None

if "last_alarm" not in st.session_state:
    st.session_state.last_alarm = 0

# =========================================
# BUTTONS
# =========================================
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Monitoring"):
        st.session_state.run = True

with col2:
    if st.button("Stop Monitoring"):
        st.session_state.run = False

        if st.session_state.camera is not None:
            st.session_state.camera.release()
            st.session_state.camera = None

# =========================================
# FRAME PLACEHOLDER
# =========================================
frame_placeholder = st.empty()

# =========================================
# CAMERA INIT
# =========================================
def get_camera():

    if st.session_state.camera is None:

        st.session_state.camera = cv2.VideoCapture(0)

    return st.session_state.camera

# =========================================
# PLAY SOUND FUNCTION
# =========================================
def play_alarm():

    with open("alerts/sounds/alarm.wav", "rb") as f:

        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio autoplay>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """

    st.markdown(audio_html, unsafe_allow_html=True)

# =========================================
# MAIN STREAM
# =========================================
camera = get_camera()

while st.session_state.run:

    success, frame = camera.read()

    # =========================================
    # CAMERA FAIL SAFE
    # =========================================
    if not success or frame is None:

        st.warning("⚠ Camera reconnecting...")

        camera.release()

        st.session_state.camera = cv2.VideoCapture(0)

        time.sleep(1)

        continue

    # =========================================
    # DETECTION
    # =========================================
    frame, alarm_triggered,alert_type = detect(frame)

    # =========================================
    # ALARM SYSTEM
    # =========================================
    current_time = time.time()

    if (
        alarm_triggered
        and current_time - st.session_state.last_alarm > 5
    ):

        st.session_state.last_alarm = current_time

        play_alarm()

        if alert_type == "weapon":
            play_voice("alerts/sounds/weapon.mp3")
        elif alert_type == "fight":
            play_voice("alerts/sounds/fight.mp3")
        elif alert_type == "loitering":
            play_voice("alerts/sounds/loitering.mp3")
        elif alert_type == "abandoned":
            play_voice("alerts/sounds/abandoned_object.mp3")
        

    # =========================================
    # DISPLAY FRAME
    # =========================================
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    frame_placeholder.image(
        frame,
        channels="RGB"
    )

    # =========================================
    # SMALL DELAY
    # =========================================
    time.sleep(0.07)

# =========================================
# RELEASE CAMERA
# =========================================
if st.session_state.camera is not None:

    st.session_state.camera.release()