import shortuuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from candidates.models import Candidate
from postings.models import Job

STATUS_CHOICES = (
	(-3, 'Revoked'),
	(-2, 'Candidate Cancelled'),
	(-1, 'Employer Cancelled'),
	(0, 'Request Open'),
	(1, 'Pending Confirmation'),
	(2, 'Confirmed'),
	(3, 'Completed'),
)

class Offer_Invitation(models.Model):
	uuid = models.CharField(primary_key=True,
		max_length=5,
		default=shortuuid.ShortUUID().random(length=5).upper(),
		)
	candidate = models.ForeignKey(Candidate,  on_delete=models.CASCADE)
	job = models.ForeignKey(Job,  on_delete=models.CASCADE)
	confirmed_time = models.DateTimeField(null=True, blank=True)
	status = models.IntegerField(choices=STATUS_CHOICES, default=0)
	request_reminders_sent = models.IntegerField(default=0)
	confirmation_reminders_sent = models.IntegerField(default=0)
	candidate_accepted = models.NullBooleanField()
	employer_accepted = models.NullBooleanField()
	is_active = models.BooleanField(default=1)
	result = models.CharField(max_length=50, blank=True)
	last_modified = models.DateTimeField(auto_now_add=False, auto_now=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '<Interview C: %s B: %s>' % (self.candidate.user.email, self.job.job_title)

class Solicitation(models.Model):
	candidate = models.ForeignKey(Candidate, related_name='requested_jobs',  on_delete=models.CASCADE)
	job = models.ForeignKey(Job, related_name='requested_candidates',  on_delete=models.CASCADE)
	candidate_accepted = models.NullBooleanField()
	employer_accepted = models.NullBooleanField()
	last_modified = models.DateTimeField(auto_now_add=False, auto_now=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
'''
	def create(cls, candidate, job, last_modified):
		solicitation = cls(candidate=candidate, job=job, last_modified = last_modified)
		# do something with the book
		return solicitation
	'''
def generate_invitation(sender, instance, created, **kwargs):
	if instance.candidate_accepted and instance.employer_accepted:
		Offer_Invitation.objects.create(
			candidate=instance.candidate,
			job=instance.job)

post_save.connect(generate_invitation, sender= Offer_Invitation)

class Candidate_Available(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	day_of_week = models.IntegerField()
	time_start = models.CharField(max_length=5)
	time_end = models.CharField(max_length=5)
	last_modified = models.DateTimeField(auto_now_add=False, auto_now=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return 'day(%s) %s-%s' % (self.day_of_week, self.time_start, self.time_end)


class Candidate_Exclusion(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField()
