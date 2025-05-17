# from rest_framework import viewsets
# from user.models import User
#
#
# def index(request):
#     pass
#
#     class UserViewSet(viewsets.ModelViewSet):
#         queryset = User.objects.all()
#         # serializer_class = UserSerializer
from rest_framework import viewsets
from rest_framework.views import APIView

from .serializer import ProfileSerializer

class ProfileViewSet(APIView):
    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
