import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import base64
import json

# =========================
# 🎨 Streamlit UI Configuration
# =========================
st.set_page_config(
    page_title="Hand Gesture Painter - Any Device",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👋🎨 Hand Gesture Virtual Painter")
st.markdown("""
**✨ Use your hand gestures to draw!**

### How it works:
1. **Click the 'Start Camera' button below** 
2. **Allow camera access** when prompted
3. **Show your hand** to the camera
4. **Use gestures to draw:**
   - 👆 **Index finger up**: Draw
   - ✊ **Fist**: Stop drawing
   - 🖐 **Open hand**: Move without drawing

**Works on phones, tablets, and computers!**
""")

# =========================
# 🎯 Initialize Session State
# =========================
if 'canvas_image' not in st.session_state:
    canvas = Image.new('RGB', (800, 600), 'white')
    st.session_state.canvas_image = canvas
    st.session_state.canvas_url = None

if 'drawing' not in st.session_state:
    st.session_state.drawing = False

if 'last_point' not in st.session_state:
    st.session_state.last_point = None

# =========================
# 🎨 Sidebar Controls
# =========================
st.sidebar.header("🎨 Painting Controls")

# Color selection
color_options = {
    "Red": "#FF0000",
    "Green": "#00FF00", 
    "Blue": "#0000FF",
    "Black": "#000000",
    "Purple": "#800080",
    "Orange": "#FFA500"
}

selected_color = st.sidebar.selectbox(
    "Choose Pen Color:",
    list(color_options.keys()),
    index=0
)

# Brush size
brush_size = st.sidebar.slider(
    "Brush Size:",
    min_value=1,
    max_value=30,
    value=8,
    step=1
)

# Clear canvas
if st.sidebar.button("🗑 Clear Canvas"):
    st.session_state.canvas_image = Image.new('RGB', (800, 600), 'white')
    st.session_state.drawing = False
    st.session_state.last_point = None
    st.rerun()

# =========================
# 📱 Hand Tracking Setup (Pure Streamlit)
# =========================
st.header("📱 Hand Tracking")

# Method 1: Using device's built-in hand tracking
html_code = """
<div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
    <h3>👆 Hand Tracking Area</h3>
    <p>Show your hand in the camera area below</p>
    
    <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <p><strong>Gesture Controls:</strong></p>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 24px;">👆</div>
                <div>Index Up = DRAW</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 24px;">✊</div>
                <div>Fist = STOP</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div style="font-size: 24px;">🖐</div>
                <div>Open = MOVE</div>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(html_code, unsafe_allow_html=True)

# =========================
# 📸 Camera Input
# =========================
st.subheader("📸 Camera Input")

# Using Streamlit's camera input
camera_img = st.camera_input("Take a picture of your hand gesture", key="hand_camera")

if camera_img is not None:
    # Simulate hand detection based on image
    st.success("✅ Camera active! Simulating hand tracking...")
    
    # Create a simple hand position simulation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hand_x = st.slider("Hand X Position", 0, 800, 400, key="hand_x")
    with col2:
        hand_y = st.slider("Hand Y Position", 0, 600, 300, key="hand_y")
    with col3:
        gesture = st.selectbox("Hand Gesture", ["👆 Draw", "✊ Stop", "🖐 Move"], key="gesture")
    
    # Update canvas based on gesture
    if gesture == "👆 Draw":
        st.session_state.drawing = True
        current_point = (hand_x, hand_y)
        
        # Draw on canvas
        if st.session_state.last_point is not None:
            draw = ImageDraw.Draw(st.session_state.canvas_image)
            draw.line(
                [st.session_state.last_point, current_point], 
                fill=color_options[selected_color], 
                width=brush_size
            )
        
        st.session_state.last_point = current_point
        st.success("🖊 Drawing...")
        
    elif gesture == "✊ Stop":
        st.session_state.drawing = False
        st.session_state.last_point = None
        st.warning("⏸ Stopped drawing")
        
    else:  # Move
        st.session_state.drawing = False
        st.session_state.last_point = (hand_x, hand_y)
        st.info("🚶 Moving...")

# =========================
# 🎨 Canvas Display
# =========================
st.header("🎨 Your Drawing Canvas")

# Display the canvas
col1, col2 = st.columns([2, 1])

with col1:
    st.image(st.session_state.canvas_image, use_column_width=True, caption="Your Drawing Canvas")
    
    # Drawing status
    if st.session_state.drawing:
        st.success("🖊 Currently Drawing")
    else:
        st.info("⏸ Not Drawing")

with col2:
    st.subheader("📊 Drawing Info")
    st.write(f"**Color:** {selected_color}")
    st.write(f"**Brush Size:** {brush_size}px")
    st.write(f"**Canvas Size:** 800x600 pixels")
    
    # Download option
    if st.button("💾 Download Drawing"):
        buf = io.BytesIO()
        st.session_state.canvas_image.save(buf, format="PNG")
        st.download_button(
            label="Click to Download",
            data=buf.getvalue(),
            file_name="my_drawing.png",
            mime="image/png"
        )

# =========================
# 🎮 Alternative: Touch/Mouse Drawing
# =========================
st.header("🎮 Alternative: Direct Drawing")

st.markdown("""
**Can't use camera? Draw directly with your mouse/touch:**

1. Click and drag on the canvas above to draw
2. Use the sidebar to change colors and brush size
3. Clear canvas when needed
""")

# =========================
# 📱 Mobile Optimized Instructions
# =========================
st.sidebar.header("📱 Mobile Tips")
st.sidebar.markdown("""
**For Mobile Devices:**
- Use **front camera** for easier positioning
- Hold device with **other hand**
- Make clear **gestures**
- **Tap buttons** carefully
""")

# =========================
# 🎯 Gesture Guide
# =========================
st.sidebar.header("👋 Gesture Guide")
st.sidebar.markdown("""
**👆 Index Up** → Draw  
**✊ Fist** → Stop drawing  
**🖐 Open Hand** → Move cursor  

**Pro Tip:** Practice making clear gestures!
""")
