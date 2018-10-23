from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from blog.forms import CommentForm, EmailPostForm
from blog.models import Comment, Post


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
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = CommentForm(data=request.POST or None)

    if request.method == 'POST':
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # assign current post to comment before saving to db
            new_comment.post = post
            new_comment.save()

    return render(request,
                  'post/detail.html',
                  {
                      'post': post,
                      'comments': comments,
                      'new_comment': new_comment,
                      'comment_form': comment_form,
                  })


def post_share(request, post_id):
    # Retrieve post by id
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
