from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate,login
from django.contrib.auth import get_user_model
from django.conf import settings as django_settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions
from rest_framework import serializers,exceptions
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
from .conf import settings
from .utils import *

UserModel = get_user_model()
user_name_field = 'new_' + UserModel.USERNAME_FIELD

class UserCreateSerializer(serializers.ModelSerializer):
	password = serializers.CharField(
		style={'input_type': 'password'},
		min_length=6, 
		max_length=100,
		write_only=True
		)
	password1 = serializers.CharField(
		style={'input_type': 'password'},
		min_length=6,
		max_length=100,
		write_only=True
		)	
	
	class Meta:
		model = UserModel
		fields = tuple(UserModel.REQUIRED_FIELDS) + (
			UserModel.USERNAME_FIELD, UserModel._meta.pk.name, 'password','password1'
			)
	def validate(self,attrs):
		user = self.instance
		password = attrs.get('password')
		password1 = attrs.get('password1')
		try:
			validate_password(password, user)
		except django_exceptions.ValidationError as e:
			raise serializers.ValidationError({'password': list(e.messages)})
		if password != password1:
			raise serializers.ValidationError('password mismatch please check your password')
		return attrs       

	def create(self, validated_data):
		try:
			user = self.perform_create(validated_data)
		except IntegrityError:
			self.fail('cannot_create_user')
		return user
	
	def perform_create(self, validated_data):
		password1=validated_data.pop('password1')
		with transaction.atomic():
			user = UserModel._default_manager.create_user(**validated_data)
			if settings.SEND_ACTIVATION_EMAIL:
				user.is_active = False
				user.save(update_fields=['is_active'])
		return user

class PasswordChangeSerializer(serializers.Serializer):
	current_password = serializers.CharField(
		style={'input_type': 'password'},
		)
	new_password  = serializers.CharField(
		style={'input_type': 'password'},
		min_length=6, max_length=100,
		)
	confirm_new_password =  serializers.CharField(
		style={'input_type': 'password'},
		min_length=6, max_length=100,
		)
	def validate_new_password(self, value):
		user = self.context['request'].user or self.user
		assert user is not None
		try:
			validate_password(value, user)
		except django_exceptions.ValidationError as e:
			raise serializers.ValidationError({
				'new_password': list(e.messages)
				})
		return value

	def validate(self, attrs):
		if attrs['new_password'] == attrs['confirm_new_password']:
			return attrs
		else:
		   raise serializers.ValidationError('password is mismatch,please try again ')
	
	def validate_current_password(self, value):
		is_password_valid = self.context['request'].user.check_password(value)
		if is_password_valid:
		    return value
		else:
		    raise serializers.ValidationError('type valid current_password')

class ResetPasswordSerializer(serializers.Serializer):

	email = serializers.EmailField(required = True)

	def validate_email(self, value):
		try:
			user=UserModel._default_manager.get(email=value)
		except:
			raise serializers.validationError('email id is not found,check your email id')
		return value

class ResetPasswordConfirmSerializer(serializers.Serializer):
	token_generator = default_token_generator
	new_password = serializers.CharField(style={'input_type': 'password'},write_only=True)
	new_password_2 = serializers.CharField(style={'input_type': 'password'},write_only=True)

	def __init__(self, *args, **kwargs):
		context = kwargs['context']
		uidb64, token = context.get('uidb64'), context.get('token')
		if uidb64 and token:
			uid =decode_user_id(uidb64)
			self.user = self.get_user(uid)
			self.valid_attempt = self.token_generator.check_token(self.user, token)
		super(ResetPasswordConfirmSerializer, self).__init__(*args, **kwargs)

	def get_user(self, uid):
		try:
			user = UserModel._default_manager.get(pk=uid)
		except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
			user = None
		return user
	def validate_new_password_2(self, value):
		data = self.get_initial()
		new_password = data.get('new_password')
		if new_password != value:
			raise serializers.ValidationError("Passwords doesn't match.please try again")
		return value
	def validate(self, data):
		if not self.valid_attempt:
			raise serializers.ValidationError("Operation not allowed.")
		return data

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = tuple(UserModel.REQUIRED_FIELDS) + (
			UserModel.USERNAME_FIELD, UserModel._meta.pk.name
			)

class ChangeUserNameSerializer(serializers.Serializer):
	current_password          = serializers.CharField(style={'input_type': 'password'},write_only=True)
	username                  = serializers.CharField()
	def validate_current_password(self, value):
		is_password_valid = self.context['request'].user.check_password(value)
		if is_password_valid:
			return value
		else:
		    raise serializers.ValidationError('type valid current_password')

