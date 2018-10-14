from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView


from blog.models import Post


# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()  # could have used model = Post, django will then use Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'post/detail.html',
                  {
                      'post': post
                  })
