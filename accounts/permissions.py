from django.contrib.auth.models import Group, Permission


PERMISSIONS_ROLES = {
    'Admin': [
        'can_add_review',
        'can_delete_review',
        'can_delete_any_review',
        'can_manage_brands',
        'can_manage_body_style',
        'can_manage_transmission',
        'can_add_car',
        'can_edit_car',
        'can_edit_any_car',
        'can_delete_car',
        'can_delete_any_car',
        'can_view_ai_history',
        'can_delete_ai_history',
        'can_ask_ai',
    ],
    'Seller': [
        'can_add_review',
        'can_delete_review',
        'can_add_car',
        'can_edit_car',
        'can_delete_car',
        'can_view_ai_history',
        'can_delete_ai_history',
        'can_ask_ai',
        'can_manage_brands',
        'can_manage_body_style',
        'can_manage_transmission',
    ],
    'User': [
        'can_add_review',
        'can_delete_review',
        'can_add_car',
        'can_edit_car',
        'can_delete_car',
        'can_view_ai_history',
        'can_delete_ai_history',
        'can_ask_ai',
    ]
}


def sync():
    for role_name, permissins in PERMISSIONS_ROLES.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        perms = Permission.objects.filter(codename__in=permissins)
        group.permissions.set(perms)


def assygn_role(user, role):
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)


def get_current_user(request):
    if hasattr(request, '_current_user'):
        return request._current_user

    from accounts.models import User
    user_session = request.session.get('user_id')
    if not user_session:
        request._current_user = None
        return None

    user = User.objects.filter(id=user_session).prefetch_related(
        'groups_permissions').first

    request._current_user = user
    return user


def get_user_permissions(user):
    if not user:
        return set()
    perms = set()
    for group in user.groups.all():
        for perm in group.permissions.all():
            perms.add(perm.codename)
    return perms


def build_perms(user):
    codenames = get_user_permissions(user)

    return {
        'can_add_review': 'can_add_review' in codenames,
        'can_delete_review': 'can_delete_review' in codenames,
        'can_delete_any_review': 'can_delete_any_review' in codenames,
        'can_manage_brands': 'can_manage_brands' in codenames,
        'can_manage_body_style': 'can_manage_body_style' in codenames,
        'can_manage_transmission': 'can_manage_transmission' in codenames,
        'can_add_car': 'can_add_car' in codenames,
        'can_edit_car': 'can_edit_car' in codenames,
        'can_edit_any_car': 'can_edit_any_car' in codenames,
        'can_delete_car': 'can_delete_car' in codenames,
        'can_delete_any_car': 'can_delete_any_car' in codenames,
        'can_view_ai_history': 'can_view_ai_history' in codenames,
        'can_delete_ai_history': 'can_delete_ai_history' in codenames,
        'can_ask_ai': 'can_ask_ai' in codenames,
        'is_admin': user.groups.filter(name='Admin').exists() if user else False,
        'is_seller': user.groups.filter(name='Seller').exists() if user else False,
        'is_user': user.groups.filter(name='User').exists() if user else False,
    }
