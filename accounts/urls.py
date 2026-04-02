from django.urls import path
from .views import *

urlpatterns = [
	 path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('auth/resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(),name='forgot_password'),
    path('auth/reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password_confirm'),


    path('profile/my-listings/', ViewMyListings.as_view(), name='my_listings'),
    path('profile/add-listing/', AddCarListings.as_view(), name='add_listing'),
    path('profile/edit-listing/<int:pk>/', EditCarListings.as_view(), name='edit_listing'),
    path('profile/quickedit/<int:pk>/', QuickEditCar.as_view(), name='quickedit'),
    path('profile/delete-listing/<int:pk>/', SoftDeleteCarListings.as_view(), name='delete_listing'),
    path('profile/restore-listing/<int:pk>/', RestoreCarListing.as_view(), name='restore_listing'),
    path('profile/permanent-delete/<int:pk>/', PermanentDeleteCar.as_view(), name='permanent_delete'),
    path('profile/empty-trash/', EmptyTrash.as_view(), name='empty_trash'),
    path('profile/trash/', TrashCarListings.as_view(), name='trash_listings'),
    path('add-review/<int:pk>/', AddReviewView.as_view(), name='add_review'),
    path('delete-review/<int:pk>/', DeleteReviewView.as_view(), name='delete_review'),

    
    path('profile/', ViewProfile.as_view(), name='profile'),
    path('profile/edit/', EditProfile.as_view(), name='edit_profile'),
    path('profile/<int:pk>/', ViewOtherProfile.as_view(), name='other_profile'),
]
