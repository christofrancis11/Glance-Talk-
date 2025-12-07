
# 🧠 Eye Tracking Communication System

A gaze-controlled interaction system designed to help **paralyzed patients** communicate essential needs using **eye movements**, **gaze detection**, and **blink-based calibration**.

---

## 🚀 Features

* Real-time **eye tracking** using OpenCV + dlib
* **Fullscreen gaze regions** for Food, Water, Medicine, Help, Rest
* Smooth, stabilized **gaze estimation**
* **Blink-based calibration** for accuracy
* Region **auto-selection** using gaze-lock timer
* Visual overlays for all selectable regions
* Live EAR (Eye Aspect Ratio), FPS, gaze coordinates, and debug info
* Tkinter-based fullscreen UI with control panel

---

## 📦 Requirements

Install dependencies:

```
pip install opencv-python dlib numpy pillow
```

You also need Tkinter (included with most Python installations).

---

## 🤖 Facial Landmark Model (Required)

This project needs the **dlib 68-point facial landmark model**:

🔗 **Download the file here:**
[http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

After downloading:

1. Extract the `.bz2` file
2. Place `shape_predictor_68_face_landmarks.dat` in the **same folder as Eyetracker.py**

⚠️ This file cannot be uploaded to GitHub due to license and size restrictions.

---

## ▶️ How to Run

```
python Eyetracker.py
```

Controls:

* **Space** → Start / Stop tracking
* **ESC** → Exit fullscreen and close app
* **Calibrate Button** → Start blink-based calibration

---

## 🧭 How It Works (Short Overview)

* Detects facial landmarks using dlib
* Computes **EAR** to check blink states
* Tracks pupil position using thresholding + contour detection
* Converts gaze vector to **screen coordinates**
* Checks which region the user is looking at
* If gaze holds for `N` seconds → **selection triggered**

Ideal for applications like:

* Assistive communication
* Healthcare support systems
* Hands-free UI navigation

---

## 📂 Project Structure

```
/project-folder
│
├── Eyetracker.py
├── requirements.txt   (optional)
└── shape_predictor_68_face_landmarks.dat   (user must download manually)
```

---

## 🌟 Future Enhancements

* MQTT / IoT integration for sending commands
* MCP-enabled context-aware interaction
* Mobile/tablet version
* AI-based emotion tracking
* Cloud logging of user selections

---

## 📝 License

This project is for educational and research use.
The dlib predictor model is owned by Davis King and cannot be redistributed.

---

If you want, I can also:
✅ Create a **requirements.txt**
✅ Generate a **project banner image**
✅ Add **GitHub badges**
Just tell me!
