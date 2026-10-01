#!/usr/bin/env python3
"""
Test video processing.
Downloads a sample traffic video and processes it.
"""

import cv2
from pathlib import Path
from detector import VehicleDetector
from video_processor import VideoProcessor
import urllib.request
import os


def download_sample_video():
    """
    Download a sample traffic video for testing.
    Using a public domain traffic video.
    """
    output_dir = Path("sample")
    output_dir.mkdir(exist_ok=True)

    video_path = output_dir / "traffic_sample.mp4"

    if video_path.exists():
        print(f"✓ Sample video already exists: {video_path}")
        return video_path

    print("Downloading sample traffic video...")
    print("(This may take 30-60 seconds)")

    # Using a short public traffic video from Pexels
    # (free, public domain)
    url = "https://videos.pexels.com/video-files/3045163/3045163-sd_640_360_30fps.mp4"

    try:
        urllib.request.urlretrieve(url, video_path)
        file_size = os.path.getsize(video_path)
        print(f"✓ Sample video downloaded: {video_path} ({file_size / 1024 / 1024:.1f} MB)")
        return video_path
    except Exception as e:
        print(f"⚠ Could not download video from Pexels: {e}")
        print("Trying alternative source...")

        # Fallback: try another source
        try:
            url2 = "https://media.w3.org/2010/05/sintel/trailer.mp4"
            urllib.request.urlretrieve(url2, video_path)
            print(f"✓ Sample video downloaded from alternative source: {video_path}")
            return video_path
        except Exception as e2:
            print(f"⚠ Could not download video: {e2}")
            print("Please manually place a traffic video at: sample/traffic_sample.mp4")
            return None


def test_video_processing():
    """Test video processing."""
    print("=" * 60)
    print("VIDEO PROCESSING TEST")
    print("=" * 60)

    # Get/download sample video
    video_path = download_sample_video()

    if video_path is None or not video_path.exists():
        print("ERROR: No video file available for testing")
        print("Please place a traffic video at: sample/traffic_sample.mp4")
        return False

    # Initialize detector
    print("\nInitializing detector...")
    try:
        detector = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
    except Exception as e:
        print(f"ERROR: Could not initialize detector: {e}")
        return False

    # Process video
    print(f"\nProcessing video: {video_path.name}")

    try:
        with VideoProcessor(str(video_path)) as processor:

            # Define frame processing function
            def process_frame(frame, frame_num):
                detections = detector.detect(frame)
                annotated = detector.annotate_frame(frame, detections)
                return {
                    'frame_num': frame_num,
                    'detection_count': len(detections),
                    'detections': detections,
                    'annotated_frame': annotated
                }

            # Process first 30 frames only (for speed)
            print("Processing first 30 frames for test...")
            results = processor.process_frames(
                process_frame,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=30
            )

            print(f"\n✓ Processed {len(results)} frames")

            # Print statistics
            total_detections = sum(r['detection_count'] for r in results)
            avg_detections = total_detections / len(results) if results else 0

            print(f"Total detections: {total_detections}")
            print(f"Average per frame: {avg_detections:.1f}")

            # Save a sample annotated frame
            if results:
                sample_frame = results[5]['annotated_frame']  # Frame 5
                output_dir = Path("outputs")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / "test_video_frame_sample.jpg"
                cv2.imwrite(str(output_path), sample_frame)
                print(f"✓ Sample frame saved: {output_path}")

            # Try to write full output video (first 30 frames)
            print("\nWriting output video (30 frames)...")
            output_video_path = Path("outputs") / "test_video_output.mp4"

            def frame_processor(frame, frame_num):
                detections = detector.detect(frame)
                annotated = detector.annotate_frame(frame, detections)
                return annotated

            processor.write_output_video(
                str(output_video_path),
                frame_processor,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=30
            )

    except Exception as e:
        print(f"ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ VIDEO PROCESSING TEST PASSED")
    print("=" * 60)
    print("\nYou are ready for Phase 4 (Object Tracking).")

    return True


if __name__ == "__main__":
    success = test_video_processing()
    exit(0 if success else 1)
