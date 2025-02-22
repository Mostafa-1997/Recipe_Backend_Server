from django.contrib.auth import (
    get_user_model,
    authenticate
)
# from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):

    login = serializers.CharField(
        label="Username/Email",
        write_only=True
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if login and password:

            if '@' in login:
                login = login.lower()

            user = authenticate(
                request=self.context.get('request'),
                email=login,
                password=password
                )

            if user is None and '@' not in login:
                user = authenticate(
                    request=self.context.get('request'),
                    username=login,
                    password=password
                    )

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "Username or Email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
