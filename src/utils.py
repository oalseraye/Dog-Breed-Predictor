import os
os.environ["KERAS_BACKEND"] = "tensorflow"
import cv2
import numpy as np

from keras.models import load_model
from keras.preprocessing import image                  
from keras.applications.resnet50 import ResNet50, preprocess_input


def path_to_tensor(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    return np.expand_dims(x, axis=0)

def read_dog_names():
    with open('dog_names.txt') as f:
        dog_names = [x.split('.')[-1].replace(',','') for x in f.read().split('\n')]
    return dog_names

class DogPredictor:
    def __init__(self):
        self.model = load_model('saved_models/weights.best.Resnet50.hdf5')
        self.ResNet50_model = ResNet50(weights='imagenet')
        self.feature_extractor = ResNet50(weights='imagenet', include_top=False)
        self.face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')
        self.dog_names = read_dog_names()
    
    def predict_dog_breed_from_image(self, filename):
        if self.dog_detector(filename):
            dog_breed = self.predict_dog_breed(filename)
            message = 'This dog breed is %s'%dog_breed
        elif self.face_detector(filename):
            dog_breed = self.predict_dog_breed(filename)
            message = 'This photo looks like an %s'%dog_breed
        else:
            message = 'Error, no dog or human found in image'
        return message
    
    def ResNet50_predict_labels(self, img_path):
        img = preprocess_input(path_to_tensor(img_path))
        return np.argmax(self.ResNet50_model.predict(img))
    
    def face_detector(self, img_path):
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray)
        return len(faces) > 0
    
    def dog_detector(self, img_path):
        prediction = self.ResNet50_predict_labels(img_path)
        return ((prediction <= 268) & (prediction >= 151)) 
    
    def predict_dog_breed(self, filepath):
        tensor = path_to_tensor(filepath)
        feature = self.extract_Resnet50(tensor)
        dog_breed = np.argmax(self.model.predict(feature))
        dog_breed = self.dog_names[dog_breed]
        return dog_breed

    def extract_Resnet50(self, tensor):
    	return self.feature_extractor.predict(preprocess_input(tensor))

