#!/usr/bin/env python3
"""
Traffic Vehicle Detection & Counting System
Web Dashboard using Streamlit

Main application entry point.
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import tempfile
from detector import VehicleDetector
from tracker import CentroidTracker
from counter import LineCounter
from video_processor import VideoProcessor
from analytics import TrafficAnalytics
import time


# Page configuration
st.set_page_config(
    page_title="Traffic Vehicle Analyzer",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🚗 Traffic Vehicle Detection & Counting System")
st.markdown("""
This application analyzes traffic video to detect, classify, track, and count vehicles.

**Features:**
- Real-time vehicle detection using YOLO
- Multi-vehicle tracking
- Line-crossing vehicle counting
- Traffic statistics and analytics
- CSV data export
""")

# ============================================================================
# SIDEBAR - Configuration
# ============================================================================

st.sidebar.header("⚙️ Configuration")

# Confidence threshold
confidence_threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.5,
    step=0.05,
    help="Only detections above this confidence are shown"
)

# Frame processing
frame_skip = st.sidebar.slider(
    "Frame Skip",
    min_value=1,
    max_value=5,
    value=1,
    help="Process every Nth frame (higher = faster but less accurate)"
)

# Resize scale
resize_scale = st.sidebar.slider(
    "Resize Scale",
    min_value=0.5,
    max_value=1.0,
    value=1.0,
    step=0.1,
    help="Resize frames for faster processing (lower = faster)"
)

# Counting line position
counting_line_position = st.sidebar.slider(
    "Counting Line Position (%)",
    min_value=10,
    max_value=90,
    value=50,
    step=10,
    help="Vertical position of counting line (% of frame height)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.markdown("""
This is a prototype system using:
- **YOLOv8n** (pretrained)
- **Centroid tracking**
- **Line-crossing detection**

