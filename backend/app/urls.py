from django.urls import path
from .views import GenerateAssignmentView, TokenCreateView

urlpatterns = [
    path('generate/', GenerateAssignmentView.as_view(), name='generate'),
    path('tokens/', TokenCreateView.as_view(), name='token-create')
]