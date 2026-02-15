import cv2
import pickle
import numpy as np
from deepface import DeepFace
from datetime import datetime
import os
import time
import threading


def main():

    # ================= CONFIGURATION =================
    DETECTOR = "opencv"  
    MODEL_NAME = "Facenet512"
    THRESHOLD = 0.35  

    ENCODINGS_PATH = "encodings/embeddings.pkl"
    ATTENDANCE_PATH = "attendance"
    # =================================================

    os.makedirs(ATTENDANCE_PATH, exist_ok=True)

    print("Loading Database...")
    database = {}
    try:
        with open(ENCODINGS_PATH, "rb") as f:
            database = pickle.load(f)
        print(f"Database loaded with {len(database)} people.")
    except FileNotFoundError:
        print("Error: Embeddings file not found! Please run training first.")
        return

    # --- GLOBAL VARIABLES ---
    processing_active = False
    detected_name = "Unknown"
    detected_score = 0
    face_location = None
    feedback_message = ""
    show_confirmation_until = 0

    # ---------------- HELPER FUNCTIONS ----------------

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

    def mark_attendance_csv(name):
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(ATTENDANCE_PATH, f"{today}.csv")

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("Name,Time\n")

        with open(file_path, "r") as f:
            lines = f.readlines()

        if any(name in line for line in lines):
            return False

        with open(file_path, "a") as f:
            time_now = datetime.now().strftime("%H:%M:%S")
            f.write(f"{name},{time_now}\n")

        return True

    # --- BACKGROUND WORKER ---
    def recognition_worker(frame_copy):
        nonlocal processing_active
        nonlocal detected_name
        nonlocal detected_score
        nonlocal face_location
        nonlocal feedback_message
        nonlocal show_confirmation_until

        try:
            results = DeepFace.represent(
                img_path=frame_copy,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR,
                enforce_detection=False
            )

            if len(results) > 0:
                result = results[0]
                face_location = result["facial_area"]
                embedding = result["embedding"]

                best_match = "Unknown"
                best_score = -1

                for name, db_embedding in database.items():
                    score = cosine_similarity(embedding, db_embedding)
                    if score > best_score:
                        best_score = score
                        best_match = name

                if best_score > (1 - THRESHOLD):
                    detected_name = best_match
                    detected_score = best_score

                    was_new = mark_attendance_csv(best_match)

                    if was_new:
                        feedback_message = f"MARKED: {best_match}"
                        show_confirmation_until = time.time() + 2.0
                else:
                    detected_name = "Unknown"
                    detected_score = 0
            else:
                face_location = None

        except:
            face_location = None

        processing_active = False

    # ---------------- MAIN VIDEO LOOP ----------------

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    print("Starting Camera... Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Start thread if idle
        if not processing_active:
            processing_active = True
            thread = threading.Thread(
                target=recognition_worker,
                args=(frame.copy(),)
            )
            thread.start()

        # Draw face box
        if face_location:
            x = face_location['x']
            y = face_location['y']
            w = face_location['w']
            h = face_location['h']

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if detected_name != "Unknown":
                label = f"{detected_name} ({detected_score:.2f})"
                color = (0, 255, 0)
            else:
                label = "Scanning..."
                color = (0, 255, 255)

            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        color, 2)

        # Draw confirmation
        if time.time() < show_confirmation_until:
            h_screen, w_screen, _ = frame.shape
            cv2.rectangle(frame, (0, 0), (w_screen, h_screen),
                          (0, 255, 0), 15)

            cv2.putText(frame, feedback_message,
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 255, 0), 3)

        cv2.imshow("Fast Face Attendance", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
