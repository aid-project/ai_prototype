"""
date : 6.19
"""
import os.path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from .utils import PictogramGenerator, Parser, S3ImgUploader, S3ImgDownloader
from ai.models import Drawing, Pictogram
from ai.serializers import DrawingSerializer


# Create your views here.
# drawing을 post로 요청을 받는다.
# 픽토그램을 리스트로 다시 json에 담아서 전송한다.
# drawing 이미지는 media/images/drawing_(난수).png로 저장


@api_view(http_method_names=['POST'])
@parser_classes([MultiPartParser, JSONParser])
def pictogram_list(request):
    """
    POST:(expected)
        pictogram_url : c672cf20-a818-4500-b880-e7d85ccf993a.png
        tags : ["name": "tag1", ...]
        return [{"pictogram_data" : "픽토그램 데이터"}, {"pictogram_data" : "픽토그램 데이터"}]
    """
    if request.method == 'POST':
        # 그림 저장
        drawing_url = request.data.get('drawing_url')
        tags = request.data.get('tags', [])
        if not tags:
            return Response({
                "data": None,
                "error": "tags not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        if drawing_url:
            try:
                drawing_path = save_drawing_tags(request)
                # drawing_path: '~/media/images/drawing/~.png'
                pictograms = generate_pictograms(drawing_path, tags)
                # pictograms : ['pictogram1.png', 'pictogram2.png', ...]
                pictograms = Parser.pictograms_ai_to_uploader(pictograms)
                pictogram_urls = upload_pictograms(pictograms)  # return [uuid.png, uuid.png ...]
                response_data = Parser.pictograms_uploader_to_response(pictogram_urls)
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "data": None,
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "data": None,
                "error": "drawing url not found"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "data": None,
            "error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


def save_drawing_tags(request):
    """
    drawing_url을 받은걸 s3에 get요청을 하여
    로컬 media 디렉토리에 저장
    무결성(url인지) 확인 후 Drawing instance리턴
    """
    drawing_url = request.data.get('drawing_url')

    img_downloader = S3ImgDownloader('png')

    drawing_path = img_downloader.download(drawing_url)
    #drawing_path = settings.MEDIA_ROOT + 'test_image.jpeg' # test
    drawing_serializer = DrawingSerializer( # 프로토타입에서는 사용안할확률이 높지만, 혹시나 모델로 저장
        data={
            'drawing_url': drawing_url,  # 22WD-2RS...png
        }
    )
    if not drawing_serializer.is_valid():
        print(drawing_serializer.errors)
        raise Exception(drawing_serializer.errors)
    drawing_serializer.save()
    return drawing_path


# ai에게 픽토그램 생성 요청
def generate_pictograms(drawing_path, tags):
    """
    input : drawing_instance
    ai에게 픽토그램 요청
    """
    generator = PictogramGenerator()
    pictograms = generator.generate_pictogram(
        drawing_path,
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
    # 연결 테스트용 api '/hello/'
    print('hello world! from request!')
    data = {
        "data": "HELLO!",
        "error": None}
    return Response(data, status=status.HTTP_200_OK)
