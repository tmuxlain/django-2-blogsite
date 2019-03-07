from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from taggit.models import Tag

from blog.forms import CommentForm, EmailPostForm, SearchForm
from blog.models import Post
from blog.utils import get_similar_posts


# Create your views here.


def list_posts(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver the last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request,
                  'post/list.html',
                  {
                      'posts': posts,
                      'page': page,
                      'tag': tag,
                  })


# class PostListView(ListView):
#     queryset = Post.published.all()  # could have used model = Post, django will then use Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = CommentForm(data=request.POST or None)

    if request.method == 'POST':
        if comment_form.is_valid():
            new_comment = comment_form.save(post=post)

    similar_posts = get_similar_posts(post)

    return render(request,
                  'post/detail.html',
                  {
                      'post': post,
                      'comments': comments,
                      'new_comment': new_comment,
                      'comment_form': comment_form,
                      'similar_posts': similar_posts,
                  })


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id,
                             status='published')
    sent = False
    form = EmailPostForm(data=request.POST or None)

    if request.method == 'POST':
        # form was submitted
        if form.is_valid():
            cd = form.cleaned_data
            # send email
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = '{} ({}) recommends you read "{}"'.format(
                cd['name'], cd['email'], post.title
            )
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(
                post.title, post_url, cd['name'], cd['comments']
            )
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True

    return render(request, 'post/share.html',
                  {
                      'post': post,
                      'form': form,
                      'sent': sent
                  })


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body'),
            search_query = SearchQuery(query)
            # results = Post.objects.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(search=query).order_by('-rank')
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query)
            ).filter(similarity__gt=0.3).order_by('-similarity')

    return render(
        request,
        'post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )

