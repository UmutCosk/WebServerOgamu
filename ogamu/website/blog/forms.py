from django import forms

from website.blog.models import BlogPost


class PostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ['message']
        labels = {
            'message': 'Deine Nachricht'
        }