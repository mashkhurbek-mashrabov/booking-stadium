from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from stadium.serializers import StadiumSerializer


class BookingSerializer(serializers.ModelSerializer):
    stadium_details = StadiumSerializer(source='stadium', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'stadium', 'stadium_details', 'user', 'user_name',
            'start_time', 'end_time', 'price_per_hour', 'total_price',
            'is_cancelled', 'duration_hours', 'created_at'
        ]
        read_only_fields = ['user', 'price_per_hour', 'total_price', 'created_at']

    def get_duration_hours(self, obj):
        duration = obj.end_time - obj.start_time
        return round(duration.total_seconds() / 3600, 1)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        stadium = data.get('stadium')

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        if start_time < timezone.now():
            raise serializers.ValidationError("Cannot book time slots in the past")

        duration = end_time - start_time
        if duration.total_seconds() > 24 * 3600:
            raise serializers.ValidationError("Cannot book for more than 24 hours")

        overlapping_bookings = Booking.objects.filter(
            stadium=stadium,
            is_cancelled=False,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                "Stadium is already booked for this time slot"
            )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        stadium = validated_data['stadium']
        validated_data['price_per_hour'] = stadium.price_per_hour
        
        duration = validated_data['end_time'] - validated_data['start_time']
        hours = duration.total_seconds() / 3600
        validated_data['total_price'] = stadium.price_per_hour * hours
        
        return super().create(validated_data)
