from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from .models import User, Trip
import datetime



def index(request):
	if 'id' in request.session:
		return redirect(reverse("travels"))
	return render(request, "loginandregistration/index.html")

def register(request):
	context = { 'formdata': request.POST }
	registered = User.userManager.register(context)
	if registered[0] :									# successful registration
		user = User.objects.latest('created_at')
		request.session['id'] = user.id
		request.session['name'] = user.name
		request.session['username'] = user.username
		return redirect(reverse("travels"))
	else: 												# failed registration
		for error in registered[1]:
			messages.error(request, error)
		return redirect("/")
	return redirect(reverse("travels"))

def signin(request):
	context = { 'formdata':request.POST }
	signedin = User.userManager.signin(context)
	if signedin[0]:										# successful login
		user = User.objects.get(username=request.POST['username'])
		request.session['id'] = user.id
		request.session['name'] = user.name
		request.session['username'] = user.username
		return redirect(reverse("travels"))
	else: 												# failed login
		for error in signedin[1]:
			messages.error(request, error)
		return redirect(reverse("index"))
	return render(request, "loginandregistration/index.html")


def travels(request):
	if 'id' not in request.session:
		messages.error(request, "Please login to continue")
		return redirect("/")
	user = User.objects.get(id=request.session['id'])
	mytrips = Trip.objects.filter(users=user)
	othertrips = Trip.objects.all().exclude(users=user) 

	context = {
		'mytrips': mytrips,
		'othertrips': othertrips
	}
	return render(request, "loginandregistration/travels.html", context)

def destination(request, id):
	if 'id' not in request.session:
		messages.error(request, "Please login to continue")
		return redirect("/")
	theTrip = Trip.objects.get(id=id)
	otherusers = theTrip.users.all().exclude(username=theTrip.planner.username)
	context = {
		'destination': theTrip,
		'otherusers': otherusers
	}
	return render(request, "loginandregistration/destination.html", context)

def add(request):
	if 'id' not in request.session:
		messages.error(request, "Please login to continue")
		return redirect("/")
	if request.method =="POST":
		if 'id' not in request.session:
			return redirect("/")
		context = { 'formdata': request.POST, 'plannerid': request.session['id'] }
		added = Trip.tripManager.add(context)

		if added[0]:										# successful add
			return redirect(reverse("travels"))
		else: 												# failed add
			for error in added[1]:
				messages.error(request, error)
			return redirect(reverse("add"))
	else:
		return render(request, "loginandregistration/add.html")

def join(request, id):
	if 'id' not in request.session:
		messages.error(request, "Please login to continue")
		return redirect("/")
	theTrip = Trip.objects.get(id=id) #at this point, we know this trip exists
	theUser = User.objects.get(id=request.session['id'])
	theTrip.users.add(theUser)
	return redirect(reverse("travels"))

def logoff(request):
	try:
		del request.session['id']
		del request.session['name']
		del request.session['username']
	except KeyError:
		pass			
	return redirect("/")