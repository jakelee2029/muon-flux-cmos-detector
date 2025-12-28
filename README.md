# MuonFlux V4.1: Distributed CMOS Particle Observatory
### Experimental Physics & Computer Vision Instrumentation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware: Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi-C51A4A)](https://www.raspberrypi.org/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB)](https://www.python.org/)

## 🔬 Executive Summary
An automated particle observatory utilizing a modified CMOS sensor and an NCBI-refactored denoising algorithm to catalog cosmic ray flux. By implementing adaptive spatial filtering and morphology analysis, the system isolates high-energy "Golden Hits" from thermal noise, providing verifiable data for citizen science and space weather research.

---

## 🛰️ Research Objectives
The primary goal of this project was to engineer a resilient, low-cost instrumentation suite capable of detecting ionizing radiation in uncooled, high-thermal environments ($>50^{\circ}C$). 

### Technical Challenges Addressed:
* **Thermal Noise Mitigation:** Developing a software-level cooling substitute to maintain a stable detection threshold.
* **Spatial Verification:** Distinguishing between recurring sensor artifacts (hot pixels) and stochastic cosmic events.
* **Morphological Classification:** Automating the identification of particle tracks to estimate the angle of incidence.

---

## 🛠️ System Architecture & Methodology

### 1. Instrumentation (Hardware)
* **Processor:** Raspberry Pi 4 Model B / 5
* **Sensor:** Modified Logitech C922 (Silicon-based CMOS)
* **Shielding:** Light-tight, high-density light-proof enclosure to eliminate photon interference.

### 2. Detection Pipeline (Software)
The detection engine is built in Python using OpenCV for real-time frame analysis. 
* **NCBI-Refactored Denoising:** Employs a 60-frame calibration mask and weighted moving averages to dynamically adjust to sensor "dark current" fluctuations.
* **The "Golden List" Logic:** A spatial filtering algorithm that records the $(x, y)$ coordinates of every trigger. If a coordinate repeats, it is classified as a hardware defect; if unique, it is logged as a "Golden" cosmic candidate.



---

## 📊 Data & Results

### Particle Morphology Gallery
Below are samples captured by the observatory, stretch-processed for visibility:

| Detection Type | Morphology | Interpretation |
| :--- | :--- | :--- |
| **Golden Hit 01** | *Dot* | Vertical Muon strike |
| **Golden Hit 02** | *Linear Track* | Shallow-angle Muon (~15-30°) |
| **Golden Hit 03** | *Worm/Curl* | Low-energy secondary electron |



### Statistics (Current Dataset)
* **Total Flux Events:** [Enter Total Hits Here]
* **Validated Golden Hits:** [Enter Golden Hits Here]
* **Average Flux Rate:** [Calculate Hits/Hour Here]

---

## 🎓 Academic Significance
This project demonstrates competency in **Digital Signal Processing (DSP)**, **Computer Vision**, and **Experimental Physics**. It contributes to the global "Open Science" movement, proving that distributed sensor networks can provide high-fidelity data previously reserved for multimillion-dollar facilities like IceCube or CERN.

---

## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)[Your-Username]/MuonFlux-V4.git


Install dependencies:

Bash

sudo apt install python3-opencv python3-numpy v4l-utils
Execute the observatory:

Bash

python3 cosmic.py
📈 Future Work
Phase II: Implementation of a lightweight Vision Transformer (ViT) for automated particle classification.
