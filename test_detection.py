#!/usr/bin/env python3
"""
Test YOLO detection on a sample image.
Downloads a public traffic image and runs detection.
"""

import cv2
import numpy as np
from pathlib import Path
from detector import VehicleDetector
import urllib.request


def download_sample_image():
    """
    Download a public traffic image for testing.
    Using a free, public domain traffic image.
    """
    output_dir = Path("sample")
    output_dir.mkdir(exist_ok=True)

    image_path = output_dir / "traffic_sample.jpg"

    if image_path.exists():
        print(f"✓ Sample image already exists: {image_path}")
        return image_path

    print("Downloading sample traffic image...")
    # Using a public traffic image from Unsplash (public domain)
    url = "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800"

    try:
        urllib.request.urlretrieve(url, image_path)
        print(f"✓ Sample image downloaded: {image_path}")
        return image_path
    except Exception as e:
        print(f"⚠ Could not download image: {e}")
        print("Creating a dummy traffic-like image for testing...")

        # Create a dummy image (this won't have real vehicles, just for testing)
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy[:] = (100, 100, 100)  # Gray background
        cv2.putText(dummy, "Test Frame", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(str(image_path), dummy)
        print(f"✓ Dummy test image created: {image_path}")
        return image_path


def test_detection():
    """Test YOLO detection."""
    print("=" * 60)
    print("YOLO DETECTION TEST")
    print("=" * 60)

    # Download/prepare sample image
    image_path = download_sample_image()

    # Load image
    print(f"\nLoading image: {image_path}")
    frame = cv2.imread(str(image_path))

    if frame is None:
        print(f"ERROR: Could not read image from {image_path}")
        return False

    print(f"✓ Image loaded: {frame.shape}")

    # Initialize detector with nano model (fastest for CPU)
    print("\nInitializing detector...")
    try:
        detector = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
    except Exception as e:
        print(f"ERROR: Could not initialize detector: {e}")
        return False

    # Run detection
    print("\nRunning detection...")
    try:
        detections = detector.detect(frame)
    except Exception as e:
        print(f"ERROR: Detection failed: {e}")
        return False

    print(f"✓ Detection complete")
    print(f"Found {len(detections)} vehicle(s)")

    # Print detections
    if detections:
        print("\nDetections:")
        for i, det in enumerate(detections, 1):
            print(f"  [{i}] {det['class_name'].upper()}: conf={det['confidence']:.3f}")
    else:
        print("(No vehicles detected - this is OK for test images)")

    # Annotate frame
    print("\nAnnotating frame...")
    annotated = detector.annotate_frame(frame, detections, show_confidence=True)

    # Save output
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_detection_output.jpg"
    cv2.imwrite(str(output_path), annotated)
    print(f"✓ Annotated image saved: {output_path}")

    print("\n" + "=" * 60)
    print("✓ DETECTION TEST PASSED")
    print("=" * 60)
    print("\nYou are ready for Phase 3 (Video Processing).")

    return True


if __name__ == "__main__":
    success = test_detection()
    exit(0 if success else 1)
