# ShadowLog: Distributed IoT Threat Analysis Node

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**ShadowLog** is a lightweight, low-interaction honeypot engineered specifically for legacy hardware constraints (Raspberry Pi Model B, 512MB RAM). It mimics a vulnerable Ubuntu server to lure, capture, and analyze automated botnet traffic in real-time.

---

## 📸 Dashboard Preview

![Dashboard Preview](dashboard_screenshot.png)

> The ShadowLog Command Center visualizing live threat vectors, origin simulation, and threat scoring algorithms.

---

## 🚀 Project Abstract

In an era of increasing IoT insecurity, residential networks are prime targets for automated botnets. ShadowLog was designed to investigate these attack vectors using "electronic waste" hardware. 

Unlike commercial IDSs that require significant resources, ShadowLog operates on a raw socket architecture, enabling it to handle concurrent TCP connections with minimal memory overhead (~12MB). The system successfully demonstrates that obsolete hardware can be repurposed into effective, decentralized security sensors.

## ⚙️ System Architecture

The application utilizes a multi-threaded architecture to separate the "Trap" logic from the "Visualization" logic, preventing blocking operations during high-traffic spikes.

1.  **The Trap (Thread A):** Listens on Port 2222. Emulates an SSH handshake (Banner Grabbing $\rightarrow$ Auth Prompt $\rightarrow$ Data Capture).
2.  **The Engine:** Parses incoming IPs, simulates Geo-Location metadata, and assigns a heuristic Threat Score (0-100).
3.  **The Logger:** Implements `RotatingFileHandler` to manage I/O on constrained SD card storage.
4.  **The Dashboard (Thread B):** A Flask-based HTTP frontend that renders the attack matrix in real-time.

## 🛠️ Tech Stack

* **Hardware:** Raspberry Pi Model B (Revision 2, 512MB RAM)
* **Language:** Python 3.9+
* **Web Framework:** Flask (Micro-framework for UI)
* **Networking:** Native `socket` and `threading` libraries
* **Visualization:** CSS3 Grid & Flexbox (No heavy JS libraries to save resources)

## 📦 Installation & Setup

### 1. Prerequisites
* A Raspberry Pi (Any model, but optimized for Model B/Zero)
* Python 3 installed

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/ShadowLog.git](https://github.com/YOUR_USERNAME/ShadowLog.git)
cd ShadowLog
