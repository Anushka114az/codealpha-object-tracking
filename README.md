# Project 3: Real-Time Object Detection Dashboard (CodeAlpha AI Internship)

A real-time object detection and analysis dashboard built using Streamlit, OpenCV, and YOLOv8. The application allows users to upload images and videos, perform instant object detection, draw bounding boxes with confidence scores, filter results by specific classes, and view real-time statistics and counts.

## Features

* **Multi-Format Support**: Upload static images (PNG, JPG, JPEG) or video files (MP4, AVI, MOV) for instant object detection.
* **YOLOv8 Inference**: Leverages a pre-trained YOLOv8 Nano model (trained on MS COCO dataset) for high-performance and lightweight detection.
* **Dynamic Bounding Boxes**: Automatically overlays bounding boxes, class labels, and confidence percentages.
* **Filter Detection Classes**: Select specific object classes (e.g. person, car, dog) to detect and count, filtering out unwanted detections.
* **Live Analytics**: Displays inference times (for images), real-time processing FPS (for videos), total detected objects, and a class count breakdown table.
* **Video Export**: Process uploaded video files frame-by-frame and download the annotated output video.
* **Premium Dark UI**: Customized Streamlit with glassmorphic cards, custom typography, and vibrant green gradients.

---

## Folder Structure

```
project3_object_tracking/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
└── README.md                  # Project instructions & details
```

---

## Technical Stack

* **Language**: Python 3.8+
* **Framework**: Streamlit
* **Computer Vision**: OpenCV (opencv-python)
* **Object Detection**: YOLOv8 (ultralytics)

---

## Installation & Setup

### 1. Navigate to the Directory
```bash
cd project3_object_tracking
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

Open https://codealpha-object-tracking.streamlit.app/ in your browser.
