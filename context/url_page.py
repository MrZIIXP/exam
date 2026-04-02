from django.http import HttpRequest
def page(request: HttpRequest):
   return {
		'page': request.path 
	}