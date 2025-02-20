from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import User
from .serializers import UserSerializer


class UserPagination(PageNumberPagination):
    """Pagination for admin users."""
    page_size = 10  # Number of users per page
    page_size_query_param = "page_size"
    max_page_size = 50


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user management:
    - Admin users get a paginated list of all users
    - Owner and User get only their own profile
    - Users can update their own profile
    """

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserPagination

    def list(self, request):
        user = request.user

        if user.role == "admin":
            queryset = User.objects.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = UserSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If not admin, return only the current user's details
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Allow anyone to sign up."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Get a specific user's details."""
        try:
            user = User.objects.get(pk=pk)
            # Check if user is admin or requesting their own profile
            if request.user.role == "admin" or request.user.id == user.id:
                serializer = UserSerializer(user)
                return Response(serializer.data)
            return Response(
                {"detail": "You do not have permission to view this user's details."},
                status=status.HTTP_403_FORBIDDEN
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        """Update a user's details."""
        try:
            user = User.objects.get(pk=pk)
            # Check if user is updating their own profile
            if request.user.id != user.id:
                return Response(
                    {"detail": "You can only update your own profile."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
