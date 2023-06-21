"""
lastest date : 6.8
s3 관련 추가
"""
import json
import csv
import os.path

from rest_framework.test import APITestCase
from django.core.files import File
from rest_framework import status
from django.conf import settings

from . import views
from .models import Drawing, Pictogram
from .serializers import DrawingSerializer
from .utils import S3ImgDownloader, S3ImgUploader, PictogramGenerator, Parser


# Create your tests here.
class AiTest(APITestCase):
    """
    views에 post, get 요청등이 없는 테스트들의 모음
    ai테스트는 여기 작성하면 될 것 같습니다!
    """

    def test_generate_pictograms(self):
        image_name = 'drawn.jpg'

        drawing_serializer = DrawingSerializer(
            data={'drawing_url': settings.MEDIA_ROOT + 'drawn.jpg',
                  'tags': [{"name": "water"}, {"name": "drop"}]})
        if drawing_serializer.is_valid():
            test_instance = drawing_serializer.save()
        else:
            test_instance = None
        pictograms = views.generate_pictograms(drawing_instance=test_instance)
        for pictogram in pictograms:
            self.assertTrue(os.path.exists(pictogram))
        print(pictograms)

    def tearDown(self):
        Drawing.objects.all().delete()


class AiApiTest(APITestCase):
    """
    get, post요청이 있는 테스트들의 모음
    """
    # 해당 코드는 post로 drawing과 tag, drawingtag를 요청에 따라 생성
    def test_post_pictograms(self):
        """
            post를 날려 직접 테스트하는것.
        """
        drawing_url = 'test_image.jpg'
        tags = [{'name': 'drop'}, {'name': 'water'}]
        data = {
            'drawing_url': drawing_url,
            'tags': tags
        }

        print(json.dumps(data))
        # POST 요청 전송 json?
        response = self.client.post('/pictograms/', data=json.dumps(data), content_type='application/json')
        # 객체 확인
        print(response.content.decode())
        self.assertTrue(Drawing.objects.exists())
        drawing = Drawing.objects.first()

        # 결과값
        self.assertEqual(response.status_code, 201)
        json_decoder = json.JSONDecoder()
        response_json = json_decoder.decode(response.json())
        print("uploaded pictograms")
        for pictogram_url in response_json[1]['pictograms']:
            print(pictogram_url)

    def test_post_and_get_tags(self):  # Tags Api test
        model = [{'name': 'pineapple'}, {'name': 'pen'}]
        post_response = self.client.post('/tags/', data={'tags': model}, follow=True,
                                         format='json')
        get_response = self.client.get('/tags/', follow=True, format='json')
        print("=== test post and get tags ===")
        print("Response : Post " + post_response.content.decode('utf-8'))
        print("Response : Get " + get_response.content.decode('utf-8'))
        print("==============================")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        Drawing.objects.all().delete()


class S3Test(APITestCase):
    """
    주의사항 : 이 테스트는 s3를 직접 사용하는 테스트입니다.
            사용이 곧 비용이니 너무 남용하지 않는게 좋을 것 같습니다.
    """

    def test_download(self):
        """
        expected : media디렉토리에 s3에 있는 test_image.jpg, test_image.png 저장
        """
        url = 'https://' + settings.AWS_S3_CUSTOM_DOMAIN + '/test_image.jpg'
        s3_png = S3ImgDownloader('png')
        media_url = s3_png.download(url)
        self.assertTrue('test_image.png' in media_url)
        s3_jpeg = S3ImgDownloader()
        media_url = s3_jpeg.download(url)
        self.assertTrue('test_image.jpeg' in media_url)

    def test_upload(self):
        name = 'pictogram1.png'
        s3 = S3ImgUploader(name)
        url = s3.upload()
        print("s3 upload complete")
        print("uploaded url : ", url)


class djangoTest(APITestCase):
    """
    기타 확인용 테스트
    assert문이 없는 경우에 여기에 작성하였습니다.
    """

    def test_hello(self):
        response = self.client.get('/hello', content_type='application/json')
        print(response)
        print(type(response))

    def test_path_check(self):
        print(settings.MEDIA_ROOT)
        print(settings.MEDIA_URL)
        print(settings.MEDIA_FILES)

    def test_csv_file(self):
        """
        csv파일이 잘 불러와지는가?
        settings.MEDIA_FILES = "~~~media/files/"
        """
        with open(settings.MEDIA_FILES + "test.csv") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                print('|'.join(row))

class UtilTest(APITestCase):
    def test_tags_request_to_ai(self):
        input = [{"name": "water"}, {"name": "drop"}]
        result = Parser.tags_request_to_ai(input)
        print(type(result))

    def test_delete_files(self):
        """
        windows환경에서는 관리자 문제로 사용 못함.
        """
        # given
        file_name = 'test.jpg'
        # when
        views.delete_files(settings.MEDIA_DRAWING + file_name)

