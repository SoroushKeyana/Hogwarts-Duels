from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from .models import UserProfile, HOUSES, Follow, Duel, HousePoints
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.db import IntegrityError
import random


import random
import json


SPELL_DATA = {
    # Attack Spells
    "Stupefy": {"type": "attack", "power": 3, "counters": ["Protego", "Expelliarmus"], "description": "Stunning Spell"},
    "Expelliarmus": {"type": "attack", "power": 2, "counters": ["Protego"], "description": "Disarming Charm"},
    "Sectumsempra": {"type": "attack", "power": 4, "counters": ["Vulnera Sanentur"], "description": "Lacerating Curse"},
    "Avada Kedavra": {"type": "attack", "power": 100, "counters": [], "description": "Killing Curse (Unblockable)", "unblockable": True},
    "Confringo": {"type": "attack", "power": 3, "counters": ["Protego"], "description": "Blasting Curse"},
    "Reducto": {"type": "attack", "power": 3, "counters": ["Protego"], "description": "Reductor Curse"},
    "Bombarda": {"type": "attack", "power": 4, "counters": ["Protego"], "description": "Explosive Charm"},

    # Defense Spells
    "Protego": {"type": "defense", "power": 2, "counters": ["Stupefy", "Expelliarmus", "Confringo", "Reducto", "Bombarda"], "description": "Shield Charm"},
    "Vulnera Sanentur": {"type": "defense", "power": 5, "counters": ["Sectumsempra"], "description": "Healing Charm"},
    "Rennervate": {"type": "defense", "power": 1, "counters": ["Stupefy"], "description": "Reviving Charm"},
    "Finite Incantatem": {"type": "defense", "power": 3, "counters": ["Petrificus Totalus", "Impedimenta"], "description": "General Counter-Spell"},

    # Utility/Other Spells (can have minor effects or be countered)
    "Petrificus Totalus": {"type": "utility", "power": 1, "counters": ["Finite Incantatem"], "description": "Full Body-Bind Curse"},
    "Impedimenta": {"type": "utility", "power": 1, "counters": ["Finite Incantatem"], "description": "Impediment Jinx"},
    "Lumos": {"type": "utility", "power": 0, "counters": [], "description": "Wand-Lighting Charm"},
    "Nox": {"type": "utility", "power": 0, "counters": [], "description": "Disarming Charm (Lumos Counter)"},
    "Accio": {"type": "utility", "power": 0, "counters": [], "description": "Summoning Charm"},
    "Alohomora": {"type": "utility", "power": 0, "counters": [], "description": "Unlocking Charm"},
    "Obliviate": {"type": "utility", "power": 0, "counters": [], "description": "Memory Charm"},
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
    house_points = HousePoints.objects.all().order_by('-points')
    following_qs = Follow.objects.filter(follower=request.user).select_related('following')
    following_users = [f.following for f in following_qs]
    return render(request, 'dashboard.html', {'profile': profile, 'house_points': house_points, 'following_users': following_users})   


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
        return redirect('duel_declined_info', duel_id=duel.id)
    return render(request, 'wait_for_opponent.html', {'duel': duel})


@login_required
def duel_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    if duel.status == 'pending':
        if duel.challenger == request.user:
            return redirect('wait_for_opponent', duel_id=duel.id)
        else:
            return render(request, 'accept_duel.html', {'duel': duel})
    elif duel.status == 'declined':
        return render(request, 'duel_declined.html', {'duel': duel})
    elif duel.status == 'finished':
        return render(request, 'duel_results.html', {'duel': duel})
    elif duel.status == 'cancelled':
        return redirect('duel_cancelled', duel_id=duel.id)

    print(f"Rendering duel.html for duel {duel.id} with status: {duel.status}")
    return render(request, "duel.html", {"duel": duel, "spell_data_json": json.dumps(SPELL_DATA)})


@login_required
def attack(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    if duel.current_turn != request.user or duel.status != 'accepted':
        return HttpResponseForbidden("Not your turn or duel not active.")

    spell_name = request.POST.get("spell", "").strip()
    actual_spell_name = next((key for key in SPELL_DATA if key.lower() == spell_name.lower()), None)

    if not actual_spell_name:
        return HttpResponseForbidden("Invalid spell.")

    spell_data = SPELL_DATA[actual_spell_name]
    is_defense_phase = duel.last_spell_cast is not None

    if is_defense_phase:
        # Defense phase
        attacking_spell_data = SPELL_DATA[duel.last_spell_cast]
        damage_dealt = attacking_spell_data["power"]

        if not attacking_spell_data.get("unblockable", False):
            if actual_spell_name in attacking_spell_data.get("counters", []):
                damage_dealt = 0
            elif spell_data["type"] == "defense":
                damage_dealt = max(0, damage_dealt - spell_data["power"])

        if duel.challenger == request.user:
            duel.challenger_health -= damage_dealt
        else:
            duel.opponent_health -= damage_dealt

        duel.last_defender_spell = actual_spell_name
        duel.last_spell_cast = None  # Transition to attack phase

        if duel.challenger_health <= 0 or duel.opponent_health <= 0:
            duel.status = 'finished'
            duel.winner = duel.opponent if duel.challenger_health <= 0 else duel.challenger
            
            # Finalize winner and loser stats
            winner_profile = duel.winner.userprofile
            winner_profile.wins += 1
            winner_profile.save()

            loser = duel.challenger if duel.winner == duel.opponent else duel.opponent
            loser_profile = loser.userprofile
            loser_profile.losses += 1
            loser_profile.save()

            if winner_profile.house != loser_profile.house:
                house_points, _ = HousePoints.objects.get_or_create(house=winner_profile.house)
                house_points.points += 1
                house_points.save()
        
    else:
        # Attack phase
        duel.last_spell_cast = actual_spell_name
        duel.last_defender_spell = None
        duel.current_turn = duel.opponent if duel.challenger == request.user else duel.challenger

    duel.save()
    return redirect("duel_view", duel_id=duel.id)


@login_required
def duel_status(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    
    turn_phase = 'defend' if duel.last_spell_cast else 'attack'

    data = {
        "current_turn": duel.current_turn.username if duel.current_turn else None,
        "challenger_health": duel.challenger_health,
        "opponent_health": duel.opponent_health,
        "status": duel.status,
        "winner": duel.winner.username if duel.winner else None,
        "turn_phase": turn_phase,
        "last_spell_cast": duel.last_spell_cast,
        "last_defender_spell": duel.last_defender_spell
    }
    return JsonResponse(data)


@login_required
def my_duels(request):
    duels = Duel.objects.filter(
        Q(challenger=request.user) | Q(opponent=request.user)
    ).exclude(status='pending')

    active_duels = duels.filter(status='accepted')
    ended_duels = duels.filter(status__in=['finished', 'declined', 'cancelled']).order_by('-updated_at')

    return render(request, "my_duels.html", {"active_duels": active_duels, "ended_duels": ended_duels})


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


@login_required
@require_POST
def end_duel(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    if request.user != duel.challenger and request.user != duel.opponent:
        return HttpResponseForbidden("You are not a participant in this duel.")

    duel.status = 'cancelled'
    if request.user == duel.challenger:
        duel.winner = duel.opponent
    else:
        duel.winner = duel.challenger
    duel.save()

    return redirect('my_duels')


@login_required
def duel_cancelled(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    return render(request, 'duel_cancelled.html', {'duel': duel})


@login_required
def duel_declined_info(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)
    return render(request, 'duel_declined.html', {'duel': duel})