**Limitations:**
- Pretrained model (not fine-tuned for traffic)
- Simple centroid tracking (can fail with occlusion)
- CPU-based (slower on laptops)
""")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Video upload
st.header("📹 Upload Traffic Video")

video_file = st.file_uploader(
    "Choose a video file",
    type=['mp4', 'avi', 'mov', 'mkv'],
    help="Supported formats: MP4, AVI, MOV, MKV"
)

if video_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_file.read())
        temp_video_path = tmp_file.name

    st.success(f"✓ Video uploaded: {video_file.name}")

    # Show video info
    with st.spinner("Loading video..."):
        try:
            cap = cv2.VideoCapture(temp_video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Resolution", f"{frame_width}x{frame_height}")
            with col2:
                st.metric("FPS", f"{fps:.1f}")
            with col3:
                st.metric("Duration", f"{duration:.1f}s")
            with col4:
                st.metric("Total Frames", total_frames)

        except Exception as e:
            st.error(f"Error reading video: {e}")
            st.stop()

    # Processing options
    st.header("🔧 Processing Options")

    col1, col2 = st.columns(2)
    with col1:
        max_frames_to_process = st.number_input(
            "Max Frames to Process",
            min_value=10,
            max_value=total_frames,
            value=min(300, total_frames),
            step=10,
            help="Limit processing to first N frames"
        )

    with col2:
        process_button = st.button("🚀 Start Processing", use_container_width=True)

    if process_button:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            with st.spinner("Processing video..."):
                # Initialize components
                status_text.text("Initializing detector...")
                detector = VehicleDetector(
                    model_name='yolov8n.pt',
                    confidence=confidence_threshold
                )

                tracker = CentroidTracker(max_distance=50, max_disappeared=30)

                # Calculate counting line position
                line_y = int(frame_height * (counting_line_position / 100))
                counter = LineCounter(line_y=line_y, frame_height=frame_height)

                analytics = TrafficAnalytics(video_duration_seconds=duration)

                # Process video
                status_text.text("Processing frames...")
                results = []
                annotated_frames = []

                with VideoProcessor(temp_video_path) as processor:
                    frame_num = 0
                    processed_count = 0

                    while True:
                        ret, frame = processor.cap.read()
                        if not ret:
                            break

                        if frame_num % frame_skip != 0:
                            frame_num += 1
                            continue

                        # Resize if needed
                        if resize_scale != 1.0:
                            h, w = frame.shape[:2]
                            new_w = int(w * resize_scale)
                            new_h = int(h * resize_scale)
                            frame = cv2.resize(frame, (new_w, new_h))

                        # Detect
                        detections = detector.detect(frame)

                        # Track
                        tracked_detections = tracker.update(detections)

                        # Count
                        count_result = counter.update(tracked_detections)

                        # Annotate
                        annotated = detector.annotate_frame(
                            frame,
                            tracked_detections,
                            show_confidence=True,
                            show_track_id=True
                        )
                        annotated = counter.draw_line(annotated)
                        annotated = counter.draw_counts(annotated, position='top-right')

                        annotated_frames.append(annotated)
                        results.append(count_result)

                        processed_count += 1
                        progress = processed_count / max_frames_to_process
                        progress_bar.progress(min(progress, 1.0))
                        status_text.text(f"Processed {processed_count}/{max_frames_to_process} frames...")

                        if processed_count >= max_frames_to_process:
                            break

                        frame_num += 1

                # Get final counts
                final_counts = counter.get_counts_by_type()
                analytics.add_counts(final_counts)

                status_text.text("✓ Processing complete!")
                progress_bar.progress(1.0)

                # ============================================================
                # RESULTS
                # ============================================================

                st.header("📊 Analysis Results")

                # Summary metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Vehicles", final_counts['total'])
                with col2:
                    st.metric("Cars", final_counts['car'])
                with col3:
                    st.metric("Motorcycles", final_counts['motorcycle'])
                with col4:
                    st.metric("Buses", final_counts['bus'])
                with col5:
                    st.metric("Trucks", final_counts['truck'])

                # Vehicle distribution chart
                if final_counts['total'] > 0:
                    st.subheader("Vehicle Type Distribution")
                    chart_data = {
                        'Car': final_counts['car'],
                        'Motorcycle': final_counts['motorcycle'],
                        'Bus': final_counts['bus'],
                        'Truck': final_counts['truck'],
                    }
                    st.bar_chart(chart_data)

                # Display sample frame
                st.subheader("Sample Annotated Frame")
                if annotated_frames:
                    # Convert BGR to RGB for display
                    sample_frame = annotated_frames[len(annotated_frames) // 2]
                    sample_frame_rgb = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
                    st.image(sample_frame_rgb, use_column_width=True)

                # Export options
                st.subheader("💾 Export Results")

                col1, col2 = st.columns(2)

                with col1:
                    # CSV export
                    csv_path = Path("outputs") / "traffic_analysis.csv"
                    csv_path.parent.mkdir(exist_ok=True)
                    analytics.export_csv(str(csv_path))

                    with open(csv_path, 'r') as f:
                        csv_content = f.read()

                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_content,
                        file_name="traffic_analysis.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col2:
                    # JSON export
                    import json
                    json_data = json.dumps(analytics.get_summary(), indent=2)

                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name="traffic_analysis.json",
                        mime="application/json",
                        use_container_width=True
                    )

                # Detailed results
                st.subheader("📋 Detailed Statistics")

                with st.expander("View Summary"):
                    summary = analytics.get_summary()
                    for key, value in summary.items():
                        st.write(f"**{key}:** {value}")

        except Exception as e:
            st.error(f"Error during processing: {e}")
            import traceback
            st.error(traceback.format_exc())

    # Clean up
    Path(temp_video_path).unlink(missing_ok=True)

else:
    st.info("👆 Upload a video file to get started")

    st.markdown("""
    ---
    ### Example Usage:
    1. Upload a traffic video (MP4, AVI, MOV, or MKV)
    2. Adjust detection and processing settings in the sidebar
    3. Click "Start Processing"
    4. View results and download analytics

    ### Sample Videos:
    You can find free traffic videos on:
    - [Pexels](https://www.pexels.com/search/traffic/)
    - [Pixabay](https://pixabay.com/videos/search/traffic/)
    - [Unsplash](https://unsplash.com/napi/videos/search)
    """)
