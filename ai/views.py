"""
date : 6.19
"""
import os.path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from .utils import PictogramGenerator, Parser, S3ImgUploader, S3ImgDownloader
from ai.models import Drawing, Pictogram
from ai.serializers import DrawingSerializer


# Create your views here.
# drawing을 post로 요청을 받는다.
# 픽토그램을 리스트로 다시 json에 담아서 전송한다.
# drawing 이미지는 media/images/drawing_(난수).png로 저장


@api_view(http_method_names=['POST'])
@parser_classes([FormParser, JSONParser, MultiPartParser])
def pictogram_list(request):
    """
    POST:(expected)
        pictogram_uri : c672cf20-a818-4500-b880-e7d85ccf993a.png
        tags : ["name": "tag1", ...]
        return [{"pictogram_data" : "픽토그램 데이터"}, {"pictogram_data" : "픽토그램 데이터"}]
    """
    if request.method == 'POST':
        # 그림 저장
        drawing_uri = request.data.get('drawing_uri')
        #tags = request.data.getlist('tags')
        tags = []
        # if not tags:
        #     return Response({
        #         "data": None,
        #         "error": "tags not found"
        #     }, status=status.HTTP_400_BAD_REQUEST)
        if drawing_uri:
            try:
                drawing_bytes = save_drawing_in_memory(request)
                # drawing_bytes: bytes타입의 drawing -> PIL을 이용하여 사용
                # drawing_path: '~/media/images/drawing/~.png'
                pictograms = generate_pictograms(drawing_bytes, tags)
                # pictograms : ['pictogram1.png', 'pictogram2.png', ...]
                pictograms = Parser.pictograms_ai_to_uploader(pictograms)
                pictogram_uris = upload_pictograms(pictograms)  # return [uuid.png, uuid.png ...]
                response_data = Parser.pictograms_uploader_to_response(pictogram_uris)
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(str(e))
                return Response({
                    "data": None,
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "data": None,
                "error": "drawing uri not found"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "data": None,
            "error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


def save_drawing_in_local(request):
    """
    drawing_uri을 받은걸 s3에 get요청을 하여
    로컬 media 디렉토리에 저장
    무결성(uri인지) 확인 후 Drawing instance리턴
    """
    drawing_uri = request.data.get('drawing_uri')

    img_downloader = S3ImgDownloader('png')

    drawing_path = img_downloader.download(drawing_uri)
    #drawing_path = settings.MEDIA_ROOT + 'test_image.jpeg' # test
    drawing_serializer = DrawingSerializer( # 프로토타입에서는 사용안할확률이 높지만, 혹시나 모델로 저장
        data={
            'drawing_uri': drawing_uri,  # 22WD-2RS...png
        }
    )
    if not drawing_serializer.is_valid():
        print(drawing_serializer.errors)
        raise Exception(drawing_serializer.errors)
    drawing_serializer.save()
    return drawing_path

def save_drawing_in_memory(request):
        """
        drawing_uri을 받은걸 s3에 get요청을 하여
        로컬 media 디렉토리에 저장
        무결성(uri인지) 확인 후 Drawing instance리턴
        """
        drawing_uri = request.data.get('drawing_uri')
        # drawing_path = settings.MEDIA_ROOT + 'test_image.jpeg' # test
        drawing_serializer = DrawingSerializer(  # Serializer로 확인 후 S3에 값을 가져옴.
            data={
                'drawing_uri': drawing_uri,  # 22WD-2RS...png
            }
        )
        if not drawing_serializer.is_valid():
            print(drawing_serializer.errors)
            raise Exception(drawing_serializer.errors)
        drawing_serializer.save()
        img_downloader = S3ImgDownloader('png')
        drawing_bytes = img_downloader.download_in_memory(drawing_uri)
        return drawing_bytes


# ai에게 픽토그램 생성 요청
def generate_pictograms(drawing_bytes: bytes, tags):
    """
    input : drawing_instance
    ai에게 픽토그램 요청
    """
    generator = PictogramGenerator()
    pictograms = generator.generate_pictogram(
        drawing_bytes,
        Parser.tags_request_to_ai(tags)
    )
    return pictograms


def upload_pictograms(pictograms):
    """
    input -> [pictogram1.png, pictogram2.png, ...]
    s3에 픽토그램 생성 및 생성된 url 리턴
    """
    pictogram_urls = []
    for pictogram in pictograms:
        try:
            img_uploader = S3ImgUploader(pictogram)
            upload_url = img_uploader.upload()  # return "uuid.png"
        except Exception as e:
            raise e
        pictogram_urls.append(upload_url)
    return pictogram_urls


def delete_files(path):
    """
    window기준으로 권한 에러 발생
    혹시나의 보안을 위해 따로 설정은 안하고 나중에 확인
    배열안에 있는 파일 삭제
    input : [path1, path2, ...]
    """
    for file in path:
        if os.path.exists(file):
            os.remove(file)


@api_view(['GET'])
def hello(request):
    # 연결 테스트용 api 'api/hello/'
    print('hello world! from request!')
    data = {
        "data": "HELLO!",
        "error": None}
    return Response(data, status=status.HTTP_200_OK)
