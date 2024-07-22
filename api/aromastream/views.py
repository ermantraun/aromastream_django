import logging
import random
import requests
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.auth.models import update_last_login
from .models import TimeStamp, ChangeRequest, Video
from .serializators import UserSerializer, TimeStampSerializer, VideoSerializer
from django.conf import settings


def generate_verification_code(length=6):
    digits = "0123456789"
    verification_code = "".join(random.choice(digits) for _ in range(length))
    return verification_code

def send_confirm_code(user, code):
    logger.info(f"Sending confirmation code {code} to user {user.username}")


logger = logging.getLogger(__name__)

class UserCreateView(APIView):
    def post(self, request):
        logger.info(f"Request data: {request.data}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            token = SlidingToken.for_user(serializer.instance)
            update_last_login(None, serializer.instance)
            logger.info(f"User created successfully: {serializer.data}")
            return Response({'token': str(token)}, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"User creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logger.info(f"UserView: User {request.user.username} requested profile")
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        logger.info(f"UserView: User {request.user.username} requested profile update")
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("User profile updated successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error(f"User profile update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimeStampListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, video_id):
        logger.info(f"TimeStampListView: Requested timestamps for video ID {video_id}")
        try:
            video_id = int(video_id)
        except ValueError:
            logger.error("Invalid video ID format")
            return Response({"detail": "Invalid video ID."}, status=status.HTTP_400_BAD_REQUEST)

        timestamps = TimeStamp.objects.filter(video_id=video_id)
        results = self.paginate_queryset(timestamps, request, view=self)
        serializer = TimeStampSerializer(results, many=True)
        logger.info(f"Successfully retrieved {len(serializer.data)} timestamps")
        return self.get_paginated_response(serializer.data)

class TimeStampCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info("TimeStampCreateView: Received POST request to create timestamp")
        serializer = TimeStampSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Timestamp created successfully")
            return Response(status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Timestamp creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"UserPasswordUpdateView: User {request.user.username} requested password update")
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'required_partial_fields': ['password']})
        if serializer.is_valid():
            confirm_code = generate_verification_code()
            ChangeRequest(user=user, field='password', confirm_code=confirm_code, new_value=serializer.validated_data['password']).save()
            send_confirm_code(user, confirm_code)
            logger.info("Password update request processed successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error(f"Password update request failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordUpdateConfirmView(APIView):
    def post(self, request):
        logger.info("UserPasswordUpdateConfirmView: Received POST request to confirm password update")
        confirm_code = request.data.get('confirm_code', None)
        user = request.user
        if confirm_code is None:
            logger.error("Confirmation code not provided")
            return Response({"detail": {'confirm_code': 'field is required'}}, status=status.HTTP_400_BAD_REQUEST)

        ChangeRequest.cleanup_expired_user_change_requests(user, 'password')
        try:
            change_request = ChangeRequest.objects.get(user=user, confirm_code=confirm_code, field='password')
        except ChangeRequest.DoesNotExist:
            logger.error("Invalid or expired confirmation code")
            return Response({"detail": {'confirm_code': 'invalid or expired'}}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(change_request.new_value)
        user.save()
        change_request.delete()
        logger.info("Password updated successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class VideoListView(APIView, PageNumberPagination):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        logger.info("VideoListView: Requested video list")
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        logger.info(f"Successfully retrieved {len(serializer.data)} videos")
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        logger.info("VideoListView: Received POST request to create video")
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Video created successfully")
            return Response(status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Video creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, video_id):
        logger.info(f"VideoDetailView: Requested details for video ID {video_id}")
        try:
            video_id = int(video_id)
        except ValueError:
            logger.error("Invalid video ID format")
            return Response({"detail": {'video': "Invalid ID."}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
            
        except Video.DoesNotExist:
            logger.error("Video not found")
            return Response({"detail": {'video': "not found"}}, status=status.HTTP_404_NOT_FOUND)

        video.views += 1
        video.save()
        serializer = VideoSerializer(video)
        logger.info("Video details retrieved successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PopularVideoListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        logger.info("PopularVideoListView: Requested popular videos list")
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        logger.info(f"Successfully retrieved {len(serializer.data)} popular videos")
        return self.get_paginated_response(serializer.data)

class SearchVideoListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        logger.info("SearchVideoListView: Received search query")
        query = request.query_params.get('query', None)
        if query is None:
            logger.error("Search query not provided")
            return Response({"detail": {'query': "field is required."}}, status=status.HTTP_400_BAD_REQUEST)

        search_vector = SearchVector('title', 'description')
        search_query = SearchQuery(query)
        videos = Video.objects.annotate(search=search_vector).filter(search=search_query).order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        logger.info(f"Successfully retrieved {len(serializer.data)} search results")
        return self.get_paginated_response(serializer.data)


class TriggerListView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logger.info("TriggerListView: Received POST request to trigger triggers")
        timestamp_id = request.data.get('timestamp')
        
        if timestamp_id is None:
            logger.error("Timestamp ID not provided")
            return Response({"detail": {'timestamp': "field is required."}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            timestamp = TimeStamp.objects.get(pk=timestamp_id)
        except TimeStamp.DoesNotExist:
            logger.error("Timestamp not found")
            return Response({"detail": {'timestamp': "not found"}}, status=status.HTTP_404_NOT_FOUND)
        
        aroma = timestamp.aroma
        arduino_url = settings.ARDUINO_URL.format(aroma)
        response = requests.get(arduino_url)

        if response.status_code == 200:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": f"Failed to trigger aroma {aroma}"}, status=response.status_code)