from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from accounts.models import Review
from accounts.models import User


class AddReviewView(View):
    def post(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to leave a review')
            return redirect('login')
        
        to_user = get_object_or_404(User, id=pk)
        from_user = get_object_or_404(User, id=user_id)
        
        # Check if user already reviewed this seller
        existing_review = Review.objects.filter(from_user=from_user, to_user=to_user).first()
        if existing_review:
            messages.error(request, 'You have already reviewed this seller')
            return redirect('other_profile', pk=pk)
        
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        if not rating or not text:
            messages.error(request, 'Please provide both rating and comment')
            return redirect('other_profile', pk=pk)
        
        try:
            review = Review.objects.create(
                from_user=from_user,
                to_user=to_user,
                rating=int(rating),
                text=text
            )
            messages.success(request, 'Your review has been submitted successfully!')
        except Exception as e:
            messages.error(request, f'Error submitting review: {e}')
        
        return redirect('other_profile', pk=pk)


class DeleteReviewView(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to delete a review')
            return redirect('login')
        
        review = get_object_or_404(Review, id=pk)
        
        # Check if user is the author or has permission
        if review.from_user.id != user_id:
            messages.error(request, 'You can only delete your own reviews')
            return redirect('other_profile', pk=review.to_user.id)
        
        to_user_id = review.to_user.id
        review.delete()
        messages.success(request, 'Review deleted successfully')
        
        return redirect('other_profile', pk=to_user_id)