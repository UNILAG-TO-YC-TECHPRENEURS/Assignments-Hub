import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .serializers import GenerateAssignmentSerializer, TokenCreateSerializer
from .models import Token
from .tasks import generate_assignment_task

class GenerateAssignmentView(APIView):
    @extend_schema(
        request=GenerateAssignmentSerializer,
        responses={202: {'description': 'Assignment generation started'}}
    )
    def post(self, request):
        serializer = GenerateAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Trigger Celery task
        generate_assignment_task.delay(
            token_str=data['token'],
            name=data['name'],
            matric_number=data['matric_number'],
            email=data['email']
        )

        return Response(
            {"message": "Assignment generation started. You will receive an email shortly."},
            status=status.HTTP_202_ACCEPTED
        )

class TokenCreateView(APIView):
    permission_classes = [AllowAny]  # Only staff can create tokens

    @extend_schema(
        request=TokenCreateSerializer,
        responses={201: {'description': 'Token created', 'example': {'token': 'abc123...'}}}
    )
    def post(self, request):
        # Generate a unique token
        token_value = secrets.token_urlsafe(32)  # e.g., 43 chars
        # Ensure uniqueness (though probability of collision is extremely low)
        while Token.objects.filter(token=token_value).exists():
            token_value = secrets.token_urlsafe(32)
        
        token = Token.objects.create(token=token_value)
        return Response(
            {"token": token.token},
            status=status.HTTP_201_CREATED
        )