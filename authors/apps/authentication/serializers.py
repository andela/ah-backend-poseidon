import os

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..profiles.serializers import ProfileSerializer
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    regex = (r'^[a-zA-Z0-9]+$')
    password = serializers.RegexField(
        regex,
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            "min_length":
            "Password should not be less than {min_length} characters.",
            "invalid":
            "Password should be alphanuemric (a-z,A_Z,0-9)."
        })

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'token']
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "invalid":
                    "Please enter a valid email in the format xxxx@xxx.xxx"
                }
            }
        }

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        username = data.get('username', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if username is None:
            raise serializers.ValidationError(
                'A username is required to log in.')

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.')

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=username, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.')

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.')

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True)

    profile = ProfileSerializer(write_only=True)

    # Get the `bio` and `image` from user's profile
    bio = serializers.CharField(source='profile.bio', read_only=True)
    image = serializers.CharField(source='profile.image', read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token', 'profile', 'bio',
                  'image')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        # Remove the profile data from the validated_data dictionary.
        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)

        # Save the profile.
        instance.profile.save()

        return instance


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False)

    def validate(self, data):
        """
        For user to reset thier password the email
        has to be validate with what is in the database
        """
        email = data.get('email', None)
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # function to check whether user is in the database
        # user email entered should be what the user user on registartion
        # else link wont be sent to the user
        # This gets the current user token which will later be used for
        # identifing user.
        # The token is passed in within the link send to the user email
        user = get_object_or_404(User, email=email)
        if email is None:
            raise serializers.ValidationError(
                'The email entered is wrong'
            )
        recipient = user.email
        subject = "Authors Heven. Reset your password"
        token = user.token
        url_param = os.environ.get(
            'FRONTEND_URL', 'http://127.0.0.1:8000/api')
        body = " Click on this link to reset your password {}{}/".format(
            url_param + '/password-reset/', token)
        send_mail(subject, body, 'from', [
                    recipient], fail_silently=False)
        return {
            'email': user,
        }
