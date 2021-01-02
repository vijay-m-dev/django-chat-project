from django.contrib import admin
from .models import GroupChat,GroupMessages,GroupUsers,SingleChat,SingleMessages
# Register your models here.
admin.site.register(GroupChat)
admin.site.register(GroupMessages)
admin.site.register(GroupUsers)
admin.site.register(SingleChat)
admin.site.register(SingleMessages)