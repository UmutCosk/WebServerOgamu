from django.shortcuts import render
from .models import BlogPost
from .forms import PostForm

def index(request):
    return render(request, 'blog/base.html')


def timeline_view(request):
    post_form = PostForm()
    if request.method == "POST":
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
    posts = BlogPost.objects.filter(user=request.user)
    return render(request, 'blog/timeline.html', {'posts:': posts, 'post_form': post_form} )