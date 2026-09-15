from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def chat_room(request, user_id=None):
    target = get_object_or_404(User, id=user_id) if user_id else None
    return render(request, 'chat/chat_room.html', {'target': target})
