from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Manager, Employee, Skill, UserDetail

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'role')
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'email', 'role']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class EmployeeDetailSerializer(serializers.ModelSerializer):
    user = EmployeeSerializer()
    skillset = SkillSerializer(many=True)
    get_pic = serializers.SerializerMethodField()

    class Meta:
        model = UserDetail
        fields = ['id', 'first_name', 'last_name', 'address', 'skillset', 'user', 'gender', 'phone', 'dob', 'get_pic']

    def get_get_pic(self, obj):
        return obj.get_pic()

class AddUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['id', 'first_name', 'last_name', 'address', 'skillset', 'user', 'pic', 'gender', 'phone', 'dob']

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'email', 'role']