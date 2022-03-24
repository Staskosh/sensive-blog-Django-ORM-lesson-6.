from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': post.tags.all(),
        'first_tag_title': post.tags.first().title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts.count(),
    }


def index(request):
    most_popular_posts = Post.objects.popular().prefetch_related('author', 'tags')[:5].fetch_with_comments_count()
    most_fresh_posts = Post.objects.prefetch_related('author', 'tags').order_by('-published_at').annotate(
        comments_count=Count('comments'))[:5]
    most_popular_tags = Tag.objects.popular().prefetch_related('posts')[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.annotate(likes_count=Count('likes')).select_related('author')
    post = get_object_or_404(posts, slug=slug)
    post_comments = post.comments.all().select_related('author')
    related_tags = post.tags.all().prefetch_related('posts')
    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': post_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': related_tags,
    }
    most_popular_tags = Tag.objects.popular().prefetch_related('posts')[:5]
    most_popular_posts = Post.objects.popular().prefetch_related('author', 'tags')[:5].fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    most_popular_tags = Tag.objects.popular().prefetch_related(Prefetch('posts'))[:5]
    most_popular_posts = Post.objects.popular().prefetch_related('author', 'tags')[:5].fetch_with_comments_count()
    related_posts = tag.posts.all().prefetch_related('author', 'tags').annotate(comments_count=Count('comments'))[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
