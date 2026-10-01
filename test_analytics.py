#!/usr/bin/env python3
"""
Test analytics and data export.
"""

from pathlib import Path
from analytics import TrafficAnalytics


def test_analytics():
    """Test analytics system."""
    print("=" * 60)
    print("ANALYTICS & EXPORT TEST")
    print("=" * 60)

    # Create analytics instance
    print("\nInitializing analytics...")
    analytics = TrafficAnalytics(video_duration_seconds=120)

    # Simulate some vehicle counts
    test_counts = {
        'car': 27,
        'motorcycle': 18,
        'bus': 3,
        'truck': 5,
        'total': 53,
    }

    analytics.add_counts(test_counts)

    # Simulate some vehicle records
    test_records = [
        {'track_id': 0, 'class': 'car', 'direction': 'down', 'time': 2.5},
        {'track_id': 1, 'class': 'motorcycle', 'direction': 'up', 'time': 3.2},
        {'track_id': 2, 'class': 'car', 'direction': 'down', 'time': 4.1},
        {'track_id': 3, 'class': 'truck', 'direction': 'down', 'time': 5.5},
        {'track_id': 4, 'class': 'bus', 'direction': 'up', 'time': 7.2},
    ]

    for record in test_records:
        analytics.add_vehicle_record(record)

    print("✓ Analytics initialized with test data")

    # Print summary
    print("\nGenerating summary...")
    analytics.print_summary()

    # Export CSV
    print("\nExporting to CSV...")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "test_traffic_analysis.csv"
    analytics.export_csv(str(csv_path))

    # Verify CSV was created
    if csv_path.exists():
        print(f"✓ CSV file created: {csv_path}")
        print("\nCSV Contents:")
        with open(csv_path, 'r') as f:
            for line in f:
                print(f"  {line.rstrip()}")
    else:
        print(f"ERROR: CSV file not created at {csv_path}")
        return False

    # Export JSON
    print("\nExporting to JSON...")
    json_path = output_dir / "test_traffic_analysis.json"
    analytics.export_json(str(json_path))

    # Verify JSON was created
    if json_path.exists():
        print(f"✓ JSON file created: {json_path}")
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"✓ JSON is valid")
        print(f"  Total vehicles in JSON: {data['summary']['total_vehicles']}")
    else:
        print(f"ERROR: JSON file not created at {json_path}")
        return False

    print("\n" + "=" * 60)
    print("✓ ANALYTICS & EXPORT TEST PASSED")
    print("=" * 60)
    print("\nYou are ready for Phase 7 (Streamlit Dashboard).")

    return True


if __name__ == "__main__":
    success = test_analytics()
    exit(0 if success else 1)
