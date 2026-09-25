# ✊✋✌️ Rock Paper Scissors — Computer Vision Edition

A real-time **Rock Paper Scissors** game that uses your webcam and **MediaPipe's hand gesture recognition** to detect your move. No keyboard input needed — just show your hand!

---

## 📸 How It Works

1. Press **SPACE** to start a round.
2. A **3-2-1 countdown** appears on screen.
3. On **GO!**, hold your gesture in front of the webcam.
4. The app detects your hand shape, the computer picks randomly, and the winner is shown instantly.
5. Press **SPACE** to play the next round, or **Q** to quit.

---

## 🤖 Gesture Detection

The game uses **Google MediaPipe's pre-trained Gesture Recognizer** model to classify hand shapes in real time via a live-stream pipeline.

| Your Hand | Detected As |
|-----------|-------------|
| ✊ Closed Fist | Rock |
| ✋ Open Palm | Paper |
| ✌️ Victory Sign | Scissors |

A **gesture history buffer** (last 5 frames) is used to stabilize predictions and avoid flickering, with a minimum confidence threshold of **0.50**.

---

## 🗂️ Project Structure

```
ROCK-PAPER-SCISSORS/
│
├── main.py                  # Main game loop (webcam + UI + state machine)
├── game_logic.py            # Computer move & winner determination
├── score.py                 # Score tracking (player / computer / draws)
├── round.py                 # Single round orchestration
├── gesture_recognizer.py    # MediaPipe gesture recognizer wrapper class
├── countdown.py             # CLI countdown utility
│
├── models/
│   └── gesture_recognizer.task   # Pre-trained MediaPipe model file
│
├── game_logic_test.py       # Tests for game logic
├── score_test.py            # Tests for score tracking
├── gesture_test.py          # Tests for gesture detection pipeline
├── round_test.py            # Tests for round orchestration
├── webcam_test.py           # Tests for webcam access
└── test.py                  # General integration tests
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python **3.9+**
- A working **webcam**

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ROCK-PAPER-SCISSORS
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install opencv-python mediapipe
```

### 4. Download the MediaPipe model

Download the **Gesture Recognizer** task file from Google MediaPipe:

🔗 https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer

Place the downloaded file inside the `models/` folder:

```
models/gesture_recognizer.task
```

---

## ▶️ Running the Game

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `SPACE` | Start round / Next round |
| `Q` | Quit the game |

---

## 🧩 Module Overview

### `game_logic.py`
- `computer_move()` — randomly selects Rock, Paper, or Scissors.
- `determine_winner(player, computer)` — returns `"Player"`, `"Computer"`, or `"Draw"`.

### `score.py`
- `Score` class tracks `player_score`, `computer_score`, and `draws`.
- `update(result)` — increments the correct counter.
- `display()` — prints the current scoreboard to the console.

### `round.py`
- `play_round(player_choice, score)` — validates input, gets computer move, determines winner, updates score, and returns `(computer_choice, result, status)`.

### `gesture_recognizer.py`
- `GestureRecognizer` class wraps the MediaPipe live-stream pipeline.
- `process_frame(frame)` — sends an OpenCV frame for async recognition.
- `get_result()` — returns `(latest_gesture, latest_confidence)`.

### `main.py`
- Full game loop with a **state machine**: `READY → COUNTDOWN → CAPTURE → RESULT`.
- Renders live gesture overlay, scoreboard, countdown, and result UI using OpenCV.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| OpenCV | Webcam capture & UI rendering |
| MediaPipe | Real-time hand gesture recognition |
| Python `collections.deque` | Gesture history buffer for stabilization |
| Python `random` | Computer move selection |

---

## 📝 Notes

- The game uses **DirectShow** (`cv2.CAP_DSHOW`) for webcam access on Windows for lower latency.
- If your gesture is not recognized confidently enough (below 0.50), it will not be added to the history buffer.
- Make sure your hand is well-lit and clearly visible to the camera for best results.

---

## 📄 License

This project was built as an internship learning exercise. Feel free to use and extend it.
