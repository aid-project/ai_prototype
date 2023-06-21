"""
date : 5.30

"""
from rest_framework import serializers
from .models import Drawing, Pictogram


#class TagSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Tag
#        fields = ['name']


class DrawingSerializer(serializers.ModelSerializer):
    drawing_uri = serializers.CharField()
#    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Drawing
        fields = ['drawing_uri']


# class DrawingTagSerializer(serializers.ModelSerializer):
#     tags = serializers.StringRelatedField(many=True, read_only=True)
#     drawing = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         model = DrawingTag
#         fields = ['drawing', 'tag']


class PictogramSerializer(serializers.ModelSerializer):
    drawing = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Pictogram
        fields = ['drawing', 'pictogram']
