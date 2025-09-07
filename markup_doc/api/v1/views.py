from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from markup_doc.api.v1.serializers import ArticleDocxSerializer
from markup_doc.marker import mark_article

import json

# Create your views here.

class ArticleViewSet(
    GenericViewSet,  # generic view functionality
    CreateModelMixin,  # handles POSTs
):
    serializer_class = ArticleDocxSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        return self.api_article(request)

    def api_article(self, request):
        try:
            data = json.loads(request.body)
            post_text = data.get('text')  # Obtiene el parámetro
            post_metadata = data.get('metadata')  # Obtiene el parámetro

            resp_data = mark_article(post_text, post_metadata)

            response_data = {
                'message': resp_data,
            }
        except json.JSONDecodeError:
            response_data = {
                'error': 'Error processing'
            }

        return JsonResponse(response_data)