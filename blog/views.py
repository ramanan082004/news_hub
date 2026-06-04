import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, CommentLike, UserProfile, BreakingNews
from .forms import CommentForm


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def index(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(title__icontains=query) if query else Post.objects.all()
    breaking_posts = Post.objects.order_by('-created_at')[:10]
    breaking_news = BreakingNews.objects.order_by('-id')[:10]

    try:
        ip = get_client_ip(request)
        if ip == '127.0.0.1' or ip == '::1':
            city = 'Chennai'
        else:
            try:
                geo = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5).json()
                city = geo.get('city', 'Chennai')
            except:
                city = 'Chennai'

        api_key = "e3547251fd656762b57cae92ed03c564"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        weather = requests.get(url, timeout=5).json()

        if weather.get('cod') != 200:
            weather = None
    except:
        weather = None

    return render(request, 'blog/index.html', {
        'posts': posts,
        'query': query,
        'breaking_posts': breaking_posts,
        'breaking_news': breaking_news,
        'weather': weather,
    })


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save()
    if post.category:
        latest_posts = Post.objects.filter(
            category=post.category
        ).exclude(id=post.id)[:20]
    else:
        latest_posts = Post.objects.exclude(id=post.id)[:5]
    comments = post.comments.all().order_by('-created_at')
    liked_ids = []
    if request.user.is_authenticated:
        liked_ids = list(CommentLike.objects.filter(
            user=request.user,
            comment__post=post
        ).values_list('comment_id', flat=True))
    form = CommentForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('blog:login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('blog:detail', pk=pk)

    post_url = 'https://news-hub-jjaf.onrender.com/' + reverse('blog:detail', kwargs={'pk': pk})

    return render(request, 'blog/detail.html', {
        'post': post,
        'latest_posts': latest_posts,
        'comments': comments,
        'form': form,
        'current_url': post_url,
        'liked_ids': liked_ids,
    })





def old_url_redirect(request):
    return redirect(reverse('blog:new_page_url'))


def new_url_view(request):
    return HttpResponse("this the new URL")


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})


def some_view(request):
    return render(request, 'blog/post_home.html')


def copy_post(request, pk):
    original = get_object_or_404(Post, pk=pk)
    Post.objects.create(
        title="Copy of " + original.title,
        content=original.content,
        category=original.category,
    )
    return redirect('blog:detail', pk=pk)


def download_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = f"{post.title}\n\n{post.content}"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{post.title}.txt"'
    return response


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog:index')
        else:
            return render(request, 'blog/login.html', {'error': 'Invalid credentials'})
    return render(request, 'blog/login.html')


def logout_view(request):
    logout(request)
    return redirect('blog:index')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total': post.total_likes()})


@login_required(login_url='/login/')
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    print("Method:", request.method)
    print("FILES:", request.FILES)
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile.profile_image = request.FILES['profile_image']
        profile.save()
        return redirect('blog:profile')
    return render(request, 'blog/profile.html', {'profile': profile})


def like_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('blog:login')
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()
    return redirect('blog:detail', pk=comment.post.pk)