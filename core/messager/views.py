from django.shortcuts import render
from .models import GroupChat,GroupUsers,SingleChat
from django.contrib.auth.decorators import login_required
from account.decorators import allowed_users
from django.contrib.auth import get_user_model
from django.db.models import Q
from datetime import datetime
import time
# Create your views here.

def conversion_utc_to_local(utc):
	now_timestamp=time.time()
	offset=datetime.fromtimestamp(now_timestamp)-datetime.utcfromtimestamp(now_timestamp)
	return utc+offset

@login_required()
@allowed_users(allowed_roles=['chatters','admins'])
def home(request):
	user=request.user
	groups=GroupChat.objects.filter(groupusers__users=user).all()
	created_chats=SingleChat.objects.filter(Q(user1=user)|Q(user2=user)).all()
	created_persons=[]
	created_persons_id=[]
	last_seen=[]
	unread=[]
	for i in created_chats:
		if i.user1==user:
			created_persons.append(i.user2)
			if(i.user2_online==0):
				last_seen.append(conversion_utc_to_local(i.user2_last_seen))
			else:
				last_seen.append("online")
			unread.append(i.user1_unread)
			created_persons_id.append(i.user2.id)
		else:
			created_persons.append(i.user1)
			if(i.user1_online==0):
				last_seen.append(conversion_utc_to_local(i.user1_last_seen))
			else:
				last_seen.append("online")
			unread.append(i.user2_unread)
			created_persons_id.append(i.user1.id)
	friends=zip(created_persons,unread,last_seen)
	Users=get_user_model()
	new_users=Users.objects.exclude(Q(id__in=created_persons_id)|Q(id=user.id))
	context={'groups':groups,'friends':friends,'new_users':new_users}
	return render(request,'messager/home.html', context)