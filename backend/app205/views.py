import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from .serializers import GenerateAssignment205Serializer, TokenCreate205Serializer
from .models import Token205
from .tasks import generate_assignment205_task

class GenerateAssignment205View(APIView):
    @extend_schema(
        request=GenerateAssignment205Serializer,
        responses={202: {'description': 'Assignment generation started'}}
    )
    def post(self, request):
        serializer = GenerateAssignment205Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        generate_assignment205_task.delay(
            token_str=data['token'],
            name=data['name'],
            matric_number=data['matric_number'],
            email=data['email']
        )
        return Response(
            {"message": "COS205 assignment generation started. You will receive an email shortly."},
            status=status.HTTP_202_ACCEPTED
        )

class TokenCreate205View(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=TokenCreate205Serializer,
        responses={201: {'description': 'Token created', 'example': {'token': 'abc123...'}}}
    )
    def post(self, request):
        token_value = secrets.token_urlsafe(32)
        while Token205.objects.filter(token=token_value).exists():
            token_value = secrets.token_urlsafe(32)
        token = Token205.objects.create(token=token_value)
        return Response({"token": token.token}, status=status.HTTP_201_CREATED)