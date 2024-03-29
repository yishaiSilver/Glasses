import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import cv2
import time
import threading
import os
from getkeys import key_check

import run_inference
from run_inference import predict
from run_inference import set
import playsound
import face_rec
from face_rec import save_face

run_inference.initSound()

last_thread = None

frame_lock = threading.RLock()
result_lock = threading.RLock()

frame_field = {'f': []}

bool_values = {'fl': False, 'fm': True, 'rl': False, 'rm': True}

result = {'r': None}

running = True


def main():
	global last_thread
	global bool_values

	cap = cv2.VideoCapture(0)
	#last_time = time.time()

	should_draw_boxes = False
	frame_count = 0

	print("Starting thread")
	t = threading.Thread(target=main_box)
	t.start()

	output_dict = None

	while True:
		ret, frame = cap.read()
		keys = key_check()

		if '1' in keys:
			cv2.imwrite("image.jpg", frame)
			filename = "image.jpg"

			print(last_thread.is_alive())
			if(not last_thread.is_alive()):
				cv2.imshow('last_picture', frame)
				t = threading.Thread(target=predict, args=(filename,))
				t.start()
				last_thread = t
		elif '2' in keys:
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

		elif '3' in keys:
			face_rec.delete_face()
		elif '4' in keys:
			if(frame_count == 0):
				should_draw_boxes = not should_draw_boxes
				print("Toggling boxes")
			frame_count += 1
		elif len(keys) == 1:
			run_inference.set(keys[0])
		else:
			frame_count = 0

		if(should_draw_boxes):
			if(bool_values['fm']):
				frame_field["f"] = frame
				bool_values['fm'] = False
				bool_values['fl'] = True

			if(bool_values['rm']):
				output_dict = result['r']
				bool_values['rm'] = False
				bool_values['rl'] = True

			if(output_dict != None):
				vis_util.visualize_boxes_and_labels_on_image_array(
					frame,
					output_dict['detection_boxes'],
					output_dict['detection_classes'],
					output_dict['detection_scores'],
					category_index,
					instance_masks=output_dict.get('detection_masks'),
					use_normalized_coordinates=True,
					line_thickness=8)

		cv2.imshow('original', frame)
		
		if cv2.waitKey(20) & 0xFF == ord('q'):
			# ser.write(b'q')q
			cap.release()
			cv2.destroyAllWindows()
			break



# - - - BOUNDING BOXES STARTS HERE - - -

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

# In[18]:


category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


def run_inference_for_single_image(image, graph):
  
  # Get handles to input and output tensors
  ops = tf.get_default_graph().get_operations()
  all_tensor_names = {output.name for op in ops for output in op.outputs}
  tensor_dict = {}
  for key in [
      'num_detections', 'detection_boxes', 'detection_scores',
      'detection_classes', 'detection_masks'
  ]:
    tensor_name = key + ':0'
    if tensor_name in all_tensor_names:
      tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
          tensor_name)
  if 'detection_masks' in tensor_dict:
    # The following processing is only for single image
    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
        detection_masks, detection_boxes, image.shape[1], image.shape[2])
    detection_masks_reframed = tf.cast(
        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
    # Follow the convention by adding back the batch dimension
    tensor_dict['detection_masks'] = tf.expand_dims(
        detection_masks_reframed, 0)
  image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

  # Run inference
  output_dict = sess.run(tensor_dict,
                         feed_dict={image_tensor: image})

  # all outputs are float32 numpy arrays, so convert types as appropriate
  output_dict['num_detections'] = int(output_dict['num_detections'][0])
  output_dict['detection_classes'] = output_dict[
      'detection_classes'][0].astype(np.int64)
  output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
  output_dict['detection_scores'] = output_dict['detection_scores'][0]
  if 'detection_masks' in output_dict:
    output_dict['detection_masks'] = output_dict['detection_masks'][0]

  return output_dict


# In[22]:
def main_box():
	global detection_graph
	global sess
	global running

	r = {}

	with detection_graph.as_default():
		with tf.Session() as sess:
			while running:
				if(bool_values['fl']):
					if(len(frame_field['f']) != 0):
						image_np_expanded = np.expand_dims(frame_field["f"], axis=0)
						# Actual detection.
						r = run_inference_for_single_image(image_np_expanded, detection_graph)
					bool_values['fl'] = False
					bool_values['fm'] = True

				if(bool_values['rl']):
					if(len(r) != 0):
						result['r'] = r
					bool_values['rl'] = False
					bool_values['rm'] = True

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

running = False