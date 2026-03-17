from rest_framework import serializers
from .models import DetectRecord


class DetectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectRecord
        fields = '__all__'
        read_only_fields = ['id', 'detect_time']
