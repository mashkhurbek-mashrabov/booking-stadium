from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.db.models import Q
from .models import Stadium, StadiumPhoto
from .serializers import StadiumSerializer, StadiumPhotoSerializer
from .permissions import IsOwnerOrAdmin
from .constants import StadiumStatus


class StadiumViewSet(viewsets.ModelViewSet):
    """
    ViewSet for stadium management:
    - List: All authenticated users can view available stadiums
    - Create: Only owners and admins can create stadiums
    - Update/Delete: Only stadium owner or admin can modify
    """
    serializer_class = StadiumSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """
        Return all active stadiums for normal users.
        Owners see their own stadiums (including archived).
        Admins see all stadiums.
        """
        user = self.request.user
        if user.role == 'admin':
            return Stadium.objects.all()
        elif user.role == 'owner':
            return Stadium.objects.filter(owner=user)
        else:
            # Regular users only see available stadiums
            return Stadium.objects.filter(status=StadiumStatus.AVAILABLE)

    @action(detail=True, methods=['post'])
    def upload_photos(self, request, pk=None):
        """Upload photos for a stadium."""
        stadium = self.get_object()
        
        # Check if files were provided
        if 'photos' not in request.FILES:
            return Response(
                {'error': 'No photos provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        photos = request.FILES.getlist('photos')
        photo_objects = []
        
        for photo in photos:
            # Set the first photo as main if no main photo exists
            is_main = not StadiumPhoto.objects.filter(stadium=stadium, is_main=True).exists()
            photo_obj = StadiumPhoto.objects.create(
                stadium=stadium,
                image=photo,
                is_main=is_main
            )
            photo_objects.append(photo_obj)

        serializer = StadiumPhotoSerializer(photo_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def set_main_photo(self, request, pk=None):
        """Set a photo as the main photo for the stadium."""
        stadium = self.get_object()
        photo_id = request.data.get('photo_id')

        try:
            # Get the photo and verify it belongs to this stadium
            photo = StadiumPhoto.objects.get(id=photo_id, stadium=stadium)
            
            # Remove main flag from all other photos
            stadium.photos.update(is_main=False)
            
            # Set this photo as main
            photo.is_main = True
            photo.save()

            return Response({'status': 'Main photo set successfully'})
        except StadiumPhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )