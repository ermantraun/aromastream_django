from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Video, TimeStamp
from django.core.validators import FileExtensionValidator
from django.conf import settings

USER_MODEL = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = USER_MODEL
        extra_kwargs = {'password': {'write_only': True}}
        exclude = ['id', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']
    def create(self, validated_data):
        user = USER_MODEL.objects.create_user(**validated_data)
        
        return user
    
    
    def update(self, instance, validated_data):
        username = validated_data.get('username', None)
        email = validated_data.get('email', None)
        
        if username is not None:
            instance.username = validated_data['username']
        if email is not None:
            instance.email = validated_data['email']
            
        instance.save()
        
        return instance
    
class UserUpdateSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = USER_MODEL
        exclude = UserSerializer.Meta.exclude + ['password']


class PasswordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ['password']


class PasswordUpdateConfirmSerializer(serializers.Serializer):
    confirm_code = serializers.CharField(max_length=settings.VERIFICATION_CODE_LENGTH)


class TimeStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStamp
        exclude = ['id', 'created_at']
        
    
    def create(self, validated_data):
        timestamp = TimeStamp.objects.create(**validated_data)
        
        return timestamp
    
    
class VideoSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Video
        extra_kwargs = {'file': {'validators': [FileExtensionValidator(allowed_extensions=['mp4'])]}, 'views': {'read_only': True}}
        exclude = ['id', 'created_at', 'updated_at']
    def create(self, validated_data):
        video = Video.objects.create(**validated_data)
        
        return video
    
class TriggerSerializer(serializers.Serializer):
    timestamp = serializers.PrimaryKeyRelatedField(queryset=TimeStamp.objects.all())
    
    
class Response400Serializer(serializers.Serializer):
    detail = serializers.DictField(child=serializers.CharField(help_text="invalid parameter"), 
                                   help_text="invalid parameters")


class BasePaginateSchema(serializers.Serializer):
        count = serializers.IntegerField()
        next = serializers.CharField(allow_blank=True, required=False)
        previous = serializers.CharField(allow_blank=True, required=False)
        results = None

class TimeStampPaginateSchema(BasePaginateSchema):
    results = serializers.ListSerializer(child=TimeStampSerializer())
    
class VideoPaginateSchema(BasePaginateSchema):
    results = serializers.ListSerializer(child=VideoSerializer())
    
