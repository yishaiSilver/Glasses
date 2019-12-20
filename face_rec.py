import face_recognition
import cv2
import os
import gtts
import numpy as np
import sound

scale = 1
reciprical_scale = 1 #must be int

known_face_encodings = []
known_face_names = []

def save_face(faceFile, name):
	global known_face_names
	try:
		if name == "cancel":
			raise Exception('Canceling name.')

		face_image = face_recognition.load_image_file(faceFile)
		face_encoding = face_recognition.face_encodings(face_image)[0]

		known_face_encodings.append(face_encoding)
		known_face_names.append(name)

		np.save('np_known_face_names', known_face_names)
	except:
		print("Face not found. Please try again.")
		sound.sound("Face not found. Please try again.")
		os.remove(faceFile)

def find_face(filename):
	if(len(known_face_encodings) > 0):
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
	else:
		print("No known faces!")
		return "Unknown"

def init():
	global known_face_encodings
	global known_face_names

	print("Initializing facial recognition.")

	counter = 0
	while True:
		file_name = 'face_{}.jpg'.format(counter)
		if os.path.isfile(file_name):
			face_image = face_recognition.load_image_file(file_name)
			face_encoding = face_recognition.face_encodings(face_image)[0]
			known_face_encodings.append(face_encoding)

			counter += 1
		else:
			print('{} Faces found. Continuing.'.format(counter))
			break

	if(os.path.isfile('np_known_face_names.npy')):
		known_face_names = np.load('np_known_face_names.npy').tolist()

	print(known_face_names)

def delete_face():
	print("Please choose a face to delete:\n")
	counter = 0
	while True:
		file_name = 'face_{}.jpg'.format(counter)
		if os.path.isfile(file_name):
			print("{}: {}".format(counter, known_face_names[counter]))
			counter += 1
		else:
			try:
				print('\n')
				choice = input('')
				if(int(choice) <= counter):
					os.remove('face_{}.jpg'.format(choice))
					del known_face_names[choice]
					index = int(choice) + 1
					while index <= counter:
						os.rename('face_{}.jpg'.format(index), 'face_{}.jpg'.format(index - 1))
			except:
				print('input not a number')
			finally:
				break