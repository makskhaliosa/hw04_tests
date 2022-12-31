from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render, get_object_or_404,
    redirect
)

from .models import Post, Group, User
from .forms import PostForm
from core.utils import pagination

# Количество выводимых записей
NUMBER_OF_ITEMS = 10
POST_FIRST_ITEMS = 30


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = pagination(request, post_list, NUMBER_OF_ITEMS)
    context = {
        'post_list': post_list,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(request, post_list, NUMBER_OF_ITEMS)
    context = {
        'group': group,
        'post_list': post_list,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = pagination(request, post_list, NUMBER_OF_ITEMS)
    context = {
        'author': author,
        'post_list': post_list,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_list = post.author.posts.all()
    text_in_title = post.text[:POST_FIRST_ITEMS]
    context = {
        'post': post,
        'post_list': post_list,
        'text_in_title': text_in_title,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template_name = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', request.user)
        return render(request, template_name, {'form': form})
    form = PostForm()
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    template_name = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        instance=post
    )
    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, template_name, context)
