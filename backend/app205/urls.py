from django.urls import path
from .views import GenerateAssignment205View, TokenCreate205View

urlpatterns = [
    path('generate/', GenerateAssignment205View.as_view(), name='generate_205'),
    path('tokens/', TokenCreate205View.as_view(), name='token_create_205'),
]