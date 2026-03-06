from rest_framework import serializers
from .models import Token205

class GenerateAssignment205Serializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    matric_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()

    def validate_token(self, value):
        try:
            token_obj = Token205.objects.get(token=value, used=False)
        except Token205.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used token.")
        return value

class TokenCreate205Serializer(serializers.Serializer):
    pass