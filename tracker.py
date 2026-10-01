"""
Object Tracker Module
Tracks detected vehicles across frames using centroid tracking.
"""

import numpy as np
from scipy.spatial.distance import cdist
from typing import Dict, List, Tuple


class CentroidTracker:
    """
    Simple centroid-based object tracker.

    How it works:
    1. Compute centroid of each detection in current frame
    2. Match with previous frame centroids (closest = same object)
    3. Assign tracking IDs
    4. Remove tracks that disappear for too long

    This is a simple approach suitable for moderate traffic density.
    Works well when:
    - Objects don't overlap too much
    - Objects move predictably
    - No rapid direction changes

    Limitations:
    - Can fail with dense traffic/occlusion
    - ID switches when objects cross
    - Requires tuning of distance threshold
    """

    def __init__(self, max_distance=50, max_disappeared=30):
        """
        Initialize tracker.

        Args:
            max_distance (int): Maximum pixel distance to match centroid
                               Decrease for stricter matching (more ID switches)
                               Increase for looser matching (more ID drift)
            max_disappeared (int): Max frames before removing track
        """
        self.next_object_id = 0
        self.objects = {}  # {track_id: last_centroid}
        self.disappeared = {}  # {track_id: frames_disappeared}
        self.max_distance = max_distance
        self.max_disappeared = max_disappeared

    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections.

        Args:
            detections (list): List of detections from detector
                             Each has: box, confidence, class_name, etc.

        Returns:
            list: Detections with added 'track_id' field
        """
        if len(detections) == 0:
            # No detections this frame
            # Mark all tracks as disappeared
            for track_id in list(self.disappeared.keys()):
                self.disappeared[track_id] += 1

                if self.disappeared[track_id] > self.max_disappeared:
                    self._deregister(track_id)

            return []

        # Compute centroids of current detections
        centroids = []
        for det in detections:
            x1, y1, x2, y2 = det['box']
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            centroids.append([cx, cy])

        centroids = np.array(centroids)

        # If no tracked objects, register all detections as new
        if len(self.objects) == 0:
            for i, centroid in enumerate(centroids):
                self._register(centroid)
                detections[i]['track_id'] = self.next_object_id - 1
            return detections

        # Match current centroids to tracked objects
        object_ids = list(self.objects.keys())
        object_centroids = np.array(list(self.objects.values()))

        # Compute distances
        distances = cdist(object_centroids, centroids)

        # Greedy matching: assign each detection to closest track
        row_indices = np.arange(0, distances.shape[0])
        col_indices = np.zeros(distances.shape[0], dtype=int)

        # Simple greedy assignment
        used_cols = set()
        for i in range(len(row_indices)):
            # Find closest unused detection
            valid_cols = [j for j in range(distances.shape[1]) if j not in used_cols]
            if not valid_cols:
                break

            valid_distances = distances[i, valid_cols]
            best_valid_idx = np.argmin(valid_distances)
            best_col = valid_cols[best_valid_idx]
            best_distance = valid_distances[best_valid_idx]

            if best_distance < self.max_distance:
                col_indices[i] = best_col
                used_cols.add(best_col)
            else:
                # No match for this track
                col_indices[i] = -1

        # Process matched and unmatched tracks/detections
        matched_object_ids = set()
        for i, row_idx in enumerate(row_indices):
            track_id = object_ids[row_idx]
            col_idx = col_indices[i]

            if col_idx >= 0:
                # Match found
                centroid = centroids[col_idx]
                self.objects[track_id] = centroid
                self.disappeared[track_id] = 0
                detections[col_idx]['track_id'] = track_id
                matched_object_ids.add(col_idx)
            else:
                # No match - mark as disappeared
                self.disappeared[track_id] += 1

                if self.disappeared[track_id] > self.max_disappeared:
                    self._deregister(track_id)

        # Register unmatched detections as new objects
        unmatched_cols = [i for i in range(len(centroids)) if i not in matched_object_ids]
        for col_idx in unmatched_cols:
            centroid = centroids[col_idx]
            self._register(centroid)
            detections[col_idx]['track_id'] = self.next_object_id - 1

        return detections

    def _register(self, centroid):
        """Register a new object."""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def _deregister(self, object_id):
        """Deregister a tracked object."""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def get_active_ids(self):
        """Get list of currently active track IDs."""
        return list(self.objects.keys())
