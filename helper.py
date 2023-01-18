# Each frame of the webcam will be send to this program
# We will process this frame, and generate a verdict on whether this person is known or unknown

import os
import face_recognition
import cv2
import numpy as np
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class Verdict():
    known_face_encodings = []
    known_face_names = []
    def __init__(self):
        s = os.path.normcase(os.getcwd() + "/faces")
        self.known_face_encodings = []
        self.known_face_names = []
        """
        for directory in os.listdir(s):
            wd = os.path.normcase(s + f'/{directory}')
            l = os.listdir(wd)
            for filename in os.listdir(wd):
                newPath = os.path.normcase(wd + "/" + filename)
                trainImage = face_recognition.load_image_file(os.path.normcase(newPath))
                self.known_face_encodings.append(face_recognition.face_encodings(trainImage)[0])
                self.known_face_names.append(directory)
        """
        for filename in os.listdir(s):
            newPath = os.path.normcase(s + "/" + filename)
            trainImage = face_recognition.load_image_file(os.path.normcase(newPath))
            self.known_face_encodings.append(face_recognition.face_encodings(trainImage)[0])
            self.known_face_names.append(filename.split(".")[0])
        
    def process(self, frame):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)

        # Display the results
        scaled_locations = []
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            scaled_locations.append((top, right, bottom, left))
            
        return [frame, face_names, scaled_locations]

    def store(self, trainingPic, textbox):
        """
        name = textbox.text().lower()
        dashedName = name.replace(" ", "_")
        parent_dir = os.path.normcase(os.getcwd() + "/faces")
        directory = dashedName
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        for i in range(0, len(trainingPics)):
            filePath = os.path.join(path, f"{dashedName}-{i}.jpg")
            trainingPics[i].save(filePath, 'JPEG')
            trainImage = face_recognition.load_image_file(filePath)
            self.known_face_encodings.append(face_recognition.face_encodings(trainImage)[0])
            self.known_face_names.append(name)
        """
        name = textbox.text().lower()
        dashedName = name.replace(" ", "_")
        parent_dir = os.path.normcase(os.getcwd() + "/faces")
        filePath = os.path.join(parent_dir, f"{dashedName}.jpg")
        trainingPic.save(filePath, 'JPEG')
        trainImage = face_recognition.load_image_file(filePath)
        self.known_face_encodings.append(face_recognition.face_encodings(trainImage)[0])
        self.known_face_names.append(name)
        trainingPic = None
        

