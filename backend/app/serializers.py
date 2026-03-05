from rest_framework import serializers

class GenerateAssignmentSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    matric_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()

    def validate_token(self, value):
        from .models import Token
        try:
            token_obj = Token.objects.get(token=value, used=False)
        except Token.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used token.")
        return value

class TokenCreateSerializer(serializers.Serializer):
    # No input fields needed; just a placeholder for documentation
    pass