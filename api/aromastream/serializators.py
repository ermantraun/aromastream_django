from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Video, TimeStamp
from django.core.validators import FileExtensionValidator

USER_MODEL = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = USER_MODEL
        extra_kwargs = {'password': {'write_only': True}}
        exclude = ['id', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']
    def create(self, validated_data):
        user = USER_MODEL.objects.create_user(**validated_data)
        
        return user
    
    def validate(self, data):
        required_partial_fields = self.context.get('required_partial_fields', [])
        
        if required_partial_fields:
            fields = set(data.keys())
            required_partial_fields = set(required_partial_fields)
            
            if not(required_partial_fields <= fields):
                error_detail = {}
                for field in (required_partial_fields - fields ):
                    error_detail[field] = 'field is required'
                raise serializers.ValidationError({'detail': error_detail})
            
        return data
    
    def update(self, instance, validated_data):
        username = validated_data.get('username', None)
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        
        if username is not None:
            instance.username = validated_data['username']
        if email is not None:
            instance.email = validated_data['email']
        if password is not None:
            instance.set_password(validated_data['password'])
            
        instance.save()
        
        return instance

class TimeStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStamp
        exclude = ['id']
    def create(self, validated_data):
        timestamp = TimeStamp.objects.create(**validated_data)
        
        return timestamp
    
class VideoSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Video
        extra_kwargs = {'file': {'validators': [FileExtensionValidator(allowed_extensions=['mp4'])]}}
        exclude = ['id', 'created_at', 'updated_at']
    def create(self, validated_data):
        video = Video.objects.create(**validated_data)
        
        return video