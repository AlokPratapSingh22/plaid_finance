from djoser.serializers import UserCreateSerializer as DefaultUserCreateSerializer, UserSerializer as DefaultUserSerializer


class UserCreateSerializer(DefaultUserCreateSerializer):
    """Added fiels in the default user_creation serializer"""
    class Meta(DefaultUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']


class UserSerializer(DefaultUserSerializer):
    """Added fiels in the default user serializer"""
    class Meta(DefaultUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
