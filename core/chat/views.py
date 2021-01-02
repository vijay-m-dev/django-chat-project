from django.shortcuts import render,redirect
from messager.models import GroupMessages,GroupChat,SingleChat,SingleMessages
from django.contrib.auth.decorators import login_required
from account.decorators import allowed_users
from django.db.models import Q
from django.contrib.auth import get_user_model
# Create your views here.

@login_required()
@allowed_users(allowed_roles=['chatters'])
def room(request, room_name):
	user=request.user
	try:
		group=GroupChat.objects.filter(id=room_name,groupusers__users=user)[0]
	except:
		return redirect('home')
	if group:
		admin=group.admin.username
		chats=GroupMessages.objects.get_exists_message(group,user.id)
		context={'room_name':room_name, 'chats':chats,"admin":admin}
		return render(request, 'chat/chatroom.html', context)
	return redirect('home')

@login_required()
@allowed_users(allowed_roles=['chatters','admins'])
def singleChatRoom(request, person_id):
	user=request.user
	User=get_user_model()
	person=User.objects.get(id=person_id)
	if person:
		single_chat_room=SingleChat.objects.filter((Q(user1=user)&Q(user2=person))|(Q(user1=person)&Q(user2=user)))
		if single_chat_room:
			room_name=single_chat_room[0].id
			chats=SingleMessages.objects.get_exists_message(room=room_name)
		else:
			obj=SingleChat.create(user1=user,user2=person)
			room_name=obj.pk
			chats=[]
		context={'room_name':room_name, 'chats':chats, 'person':person.username}
		return render(request, 'chat/singlechatroom.html', context)
	else:
		return redirect('home')