from gesture_test import ret
import cv2 
import mediapipe as mp
import time

BaseOptions = mp.tasks.BaseOptions
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
MediaPipeGestureRecognize = mp.tasks.vision.GestureRecognizer
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
RunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "models/gesture_recognizer.task"

GESTURE_MAPPING = {
    "Closed_Fist": "Rock",
    "Open_Palm": "Paper",
    "Victory": "Scissors"
}

class GestureRecognizer:
    def __init__(self, model_path):
        self.latest_gesture = "Unknown"
        self.latest_confidence = 0.0
        self.timestamp_ms = 0

        options = GestureRecognizerOptions(
            base_options = BaseOptions(model_asset_path = model_path),
            running_mode = RunningMode.LIVE_STREAM,
            num_hands = 1,
            result_callback = self._process_result
        )

        self.recognizer = MediaPipeGestureRecognize.create_from_options(options)

    def _process_result(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        if result.gestures:
            gesture = result.gestures[0][0]
            
            raw_gesture = gesture.category_name
            confidence = gesture.score

            self.latest_gesture = GESTURE_MAPPING.get(raw_gesture, "Unknown")

            self.latest_confidence = confidence 
        else:
            self.latest_gesture = "Unknown"
            self.latest_confidence = 0.0
        
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = rgb_frame)

        self.recognizer.recognize_async(mp_image, self.timestamp_ms)

        self.timestamp_ms +=1
    
    def get_result(self):
        return self.latest_gesture, self.latest_confidence

    def close(self):
        self.recognizer.close()
        
    