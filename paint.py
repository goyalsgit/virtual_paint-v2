import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
import time

# =========================
# 🎨 Streamlit UI
# =========================
st.set_page_config(page_title="Virtual Painter", layout="wide")
st.title("🎨 Virtual Painter - Smooth Web Version")
st.caption("👉 Draw when only your index finger is up. Your hand stays visible always.")

# Initialize persistent session state
if "canvas" not in st.session_state:
    st.session_state.canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
if "prev_x" not in st.session_state:
    st.session_state.prev_x, st.session_state.prev_y = 0, 0
if "smooth_x" not in st.session_state:
    st.session_state.smooth_x, st.session_state.smooth_y = 0, 0
if "last_hand" not in st.session_state:
    st.session_state.last_hand, st.session_state.last_seen_time = None, 0

col1, col2 = st.columns([2, 1])

with col1:
    run = st.checkbox("▶️ Run Virtual Painter", value=True)
    brush_thickness = st.slider("✏️ Brush Size", 1, 50, 6)

with col2:
    st.markdown("### 🎨 Choose Pen Color")
    selected_pen = st.radio(
        "Pen Type",
        ["Red", "Green", "Blue", "Black", "Eraser (White)", "Custom Color"],
        horizontal=False,
    )
    if selected_pen == "Custom Color":
        custom_color = st.color_picker("Pick Custom Color", "#FF5733")

FRAME_WINDOW = st.image([], use_container_width=True)

# =========================
# 🖐 Mediapipe Setup
# =========================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# =========================
# 📸 Camera Setup
# =========================
canvas_h, canvas_w = 480, 640
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, canvas_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, canvas_h)

# =========================
# ⚙️ Helpers
# =========================
def fingers_up(lm):
    tips = [8, 12, 16, 20]
    return [lm[tip].y < lm[tip - 2].y for tip in tips]

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])

# =========================
# ⚙️ Constants
# =========================
ALPHA = 0.75
FPS_LIMIT = 15
border_thickness = 4
detect_area = {"top": 40, "bottom": canvas_h - 40, "left": 40, "right": canvas_w - 40}
HAND_MEMORY_DURATION = 0.5
prev_time = 0

# =========================
# 🖊 Main Loop
# =========================
while run:
    ret, frame = cap.read()
    if not ret:
        st.warning("⚠️ Camera not detected.")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    display = st.session_state.canvas.copy()

    # 🎯 Draw borders
    cv2.rectangle(display, (0, 0), (canvas_w - 1, canvas_h - 1), (0, 0, 0), border_thickness)
    cv2.rectangle(display, (detect_area["left"], detect_area["top"]),
                  (detect_area["right"], detect_area["bottom"]), (200, 200, 200), 2)

    # 🖍 Color
    color_map = {
        "Red": (0, 0, 255),
        "Green": (0, 255, 0),
        "Blue": (255, 0, 0),
        "Black": (0, 0, 0),
        "Eraser (White)": (255, 255, 255)
    }
    draw_color = hex_to_bgr(custom_color) if selected_pen == "Custom Color" else color_map[selected_pen]

    # ✅ Hand memory logic
    if result.multi_hand_landmarks:
        st.session_state.last_hand = result.multi_hand_landmarks[0]
        st.session_state.last_seen_time = time.time()
    elif st.session_state.last_hand and time.time() - st.session_state.last_seen_time < HAND_MEMORY_DURATION:
        pass
    else:
        st.session_state.last_hand = None

    # 🖐 Drawing
    if st.session_state.last_hand:
        lm = st.session_state.last_hand.landmark
        h, w, _ = frame.shape
        index_x, index_y = int(lm[8].x * w), int(lm[8].y * h)

        if (detect_area["left"] < index_x < detect_area["right"]) and (detect_area["top"] < index_y < detect_area["bottom"]):
            if st.session_state.smooth_x == 0 and st.session_state.smooth_y == 0:
                st.session_state.smooth_x, st.session_state.smooth_y = index_x, index_y
            else:
                st.session_state.smooth_x = int(ALPHA * st.session_state.smooth_x + (1 - ALPHA) * index_x)
                st.session_state.smooth_y = int(ALPHA * st.session_state.smooth_y + (1 - ALPHA) * index_y)

            fingers = fingers_up(lm)
            if fingers[0] and not any(fingers[1:]):
                if st.session_state.prev_x == 0 and st.session_state.prev_y == 0:
                    st.session_state.prev_x, st.session_state.prev_y = st.session_state.smooth_x, st.session_state.smooth_y
                cv2.line(
                    st.session_state.canvas,
                    (st.session_state.prev_x, st.session_state.prev_y),
                    (st.session_state.smooth_x, st.session_state.smooth_y),
                    draw_color,
                    brush_thickness,
                )
                st.session_state.prev_x, st.session_state.prev_y = st.session_state.smooth_x, st.session_state.smooth_y
            else:
                st.session_state.prev_x, st.session_state.prev_y = 0, 0

        mp_drawing.draw_landmarks(display, st.session_state.last_hand, mp_hands.HAND_CONNECTIONS)

    # 🕒 Update Streamlit frame
    now = time.time()
    if now - prev_time > 1 / FPS_LIMIT:
        FRAME_WINDOW.image(display, channels="BGR")
        prev_time = now

cap.release()
st.write("🛑 Stopped.")
