"""
Video Processing Module
Handles video input, frame extraction, and output video writing.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Tuple


class VideoProcessor:
    """
    Processes video files frame-by-frame.
    Supports input, frame-by-frame processing, and video output.
    """

    def __init__(self, video_path: str):
        """
        Initialize video processor.

        Args:
            video_path (str): Path to input video file
        """
        self.video_path = Path(video_path)
        self.cap = None
        self.fps = None
        self.frame_width = None
        self.frame_height = None
        self.total_frames = None

        self._open_video()

    def _open_video(self):
        """Open video file and extract metadata."""
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")

        self.cap = cv2.VideoCapture(str(self.video_path))

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video: {self.video_path}")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.fps <= 0:
            self.fps = 30  # Default fallback

        print(f"Video loaded: {self.video_path.name}")
        print(f"  Resolution: {self.frame_width}x{self.frame_height}")
        print(f"  FPS: {self.fps}")
        print(f"  Total frames: {self.total_frames}")
        print(f"  Duration: {self.total_frames / self.fps:.2f} seconds")

    def process_frames(
        self,
        process_fn: Callable,
        frame_skip: int = 1,
        resize_scale: float = 1.0,
        max_frames: Optional[int] = None
    ) -> list:
        """
        Process video frames with a custom function.

        Args:
            process_fn: Function to call for each frame
                       Signature: process_fn(frame, frame_num) -> result
            frame_skip: Process every Nth frame (1 = all frames)
            resize_scale: Resize frames (0.5 = half size, 1.0 = original)
            max_frames: Maximum frames to process (None = all)

        Returns:
            list: Results from process_fn for each processed frame
        """
        results = []
        frame_num = 0
        processed_count = 0

        while True:
            ret, frame = self.cap.read()

            if not ret:
                break

            # Skip frames if requested
            if frame_num % frame_skip != 0:
                frame_num += 1
                continue

            # Resize if requested
            if resize_scale != 1.0:
                h, w = frame.shape[:2]
                new_w = int(w * resize_scale)
                new_h = int(h * resize_scale)
                frame = cv2.resize(frame, (new_w, new_h))

            # Process frame
            result = process_fn(frame, frame_num)
            results.append(result)

            processed_count += 1

            if max_frames and processed_count >= max_frames:
                break

            frame_num += 1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start

        return results

    def write_output_video(
        self,
        output_path: str,
        frame_fn: Callable,
        frame_skip: int = 1,
        resize_scale: float = 1.0,
        max_frames: Optional[int] = None
    ) -> str:
        """
        Process video and write annotated output.

        Args:
            output_path (str): Path to output video file
            frame_fn: Function to process each frame
                     Signature: frame_fn(frame, frame_num) -> annotated_frame
            frame_skip: Process every Nth frame
            resize_scale: Resize frames
            max_frames: Maximum frames to process

        Returns:
            str: Path to output video
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine output properties
        out_fps = self.fps
        if frame_skip > 1:
            out_fps = self.fps / frame_skip

        # For output, we'll use original resolution
        out_width = self.frame_width
        out_height = self.frame_height

        # Adjust for resize
        if resize_scale != 1.0:
            out_width = int(self.frame_width * resize_scale)
            out_height = int(self.frame_height * resize_scale)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            out_fps,
            (out_width, out_height)
        )

        if not out.isOpened():
            raise RuntimeError(f"Could not create output video: {output_path}")

        frame_num = 0
        processed_count = 0

        print(f"Writing output video: {output_path.name}")

        while True:
            ret, frame = self.cap.read()

            if not ret:
                break

            # Skip frames if requested
            if frame_num % frame_skip != 0:
                frame_num += 1
                continue

            # Resize if requested
            if resize_scale != 1.0:
                h, w = frame.shape[:2]
                new_w = int(w * resize_scale)
                new_h = int(h * resize_scale)
                frame = cv2.resize(frame, (new_w, new_h))

            # Process frame
            annotated = frame_fn(frame, frame_num)

            # Write frame
            out.write(annotated)

            processed_count += 1
            if processed_count % 30 == 0:
                print(f"  Processed {processed_count} frames...", end='\r')

            if max_frames and processed_count >= max_frames:
                break

            frame_num += 1

        out.release()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start

        print(f"✓ Output video written: {output_path}")
        return str(output_path)

    def close(self):
        """Release video resources."""
        if self.cap:
            self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
