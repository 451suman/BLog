from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from blog_app.forms import PostForm
from blog_app.models import Post
from django.contrib.auth.decorators import login_required  #: This mixin ensures that the user must be logged in to access the view. If a user who

# is not authenticated tries to access this view, they will be redirected to the login page.
from django.utils import timezone

from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        posts = Post.objects.filter(published_at__isnull=False).order_by(
            "-published_at"
        )  # - published_at is used for desending order
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=False)
        return queryset


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull=True).order_by(
            "-published_at"
        )
        return queryset


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "draft_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=True)
        return queryset


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("post-list")
    # success_url: This attribute defines the URL to redirect to after the Post has been successfully deleted.

    def form_valid(self, form):
        messages.success(self.request, "Post was Deleted Successfully")
        return super().form_valid(form)

# if you wuse Delete view then u have to make form to delete data

# class PostDeleteView(LoginRequiredMixin, View):
#     def get(self, request, pk):
#         post = Post.objects.get(pk=pk)
#         post.delete()
#         return redirect("post-list")


class DraftPublishView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        messages.success(request, "Post was published successfully!")
        return redirect("post-detail", pk)
    


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm
    # success_url = reverse_lazy("post-list")

    def get_success_url(self) -> str:
        return reverse_lazy("draft-detail", kwargs={"pk": self.object.pk})

    # get_success_url: This method is overridden to define the URL to which the user should be redirected after successfully creating a Post.

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_success_url(self):
        post = self.get_object()
        if post.published_at:
            return reverse_lazy("post-detail", kwargs={"pk": post.pk})
        else:
            return reverse_lazy("draft-detail", kwargs={"pk": post.pk})
