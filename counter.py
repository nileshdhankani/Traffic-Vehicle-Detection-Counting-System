"""
Vehicle Counting Module
Detects when vehicles cross a virtual line and counts them.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, List


class LineCounter:
    """
    Counts vehicles crossing a virtual counting line.

    How it works:
    1. Define a horizontal line (y-coordinate)
    2. Track vehicle centroids frame-by-frame
    3. Detect when centroid crosses the line
    4. Count each vehicle only once
    5. Track vehicles by direction (up/down)
    """

    def __init__(self, line_y: int, frame_height: int):
        """
        Initialize line counter.

        Args:
            line_y (int): Y-coordinate of the counting line
            frame_height (int): Height of video frames
        """
        self.line_y = line_y
        self.frame_height = frame_height

        # Tracking data
        self.tracked_vehicles = {}  # {track_id: {'last_y': y, 'counted': bool, 'direction': 'up'/'down'}}

        # Counts by vehicle type
        self.counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'total': 0
        }

        # Directional counts
        self.direction_counts = {
            'up': 0,
            'down': 0
        }

    def update(self, detections: List[Dict]) -> Dict:
        """
        Update counter with new detections (should have track_id and centroids).

        Args:
            detections (list): List of tracked detections

        Returns:
            dict: Updated counts and new_crosses
        """
        new_crosses = []

        for det in detections:
            track_id = det.get('track_id')
            class_name = det.get('class_name', 'unknown')
            x1, y1, x2, y2 = det['box']

            # Calculate centroid
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if track_id is None:
                continue

            # Check if this is a new track
            if track_id not in self.tracked_vehicles:
                self.tracked_vehicles[track_id] = {
                    'last_y': cy,
                    'counted': False,
                    'class_name': class_name,
                }
            else:
                vehicle = self.tracked_vehicles[track_id]
                last_y = vehicle['last_y']

                # Check for line crossing
                if not vehicle['counted']:
                    # Did centroid cross the line?
                    if (last_y < self.line_y <= cy) or (last_y > self.line_y >= cy):
                        # Line crossed!
                        direction = 'down' if cy > last_y else 'up'

                        # Increment counts
                        self.counts[class_name] += 1
                        self.counts['total'] += 1
                        self.direction_counts[direction] += 1

                        vehicle['counted'] = True
                        vehicle['direction'] = direction

                        new_crosses.append({
                            'track_id': track_id,
                            'class_name': class_name,
                            'direction': direction,
                            'x': cx,
                            'y': cy,
                        })

                # Update last position
                vehicle['last_y'] = cy

        # Clean up old tracks (optional - could keep history)
        # For now, keep all tracks

        return {
            'counts': self.counts.copy(),
            'direction_counts': self.direction_counts.copy(),
            'new_crosses': new_crosses,
        }

    def get_counts(self) -> Dict:
        """Get current vehicle counts."""
        return self.counts.copy()

    def get_counts_by_type(self) -> Dict:
        """Get counts broken down by vehicle type."""
        return {
            'car': self.counts['car'],
            'motorcycle': self.counts['motorcycle'],
            'bus': self.counts['bus'],
            'truck': self.counts['truck'],
            'total': self.counts['total'],
        }

    def draw_line(self, frame, color=(255, 0, 0), thickness=2):
        """
        Draw the counting line on frame.

        Args:
            frame (np.ndarray): Input frame (BGR)
            color (tuple): Line color (BGR)
            thickness (int): Line thickness

        Returns:
            np.ndarray: Frame with line drawn
        """
        h, w = frame.shape[:2]
        cv2.line(frame, (0, self.line_y), (w, self.line_y), color, thickness)

        # Add label
        cv2.putText(
            frame,
            "COUNTING LINE",
            (10, self.line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        return frame

    def draw_counts(self, frame, position='top-right'):
        """
        Draw vehicle counts on frame.

        Args:
            frame (np.ndarray): Input frame (BGR)
            position (str): 'top-right', 'top-left', 'bottom-right', 'bottom-left'

        Returns:
            np.ndarray: Frame with counts drawn
        """
        h, w = frame.shape[:2]

        # Prepare text
        lines = [
            f"TRAFFIC ANALYSIS",
            f"",
            f"Cars:        {self.counts['car']:3d}",
            f"Motorcycles: {self.counts['motorcycle']:3d}",
            f"Buses:       {self.counts['bus']:3d}",
            f"Trucks:      {self.counts['truck']:3d}",
            f"",
            f"Total:       {self.counts['total']:3d}",
        ]

        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 1
        line_height = 25

        # Calculate text box size
        max_width = 0
        for line in lines:
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            max_width = max(max_width, text_size[0])

        box_width = max_width + 20
        box_height = len(lines) * line_height + 15

        # Determine position
        if position == 'top-right':
            x = w - box_width - 10
            y = 30
        elif position == 'top-left':
            x = 10
            y = 30
        elif position == 'bottom-right':
            x = w - box_width - 10
            y = h - box_height - 10
        else:  # bottom-left
            x = 10
            y = h - box_height - 10

        # Draw background box
        cv2.rectangle(frame, (x, y), (x + box_width, y + box_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (x, y), (x + box_width, y + box_height), (0, 255, 0), 2)

        # Draw text
        for i, line in enumerate(lines):
            text_y = y + 20 + i * line_height
            cv2.putText(frame, line, (x + 10, text_y), font, font_scale, (0, 255, 0), thickness)

        return frame

    def reset(self):
        """Reset all counts."""
        self.counts = {'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0, 'total': 0}
        self.direction_counts = {'up': 0, 'down': 0}
        self.tracked_vehicles = {}
