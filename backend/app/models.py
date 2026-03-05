from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    used_by_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token