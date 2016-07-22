from __future__ import unicode_literals
from django.db import models
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import datetime
import bcrypt


class UserManager(models.Manager):

	##################### VALIDATOR FUNCTIONS ######################

	def checkEmptyFields(self, err_msgs, **kwarg):
		print kwarg
		for field in kwarg.itervalues():
			if len(field) < 1:
				err_msgs.append("All fields are required")
				return False
		return True

	def checkName(self, formdata, err_msgs):
		if len(formdata['name']) < 3:
			err_msgs.append("Name must be at least 3 letters")
		if len(formdata['username']) < 3:
			err_msgs.append("Username must be at least 3 letters")

	def checkPassword(self, formdata, err_msgs):
		if len(formdata['password1']) < 8:
			err_msgs.append("Password must be longer than 8 letters")
		if formdata['password2'] != formdata['password1']:
			err_msgs.append("Must have matching passwords")
			
	#################################################################


	def add(self, formdata, err_msgs):
		if self.checkEmptyFields(	err_msgs,							# check for empty fields on request.POST
									n=formdata['name'], 
									u=formdata['username'], 
									pw1=formdata['password1'],
									pw2=formdata['password2']	):	
			self.checkName(formdata, err_msgs)							# check for names' length and alpha
			self.checkPassword(formdata, err_msgs)						# check for password length and match
			try:														# check existance of credential in record
				self.get(username=formdata['username'])
				err_msgs.append("Provided username already exists in our record")
			except ObjectDoesNotExist:
				pass 													# do nothing if record doens't exist, which is good
		
		if len(err_msgs) > 0:											# false(i.e. failed validation) if any error exists
			return False

		else:															# true if no error exists. add the new user to db
			hashed = bcrypt.hashpw(formdata['password1'].encode(encoding="utf-8", errors="strict"), bcrypt.gensalt())
			self.create(	name=formdata['name'],
							username=formdata['username'],
							hashedpw=hashed ) 
			return True

	def register(self, context):
		formdata = context['formdata']
		err_msgs = []
		return (self.add(formdata, err_msgs), err_msgs)
	
	def signin(self, context):
		formdata = context['formdata']
		err_msgs = []
		user = None
		if self.checkEmptyFields(	err_msgs, 
									u=formdata['username'],
									pw=formdata['password']	):
			try:
				user = self.get(username=formdata['username'])
				hashed = user.hashedpw.encode(encoding="utf-8", errors="strict")
				if not bcrypt.hashpw(formdata['password'].encode(encoding="utf-8", errors="strict"), hashed) == hashed:
					err_msgs.append("Wrong password! Try again!")
			except ObjectDoesNotExist:
				err_msgs.append("Provided username does not exist in our record")
				
		return (len(err_msgs) == 0, err_msgs)



class User(models.Model):
	name = models.CharField(max_length=100)
	username = models.CharField(max_length=100)
	hashedpw = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = models.Manager()
	userManager = UserManager()

class TripManager(models.Manager):

	##################### VALIDATOR FUNCTIONS ######################

	def checkEmptyFields(self, err_msgs, **kwarg):
		for field in kwarg.itervalues():
			if len(field) < 1:
				err_msgs.append("All fields are required")
				return False
		return True

	def checkDate(self, formdata, err_msgs):
		datefrom = datetime.datetime.strptime(formdata['datefrom'], '%Y-%m-%d').date()
		dateto = datetime.datetime.strptime(formdata['dateto'], '%Y-%m-%d').date()
		today = datetime.date.today()
		if ((today.year, today.month, today.day) >= (datefrom.year, datefrom.month, datefrom.day)):
			err_msgs.append("Please pick a future departure date")
		if ((dateto.year, dateto.month, dateto.day) <= (datefrom.year, datefrom.month, datefrom.day)):
			err_msgs.append("'Date to' must be a later date then 'Date from")

	#################################################################


	def add(self, context):
		formdata = context['formdata']
		plannerid = context['plannerid']
		err_msgs = []
		if self.checkEmptyFields(	err_msgs,							# check for empty fields on request.POST
									fn=formdata['destination'], 
									ln=formdata['description'], 
									pw1=formdata['datefrom'],
									pw2=formdata['dateto']	):	
			self.checkDate(formdata, err_msgs)							# check for date
			
		if len(err_msgs) > 0:											# false(i.e. failed validation) if any error exists
			return (False, err_msgs)

		else:															# true if no error exists. add trip to db
			planner = User.objects.get(id=plannerid)
			latest = self.create(	destination=formdata['destination'],
									description=formdata['description'],
									date_from=formdata['datefrom'],
									date_to=formdata['dateto'],
									planner=planner) 
			latest.users.add(planner)
			return (True, err_msgs)

class Trip(models.Model):
	destination = models.CharField(max_length=100)
	description = models.TextField(max_length=100)
	date_from = models.DateTimeField()
	date_to = models.DateTimeField()
	planner = models.ForeignKey(User, related_name="planner")
	users = models.ManyToManyField(User, related_name="users")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = models.Manager()
	tripManager = TripManager()