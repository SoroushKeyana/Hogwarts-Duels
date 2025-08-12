from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from .models import UserProfile, HOUSES, Follow
from django.db import IntegrityError
from django.http import JsonResponse

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        house = request.POST.get('house')

        if not all([username, password, password_confirm, email, house]):
            error = "All fields are required."

        elif password != password_confirm:
            error = "Passwords do not match."
        
        else:
            try:
                user = User.objects.create_user(username=username, password=password, email=email)
                UserProfile.objects.create(user=user, house=house)
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                error = "Username already exists."
    
    return render(request, 'register.html', {'error': error, 'houses': HOUSES})
    
def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid username or password."
    return render(request, 'login.html', {'error': error, 'houses': HOUSES})

@login_required
def dashboard_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'dashboard.html', {'profile': profile})   


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get(user=user)
    is_following = Follow.objects.filter(follower=request.user, following=user).exists() if request.user.is_authenticated else False
    following_qs = Follow.objects.filter(follower=user).select_related('following')
    following_users = [f.following for f in following_qs]
    return render(request, 'profile.html', {'profile': profile, 'is_following': is_following, 'following_users': following_users})

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else []
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

    results = [
        {
            'username': u.username,
            'id': u.id,
            'is_following': u.id in following_ids
        }
        for u in users
    ]
    return JsonResponse(results, safe=False)


@login_required
@require_POST
def follow_user(request, user_id):
    target = User.objects.get(id=user_id)
    if target != request.user:
        Follow.objects.get_or_create(follower=request.user, following=target)
    return JsonResponse({'status': 'followed'})

@login_required
@require_POST
def unfollow_user(request, user_id):
    Follow.objects.filter(follower=request.user, following_id=user_id).delete()
    return JsonResponse({'status': 'unfollowed'})

@login_required
def user_follows(request, user_id):
    user = get_object_or_404(User, id=user_id)
    follows = Follow.objects.filter(follower=user).select_related('following')
    return render(request, 'core/follows.html', {'follows': follows, 'profile_user': user})
