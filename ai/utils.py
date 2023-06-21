"""
date : 6.8
s3 사용하게 수정
"""
import json
import uuid
import boto3
from PIL import Image
from io import BytesIO
from django.conf import settings
import requests
import numpy as np
import time
from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.models import load_model
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.models import Model
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from ai.__init__ import model, features_array, images_files

class PictogramGenerator:

    def extract_features(self, image_path):
        img = load_img(image_path)  # 이미지 로드
        img = img_to_array(img)  # 이미지를 배열로 변환
        img = np.expand_dims(img, axis=0)  # 배치 차원 추가
        img = preprocess_input(img)  # 이미지 전처리
        features = model.predict(img)  # 특성 추출
        return features.flatten()  # 1차원 벡터로 변환

    def generate_pictogram(self, image: str, tags_id: list):
        """
        # image : "media/drawing/04818-18464...-854.png"
        # tags : list[tag1, tag2, ...]
        # expected return : ["~~.png", "~~.png",...]? 정해지면 구현
        """
        start = time.time()
        drawing_features = self.extract_features(image)
        
        similarities = []
        
        for features in features_array:
            similarity = 1 - cosine(features, drawing_features)  # 코사인 유사도 계산
            similarities.append(similarity)
            pass
        
        top_indices = np.argsort(np.array(similarities).flatten())[::-1][:5]
        
        top = []
        
        for index in top_indices:
            top.append(images_files[index])
            print(images_files[index])
            pass

        end = time.time()
        
        print("time : " + str(end - start))
        
        paths = [  # 테스트용 픽토그램 리턴값. 구현되면 지울것
            top[0],
            top[1],
            top[2],
            top[3],
            top[4]
        ]
        return paths


class Parser:
    """
    Serializers에 알맞은 타입변환을 위한 클래스
    나중에 api받는값 설정되 무조건 리턴이
    """

    # @staticmethod
    # def tags_request_to_serializers(data):
    #    """
    #    input : [{'name' : 'drop'}, {'name': 'water'}]
    #    output : tags = ['drop',]
    #    """
    # tags = [{"name": "water"}, {"name": "drop"}]  # serializer가 필요한 리턴 방식
    #    print(data)
    #    return data

    @staticmethod
    def tags_request_to_ai(tags):
        """
        input : [{'name' : 'drop'}, {'name': 'water'}]
        ai측이 원하는 데이터로 리턴
        tags = ["water", "drop"]
        """
        lst = []
        for item in tags:
            lst.append(item['name'])
        return lst

    @staticmethod
    def pictograms_uploader_to_response(pictogram_urls):
        """
        input : s3에 저장한 urls 5개

        """
        response_data = {
            'data':
                [{'pictogram_url': pictogram_urls[0]},
                 {'pictogram_url': pictogram_urls[1]},
                 {'pictogram_url': pictogram_urls[2]},
                 {'pictogram_url': pictogram_urls[3]},
                 {'pictogram_url': pictogram_urls[4]}, ],
            'error': None
        }
        return json.dumps(response_data)

    @staticmethod
    def pictograms_ai_to_uploader(pictograms):
        """
        expected output : ~~/media/image.jpg
        """
        return pictograms


class S3ImgUploader:
    def __init__(self, file: str):  # test.jpg, test.png
        self.file = settings.MEDIA_PICTOGRAM + file  # self.file = ~/media/images/pictogram

    def upload(self):
        """
        return example : 'c672cf20-a818-4500-b880-e7d85ccf993a.png'
        """
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        file_format_index = self.file.rfind('.')
        url = str(uuid.uuid4()) + self.file[file_format_index:]  # random uuid1~5설정에 대해 알아보고 수정해야할수도?
        s3_client.upload_file(
            self.file,
            settings.AWS_STORAGE_BUCKET_NAME,
            url
        )
        return url


class S3ImgDownloader:
    """
        s3기준으로 받은 url(0004-8481-451....jpeg/png)를 media폴더에 저장 및 이미지 url리턴
        * format type는 PIL기준으로 input할것
        example)
        img_downloader = S3ImgDownloader('png')
        img_path= img_downloader.download(url) # url은 spring에서 전송된 url로
        img_path -> media/images//0004-8485-...447.png <- format 타입 지정한 대로 save
    """

    def __init__(self, format_type='jpeg'):
        self.format_type = format_type

    def download(self, url: str):
        # path = settings.MEDIA_DRAWING + url
        url = 'https://' + settings.AWS_S3_CUSTOM_DOMAIN + '/' + url
        response = requests.get(url)
        image_content = response.content
        file_name = url[url.rfind('/') + 1:]  # test_image.jpg
        format_index = file_name.rfind('.')
        path = file_name[:format_index] + '.' + self.format_type
        image = Image.open(BytesIO(image_content))
        image.save(settings.MEDIA_DRAWING + path, format=self.format_type)
        return settings.MEDIA_DRAWING + path
