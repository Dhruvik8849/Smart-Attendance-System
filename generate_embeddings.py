import os
import pickle
import numpy as np
from deepface import DeepFace


def main():

    # ================= CONFIGURATION =================
    DATASET_PATH = "dataset"
    ENCODINGS_PATH = "encodings/embeddings.pkl"
    MODEL_NAME = "Facenet512"
    DETECTOR_BACKEND = "retinaface"
    MIN_IMAGES_REQUIRED = 5 

    database = {}

    # Ensure encodings folder exists
    os.makedirs(os.path.dirname(ENCODINGS_PATH), exist_ok=True)

    print(f"Starting encoding process using {MODEL_NAME} + {DETECTOR_BACKEND}")

    if not os.path.exists(DATASET_PATH):
        print("Dataset folder not found.")
        return

    for person_name in os.listdir(DATASET_PATH):

        person_path = os.path.join(DATASET_PATH, person_name)

        if not os.path.isdir(person_path):
            continue

        embeddings = []
        valid_images = 0

        print(f"\nProcessing {person_name}...")

        for image_name in os.listdir(person_path):

            if image_name.startswith(".") or not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            image_path = os.path.join(person_path, image_name)

            try:
                embedding_objs = DeepFace.represent(
                    img_path=image_path,
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=True
                )

                embedding = np.array(embedding_objs[0]["embedding"])

                # Normalize each embedding first
                embedding = embedding / (np.linalg.norm(embedding) + 1e-8)

                embeddings.append(embedding)
                valid_images += 1

            except ValueError:
                print(f"  Skipping {image_name}: No face detected.")
            except Exception as e:
                print(f"  Error processing {image_name}: {e}")

        # Quality Control
        if len(embeddings) >= MIN_IMAGES_REQUIRED:

            mean_embedding = np.mean(embeddings, axis=0)

            norm = np.linalg.norm(mean_embedding)

            if norm > 0:
                normalized_embedding = mean_embedding / norm
            else:
                print(f"  Skipped {person_name}: Normalization error.")
                continue

            database[person_name] = normalized_embedding

            print(f"  Registered {person_name} ({valid_images} valid images)")

        else:
            print(f"  Skipped {person_name}: Not enough valid images ({len(embeddings)})")

    # Save embeddings
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump(database, f)

    print("\nEmbeddings saved successfully.")
    print(f"Total registered identities: {len(database)}")

 
if __name__ == "__main__":
    main()
