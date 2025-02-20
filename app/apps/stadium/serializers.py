from rest_framework import serializers
from .models import Stadium, StadiumPhoto


class StadiumPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumPhoto
        fields = ['id', 'image', 'is_main']


class StadiumSerializer(serializers.ModelSerializer):
    photos = StadiumPhotoSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    price_formatted = serializers.CharField(source='get_price_formatted', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)
    distance_formatted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Stadium
        fields = [
            'id', 'name', 'location', 'address', 'contact',
            'price_per_hour', 'price_formatted', 'status',
            'owner', 'owner_name', 'photos', 'created_at',
            'distance', 'distance_formatted'
        ]
        read_only_fields = ['owner', 'created_at']

    def get_distance_formatted(self, obj):
        """Format distance in kilometers or meters"""
        if not hasattr(obj, 'distance'):
            return None
            
        distance = obj.distance
        if distance < 1:
            return f"{int(distance * 1000)}m"
        return f"{round(distance, 1)}km"

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = user
        return super().create(validated_data)
