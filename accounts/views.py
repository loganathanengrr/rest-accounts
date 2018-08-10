from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework import status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.views import (
	ObtainJSONWebToken,
	)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import AnonPermissionOnly
from .utils import *
from .conf import settings
from .signals import (
	user_registered,
	user_activated
	)

UserModel = get_user_model()


class LoginAPIView(ObtainJSONWebToken):
	authentication_classes = (JSONWebTokenAuthentication,)
	permission_classes =(AnonPermissionOnly,)


class CreateUserView(generics.CreateAPIView):
	permission_classes =(AnonPermissionOnly,)
	queryset           = UserModel._default_manager.all()
	serializer_class   = settings.SERIALIZERS.user_create

	def perform_create(self,serializer):
		user = serializer.save()
		user_registered.send(
			sender=self.__class__, user=user, request=self.request
			)
		if settings.SEND_ACTIVATION_EMAIL:
			self.send_activation_email(user)

	def send_activation_email(self,user):
		context = {'user': user}
		to = [get_user_email(user)]
		settings.EMAIL.activation(self.request, context).send(to)


class PasswordChangeView(generics.GenericAPIView):
	permission_classes = (IsAuthenticated,)

	def get_serializer_class(self):
		return settings.SERIALIZERS.password_change

	def post(self, request,*args,**kwargs):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			new_password = serializer.data.get('new_password')
			self.request.user.set_password(new_password)
			self.request.user.save()
			return Response(
				{settings.MESSAGE.password_change},
				status=status.HTTP_204_NO_CONTENT
				)
		return Response(
			serializer.errors,status=status.HTTP_400_BAD_REQUEST
			)
class PasswordResetView(generics.GenericAPIView):
    permission_classes = (AnonPermissionOnly,)
    serializer_class =  settings.SERIALIZERS.password_reset

    _users = None
    def post(self, request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)

    def _action(self, serializer):
        for user in self.get_users(serializer.data['email']):
            self.send_password_reset_email(user)
        return Response(settings.MESSAGE.password_reset,status=status.HTTP_204_NO_CONTENT)

    def get_users(self, email):
        if self._users is None:
            email_field_name = get_user_email_field_name(UserModel)
            users = UserModel._default_manager.filter(**{
                email_field_name + '__iexact': email
            })
            self._users = [
                u for u in users if u.is_active and u.has_usable_password()
            ]
        return self._users

    def send_password_reset_email(self, user):
        context = {'user': user}
        to = [get_user_email(user)]
        settings.EMAIL.password_reset(self.request, context).send(to)

class PasswordResetConfirmView(generics.GenericAPIView):
	permission_classes = (AnonPermissionOnly,)
	serializer_class =  settings.SERIALIZERS.password_reset_confirm
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(
			data=request.data,
			context={
				'uidb64': kwargs['uidb64'],
				'token': kwargs['token']
				})
		if serializer.is_valid(raise_exception=True):
			new_password = serializer.validated_data.get('new_password')
			user = serializer.user
			user.set_password(new_password)
			user.save()
			return Response(settings.MESSAGE.password_reset_confirm, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailActivationView(APIView):
	permission_classes = (AnonPermissionOnly,)
	token_generator = default_token_generator
	def get(self,request,*args,**kwargs):
		uidb64   =kwargs.get('uidb64')
		token =kwargs.get('token')
		uid   = decode_user_id(uidb64)
		self.user = self.get_user(uid)
		if self.user is not None and self.token_generator.check_token(self.user,token):
			self.user.is_active=True
			self.user.save()
			user_activated.send(
				sender=self.__class__, user=self.user, request=request
				)
			return Response(settings.MESSAGE.activation,
				status=status.HTTP_200_OK
				)
		return Response(settings.MESSAGE.activation_fail)

	def get_user(self, uid):
		try:
			user = UserModel._default_manager.get(pk=uid)
		except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
			user = None
		return user

class UserView(generics.RetrieveAPIView):
	permission_classes = (IsAuthenticated,)
	serializer_class  = settings.SERIALIZERS.user

	def get(self,*args,**kwargs):
		instance = self.get_object()
		serializer= self.serializer_class(instance)
		return Response(serializer.data)
	
	def get_object(self):
		return self.request.user

class UserNameChangeView(generics.GenericAPIView):
	permission_classes = (IsAuthenticated,)

	def get_serializer_class(self):
		return  settings.SERIALIZERS.username_change

	def post(self,request,*args,**kwargs):
		serializer= self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		username =serializer.validated_data.get('username')
		user=self.request.user
		setattr(user, UserModel.USERNAME_FIELD, username)
		if settings.SEND_ACTIVATION_EMAIL:
			user.is_active=False
			self.send_activation_email(user)
		user.save()
		return Response(settings.MESSAGE.username_change)

	def send_activation_email(self,user):
		context = {'user': user}
		to = [get_user_email(user)]
		settings.EMAIL.activation(self.request, context).send(to)
		


