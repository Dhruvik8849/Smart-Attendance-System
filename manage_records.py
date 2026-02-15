import os
import csv
import time
import gc
from datetime import datetime
 
DATASET_PATH = "dataset"
ATTENDANCE_PATH = "attendance"
RECORDS_PATH = "records"
MAIN_FILE = os.path.join(RECORDS_PATH, "main_list.csv")
# ==========================================

 
def get_registered_students():
    if not os.path.exists(DATASET_PATH):
        return []

    return sorted([
        name.strip()
        for name in os.listdir(DATASET_PATH)
        if os.path.isdir(os.path.join(DATASET_PATH, name))
    ])

 
def get_today_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = os.path.join(ATTENDANCE_PATH, f"{today}.csv")

    present_students = set()

    if not os.path.exists(today_file):
        return present_students, today

    try:
        with open(today_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Name"):
                    present_students.add(row["Name"].strip())
    except Exception as e:
        print(f"Error reading attendance file: {e}")

    return present_students, today


# ------------------------------------------------
# 3. Load Main Records
# ------------------------------------------------
def load_main_records():
    if not os.path.exists(MAIN_FILE):
        return [], []

    try:
        with open(MAIN_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            data = list(reader)

        if not data:
            return [], []

        header = data[0]
        rows = data[1:]
        return header, rows
    except Exception:
        return [], []


# ------------------------------------------------
# 4. Save Main Records
# ------------------------------------------------
def save_main_records(header, rows):
    os.makedirs(RECORDS_PATH, exist_ok=True)

    with open(MAIN_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# ------------------------------------------------
# 5. Update Main Records
# ------------------------------------------------
def update_records():
    registered_students = get_registered_students()
    today_present, today = get_today_attendance()

    header, rows = load_main_records()

    # First Run - Create file
    if not header:
        header = ["Name", today]
        rows = []

        for student in registered_students:
            status = "Present" if student in today_present else "NR"
            rows.append([student, status])

        save_main_records(header, rows)
        print("Main list created.")
        return

    # Add new date column if needed
    if today not in header:
        header.append(today)
        for row in rows:
            row.append("NR")

    name_index = 0
    date_index = header.index(today)
    existing_names = {row[name_index] for row in rows}

    # Update existing students
    for row in rows:
        student_name = row[name_index]
        if student_name in today_present:
            row[date_index] = "Present"

    # Add new students
    for student in today_present:
        if student not in existing_names:
            new_row = [student]

            # Fill older dates with NR
            for _ in range(len(header) - 2):
                new_row.append("NR")

            new_row.append("Present")
            rows.append(new_row)
            print(f"New student added: {student}")

    # Sort alphabetically
    rows.sort(key=lambda x: x[0].lower())

    save_main_records(header, rows)

    print("Records updated successfully.")
    print(f"Date: {today}")
    print(f"Present students: {len(today_present)}")


# ------------------------------------------------
# 6. Generate Today's Summary
# ------------------------------------------------
def generate_today_summary():
    today_present, today = get_today_attendance()
    registered_students = get_registered_students()

    os.makedirs(RECORDS_PATH, exist_ok=True)
    summary_file = os.path.join(RECORDS_PATH, f"{today}_summary.csv")

    with open(summary_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Status"])

        for student in registered_students:
            status = "Present" if student in today_present else "NR"
            writer.writerow([student, status])

    print("Today's summary generated.")


# ------------------------------------------------
# 7. Clear Attendance Folder (Delete and Recreate)
# ------------------------------------------------
def clear_attendance_folder():
    if not os.path.exists(ATTENDANCE_PATH):
        return

    print("Cleaning attendance folder...")

    # Force release file handles
    gc.collect()

    try:
        # Delete entire attendance folder
        for root, dirs, files in os.walk(ATTENDANCE_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file}: {e}")

        print("Attendance folder cleaned.")

    except Exception as e:
        print(f"Error during cleanup: {e}")


# ------------------------------------------------
# MAIN
# ------------------------------------------------
def main():
    print("Processing Attendance Data...")
    update_records()
    generate_today_summary()
    clear_attendance_folder()
    print("Process complete. System ready for next session.")


if __name__ == "__main__":
    main()
