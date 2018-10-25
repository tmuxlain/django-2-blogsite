from django.db.models import Count

from blog.models import Post


def get_similar_posts(post: Post):
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = (Post.published
                     .filter(tags__in=post_tags_ids)
                     .exclude(id=post.id)
                     .annotate(same_tags=Count('tags'))
                     .order_by('-same_tags', '-publish')[:4])
    return similar_posts
