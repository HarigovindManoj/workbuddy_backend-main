from django.contrib import admin
# from django.contrib.auth import get_user_model
from .models import Admin, Manager, Employee, UserDetail, Skill
# Register your models here.

# User = get_user_model()

admin.site.register(Admin)
admin.site.register(Manager)
admin.site.register(Employee)
admin.site.register(UserDetail)
admin.site.register(Skill)