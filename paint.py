import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Virtual Painter", layout="wide")
st.title("🎨 Virtual Painter - Smooth Web Version")

# Initialize session state
if "canvas" not in st.session_state:
    st.session_state.canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
if "prev_x" not in st.session_state:
    st.session_state.prev_x, st.session_state.prev_y = 0, 0
if "smooth_x" not in st.session_state:
    st.session_state.smooth_x, st.session_state.smooth_y = 0, 0
if "detection_status" not in st.session_state:
    st.session_state.detection_status = "Starting..."

# UI
col1, col2 = st.columns([2, 1])
with col1:
    run = st.checkbox("▶️ Run Virtual Painter", value=True)
    brush_thickness = st.slider("✏️ Brush Size", 1, 50, 6)

with col2:
    st.markdown("### 🎨 Choose Pen Color")
    selected_pen = st.radio("Pen Type", ["Red", "Green", "Blue", "Black", "Eraser"], index=0)

# Debug info
st.sidebar.markdown("### 🔧 Debug Info")
status_placeholder = st.sidebar.empty()

# Initialize MediaPipe
try:
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=0
    )
except Exception as e:
    st.error(f"Failed to initialize MediaPipe: {e}")
    hands = None

# Camera initialization
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Cannot access camera. Trying alternative...")
        cap = cv2.VideoCapture(1)
        
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        st.success("✅ Camera initialized successfully")
    else:
        st.warning("⚠️ Running in demo mode without camera")
        run = False
except Exception as e:
    st.error(f"Camera error: {e}")
    cap = None
    run = False

FRAME_WINDOW = st.image([], use_container_width=True)

# Rest of your drawing functions remain the same...
def fingers_up(lm):
    tips = [8, 12, 16, 20]
    return [lm[tip].y < lm[tip - 2].y for tip in tips]

# Main loop
while run and cap and cap.isOpened():
    try:
        ret, frame = cap.read()
        if not ret:
            st.session_state.detection_status = "❌ Failed to read frame"
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        result = hands.process(rgb)
        
        display = st.session_state.canvas.copy()
        
        # Draw UI elements
        cv2.rectangle(display, (0, 0), (639, 479), (0, 0, 0), 2)
        
        # Update detection status
        if result.multi_hand_landmarks:
            st.session_state.detection_status = f"✅ Hand detected ({len(result.multi_hand_landmarks)})"
            # Your existing drawing logic here...
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(display, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            st.session_state.detection_status = "❌ No hand detected"
        
        # Update debug info
        status_placeholder.markdown(f"**Status:** {st.session_state.detection_status}")
        
        # Display frame
        FRAME_WINDOW.image(display, channels="BGR")
        time.sleep(0.05)  # Limit frame rate
        
    except Exception as e:
        st.error(f"Error in main loop: {e}")
        break

# Cleanup
if cap:
    cap.release()
cv2.destroyAllWindows()

if not run:
    st.info("⏸️ Virtual Painter is paused")
