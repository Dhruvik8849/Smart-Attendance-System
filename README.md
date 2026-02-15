# Smart Attendance System (Face Recognition)

A desktop-based Face Recognition Smart Attendance System built using
Python, OpenCV, DeepFace, and Tkinter.

This system enables automatic student registration, face embedding
generation, real-time attendance marking, and secure record management
through a user-friendly desktop interface.

## FEATURES

-   Student Face Registration (Multi-angle capture)
-   DeepFace Embedding Generation (FaceNet512 + RetinaFace)
-   Real-time Face Recognition Attendance
-   Automatic Main Attendance Record Creation
-   Auto-clean Attendance Folder After Update
-   Admin-Protected Main List Deletion
-   Changeable Admin Password
-   Tkinter Desktop GUI
-   Convertible to Windows .exe Application

## TECHNOLOGIES USED

-   Python 3.11
-   OpenCV
-   DeepFace
-   TensorFlow / Keras
-   RetinaFace
-   Tkinter
-   Pandas
-   CSV-based record management system

## PROJECT STRUCTURE

Smart-Attendance-System/
├── app.py 
├── register.py 
├── recognize.py 
├── generate_embeddings.py
├── manage_records.py 
│ 
├── dataset/ 
├── encodings/ 
├── attendance/ 
├── records/ 
└── config/

## HOW IT WORKS

### 1.  Register Student
  -   Enter student name
  -   Capture multiple face angles
  -   Images are saved in dataset/
### 2.  Train Model
  -   Generates embeddings using DeepFace
  -   Stores averaged and normalized vectors in encodings/
### 3.  Start Attendance
  -   Performs real-time face recognition
  -   Marks present students in attendance/YYYY-MM-DD.csv
### 4.  Update Records
  -   Updates records/main_list.csv
  -   Adds a new date column automatically
  -   Marks students as Present or NR
  -   Generates daily summary file
  -   Clears attendance folder for the next session

## HOW TO RUN (Python Version)

Step 1:Create Virtual Environment   
   -     python -m venv venv venv
Step 2:Install Requirements
   -     pip install -r requirements.txt
Step 3:Run Application
   -     python app.py

## ADMIN PROTECTION

Default Admin Password: Dhruvik

The password can be changed inside the application. Main attendance
records can only be deleted after admin verification.

## WINDOWS EXECUTABLE VERSION

This project can be converted into a standalone Windows .exe application
using PyInstaller.

## LICENSE

This project is licensed under the MIT License. You are free to use,
modify, and distribute this software.

PROJECT STATUS

This project is under active development. Additional optimizations, UI
improvements, and feature enhancements are planned for future releases.

CONTRIBUTIONS

Contributions, improvements, and feature suggestions are welcome.
You may fork the repository and submit a pull request.
