from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from .models import UserProfile, HOUSES, Follow, Duel
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.db import IntegrityError
import random


SPELLS = {
    "Stupefy": 3,
    "Expelliarmus": 2,
    "Sectumsempra": 4,
}

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
def start_duel(request, user_id=None):
    user = request.user

    if user_id:
        opponent = get_object_or_404(User, id=user_id)
        if opponent == user:
            return render(request, "dashboard.html", {"error": "You cannot challenge yourself."})
    else:
        # pick a random opponent should not be the same as the user
        opponents = User.objects.exclude(id=user.id)
        if not opponents.exists():
            return render(request, "dashboard.html", {"error": "No opponents available for a random duel."})
        opponent = random.choice(opponents)

    duel = Duel.objects.create(
        challenger=user,
        opponent=opponent,
        current_turn=user,
        status='pending'
    )

    return redirect("wait_for_opponent", duel_id=duel.id)


@login_required
def wait_for_opponent(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id, challenger=request.user)
    if duel.status == 'accepted':
        return redirect('duel_view', duel_id=duel.id)
    elif duel.status == 'declined':
        return render(request, 'duel_declined.html', {'duel': duel})
    return render(request, 'wait_for_opponent.html', {'duel': duel})


@login_required
def duel_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    if duel.status == 'pending':
        if duel.challenger == request.user:
            return redirect('wait_for_opponent', duel_id=duel.id)
        else:
            return render(request, 'accept_duel.html', {'duel': duel})
    elif duel.status in ['declined', 'finished']:
        return render(request, 'duel_results.html', {'duel': duel})

    return render(request, "duel.html", {"duel": duel})


@login_required
def attack(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    # Check it's the user's turn
    if duel.current_turn != request.user or duel.status != 'accepted':
        return HttpResponseForbidden("Not your turn or duel not active.")

    # Get spell from POST
    spell = request.POST.get("spell")
    if spell not in SPELLS:
        return HttpResponseForbidden("Invalid spell.")

    damage = SPELLS[spell]

    # Apply damage
    if duel.challenger == request.user:
        duel.opponent_health -= damage
        if duel.opponent_health <= 0:
            duel.opponent_health = 0
            duel.status = 'finished'
            duel.winner = request.user
    else:
        duel.challenger_health -= damage
        if duel.challenger_health <= 0:
            duel.challenger_health = 0
            duel.status = 'finished'
            duel.winner = request.user

    # Switch turn (if duel not over)
    if duel.status == 'accepted':
        duel.current_turn = duel.opponent if duel.challenger == request.user else duel.challenger

    duel.save()
    return redirect("duel_view", duel_id=duel.id)


@login_required
def duel_status(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    
    data = {
        "current_turn": duel.current_turn.username if duel.current_turn else None,
        "challenger_health": duel.challenger_health,
        "opponent_health": duel.opponent_health,
        "status": duel.status,
        "winner": duel.winner.username if duel.winner else None
    }
    return JsonResponse(data)


@login_required
def my_duels(request):
    duels = Duel.objects.filter(
        Q(challenger=request.user) | Q(opponent=request.user)
    ).exclude(status='pending')

    return render(request, "my_duels.html", {"duels": duels})


@login_required
def get_duel_invitations(request):
    invitations = Duel.objects.filter(opponent=request.user, status='pending')
    data = [{'id': inv.id, 'challenger': inv.challenger.username} for inv in invitations]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def accept_duel(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id, opponent=request.user)
    duel.status = 'accepted'
    duel.save()
    return redirect('duel_view', duel_id=duel.id)


@login_required
@require_POST
def decline_duel(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id, opponent=request.user)
    duel.status = 'declined'
    duel.save()
    return redirect('dashboard')