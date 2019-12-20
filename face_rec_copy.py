import face_recognition
import cv2
import os
import numpy as np

scale = 1
reciprical_scale = 1 #must be int

yishai_face_image = face_recognition.load_image_file("me.jpg")
yishai_face_encoding = face_recognition.face_encodings(yishai_face_image)[0]

nimish_face_image = face_recognition.load_image_file("nimish.jpg")
nimish_face_encoding = face_recognition.face_encodings(nimish_face_image)[0]

known_face_encodings = []
known_face_encodings.append(yishai_face_encoding)
known_face_encodings.append(nimish_face_encoding)

known_face_names = []
known_face_names.append('Yishai')
known_face_names.append('Nimish')

def save_face(faceFile, name):
	face_image = face_recognition.load_image_file(faceFile)
	face_encoding = face_recognition.face_encodings(face_image)[0]

	# If there is no numpy file, create a numpy file
	if(not os.path.isfile('known_face_encodings.npy')):
		print("Creating new numpy files")

		np_known_face_encodings = []
		np.save('np_known_face_encodings', np_known_face_encodings)

		np_known_face_names = []
		np.save('np_known_face_names', np_known_face_names)

	np_known_face_encodings = np.load('np_known_face_encodings.npy')
	np.append(np_known_face_encodings, face_encoding)
	np.save('np_known_face_encodings', np_known_face_encodings)

	np_known_face_names = np.load('np_known_face_names.npy')
	np.append(np_known_face_encodings, name)
	np.save('np_known_face_names', np_known_face_names)

def find_face(filename):
	global known_face_encodings

	image = cv2.imread(filename)

	resized_frame = cv2.resize(image, (0, 0), fx=scale, fy=scale)

	rgb_small_frame = resized_frame[:, :, ::-1]

	face_locations = face_recognition.face_locations(rgb_small_frame)
	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

	#if(not os.path.isfile('known_face_encodings.npy')):
	#	return "Unknown"

	face_names = []
	for face_encoding in face_encodings:
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
		name = "Unknown"

		face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
		best_match_index = np.argmin(face_distances)
		if matches[best_match_index]:
			name = known_face_names[best_match_index]

		face_names.append(name)

	return face_names[0]

def init():
	counter = 0
	while True:
		file_name = 'face_{}.npy'.format(counter)
		if os.path.isfile(file_name):
			file_data = np.load(file_name)
			for data in file_data:
				all_data.append([data[0], data[1]])
			counter += 1
		else:
			print('Batch {} does not exist, recording all existent data; starting fresh batch'.format(counter))
			break

