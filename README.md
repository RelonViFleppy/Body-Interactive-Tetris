# 🧩 Body-Interactive Tetris (Computer Vision & Movement Analysis)

This project is a sophisticated reimagining of the classic Tetris game, integrating **OpenCV** to transform a player's physical movements and hand gestures into real-time game commands.

## 🛠️ Engineering & Technical Highlights
* **Motion-Based Horizontal Control:** Utilized the `cv2.createBackgroundSubtractorMOG2` algorithm to isolate the player from the background and calculate the **body's centroid** for left/right block movement.
* **Cross-Hand Rotation System:** Developed a specialized rotation trigger based on **Skin Color Segmentation** (HSV Range: 0-20) that detects when both hands are raised simultaneously in the upper ROI.
* **Computational Optimization:** To minimize latency, the image processing pipeline scales input frames by **0.5x** and focuses analysis on specific **Regions of Interest (ROI)**.
* **Input Stabilization:** Implemented a **Deadzone logic** (`THRESHOLD_X = 50`) and a `MOVE_DELAY` buffer (200ms) to prevent accidental movements caused by minor physical jitter.

## 🧠 Key Challenges Solved
1. **Asynchronous Execution:** Successfully synchronized the high-frequency camera feed with the constant gravity-based fall speed of the Tetris engine.
2. **Environmental Robustness:** Tuned `CONTOUR_AREA_THRESHOLD` (7000) to ensure reliable gesture detection across different lighting conditions and background complexities.
3. **Modular Control Logic:** Architected the `camera_control` function to act as a standalone input bridge, allowing for easy transitions between keyboard and vision-based controls.

## 🚀 Technologies Used
* **Python:** Core development and system integration.
* **OpenCV:** Real-time image processing, contour analysis, and background subtraction.
* **Pygame:** Game state management, collision detection, and UI rendering.

---
### 🤝 Contributors
* **Enes Malik Dincer** ([@RelonViFleppy](https://github.com/RelonViFleppy)) - Tetris Engine, Body Movement Logic, and System Integration.
* **                                                                         - Contribution to Gesture Detection and Vision-based Controls.
