import cv2
import run_inference
from run_inference import predict
from run_inference import set
import silverStandardCMD as silver
import time
import playsound
import cv2
import threading
import os
import face_rec
from getkeys import key_check
from face_rec import save_face
from darkflow.net.build import TFNet
from object_detection import object_detection_tutorial

silver.main()
run_inference.initSound()

last_thread = None

def main():
	global last_thread
	cap = cv2.VideoCapture(0)
	#last_time = time.time()

	should_draw_boxes = False
	frame_count = 0

	while True:
		ret, frame = cap.read()
		cv2.imshow('original', frame)
		keys = key_check()

		

		if 'X' in keys:
			cv2.imwrite("image.jpg", frame)
			filename = "image.jpg"

			print(last_thread.is_alive())
			if(not last_thread.is_alive()):
				cv2.imshow('last_picture', frame)
				t = threading.Thread(target=predict, args=(filename,))
				t.start()
				last_thread = t
		elif 'N' in keys:
			counter = 0
			while True:
				file_name = 'face_{}.jpg'.format(counter)
				if os.path.isfile(file_name):
					counter += 1
				else:
					break

			print('\n - - - SAVING NEW FACE - - -\n')
			filename = "face_{}.jpg".format(counter)
			counter += 1
			cv2.imwrite(filename, frame)
			name = input("Please enter a name: ")
			keys = []

			print(last_thread.is_alive())
			if(not last_thread.is_alive()):
				cv2.imshow('last_picture', frame)
				t = threading.Thread(target=save_face, args=(filename, name,))
				t.start()
				last_thread = t

		elif 'Q' in keys:
			break
		elif 'P' in keys:
			should_draw_boxes = not should_draw_boxes
			print("Toggling boxes")
		elif len(keys) == 1:
			run_inference.set(keys[0])
		
		if cv2.waitKey(20) & 0xFF == ord('q'):
			# ser.write(b'q')q
			cap.release()
			cv2.destroyAllWindows()
			break

if __name__ == "__main__":
  last_thread
  j = threading.Thread(target=set, args=("1",))
  j.start()
  t = threading.Thread(target=predict, args=("image.jpg",))
  t.start()
  last_thread = t
  main()