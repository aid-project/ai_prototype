"""
date : 5.31

작성된 api의 urls가 views에 있는 메소드 실행

"""
from django.contrib import admin
from django.urls import path, include
from ai import views

urlpatterns = [
    path('pictograms/', views.pictogram_list),  # 픽토그램 생성 api
    #path('tags/', views.tag_list),
    path('hello/', views.hello)
    # path('tags/<str:name>', views.tag_detail)
]
