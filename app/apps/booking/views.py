from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Booking
from .serializers import BookingSerializer
from stadium.models import Stadium
from stadium.constants import StadiumStatus
from account.constants import UserRole


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Booking.objects.all()
        elif user.role == UserRole.OWNER:
            return Booking.objects.filter(stadium__owner=user)
        else:
            return Booking.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        if booking.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot cancel bookings that have already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.is_cancelled:
            return Response(
                {'error': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.is_cancelled = True
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        stadium_id = request.query_params.get('stadium_id')
        date = request.query_params.get('date')

        if not stadium_id or not date:
            return Response(
                {'error': 'Both stadium_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            stadium = Stadium.objects.get(id=stadium_id, status=StadiumStatus.AVAILABLE)
        except Stadium.DoesNotExist:
            return Response(
                {'error': 'Stadium not found or not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        bookings = Booking.objects.filter(
            stadium=stadium,
            is_cancelled=False,
            start_time__date=date,
        ).order_by('start_time')

        booked_slots = [
            {
                'start': booking.start_time.strftime('%H:%M'),
                'end': booking.end_time.strftime('%H:%M')
            }
            for booking in bookings
        ]

        return Response({
            'stadium_id': stadium_id,
            'date': date,
            'booked_slots': booked_slots
        })
