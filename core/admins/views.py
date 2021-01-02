from django.shortcuts import render, redirect
from messager.models import GroupChat,GroupUsers
from messager.forms import GroupForm
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from account.decorators import allowed_users
# Create your views here.

@login_required()
@allowed_users(allowed_roles=['admins'])
def dashboard(request):
	groups=GroupChat.objects.annotate(num_users=Count('groupusers'))
	context={'groups':groups,'admin':request.user}
	return render(request,'admins/dashboard.html', context)

@login_required()
@allowed_users(allowed_roles=['admins'])
def createGroup(request):
	if request.method == 'POST':
		form=GroupForm(request.POST)
		if form.is_valid():
			obj=form.save(commit=False)
			obj.admin=request.user
			obj.save()
			return redirect('dashboard')
		else:
			context={'form':form}
			return render(request,'admins/creategroup.html',context)
	form = GroupForm()
	context={'form':form}
	return render(request,'admins/creategroup.html', context)

@login_required()
@allowed_users(allowed_roles=['admins'])
def updateUser(request,pk):
	admin=request.user
	group=GroupChat.objects.get(pk=pk)
	if admin==group.admin:
		User=get_user_model()
		users2=User.objects.filter(is_superuser=False,groupusers__group=group).all()
		users1=User.objects.filter(is_superuser=False).exclude(pk__in=users2).all()
		context={'users1':users1,'users2':users2,'pk':pk}
		return render(request, 'admins/updateuser.html',context)
	else:
		return redirect(dashboard)

@login_required()
@allowed_users(allowed_roles=['admins'])
def confirmAddUser(request,id1,id2):
	group=GroupChat.objects.get(id=id1)
	admin=request.user
	if group.admin==admin:
		User=get_user_model()
		user=User.objects.get(id=id2)
		group_user=GroupUsers(group=group,users=user)
		group_user.save()
		return redirect(updateUser, pk=id1)
	else:
		return redirect(updateUser, pk=id1)

@login_required()
@allowed_users(allowed_roles=['admins'])
def deleteUser(request,id1,id2):
	admin=request.user
	group=GroupChat.objects.get(pk=id1)
	if group.admin==admin:
		User=get_user_model()
		user=User.objects.get(id=id2)
		group_user=GroupUsers.objects.filter(group=id1,users=id2)
		group_user.delete()
		context={'room_name':id1,'remove_user_id':id2,'remove_user_username':user.username}
		return render(request,'chat/delete_user_group.html',context)
	else:
		return redirect(updateUser,id1)

@login_required()
@allowed_users(allowed_roles=['admins','chatters'])
def viewGroup(request,id1):
	User=get_user_model()
	users=User.objects.filter(groupusers__group=id1).all()
	context={'users':users}
	return render(request, 'admins/viewgroup.html',context)

@login_required()
@allowed_users(allowed_roles=['admins'])
def deleteGroupUsers(request,id1):
	admin=request.user
	group=GroupChat.objects.get(pk=id1)
	if group.admin==admin:
		users=[]
		for obj in group.groupusers_set.all():
			users.append(obj.users.username)
			obj.delete()
		context={'users':users,'room_name':id1}
		return render(request,'chat/deletegroupusers.html',context)

@login_required()
@allowed_users(allowed_roles=['admins'])
def deleteGroup(request,id1):
	admin=request.user
	group=GroupChat.objects.get(pk=id1)
	if group.admin==admin:
		group.delete()
		return redirect(dashboard)


