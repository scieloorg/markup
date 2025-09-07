from rest_framework import serializers
from markup_doc.models import ArticleDocx

class ArticleDocxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleDocx
        fields = "__all__"  