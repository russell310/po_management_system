from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TimeStamp(models.Model):
    """
    An abstract base model that provides self-updating
    'created_at' and 'updated_at' fields along with user tracking.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        abstract = True
