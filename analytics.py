"""
Analytics Module
Generates traffic statistics and exports data.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime


class TrafficAnalytics:
    """
    Generates analytics from vehicle counts and detection data.
    """

    def __init__(self, video_duration_seconds: float = None):
        """
        Initialize analytics.

        Args:
            video_duration_seconds (float): Duration of processed video
        """
        self.video_duration_seconds = video_duration_seconds
        self.counts = {}
        self.vehicle_data = []

    def add_counts(self, counts: Dict):
        """
        Add vehicle counts data.

        Args:
            counts (dict): Vehicle counts by type
        """
        self.counts = counts.copy()

    def add_vehicle_record(self, record: Dict):
        """
        Add individual vehicle record.

        Args:
            record (dict): Vehicle data (track_id, class, direction, etc.)
        """
        self.vehicle_data.append(record)

    def get_summary(self) -> Dict:
        """
        Generate summary statistics.

        Returns:
            dict: Summary statistics
        """
        total = self.counts.get('total', 0)

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_vehicles': total,
            'cars': self.counts.get('car', 0),
            'motorcycles': self.counts.get('motorcycle', 0),
            'buses': self.counts.get('bus', 0),
            'trucks': self.counts.get('truck', 0),
        }

        # Calculate percentages
        if total > 0:
            summary['car_percentage'] = round(summary['cars'] / total * 100, 2)
            summary['motorcycle_percentage'] = round(summary['motorcycles'] / total * 100, 2)
            summary['bus_percentage'] = round(summary['buses'] / total * 100, 2)
            summary['truck_percentage'] = round(summary['trucks'] / total * 100, 2)
        else:
            summary['car_percentage'] = 0
            summary['motorcycle_percentage'] = 0
            summary['bus_percentage'] = 0
            summary['truck_percentage'] = 0

        # Calculate vehicles per minute if duration available
        if self.video_duration_seconds and self.video_duration_seconds > 0:
            duration_minutes = self.video_duration_seconds / 60
            summary['vehicles_per_minute'] = round(total / duration_minutes, 2)
            summary['video_duration_seconds'] = self.video_duration_seconds
            summary['video_duration_minutes'] = round(duration_minutes, 2)
        else:
            summary['vehicles_per_minute'] = None

        return summary

    def export_csv(self, output_path: str) -> str:
        """
        Export statistics as CSV.

        Args:
            output_path (str): Path to save CSV

        Returns:
            str: Path to saved CSV
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create dataframe
        data = {
            'Metric': [
                'Total Vehicles',
                'Cars',
                'Motorcycles',
                'Buses',
                'Trucks',
                '',
                'Car %',
                'Motorcycle %',
                'Bus %',
                'Truck %',
            ],
            'Count': [
                self.counts.get('total', 0),
                self.counts.get('car', 0),
                self.counts.get('motorcycle', 0),
                self.counts.get('bus', 0),
                self.counts.get('truck', 0),
                '',
                f"{self.counts.get('car', 0) / max(1, self.counts.get('total', 1)) * 100:.2f}%",
                f"{self.counts.get('motorcycle', 0) / max(1, self.counts.get('total', 1)) * 100:.2f}%",
                f"{self.counts.get('bus', 0) / max(1, self.counts.get('total', 1)) * 100:.2f}%",
                f"{self.counts.get('truck', 0) / max(1, self.counts.get('total', 1)) * 100:.2f}%",
            ]
        }

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)

        print(f"✓ CSV exported: {output_path}")
        return str(output_path)

    def export_json(self, output_path: str) -> str:
        """
        Export detailed statistics as JSON.

        Args:
            output_path (str): Path to save JSON

        Returns:
            str: Path to saved JSON
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'summary': self.get_summary(),
            'vehicle_counts': self.counts,
            'vehicle_records': self.vehicle_data,
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ JSON exported: {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("TRAFFIC ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"\nTotal Vehicles Detected: {summary['total_vehicles']}")
        print(f"\nBreakdown by Type:")
        print(f"  Cars:        {summary['cars']:3d} ({summary['car_percentage']:5.1f}%)")
        print(f"  Motorcycles: {summary['motorcycles']:3d} ({summary['motorcycle_percentage']:5.1f}%)")
        print(f"  Buses:       {summary['buses']:3d} ({summary['bus_percentage']:5.1f}%)")
        print(f"  Trucks:      {summary['trucks']:3d} ({summary['truck_percentage']:5.1f}%)")

        if summary['vehicles_per_minute'] is not None:
            print(f"\nTiming:")
            print(f"  Video Duration: {summary['video_duration_minutes']:.1f} minutes")
            print(f"  Vehicles/min:   {summary['vehicles_per_minute']:.1f}")

        print("\n" + "=" * 60)
