import cv2
import mediapipe as mp
from collections import deque

CONFIDENCE_THRESHOLD = 0.50
GESTURE_HISTORY_SIZE = 5

gesture_history = deque(maxlen=GESTURE_HISTORY_SIZE)

def get_stable_gesture():
    if not gesture_history:
        return "Unknown"
    
    # Count occurrences of each gesture
    gesture_counts = {gesture: gesture_history.count(gesture) for gesture in set(gesture_history)}

    # Get the most common gesture
    stable_gesture = max(gesture_counts, key=gesture_counts.get)
    
    return max(gesture_counts, key = gesture_counts.get)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
RunningMode = mp.tasks.vision.RunningMode


MODEL_PATH = "models/gesture_recognizer.task"


# --------------------------------------------------
# Store the latest recognition result
# --------------------------------------------------

latest_gesture = "No hand detected"
latest_confidence = 0.0


# --------------------------------------------------
# Callback function
# --------------------------------------------------
def map_gesture(raw_gesture):
    mapping = {
        "Closed_Fist": "Rock",
        "Open_Palm": "Paper",
        "Victory": "Scissors"
    }

    return mapping.get(raw_gesture, "Unknown")

def process_result(
    result: GestureRecognizerResult,
    output_image: mp.Image,
    timestamp_ms: int
):
    global latest_gesture
    global latest_confidence

    if result.gestures:
        gesture = result.gestures[0][0]
        
        raw_gesture = gesture.category_name
        confidence = gesture.score

        if confidence >= CONFIDENCE_THRESHOLD:

            mapped_gesture = map_gesture(raw_gesture)

            if mapped_gesture != "Unknown":
                gesture_history.append(mapped_gesture)

            latest_gesture = get_stable_gesture()
            latest_confidence = confidence

        else:

            latest_gesture = get_stable_gesture()
            latest_confidence = confidence


    else:
        latest_gesture = get_stable_gesture()
        latest_confidence = 0.0


# --------------------------------------------------
# Configure Gesture Recognizer
# --------------------------------------------------

options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.LIVE_STREAM,
    num_hands=1,
    result_callback=process_result
)


# --------------------------------------------------
# Create recognizer
# --------------------------------------------------

recognizer = GestureRecognizer.create_from_options(options)


# --------------------------------------------------
# Open webcam
# --------------------------------------------------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()


# --------------------------------------------------
# Main loop
# --------------------------------------------------

timestamp_ms = 0

while True:

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Convert NumPy image → MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Send frame to MediaPipe asynchronously
    recognizer.recognize_async(
        mp_image,
        timestamp_ms
    )

    timestamp_ms += 1

    # Display latest recognition result
    text = f"{latest_gesture} ({latest_confidence:.2f})"

    cv2.putText(
        frame,
        text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Gesture Recognition",
        frame
    )

    # Quit with Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

cap.release()
cv2.destroyAllWindows()
recognizer.close()