"""
date : 6.20

imageField는 Drawing(API로 요청받음), Pictogram(AI가 생성)으로,
- 6.04
Drawing에 태그, 요청한 그림이 담겨있도록 세팅
Tags제거
"""
from django.db import models


# Create your models here.

#class Tag(models.Model):
#    name = models.CharField(max_length=20)


class Drawing(models.Model):
    drawing_url = models.CharField(max_length=100)
#    tags = models.ManyToManyField(Tag)


# 이미지 필드 및 기타 필드들


# class DrawingTag(models.Model):
#     drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="drawing_id")
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tag_name")
#     # 이미지와 태그 간의 관계를 나타내는 N:N 관계 모델


class Pictogram:  # 1(drawing):N(pictogram)
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE)
    pictogram = models.ImageField()
