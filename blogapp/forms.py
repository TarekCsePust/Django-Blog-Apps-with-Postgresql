from django import forms

from .models import article,author,comment,category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class CreateForm(forms.ModelForm):

    class Meta:
        model = article
        fields = [

            'title',
            'body',
            'image',
            'category'
        ]

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields=[
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2'
        ]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = author
        fields=[
            'profile_picture',
            'details',

        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = comment
        fields=[
            'name',
            'email',
            'post_comment'

        ]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields=[
            'name'

        ]