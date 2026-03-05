from django.db import models


class Token(models.Model):
    class AssignmentStatus(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        DONE     = 'done',     'Done'
        FAILED   = 'failed',   'Failed'

    token          = models.CharField(max_length=100, unique=True)
    used           = models.BooleanField(default=False)
    used_by_email  = models.EmailField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    # Task tracking
    task_id        = models.CharField(max_length=255, null=True, blank=True)
    task_status    = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.PENDING,
        null=True, blank=True,
    )

    # Cloudinary links stored as JSON: { "filename": "https://..." }
    file_links     = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.token