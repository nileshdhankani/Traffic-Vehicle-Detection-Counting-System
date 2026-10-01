#!/usr/bin/env python3
"""
Phase 8 Test: Streamlit Dashboard
Tests that all dashboard components are properly configured.
"""

import sys
import io
from pathlib import Path

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("PHASE 8: STREAMLIT DASHBOARD TEST")
    print("=" * 60)

    print("\n1. Testing imports...")
    try:
        import streamlit as st
        print("  ✓ streamlit")
    except ImportError as e:
        print(f"  ✗ streamlit: {e}")
        return False

    try:
        from detector import VehicleDetector
        print("  ✓ detector.VehicleDetector")
    except ImportError as e:
        print(f"  ✗ detector: {e}")
        return False

    try:
        from tracker import CentroidTracker
        print("  ✓ tracker.CentroidTracker")
    except ImportError as e:
        print(f"  ✗ tracker: {e}")
        return False

    try:
        from counter import LineCounter
        print("  ✓ counter.LineCounter")
    except ImportError as e:
        print(f"  ✗ counter: {e}")
        return False

    try:
        from video_processor import VideoProcessor
        print("  ✓ video_processor.VideoProcessor")
    except ImportError as e:
        print(f"  ✗ video_processor: {e}")
        return False

    try:
        from analytics import TrafficAnalytics
        print("  ✓ analytics.TrafficAnalytics")
    except ImportError as e:
        print(f"  ✗ analytics: {e}")
        return False

    return True


def test_model_loading():
    """Test that YOLO model can be loaded."""
    print("\n2. Testing YOLO model loading...")
    try:
        from detector import VehicleDetector
        detector = VehicleDetector(model_name='yolov8n.pt', confidence=0.5)
        print(f"  ✓ Model loaded: {detector.model_name}")
        print(f"  ✓ Confidence threshold: {detector.confidence}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading model: {e}")
        return False


def test_sample_video():
    """Test that sample video exists and is readable."""
    print("\n3. Testing sample video...")
    try:
        import cv2
        video_path = Path("sample/traffic_sample.mp4")

        if not video_path.exists():
            print(f"  ✗ Sample video not found: {video_path}")
            return False

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"  ✗ Cannot open video: {video_path}")
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0

        cap.release()

        print(f"  ✓ Sample video: {video_path.name}")
        print(f"    Resolution: {width}x{height}")
        print(f"    FPS: {fps:.1f}")
        print(f"    Duration: {duration:.1f}s ({frames} frames)")
        return True
    except Exception as e:
        print(f"  ✗ Error reading video: {e}")
        return False


def test_output_directory():
    """Test that output directory exists."""
    print("\n4. Testing output directory...")
    try:
        output_dir = Path("outputs")
        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True)
            print(f"  ✓ Created outputs directory")
        else:
            print(f"  ✓ Outputs directory exists")
        return True
    except Exception as e:
        print(f"  ✗ Error with outputs directory: {e}")
        return False


def test_app_structure():
    """Test that app.py has all required sections."""
    print("\n5. Testing app.py structure...")
    try:
        app_path = Path("app.py")
        if not app_path.exists():
            print(f"  ✗ app.py not found")
            return False

        # Read with error handling for encoding
        try:
            content = app_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = app_path.read_text(encoding='latin-1')

        # Check for key sections
        checks = {
            'page_config': 'st.set_page_config' in content,
            'sidebar_config': 'st.sidebar.header' in content,
            'video_upload': 'st.file_uploader' in content,
            'processing': 'VehicleDetector' in content,
            'tracking': 'CentroidTracker' in content,
            'counting': 'LineCounter' in content,
            'results_display': 'st.metric' in content,
            'csv_export': 'st.download_button' in content,
            'chart': 'st.bar_chart' in content,
        }

        all_pass = True
        for check_name, check_result in checks.items():
            status = "[OK]" if check_result else "[FAIL]"
            print(f"  {status} {check_name}")
            if not check_result:
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"  [ERROR] Error checking app structure: {e}")
        return False


def test_configuration_options():
    """Test that configuration options are accessible."""
    print("\n6. Testing configuration options...")
    try:
        from detector import VehicleDetector
        from tracker import CentroidTracker
        from counter import LineCounter
        from analytics import TrafficAnalytics

        # Test detector config
        detector = VehicleDetector(confidence=0.6)
        print(f"  ✓ Detector confidence: {detector.confidence}")

        # Test tracker config
        tracker = CentroidTracker(max_distance=50, max_disappeared=30)
        print(f"  ✓ Tracker max_distance: {tracker.max_distance}")
        print(f"  ✓ Tracker max_disappeared: {tracker.max_disappeared}")

        # Test counter config
        counter = LineCounter(line_y=240, frame_height=480)
        print(f"  ✓ Counter line_y: {counter.line_y}")

        # Test analytics
        analytics = TrafficAnalytics(video_duration_seconds=10.0)
        print(f"  ✓ Analytics video_duration: {analytics.video_duration_seconds}s")

        return True
    except Exception as e:
        print(f"  ✗ Error testing configuration: {e}")
        return False


def test_analytics_export():
    """Test that analytics can export data."""
    print("\n7. Testing analytics export...")
    try:
        from analytics import TrafficAnalytics

        analytics = TrafficAnalytics(video_duration_seconds=30.0)
        analytics.add_counts({
            'car': 10,
            'motorcycle': 5,
            'bus': 2,
            'truck': 3,
            'total': 20
        })

        # Get summary
        summary = analytics.get_summary()
        print(f"  ✓ Summary generated")
        print(f"    Total: {summary['total_vehicles']}")
        print(f"    Cars: {summary['cars']} ({summary['car_percentage']}%)")

        # Test CSV export
        csv_path = Path("outputs/test_export.csv")
        csv_path.parent.mkdir(exist_ok=True)
        analytics.export_csv(str(csv_path))

        if csv_path.exists():
            print(f"  ✓ CSV exported: {csv_path}")
            csv_path.unlink()
        else:
            print(f"  ✗ CSV export failed")
            return False

        return True
    except Exception as e:
        print(f"  ✗ Error testing analytics: {e}")
        return False


def main():
    """Run all tests."""
    tests = [
        test_imports,
        test_model_loading,
        test_sample_video,
        test_output_directory,
        test_app_structure,
        test_configuration_options,
        test_analytics_export,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_func.__name__}: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if all(results):
        print("\n✓ PHASE 8 COMPLETE: Streamlit Dashboard Ready!")
        print("\nTo run the dashboard:")
        print("  streamlit run app.py")
        print("\nOr with venv:")
        print("  venv/Scripts/streamlit run app.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
