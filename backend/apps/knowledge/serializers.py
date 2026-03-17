from rest_framework import serializers
from .models import KnowledgeInfo


class KnowledgeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeInfo
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']
