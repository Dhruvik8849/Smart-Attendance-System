import cv2
import os
import time
import sys


def main():

    # ===== GET STUDENT NAME FROM APP.PY =====
    if len(sys.argv) > 1:
        STUDENT_NAME = sys.argv[1]
    else:
        print("Error: Student name not provided.")
        return

    SAVE_PATH = os.path.join("dataset", STUDENT_NAME)

    # ================= CONFIGURATION =================
    STAGES = [
        "1_FRONT_NEUTRAL_SMILE", 
        "2_HEAD_LEFT", 
        "3_HEAD_RIGHT", 
        "4_HEAD_UP", 
        "5_HEAD_DOWN"
    ]

    PHOTOS_PER_STAGE = 7
    TIME_GAP = 0.5
    # =================================================

    os.makedirs(SAVE_PATH, exist_ok=True)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    stage_index = 0

    print(f"--- Registration for {STUDENT_NAME} Started ---")
    print("Controls: Press [SPACE] to capture current stage. Press [ESC] to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if stage_index < len(STAGES):
            current_stage_name = STAGES[stage_index]
            msg = f"STAGE {stage_index + 1}/{len(STAGES)}: {current_stage_name}"
            sub_msg = "Align Face & Press [SPACE] to start burst"
            color = (0, 255, 255)
        else:
            msg = "ALL STAGES COMPLETE!"
            sub_msg = "Press [ESC] to exit"
            color = (0, 255, 0)

        cv2.putText(frame, msg, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, sub_msg, (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Face Capture System", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 32 and stage_index < len(STAGES):

            for i in range(PHOTOS_PER_STAGE):
                ret, capture_frame = cap.read()
                if not ret:
                    break

                filename = f"{STAGES[stage_index]}_{i+1}.jpg"
                file_path = os.path.join(SAVE_PATH, filename)

                cv2.imwrite(file_path, capture_frame)

                cv2.putText(capture_frame,
                            f"CAPTURING {i+1}/{PHOTOS_PER_STAGE}",
                            (50, 240),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

                cv2.imshow("Face Capture System", capture_frame)
                cv2.waitKey(1)

                time.sleep(TIME_GAP)

            stage_index += 1

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Process finished.")


if __name__ == "__main__":
    main()










