import streamlit as st
import cv2
import numpy as np
import tempfile
import time
import os
from PIL import Image
from ultralytics import YOLO

# Page Configuration
st.set_page_config(
    page_title="VisionAI - Object Detection Dashboard",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphic Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .title-gradient {
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Metrics panel style */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00FF87;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0aec0;
    }
    
    /* Button Hover Effects */
    .stButton>button {
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%) !important;
        color: #0f111a !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 255, 135, 0.3) !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 255, 135, 0.5) !important;
    }
    
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: #718096;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache YOLO model loading
@st.cache_resource
def load_model():
    # Resolve absolute path to yolov8n.pt in the same folder as app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'yolov8n.pt')
    model = YOLO(model_path)
    return model


try:
    model = load_model()
    coco_classes = model.names
except Exception as e:
    st.error(f"Failed to load YOLO model: {e}")
    coco_classes = {}

# App Header
st.markdown("<h1 class='title-gradient'>👁️ VisionAI: Real-Time Object Detection</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A premium computer vision application for instant object detection, labeling, and statistical counting.</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h2 style='color:#00FF87; text-align:center;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # Mode selection
    app_mode = st.selectbox("Select Media Source", ["Upload Image", "Upload Video"])
    
    # Confidence threshold
    conf_thresh = st.slider("YOLO Confidence Threshold", min_value=0.1, max_value=1.0, value=0.35, step=0.05)
    
    # Target Class Selection
    st.write("### 🏷️ Filter Detection Classes")
    if coco_classes:
        class_options = {v: k for k, v in coco_classes.items()}
        selected_class_names = st.multiselect(
            "Select classes to detect (leave empty to detect all classes)", 
            options=sorted(list(class_options.keys())), 
            default=[]
        )
        selected_class_ids = [class_options[name] for name in selected_class_names]
    else:
        selected_class_ids = []
    
    st.write("---")
    st.write("### 🛠️ Technology Stack")
    st.caption("**Model**: YOLOv8 Nano (Pre-trained on MS COCO)")
    st.caption("**Backend**: OpenCV & PyTorch")
    st.caption("**Frontend**: Streamlit Custom Theme")

# Helper function to process frame and return annotated frame + counts
def detect_objects(frame, conf_threshold, target_classes):
    results = model(frame, conf=conf_threshold, verbose=False)
    counts = {}
    total_count = 0
    
    # Annotate frame
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0].item())
            
            # Filter class if specified
            if target_classes and cls_id not in target_classes:
                continue
                
            class_name = coco_classes.get(cls_id, "unknown")
            conf = float(box.conf[0].item())
            
            # Get coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Increment counts
            counts[class_name] = counts.get(class_name, 0) + 1
            total_count += 1
            
            # Color mapping based on class ID
            color_id = cls_id % 8
            colors = [
                (255, 87, 51), (51, 255, 87), (87, 51, 255), (255, 51, 161),
                (51, 255, 230), (255, 230, 51), (230, 51, 255), (0, 255, 135)
            ]
            color = colors[color_id]
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w + 10, y1), color, -1)
            cv2.putText(frame, label, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
    return frame, counts, total_count

# Layout Columns
col_media, col_stats = st.columns([3, 1])

if app_mode == "Upload Image":
    with col_media:
        st.subheader("🖼️ Image Detection Pane")

        uploaded_image = st.file_uploader(
            "Upload an Image (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_image is not None:

            image = Image.open(uploaded_image).convert("RGB")
            image_np = np.array(image)

            image_bgr = cv2.cvtColor(
                image_np,
                cv2.COLOR_RGB2BGR
            ).copy()

            with st.spinner("Analyzing image..."):
                start_time = time.time()
                start_time = time.time()
                annotated_bgr, counts, total_count = detect_objects(image_bgr, conf_thresh, selected_class_ids)
                inference_time = (time.time() - start_time) * 1000
                
            # Convert back to RGB for displaying
            annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
            
            st.image(annotated_rgb, caption="Annotated Output", use_container_width=True)
            
            # Render statistics in the right panel
            with col_stats:
                st.subheader("📊 Image Statistics")
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_count}</div><div class='metric-label'>Total Detected Objects</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{inference_time:.1f} ms</div><div class='metric-label'>Inference Time</div></div>", unsafe_allow_html=True)
                
                st.write("---")
                st.subheader("📋 Class Breakdown")
                if counts:
                    import pandas as pd
                    df = pd.DataFrame(list(counts.items()), columns=["Object Class", "Count"]).sort_values("Count", ascending=False)
                    st.table(df)
                else:
                    st.info("No target objects detected.")
        else:
            st.info("Upload an image file to start object detection.")
            with col_stats:
                st.subheader("📊 Image Statistics")
                st.write("Upload an image on the left to see stats.")

elif app_mode == "Upload Video":
    with col_media:
        st.subheader("🎥 Video Detection Pane")
        uploaded_video = st.file_uploader("Upload a Video (MP4, AVI, MOV)", type=["mp4", "avi", "mov"])
        
        if uploaded_video is not None:
            # Save upload to temp file
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_video.read())
            tfile.close()
            
            cap = cv2.VideoCapture(tfile.name)
            
            # Get video specs
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            
            # Display details
            st.write(f"🎞️ Original Resolution: `{width}x{height}` | Total Frames: `{total_frames}` | FPS: `{fps:.1f}`")
            
            # Process video button
            start_btn = st.button("⚡ Start Video Processing")
            
            # Placeholder for video frame preview
            frame_placeholder = st.empty()
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            # Output file configuration
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            
            # Setup columns for metrics on the right side
            with col_stats:
                st.subheader("📊 Live Video Stats")
                stat_fps = st.empty()
                stat_total = st.empty()
                st.write("---")
                st.subheader("📋 Class Breakdown")
                stat_breakdown = st.empty()
                
                stat_fps.markdown("<div class='metric-card'><div class='metric-value'>0.0</div><div class='metric-label'>Processing FPS</div></div>", unsafe_allow_html=True)
                stat_total.markdown("<div class='metric-card'><div class='metric-value'>0</div><div class='metric-label'>Objects in Frame</div></div>", unsafe_allow_html=True)
                stat_breakdown.info("Start processing to view class statistics.")
            
            if start_btn:
                # Video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                frame_idx = 0
                prev_time = time.time()
                overall_counts = {}
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    # Detect
                    start_inf = time.time()
                    annotated_frame, frame_counts, frame_total = detect_objects(frame, conf_thresh, selected_class_ids)
                    
                    # Log running maximum counts
                    for c_name, c_cnt in frame_counts.items():
                        overall_counts[c_name] = max(overall_counts.get(c_name, 0), c_cnt)
                        
                    # Write frame
                    out_writer.write(annotated_frame)
                    
                    # Display preview
                    frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(frame_rgb, use_container_width=True)
                    
                    # Calculations
                    curr_time = time.time()
                    proc_fps = 1.0 / (curr_time - prev_time)
                    prev_time = curr_time
                    
                    # Update live metrics
                    stat_fps.markdown(f"<div class='metric-card'><div class='metric-value'>{proc_fps:.1f}</div><div class='metric-label'>Processing FPS</div></div>", unsafe_allow_html=True)
                    stat_total.markdown(f"<div class='metric-card'><div class='metric-value'>{frame_total}</div><div class='metric-label'>Objects in Current Frame</div></div>", unsafe_allow_html=True)
                    
                    if overall_counts:
                        import pandas as pd
                        df = pd.DataFrame(list(overall_counts.items()), columns=["Object Class", "Max in Frame Count"]).sort_values("Max in Frame Count", ascending=False)
                        stat_breakdown.table(df)
                    
                    # Update progress bar
                    frame_idx += 1
                    prog = min(float(frame_idx) / float(total_frames), 1.0)
                    progress_bar.progress(prog)
                    status_text.text(f"Processing frame {frame_idx}/{total_frames} ({prog*100:.1f}%)")
                    
                cap.release()
                out_writer.release()
                
                status_text.text("✅ Video processing completed! Packaging for download...")
                progress_bar.empty()
                
                # Load and enable download
                with open(output_path, "rb") as file:
                    processed_bytes = file.read()
                    
                st.success("🎉 Video processed successfully!")
                st.download_button(
                    label="📥 Download Annotated Video",
                    data=processed_bytes,
                    file_name="detected_objects.mp4",
                    mime="video/mp4"
                )
                
                # Cleanup
                try:
                    os.remove(tfile.name)
                    os.remove(output_path)
                except:
                    pass
        else:
            st.info("Upload a video file to start object detection.")
            with col_stats:
                st.subheader("📊 Live Video Stats")
                st.write("Upload a video on the left to see stats.")

# Footer
st.markdown("""
<div class='footer'>
    <p>AI Internship Project | Developed for CodeAlpha | © 2026</p>
</div>
""", unsafe_allow_html=True)
