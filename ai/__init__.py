from django.conf import settings
from tensorflow.keras.models import load_model
from keras.models import Model
from tensorflow import keras
import numpy as np
import os

model = load_model(settings.MEDIA_FILES + "VGG16_model.h5")
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'] )

features_array = np.load(settings.MEDIA_FILES + "features.npy")

image_directory = settings.MEDIA_PICTOGRAM

images_files = os.listdir(image_directory)

print("Hello world!")