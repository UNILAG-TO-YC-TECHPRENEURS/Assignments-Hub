import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import GenerateAssignmentSerializer, TokenCreateSerializer
from .models import Token
from .tasks import generate_assignment_task


class GenerateAssignmentView(APIView):
    @extend_schema(
        request=GenerateAssignmentSerializer,
        responses={
            200: OpenApiResponse(description='Assignment generated, returns file_links'),
            500: OpenApiResponse(description='Generation failed'),
        }
    )
    def post(self, request):
        serializer = GenerateAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        token_obj = Token.objects.get(token=data['token'], used=False)

        # Dispatch then immediately block until the task finishes
        task = generate_assignment_task.delay(
            token_str=data['token'],
            name=data['name'],
            matric_number=data['matric_number'],
            email=data['email'],
        )

        token_obj.task_id     = task.id
        token_obj.task_status = Token.AssignmentStatus.PENDING
        token_obj.save(update_fields=['task_id', 'task_status'])

        try:
            # Blocks until Celery task returns; 5 min hard ceiling
            result = task.get(timeout=300)
        except Exception as e:
            return Response(
                {"error": f"Assignment generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Assignment generated and emailed successfully.",
                "file_links": result.get("file_links", {}),
            },
            status=status.HTTP_200_OK,
        )


class TokenCreateView(APIView):
    @extend_schema(
        request=TokenCreateSerializer,
        responses={201: OpenApiResponse(description='Token created')}
    )
    def post(self, request):
        token_value = secrets.token_urlsafe(16)
        while Token.objects.filter(token=token_value).exists():
            token_value = secrets.token_urlsafe(16)

        token = Token.objects.create(token=token_value)
        return Response({"token": token.token}, status=status.HTTP_201_CREATED)