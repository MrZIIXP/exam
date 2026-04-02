from accounts.models import Profile, User
from accounts.permissions import build_perms
def user(request):
   is_authenticated = request.session.get('is_authenticated')
   context = {
		'is_authenticated': is_authenticated,
	}
   
   if is_authenticated:
      userq = User.objects.get(id=request.session.get('user_id'))
      profile = Profile.objects.get(user=userq)
      context['profile'] = profile
      context['perms'] = build_perms(userq)

   return context