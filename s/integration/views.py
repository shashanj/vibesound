from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from soundcloud.client import Client
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from s.settings import BASE_DIR
from django.core.urlresolvers import reverse
# Create your views here.

client = Client(client_id = '03ca69ce2c518dea7e624a0516011f00',
				client_secret ='c5a09c3c3e0aac210cd7de5941557af8',
				redirect_uri = 'http://localhost:8000/login'
			)

def index(request):
	return HttpResponseRedirect(client.authorize_url(),RequestContext(request))

def upload(request):
	if request.POST:
		access_token = request.POST.get('access_token')
		user = Client(access_token = access_token)
		music = request.FILES['file']
		path = default_storage.save('%s' %music, ContentFile(music.read()))
		music.close()
		print path,os.path.join(BASE_DIR,path)
		#### add uloaded file #####
		track = user.post('/tracks', track={
		    'title': 'This is a test track',
		    'asset_data': open('%s'%os.path.join(BASE_DIR,path),'rb'),
		})
		os.remove(os.path.join(BASE_DIR,path))
		print track.id, track.permalink_url

		tracktoplay = client.get('/resolve', url=request.POST.get('track'))
		embed_info = client.get('/oembed', url=request.POST.get('track'))

		print embed_info.html
		print tracktoplay.id

		usr = []
		follow = []
		if request.POST.get('user') is not None :
			usr = client.get('/resolve', url=request.POST.get('user'))
			print usr.id
			follow = request.POST.get('bool')
		
		context = {
			'download' : track.permalink_url,
			'widget' : embed_info.html,
			'user' : usr.id,
			'follow' : follow,
			'access' : access_token,
		}
		return render_to_response('stream.html',context,RequestContext(request))
	return render_to_response('upload.html',RequestContext(request))


def login(request):
	code = request.GET['code']
	access_token = client.exchange_token(code = code)
	access_token = access_token.access_token

	return render_to_response('upload.html',{'access_token' : access_token},RequestContext(request))


def follow(request,access_token):
	if request.is_ajax():
		if request.POST:
			# print request.POST.get('link')
			print request.POST.get('id')
			print access_token
			user = Client(access_token = access_token)
			user.put('/me/followings/%d' %int(request.POST.get('id')))

			return HttpResponseRedirect(link)