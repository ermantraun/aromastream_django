from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery
from django.contrib.auth.models import update_last_login
from .models import TimeStamp, ChangeRequest, Video
from .serializators import UserSerializer, TimeStampSerializer, VideoSerializer
import random


def generate_verification_code(length=6):
    digits = "0123456789"
    verification_code = "".join(random.choice(digits) for _ in range(length))
    return verification_code


def send_confirm_code(user, code):
    pass

class UserCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        token = SlidingToken.for_user(serializer.instance)
        update_last_login(None, serializer.instance)
        return Response({'token': str(token)}, status=status.HTTP_201_CREATED)

class UserView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
class TimeStampListView(APIView, PageNumberPagination):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, video_id):
        
        try:
            video_id = int(video_id)
        except ValueError:
            return Response({"detail": "Invalid video ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        timestamps = TimeStamp.objects.filter(video_id=video_id)
        results = self.paginate_queryset(timestamps, request, view=self)
        serializer = TimeStampSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class TimeStampCreateView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TimeStampSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserPasswordUpdateView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
        
    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'required_partial_fields': ['password']})
        serializer.is_valid(raise_exception=True)
        
        confirm_code = generate_verification_code()
        
        ChangeRequest(user=user, field='password', confirm_code=confirm_code, new_value=serializer.validated_data['password']).save()
        
        send_confirm_code(user, confirm_code)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UserPasswordUpdateConfirmView(APIView):
    def post(self, request):
        confirm_code = request.data.get('confirm_code', None)
        user = request.user
        if confirm_code is None:
            return Response({"detail": {'confirm_code': 'field is required'}}, status=status.HTTP_400_BAD_REQUEST)
        
        ChangeRequest.cleanup_expired_user_change_requests(user, 'password')
        
        try:
            change_request = ChangeRequest.objects.get(user=user, confirm_code=confirm_code, field='password')
        except ChangeRequest.DoesNotExist:
            return Response({"detail": "Invalid or expired confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        user.set_password(change_request.new_value)
        user.save()
        change_request.delete()
        
        
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class VideoListView(APIView, PageNumberPagination):
    
    parser_classes = [FormParser, MultiPartParser]

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        
        return self.get_paginated_response(serializer.data)

    
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    
class VideoDetailView(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, video_id):
        try:
            video_id = int(video_id)
        except ValueError:
            return Response({"detail": {'video':"Invalid video ID."}}, status=status.HTTP_400_BAD_REQUEST)
        
        video = Video.objects.get(id=video_id)
        video.views += 1
        video.save()
        serializer = VideoSerializer(video)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PopularVideoListView(APIView, PageNumberPagination):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        
        return self.get_paginated_response(serializer.data)

    
class SearchVideoListView(APIView, PageNumberPagination):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        query = request.query_params.get('query', None)
        
        if query is None:
            return Response({"detail": {'query': "field is required."}}, status=status.HTTP_400_BAD_REQUEST)
        
        search_vector = SearchVector('title', 'description')
        search_query = SearchQuery(query)
        videos = Video.objects.annotate(search=search_vector).filter(search=search_query).order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        
        return self.get_paginated_response(serializer.data)