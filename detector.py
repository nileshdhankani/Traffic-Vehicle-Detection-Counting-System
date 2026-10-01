"""
Vehicle Detector using Ultralytics YOLO
Handles object detection, filtering, and annotation.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path


class VehicleDetector:
    """
    Detects vehicles in images/frames using pretrained YOLO model.

    Supported vehicle classes:
    - car
    - motorcycle
    - bus
    - truck
    """

    # YOLO class names to vehicle categories
    VEHICLE_CLASSES = {
        'car': 'car',
        'motorcycle': 'motorcycle',
        'bus': 'bus',
        'truck': 'truck',
        'motorbike': 'motorcycle',  # Alternative name
        'bikes': 'motorcycle',       # Alternative name
    }

    def __init__(self, model_name='yolov8n.pt', confidence=0.5):
        """
        Initialize the detector with a pretrained YOLO model.

        Args:
            model_name (str): Name of the pretrained model
                             'yolov8n.pt' = nano (fastest, ~3.2M params)
                             'yolov8s.pt' = small (faster, ~11.2M params)
                             Default is nano for CPU efficiency
            confidence (float): Confidence threshold (0-1)
        """
        self.model_name = model_name
        self.confidence = confidence

        print(f"Loading YOLO model: {model_name}")
        self.model = YOLO(model_name)
        print(f"✓ Model loaded successfully")

        # Get all class names from the model
        self.all_classes = self.model.names
        print(f"Available classes: {list(self.all_classes.values())[:10]}...")

    def filter_vehicle_classes(self, detections):
        """
        Filter detections to only vehicle classes we care about.

        Args:
            detections: YOLO results object

        Returns:
            list: Filtered detections with only vehicle classes
        """
        filtered = []

        # Get boxes and class IDs from detections
        boxes = detections.boxes

        if boxes is None or len(boxes) == 0:
            return filtered

        for box in boxes:
            class_id = int(box.cls[0])
            class_name = self.all_classes[class_id].lower()

            # Check if this class is a vehicle we care about
            if class_name in self.VEHICLE_CLASSES:
                filtered.append({
                    'box': box.xyxy[0].cpu().numpy(),  # [x1, y1, x2, y2]
                    'confidence': float(box.conf[0]),
                    'class_id': class_id,
                    'class_name': self.VEHICLE_CLASSES[class_name],
                    'raw_class_name': class_name,
                })

        return filtered

    def detect(self, frame):
        """
        Detect vehicles in a frame.

        Args:
            frame (np.ndarray): Input frame (BGR)

        Returns:
            list: List of detections
        """
        # Run YOLO inference
        results = self.model(frame, conf=self.confidence, verbose=False)

        # Filter to vehicle classes only
        detections = self.filter_vehicle_classes(results[0])

        return detections

    def annotate_frame(self, frame, detections, show_confidence=True, show_track_id=False):
        """
        Draw bounding boxes and labels on frame.

        Args:
            frame (np.ndarray): Input frame (BGR)
            detections (list): List of detections from detect()
            show_confidence (bool): Whether to show confidence scores
            show_track_id (bool): Whether to show tracking IDs

        Returns:
            np.ndarray: Annotated frame
        """
        annotated = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = map(int, det['box'])
            class_name = det['class_name'].upper()
            confidence = det['confidence']
            track_id = det.get('track_id', None)

            # Draw bounding box (green for vehicles)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Prepare label
            label_parts = [class_name]

            if show_track_id and track_id is not None:
                label_parts.append(f"#{track_id}")

            if show_confidence:
                label_parts.append(f"{confidence:.2f}")

            label = " ".join(label_parts)

            # Put text with black background for readability
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1

            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            text_x = x1
            text_y = y1 - 5

            # Background rectangle
            cv2.rectangle(
                annotated,
                (text_x, text_y - text_size[1] - 5),
                (text_x + text_size[0] + 5, text_y + 5),
                (0, 0, 0),
                -1
            )

            # Text
            cv2.putText(
                annotated,
                label,
                (text_x + 2, text_y - 2),
                font,
                font_scale,
                (0, 255, 0),
                thickness
            )

            # Draw centroid if tracking
            if show_track_id and track_id is not None:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                cv2.circle(annotated, (cx, cy), 4, (0, 255, 255), -1)

        return annotated
