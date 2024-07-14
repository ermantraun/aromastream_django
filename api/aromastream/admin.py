from django.contrib import admin
from .models import Video, TimeStamp, ChangeRequest


admin.site.register(Video)
admin.site.register(TimeStamp)
admin.site.register(ChangeRequest)