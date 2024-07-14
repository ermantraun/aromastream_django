from django.db import models
from uuid import uuid4
from datetime import datetime
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.core.validators import FileExtensionValidator
def upload_file_path(instance, file_name):
    ext = file_name.split('.')[-1]
    date = datetime.now()
    year = date.year
    month = date.month
    day = date.day
    name = uuid4().hex
    file_path = '{}/{}/{}/{}.{}'.format(year, month, day, name, ext)
    return file_path

    
class Video(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField()
    file = models.FileField(upload_to=upload_file_path, validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField()
    
class TimeStamp(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    aroma_id = models.IntegerField()
    moment = models.IntegerField()
    
class ChangeRequest(models.Model):
    FIELD_CHOICES = [('password', 'password')]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recovery_records')
    field = models.CharField(max_length=100, choices=FIELD_CHOICES)
    new_value = models.TextField()
    confirm_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def cleanup_expired_user_change_requests(cls, user, field):
        cls.objects.filter(user=user, field=field, created_at__lt=timezone.now() - timedelta(hours=1)).delete()


