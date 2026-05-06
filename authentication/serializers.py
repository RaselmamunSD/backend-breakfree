from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "full_name", "phone", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "avatar",
            "is_verified",
            "is_staff",
        )
        read_only_fields = ("id", "is_verified", "is_staff")


class FirebaseLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    provider = serializers.ChoiceField(
        choices=("google.com", "apple.com"),
        required=False,
    )


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(regex=r"^\d{5}$", max_length=5, min_length=5)


class SignupCompleteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6)
    otp = serializers.RegexField(regex=r"^\d{5}$", max_length=5, min_length=5, write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "full_name", "phone", "password", "otp")
        read_only_fields = ("id",)
        extra_kwargs = {
            "username": {"required": True},
            "full_name": {"required": False},
            "phone": {"required": False},
        }


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(regex=r"^\d{5}$", max_length=5, min_length=5)
    new_password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
