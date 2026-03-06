from django.db import models

class Token205(models.Model):
    class AssignmentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        DONE = 'done', 'Done'
        FAILED = 'failed', 'Failed'

    token = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    used_by_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Cloudinary links and task status
    file_links = models.JSONField(default=dict, blank=True)
    task_status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.PENDING,
    )

    def __str__(self):
        return self.token