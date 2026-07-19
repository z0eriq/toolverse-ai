from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "bio",
            "avatar_url",
            "locale",
            "theme",
            "public_username",
            "is_public",
            "headline",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    is_premium = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "role",
            "is_premium",
            "date_joined",
            "profile",
        )
        read_only_fields = fields

    def get_is_premium(self, obj: User) -> bool:
        sub = getattr(obj, "subscription", None)
        if sub is None:
            return False
        return bool(sub.is_active and sub.plan and sub.plan.slug != "free")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "name", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token
