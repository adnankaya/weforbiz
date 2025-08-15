# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput

# internals
from .models import Post, PostImage


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["title"].label = _("Title")
        self.fields["body"].label = _("Description")
        self.fields["category"].label = _("Category")

    class Meta:
        model = Post
        fields = ("title", "body", "category")


class PostSearchForm(forms.Form):
    query = forms.CharField()
