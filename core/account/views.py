from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from .forms import UserForm
from .decorators import unauthenticated_user, login_redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@unauthenticated_user
def registerPage(request):
	form=UserForm()
	if request.method == 'POST':
		form=UserForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('login')
	context={'form': form }
	return render(request,'account/register.html', context)

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username_or_email=request.POST.get('username_or_email')
		password=request.POST.get('password')
		user = authenticate(request, username=username_or_email, password=password)
		if user is not None:
			login(request, user)
			return login_redirect(request)
		user = authenticate(request, email=username_or_email, password=password)
		if user is not None:
			login(request, user)
			return login_redirect(request)
	context = {}
	return render(request, 'account/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

