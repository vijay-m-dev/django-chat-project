from django.db import models
from django.contrib.auth import get_user_model
import datetime

# Create your models here.
class GroupChat(models.Model):
	name = models.CharField(max_length=200)
	admin=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)

class GroupUsers(models.Model):
	users=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
	group=models.ForeignKey(GroupChat,on_delete=models.CASCADE)
	date=models.DateTimeField(auto_now=True)


class GroupMessageManager(models.Manager):
    def new_message(self,user,group,message):
    	obj=self.model(group=group,from_user=user,message=message)
    	obj.save()
    	return obj

    def get_exists_message(self,group,id1):
    	date=GroupUsers.objects.get(users=id1,group=group).date
    	chats= self.filter(group=group,date__gte=date).all()
    	return chats

class GroupMessages(models.Model):
	group = models.ForeignKey(GroupChat,on_delete=models.CASCADE)
	from_user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
	message =  models.CharField(max_length=1000,default='')
	date=models.DateTimeField(auto_now=True)
	objects=GroupMessageManager()

class SingleChat(models.Model):
	user1 = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name='user1')
	user2 = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name='user2')
	user1_online=models.IntegerField(default=0)
	user2_online=models.IntegerField(default=0)
	user1_last_seen=models.DateTimeField(default=datetime.datetime.utcnow)
	user2_last_seen=models.DateTimeField(default=datetime.datetime.utcnow)
	user1_unread=models.IntegerField(default=0)
	user2_unread=models.IntegerField(default=0)

	@classmethod
	def create(cls,user1,user2):
		obj=cls(user1=user1,user2=user2)
		obj.save()
		return obj

class SingleMessageManager(models.Manager):
    def new_message(self,user,room,message):
    	obj=self.model(room=room,from_user=user,message=message)
    	obj.save()
    	return obj

    def get_exists_message(self,room):
    	chats= self.filter(room=room).all()
    	return chats

class SingleMessages(models.Model):
	room=models.ForeignKey(SingleChat,on_delete=models.CASCADE)
	from_user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
	message =  models.CharField(max_length=1000,default='')
	date=models.DateTimeField(auto_now=True)
	objects=SingleMessageManager()
