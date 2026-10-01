#!/usr/bin/env python3
"""
Test object tracking.
Processes video with tracking enabled.
"""

import cv2
from pathlib import Path
from detector import VehicleDetector
from tracker import CentroidTracker
from video_processor import VideoProcessor


def test_tracking():
    """Test tracking system."""
    print("=" * 60)
    print("OBJECT TRACKING TEST")
    print("=" * 60)

    # Use the sample video from Phase 3
    video_path = Path("sample") / "traffic_sample.mp4"

    if not video_path.exists():
        print(f"ERROR: Video not found at {video_path}")
        print("Please run test_video.py first to download the sample video.")
        return False

    # Initialize detector and tracker
    print("\nInitializing detector and tracker...")
    try:
        detector = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
        tracker = CentroidTracker(max_distance=50, max_disappeared=30)
    except Exception as e:
        print(f"ERROR: Could not initialize: {e}")
        return False

    # Process video with tracking
    print(f"\nProcessing video with tracking: {video_path.name}")

    try:
        with VideoProcessor(str(video_path)) as processor:

            # Track statistics
            all_track_ids = set()
            frame_count = 0
            detection_count = 0

            def process_frame(frame, frame_num):
                nonlocal frame_count, detection_count

                # Detect
                detections = detector.detect(frame)
                detection_count += len(detections)

                # Track
                tracked_detections = tracker.update(detections)

                # Record all track IDs
                for det in tracked_detections:
                    if 'track_id' in det:
                        all_track_ids.add(det['track_id'])

                frame_count += 1
                return tracked_detections

            # Process first 60 frames
            print("Processing first 60 frames...")
            results = processor.process_frames(
                process_frame,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=60
            )

            print(f"\n✓ Processed {frame_count} frames")
            print(f"Total detections: {detection_count}")
            print(f"Average detections/frame: {detection_count / frame_count:.1f}")
            print(f"Unique track IDs assigned: {len(all_track_ids)}")
            print(f"Track IDs: {sorted(list(all_track_ids))[:20]}")

            # Write output video with tracking
            print("\nWriting output video with tracking...")
            tracker.next_object_id = 0  # Reset tracker
            tracker.objects = {}
            tracker.disappeared = {}

            output_video_path = Path("outputs") / "test_tracking_output.mp4"

            def frame_processor(frame, frame_num):
                detections = detector.detect(frame)
                tracked_detections = tracker.update(detections)
                annotated = detector.annotate_frame(
                    frame,
                    tracked_detections,
                    show_confidence=True,
                    show_track_id=True
                )
                return annotated

            processor.write_output_video(
                str(output_video_path),
                frame_processor,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=60
            )

    except Exception as e:
        print(f"ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ TRACKING TEST PASSED")
    print("=" * 60)
    print("\nYou are ready for Phase 5 (Vehicle Filtering & Counting).")

    return True


if __name__ == "__main__":
    success = test_tracking()
    exit(0 if success else 1)
