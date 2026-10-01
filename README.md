# Traffic Vehicle Detection & Counting System

A simple tool to count vehicles in traffic videos using computer vision.

## What it does

The project processes a traffic video and counts how many vehicles pass through. It detects cars, motorcycles, buses, and trucks, tracks them as they move, and counts each one as it crosses an invisible line in the video.

## How to use

### Install dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Run the dashboard
```bash
streamlit run app.py
```

This opens a web interface where you can:
1. Upload a traffic video
2. Adjust detection settings
3. See the results with vehicle counts
4. Download the results as CSV

## How it works

1. **Load video** → Read frames from the video file
2. **Detect vehicles** → Use YOLO to find vehicles in each frame
3. **Track vehicles** → Match detections across frames so we know which vehicle is which
4. **Count crossings** → When a vehicle crosses the counting line, increment the count
5. **Show results** → Display counts by vehicle type

## Project structure

```
├── app.py              - Streamlit dashboard
├── detector.py         - YOLO vehicle detection
├── tracker.py          - Vehicle tracking across frames
├── counter.py          - Line crossing counting
├── video_processor.py  - Video input/output
├── analytics.py        - Statistics and export
├── requirements.txt    - Dependencies
└── sample/             - Demo video
```

## Technologies used

- **Python** - Language
- **OpenCV** - Video processing
- **YOLO (v8n)** - Vehicle detection (pretrained model)
- **Streamlit** - Web dashboard
- **Pandas** - Data handling

## Important notes

- Uses a **pretrained YOLO model** - not trained on traffic data
- Optimized for **CPU** (no GPU needed)
- **Simple centroid tracking** - works for moderate traffic
- Processes about **3-5 frames per second** on a laptop

## Limitations

- Tracking can fail when vehicles overlap
- Detection accuracy depends on video quality
- Virtual line assumes specific camera angle
- Not tested on real traffic camera feeds

## How to run tests

```bash
python test_phase8_dashboard.py
```

## What's in outputs/

After processing, results are saved here:
- `traffic_analysis.csv` - Vehicle counts
- `traffic_analysis.json` - Detailed stats

## Sample video

There's a sample traffic video included. The dashboard can process it or any MP4/AVI/MOV video you upload.

---

Built as a portfolio project for traffic analysis research.
