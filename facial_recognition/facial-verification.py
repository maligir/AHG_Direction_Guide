from ctypes import sizeof
from pickle import FALSE
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import cv2
import os, shutil
from pyk4a import PyK4A

class FaceVerification:

	def __init__(self, default_image='default.jpg'):
		self.detector = MTCNN()
		self.model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
		self.defaultFaces = self.extract_face(default_image)
		self.curWidth = 0
		self.curHeight = 0
		self.origWidth = 0
		self.origHeight = 0
		self.passPhrase = "pass"
		self.failPhrase = "fail"
 
	# extract a single face from a given photograph
	def extract_face(self, filename, required_size=(224, 224)):
		# load image from file
		pixels = pyplot.imread(filename)
		oldImage = Image.fromarray(pixels)
		self.origWidth = oldImage.width
		self.origHeight = oldImage.height
		# detect faces in the image
		results = self.detector.detect_faces(pixels)
		# extract the bounding box from the first face
		if len(results) == 0:
			return self.defaultFaces
		x1, y1, width, height = results[0]['box']
		x2, y2 = x1 + width, y1 + height
		# extract the face
		face = pixels[y1:y2, x1:x2]
		# resize pixels to the model size
		image = Image.fromarray(face)
		self.curWidth = image.width
		self.curHeight = image.height
		image = image.resize(required_size)
		face_array = asarray(image)
		return face_array
	
	# extract faces and calculate face embeddings for a list of photo files
	def get_embeddings(self, filenames):
		# extract faces
		faces = [self.extract_face(f) for f in filenames]
		# convert into an array of samples
		samples = asarray(faces, 'float32')
		# prepare the face for the model, e.g. center pixels
		samples = preprocess_input(samples, version=2)
		# perform prediction
		yhat = self.model.predict(samples)
		return yhat
	
	# determine if a candidate face is a match for a known face
	def is_match(self, known_embedding, candidate_embedding, thresh=0.4):
		# calculate distance between embeddings
		score = cosine(known_embedding, candidate_embedding)
		if score <= thresh and self.curWidth/self.origWidth > 0.05 :
			print('>face is a Match (%.3f <= %.3f)' % (score, thresh))
			return True
		else:
			print('>face is NOT a Match (%.3f > %.3f)' % (score, thresh))
			return False

	def clean_images(self, imageName):
		try:
			if os.path.isfile(imageName) or os.path.islink(imageName):
						os.unlink(imageName)
		except Exception as e:
			print(e)

	def clean_folder(self, folder):
		for filename in os.listdir(folder):
			file_path = os.path.join(folder, filename)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete %s. Reason: %s' % (file_path, e))
	
	def write_result(self, trueOrNot, filename):
		f = open(filename, "r")
		fileContents = f.read()
		f.close()
		if(fileContents == self.passPhrase and trueOrNot == False):
			f = open(filename, "w")
			f.write(self.failPhrase)
		elif(fileContents == self.failPhrase and trueOrNot == True):
			f = open(filename, "w")
			f.write(self.passPhrase)

	def run(self):

		k4a = PyK4A()
		k4a.start()

		capture = k4a.get_capture()
		frame  = Image.fromarray(capture.color)
		# Create window connected to camera
		# cv2.namedWindow("Facial Verification")
		#vc = cv2.VideoCapture(0)
		# Try to read in first frame
		#if vc.isOpened():
		#	rval, frame = vc.read()
		#else:
		#	rval = False
		#Create Constants
		filenames = []
		frameCounter = 0
		fileCounter = 0
		key = 26
		# infinite loop until esc key is pressed
		while not key == 27:
			# Get frame from camera and wait a few milliseconds
			# cv2.imshow("preview", frame)
			capture = k4a.get_capture()
			frame = Image.fromarray(capture.color)
			frame = frame.convert("RGB")
			key = cv2.waitKey(20)
			# Every 120 frames, save a frame and run facial recognition
			if(frameCounter%120 == 0):
				if(fileCounter > 1):
					fileCounter = 1
				filename = "img" + str(fileCounter) + ".jpg"
				# cv2.imwrite(filename, frame)
				frame.save(filename)
				filenames.append(filename)
				if(len(filenames) > 2):
					filenames.pop(1)
				print(filenames)
				embeddings = self.get_embeddings(filenames)
				trueOrNot = self.is_match(embeddings[0], embeddings[fileCounter])
				self.write_result(trueOrNot, 'result.txt')
				fileCounter += 1
			#update frame counter
			frameCounter+=1
		# Clean up and Destroy all windows and files
		cv2.destroyWindow("preview")
		# self.clean_folder(".")
		self.clean_images("img0.jpg")
		self.clean_images("img1.jpg")


app = FaceVerification()
app.run()
