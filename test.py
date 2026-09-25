import cv2

from gesture_recognizer import GestureRecognizer


MODEL_PATH = "models/gesture_recognizer.task"


recognizer = GestureRecognizer(MODEL_PATH)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    recognizer.close()
    exit()


while True:

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    recognizer.process_frame(frame)

    gesture, confidence = recognizer.get_result()

    text = f"{gesture} ({confidence:.2f})"

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
        "Rock Paper Scissors - Gesture Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
recognizer.close()