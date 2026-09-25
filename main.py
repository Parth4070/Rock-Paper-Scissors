import cv2
import mediapipe as mp
import time

from collections import deque

from score import Score
from game_logic import computer_move, determine_winner


# ============================================================
# MediaPipe setup
# ============================================================

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
RunningMode = mp.tasks.vision.RunningMode


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = "models/gesture_recognizer.task"

# Paper was being detected around 0.52 - 0.57,
# so 0.70 was too strict.
CONFIDENCE_THRESHOLD = 0.50

GESTURE_HISTORY_SIZE = 5

gesture_history = deque(
    maxlen=GESTURE_HISTORY_SIZE
)


# ============================================================
# Current gesture state
# ============================================================

latest_gesture = "No hand detected"
latest_confidence = 0.0


# ============================================================
# UI functions
# ============================================================

def draw_text(frame, text, position, size=0.7):

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        (0, 0, 255),       # Red
        2
    )


def draw_scoreboard(frame, score, round_number):

    draw_text(
        frame,
        f"ROUND {round_number}",
        (420, 40),
        0.7
    )

    draw_text(
        frame,
        f"YOU: {score.player_score}",
        (420, 75),
        0.65
    )

    draw_text(
        frame,
        f"COMPUTER: {score.computer_score}",
        (420, 110),
        0.65
    )

    draw_text(
        frame,
        f"DRAWS: {score.draws}",
        (420, 145),
        0.65
    )


# ============================================================
# Gesture mapping
# ============================================================

def map_gesture(raw_gesture):

    if raw_gesture == "Closed_Fist":
        return "Rock"

    elif raw_gesture == "Open_Palm":
        return "Paper"

    elif raw_gesture == "Victory":
        return "Scissors"

    return "Unknown"


# ============================================================
# Gesture stabilization
# ============================================================

def get_stable_gesture():

    if not gesture_history:
        return "Unknown"

    counts = {}

    for gesture in gesture_history:

        counts[gesture] = (
            counts.get(gesture, 0) + 1
        )

    return max(
        counts,
        key=counts.get
    )


# ============================================================
# MediaPipe callback
# ============================================================

def process_result(
    result: GestureRecognizerResult,
    output_image: mp.Image,
    timestamp_ms: int
):

    global latest_gesture
    global latest_confidence

    # No gesture detected
    if not result.gestures:
        latest_confidence = 0.0
        return

    # Get highest-ranked gesture
    gesture = result.gestures[0][0]

    raw_gesture = gesture.category_name
    confidence = gesture.score

    # Ignore low-confidence predictions
    if confidence < CONFIDENCE_THRESHOLD:
        return

    # Convert MediaPipe gesture to game gesture
    mapped_gesture = map_gesture(
        raw_gesture
    )

    # Ignore gestures that are not part of RPS
    if mapped_gesture == "Unknown":
        return

    # Add valid gesture to history
    gesture_history.append(
        mapped_gesture
    )

    # Get stabilized gesture
    latest_gesture = get_stable_gesture()

    latest_confidence = confidence


# ============================================================
# Create MediaPipe recognizer
# ============================================================

options = GestureRecognizerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=RunningMode.LIVE_STREAM,

    num_hands=1,

    result_callback=process_result
)


recognizer = GestureRecognizer.create_from_options(
    options
)


# ============================================================
# Initialize webcam
# ============================================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    print(
        "Error: Could not open webcam."
    )

    exit()


# ============================================================
# Game variables
# ============================================================

score = Score()

round_number = 1

game_state = "READY"

countdown_start = None
countdown_value = None

capture_start = None
capture_duration = 0.5

player_choice = None
computer_choice = None
round_result = None

timestamp_ms = 0


# ============================================================
# Main game loop
# ============================================================

