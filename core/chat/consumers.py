from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
from messager.models import GroupMessages,GroupChat,SingleChat,SingleMessages
from django.contrib.auth import get_user_model
from datetime import datetime
import pytz

class ChatRoomConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name=self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_%s' % self.room_name
		self.user = self.scope["user"]
		self.auth = self.user.is_authenticated
		if self.auth and self.user.is_superuser==True:
			self.group = await sync_to_async(GroupChat.objects.get)(id=self.room_name)
			self.admin = await self.get_admin()
			if self.admin == self.user:
				await self.channel_layer.group_add(self.room_group_name,self.channel_name)
				await self.accept()
		else:
			try:
				self.user_group= await sync_to_async(self.user.groupusers_set.get)(group=self.room_name)
				if  self.auth and self.user_group:
					await self.channel_layer.group_add(self.room_group_name,self.channel_name)
					await self.accept()
					self.group=await sync_to_async(GroupChat.objects.get)(id=self.room_name)
			except:
				pass

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)

	async def receive(self,text_data):
		text_data_json =json.loads(text_data)
		message = text_data_json['message']
		username = text_data_json['username']
		obj = await self.message_save(message)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type':'chatroom_message',
				'message':message,
				'username': username,
			}
		)

	@database_sync_to_async
	def get_admin(self):
		return self.group.admin

	@database_sync_to_async
	def message_save(self,message):
		return GroupMessages.objects.new_message(self.user,self.group,message)

	async def chatroom_message(self,event):
		message = event['message']
		username = event['username']
		await self.send(text_data=json.dumps({
				'message':message,
				'username': username,

			}))

class SingleChatRoomConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name=self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_%s' % self.room_name
		self.user = self.scope["user"]
		self.auth = self.user.is_authenticated
		self.connected=0
		if self.auth:
			try:
				self.user_group= await sync_to_async(SingleChat.objects.get)(id=self.room_name)
				self.user1 = await self.get_user1()
				self.user2 = await self.get_user2()
				if  self.auth and self.user_group and (self.user1==self.user or self.user2==self.user):
					await self.channel_layer.group_add(self.room_group_name,self.channel_name)
					await self.accept()
					self.connected=1
					await self.reset_user_unread()
					await self.set_online()
			except:
				pass
	async def disconnect(self, close_code):
		if self.connected==1:
			if self.user==self.user1:
				await self.update_user1_last_seen()
			elif self.user==self.user2:
				await self.update_user2_last_seen()
			await self.reset_online()
		await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)

	async def receive(self,text_data):
		text_data_json =json.loads(text_data)
		message = text_data_json['message']
		username = text_data_json['username']
		if self.user==self.user1:
			await self.update_user2_unread()
		elif self.user==self.user2:
			await self.update_user1_unread()
		obj = await self.message_save(message)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type':'chatroom_message',
				'message':message,
				'username': username,
			}
		)
		


	@database_sync_to_async
	def message_save(self,message):
		return SingleMessages.objects.new_message(self.user,self.user_group,message)

	@database_sync_to_async
	def get_user1(self):
		return self.user_group.user1

	@database_sync_to_async
	def get_user2(self):
		return self.user_group.user2

	@database_sync_to_async
	def update_user1_last_seen(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		self.user_group.user1_last_seen=datetime.utcnow()
		self.user_group.save()
		return self.user_group.user1_last_seen

	@database_sync_to_async
	def update_user2_last_seen(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		self.user_group.user2_last_seen=datetime.utcnow()
		self.user_group.save()
		return self.user_group.user2_last_seen

	@database_sync_to_async
	def update_user1_unread(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		if self.user_group.user1_online==0 and self.user_group.user1_last_seen.replace(tzinfo=None)<datetime.utcnow():
			self.user_group.user1_unread+=1
			self.user_group.save()

	@database_sync_to_async
	def update_user2_unread(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		if self.user_group.user2_online==0 and self.user_group.user2_last_seen.replace(tzinfo=None)<datetime.utcnow():
			self.user_group.user2_unread+=1
			self.user_group.save()

	@database_sync_to_async
	def reset_user_unread(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		if self.user==self.user1:
			self.user_group.user1_unread=0
			self.user_group.save()
		elif self.user==self.user2:
			self.user_group.user2_unread=0
			self.user_group.save()

	@database_sync_to_async
	def set_online(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		if self.user==self.user1:
			self.user_group.user1_online=1
			self.user_group.save()
		elif self.user==self.user2:
			self.user_group.user2_online=1
			self.user_group.save()

	@database_sync_to_async
	def reset_online(self):
		self.user_group = SingleChat.objects.get(id=self.room_name)
		if self.user==self.user1:
			self.user_group.user1_online=0
			self.user_group.save()
		elif self.user==self.user2:
			self.user_group.user2_online=0
			self.user_group.save()

	async def chatroom_message(self,event):
		message = event['message']
		username = event['username']
		await self.send(text_data=json.dumps({
				'message':message,
				'username': username,

			}))