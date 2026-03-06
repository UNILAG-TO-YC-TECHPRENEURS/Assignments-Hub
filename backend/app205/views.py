import secrets
import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GenerateAssignment205Serializer, TokenCreate205Serializer
from .models import Token205
from .tasks import generate_assignment205_task


class GenerateAssignment205View(APIView):
    def post(self, request):
        try:
            serializer = GenerateAssignment205Serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            token_obj = Token205.objects.get(token=data['token'], used=False)

            task = generate_assignment205_task.delay(
                token_str=data['token'],
                name=data['name'],
                matric_number=data['matric_number'],
                email=data['email'],
            )

            result = task.get(timeout=300, disable_sync_subtasks=False)

            return Response(
                {
                    "message": "Assignment generated and emailed successfully.",
                    "file_links": result.get("file_links", {}),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"{type(e).__name__}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TokenCreate205View(APIView):
    def post(self, request):
        token_value = secrets.token_urlsafe(16)
        while Token205.objects.filter(token=token_value).exists():
            token_value = secrets.token_urlsafe(16)
        token = Token205.objects.create(token=token_value)
        return Response({"token": token.token}, status=status.HTTP_201_CREATED)