while True:

    # --------------------------------------------------------
    # Capture webcam frame
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print(
            "Error: Could not read frame."
        )

        break


    # Mirror the webcam
    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # Convert frame for MediaPipe
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # Send frame to MediaPipe
    # --------------------------------------------------------

    recognizer.recognize_async(
        mp_image,
        timestamp_ms
    )

    timestamp_ms += 1


    # ========================================================
    # COUNTDOWN
    # ========================================================

    if game_state == "COUNTDOWN":

        elapsed = (
            time.time()
            - countdown_start
        )


        if elapsed < 1:

            countdown_value = 3


        elif elapsed < 2:

            countdown_value = 2


        elif elapsed < 3:

            countdown_value = 1


        else:

            countdown_value = "GO!"

            capture_start = time.time()

            game_state = "CAPTURE"


    # ========================================================
    # CAPTURE GESTURE
    # ========================================================

    elif game_state == "CAPTURE":

        elapsed = (
            time.time()
            - capture_start
        )


        if elapsed >= capture_duration:

            # Get the stabilized gesture
            player_choice = get_stable_gesture()


            if player_choice in [
                "Rock",
                "Paper",
                "Scissors"
            ]:

                # Computer chooses randomly
                computer_choice = computer_move()


                # Determine winner
                round_result = determine_winner(
                    player_choice,
                    computer_choice
                )


                # Update score
                score.update(
                    round_result
                )


            else:

                player_choice = "Unknown"

                computer_choice = None

                round_result = "Invalid gesture"


            game_state = "RESULT"


    # ========================================================
    # BASIC UI
    # ========================================================

    draw_text(
        frame,
        f"Gesture: {latest_gesture}",
        (20, 40),
        0.75
    )


    draw_text(
        frame,
        f"Confidence: {latest_confidence:.2f}",
        (20, 75),
        0.6
    )


    draw_scoreboard(
        frame,
        score,
        round_number
    )


    # ========================================================
    # READY SCREEN
    # ========================================================

    if game_state == "READY":

        draw_text(
            frame,
            "ROCK PAPER SCISSORS",
            (100, 180),
            1.2
        )

        draw_text(
            frame,
            "Press SPACE to start",
            (145, 230),
            0.8
        )


    # ========================================================
    # COUNTDOWN UI
    # ========================================================

    if game_state == "COUNTDOWN":

        cv2.putText(
            frame,
            str(countdown_value),
            (275, 260),
            cv2.FONT_HERSHEY_SIMPLEX,
            4,
            (0, 255, 255),
            6
        )


    # ========================================================
    # CAPTURE UI
    # ========================================================

    elif game_state == "CAPTURE":

        cv2.putText(
            frame,
            "GO!",
            (225, 260),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,
            (0, 255, 255),
            6
        )


    # ========================================================
    # RESULT UI
    # ========================================================

    elif game_state == "RESULT":

        draw_text(
            frame,
            f"You: {player_choice}",
            (20, 130),
            0.8
        )


        if computer_choice is not None:

            draw_text(
                frame,
                f"Computer: {computer_choice}",
                (20, 170),
                0.8
            )


        draw_text(
            frame,
            f"Result: {round_result}",
            (20, 210),
            0.9
        )


        draw_text(
            frame,
            "SPACE = Next Round",
            (20, 260),
            0.65
        )


        draw_text(
            frame,
            "Q = Quit",
            (20, 295),
            0.65
        )


    # ========================================================
    # Display webcam
    # ========================================================

    cv2.imshow(
        "Rock Paper Scissors",
        frame
    )


    # ========================================================
    # Keyboard controls
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    # Quit
    if key == ord("q"):

        break


    # --------------------------------------------------------
    # Start first round
    # --------------------------------------------------------

    if (
        key == ord(" ")
        and game_state == "READY"
    ):

        countdown_start = time.time()

        game_state = "COUNTDOWN"

        player_choice = None

        computer_choice = None

        round_result = None

        # Clear old gesture predictions
        gesture_history.clear()


    # --------------------------------------------------------
    # Start next round
    # --------------------------------------------------------

    elif (
        key == ord(" ")
        and game_state == "RESULT"
    ):

        round_number += 1

        countdown_start = time.time()

        game_state = "COUNTDOWN"

        player_choice = None

        computer_choice = None

        round_result = None

        # Clear old gesture predictions
        gesture_history.clear()


# ============================================================
# Cleanup
# ============================================================

cap.release()

cv2.destroyAllWindows()

recognizer.close()