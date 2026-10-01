#!/usr/bin/env python3
"""
Test vehicle counting with line crossing.
Processes video and counts vehicles crossing a virtual line.
"""

import cv2
from pathlib import Path
from detector import VehicleDetector
from tracker import CentroidTracker
from counter import LineCounter
from video_processor import VideoProcessor


def test_counting():
    """Test counting system."""
    print("=" * 60)
    print("VEHICLE COUNTING TEST")
    print("=" * 60)

    # Use the sample video from Phase 3
    video_path = Path("sample") / "traffic_sample.mp4"

    if not video_path.exists():
        print(f"ERROR: Video not found at {video_path}")
        return False

    # Initialize components
    print("\nInitializing detector, tracker, and counter...")
    try:
        detector = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
        tracker = CentroidTracker(max_distance=50, max_disappeared=30)

        # We'll set the line at middle of frame
        # (will adjust based on actual frame height once we know it)
        line_y = None
        counter = None

    except Exception as e:
        print(f"ERROR: Could not initialize: {e}")
        return False

    # Process video
    print(f"\nProcessing video: {video_path.name}")

    try:
        with VideoProcessor(str(video_path)) as processor:
            # Get frame height to set line
            line_y = int(processor.frame_height / 2)
            counter = LineCounter(line_y=line_y, frame_height=processor.frame_height)

            print(f"Counting line set at Y={line_y} (middle of frame)")

            def process_frame(frame, frame_num):
                # Detect
                detections = detector.detect(frame)

                # Track
                tracked_detections = tracker.update(detections)

                # Count
                count_result = counter.update(tracked_detections)

                return {
                    'frame_num': frame_num,
                    'detections': tracked_detections,
                    'count_result': count_result,
                }

            # Process first 120 frames (5 seconds at 24 fps)
            print("Processing first 120 frames...")
            results = processor.process_frames(
                process_frame,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=120
            )

            print(f"\n✓ Processed {len(results)} frames")
            print(f"\nFinal Counts:")
            counts = counter.get_counts_by_type()
            for vehicle_type, count in counts.items():
                print(f"  {vehicle_type.capitalize():12s}: {count}")

            # Write output video with counting visualization
            print("\nWriting output video with counting...")
            detector_out = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
            tracker_out = CentroidTracker(max_distance=50, max_disappeared=30)
            counter_out = LineCounter(line_y=line_y, frame_height=processor.frame_height)

            output_video_path = Path("outputs") / "test_counting_output.mp4"

            def frame_processor(frame, frame_num):
                detections = detector_out.detect(frame)
                tracked_detections = tracker_out.update(detections)
                counter_out.update(tracked_detections)

                # Annotate with detections
                annotated = detector_out.annotate_frame(
                    frame,
                    tracked_detections,
                    show_confidence=False,
                    show_track_id=True
                )

                # Draw counting line
                annotated = counter_out.draw_line(annotated, color=(255, 0, 0), thickness=2)

                # Draw counts
                annotated = counter_out.draw_counts(annotated, position='top-right')

                return annotated

            processor.write_output_video(
                str(output_video_path),
                frame_processor,
                frame_skip=1,
                resize_scale=1.0,
                max_frames=120
            )

    except Exception as e:
        print(f"ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ COUNTING TEST PASSED")
    print("=" * 60)
    print("\nYou are ready for Phase 6 (Analytics & CSV Export).")

    return True


if __name__ == "__main__":
    success = test_counting()
    exit(0 if success else 1)
