from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import Stadium, StadiumPhoto
from .serializers import StadiumSerializer, StadiumPhotoSerializer
from .permissions import IsOwnerOrAdmin
from .constants import StadiumStatus
from django.db.models.expressions import RawSQL


class StadiumViewSet(viewsets.ModelViewSet):
    serializer_class = StadiumSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        queryset = Stadium.objects.all()

        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')

        if user.role == 'admin':
            pass  # Admin sees all stadiums
        elif user.role == 'owner':
            queryset = queryset.filter(owner=user)
        else:
            queryset = queryset.filter(status=StadiumStatus.AVAILABLE)

        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                
                distance_formula = """
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(CAST(split_part(location, ',', 1) AS FLOAT))) *
                        cos(radians(CAST(split_part(location, ',', 2) AS FLOAT)) - radians(%s)) +
                        sin(radians(%s)) * sin(radians(CAST(split_part(location, ',', 1) AS FLOAT)))
                    )
                """
                queryset = queryset.annotate(
                    distance=RawSQL(
                        distance_formula,
                        params=[lat, lng, lat]
                    )
                ).order_by('distance')
            except (ValueError, TypeError):
                pass

        return queryset

    @action(detail=True, methods=['post'])
    def upload_photos(self, request, pk=None):
        stadium = self.get_object()
        
        if 'photos' not in request.FILES:
            return Response(
                {'error': 'No photos provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        photos = request.FILES.getlist('photos')
        photo_objects = []
        
        for photo in photos:
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
        stadium = self.get_object()
        photo_id = request.data.get('photo_id')

        try:
            photo = StadiumPhoto.objects.get(id=photo_id, stadium=stadium)
            
            stadium.photos.update(is_main=False)
            
            photo.is_main = True
            photo.save()

            return Response({'status': 'Main photo set successfully'})
        except StadiumPhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )