from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
