from django.shortcuts import redirect, render
from blog_app.forms import PostForm
from blog_app.models import Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
def post_list(request):
    # posts = Post.objects.all()
    posts = Post.objects.filter(published_at__isnull=False)
    return render(request, 'post_list.html', {"posts": posts},)

def post_detail(request, pk):
    post = Post.objects.get(pk=pk, published_at__isnull=False)  
    return render(request, 'post_detail.html', {"post": post},)

@login_required
def draft_list(request):
    posts = Post.objects.filter(published_at__isnull=True)
    return render(request, 'draft_list.html', {"posts": posts},)

@login_required
def draft_detail(request,pk):
    post = Post.objects.get(pk=pk, published_at__isnull=True)
    return render(request, 'draft_detail.html', {"post": post},)

@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('post-list')

@login_required
def draft_publish(request, pk):
    post = Post.objects.get(pk=pk, published_at__isnull=True)
    post.published_at = timezone.now()
    post.save()
    return redirect('post-detail', pk)

@login_required
def post_create(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  #logged in user will be author
            post.save()
            return redirect("draft-detail",pk=post.pk)

    return render(request, "post_create.html", {"form":form},)    

@login_required
def post_update(request, pk):
    post = Post.objects.get(pk=pk)
    form = PostForm(instance = post)
    if request.method == 'POST':
        form = PostForm(request.POST,instance = post)
        if form.is_valid():
            post = form.save()
            if post.published_at:
                return redirect("post-detail",pk=post.pk)
            else:
                return redirect("draft-detail", post.pk)
    
    return render(request, "post_create.html",{"form":form})
