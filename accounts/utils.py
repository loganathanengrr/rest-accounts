import datetime
from templated_mail.mail import BaseEmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils import six
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.conf import settings

def encode_user_id(_id):
    return urlsafe_base64_encode(force_bytes(_id)).decode()

def decode_user_id(_id):
    return force_text(urlsafe_base64_decode(_id))

def get_user_email(user):
    email_field_name = get_user_email_field_name(user)
    return getattr(user, email_field_name, None)

def get_user_email_field_name(user):
    try:
        return user.get_email_field_name()
    except AttributeError:
    	return settings.USER_EMAIL_FIELD_NAME


class ActivationEmail(BaseEmailMessage):
	template_name  ='activation_email.html'
	def get_context_data(self):
		context = super(ActivationEmail, self).get_context_data()
		user = context.get('user')
		context['uid']   =  encode_user_id(user.pk)
		context['token'] =  default_token_generator.make_token(user)
		context['url']   =  settings.ACTIVATION_URL.format(**context)
		return context

class PasswordResetEmail(BaseEmailMessage):
    template_name = 'password_reset.html'

    def get_context_data(self):
    	context = super(PasswordResetEmail, self).get_context_data()
    	user = context.get('user')
    	context['uid'] = encode_user_id(user.pk)
    	context['token'] = default_token_generator.make_token(user)
    	context['url'] = settings.PASSWORD_RESET_URL.format(**context)
    	return context

