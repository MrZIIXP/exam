from django.views.generic import TemplateView, UpdateView
from accounts.models import User, Profile
from django.shortcuts import redirect, get_object_or_404, render
from catalog.models import Car, Brand, BodyStyle, Transmission
from deals.models import Deal
from review.models import Review
from favourites.models import Favourite
from django.contrib.auth import authenticate
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView
from django.db.models import Avg
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .permissions import assygn_role
from django.urls import reverse_lazy


def send_verification_email(request, user):
    token = user.email_token
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )

    subject = 'Подтвердите вашу email адрес'
    message = f"""
    Привет {user.first_name or user.username}!
    
    Спасибо за регистрацию. Пожалуйста, подтвердите вашу email адрес, 
    перейдя по ссылке ниже:
    
    {verification_link}
    
    Ссылка действительна 5 минут.
    
    С уважением,
    Команда LUXE AUTO
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def send_password_reset_email(request, user):
    token = user.reset_password_token
    reset_link = request.build_absolute_uri(
        reverse('reset_password_confirm', kwargs={'token': token})
    )

    subject = 'Сброс пароля'
    message = f"""
    Привет {user.first_name or user.username}!
    
    Мы получили запрос на сброс вашего пароля. 
    Перейдите по ссылке ниже для создания нового пароля:
    
    {reset_link}
    
    Ссылка действительна 5 минут.
    
    Если вы не делали этот запрос, игнорируйте это письмо.
    
    С уважением,
    Команда LUXE AUTO
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


class VerifyEmailView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(email_token=token)

            if not user.email_token_is_valid():
                messages.error(
                    request, 'Ссылка верификации истекла. Запросите новую.')
                return redirect('login')

            user.confirm_email_token()

            messages.success(
                request,
                'Ваш email успешно подтвержден! Теперь вы можете войти в систему.'
            )
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'Неверный или истекший токен верификации.')
            return redirect('login')


class ResendVerificationEmailView(View):
    def get(self, request):
        if not request.session.get('user_id'):
            return redirect('login')

        user = User.objects.get(id=request.session.get('user_id'))

        if user.is_verifired:
            messages.info(request, 'Ваш email уже подтвержден.')
            return redirect('home')

        user.email_send_token()

        if send_verification_email(request, user):
            messages.success(
                request,
                'Письмо с верификацией отправлено на ваш email. Проверьте почту.'
            )
        else:
            messages.error(
                request, 'Ошибка при отправке письма. Попробуйте позже.')

        return redirect('home')


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        messages.info(request, 'Вы вышли из системы')
        return redirect('login')


class RegisterView(View):
    template_name = 'auth/register.html'
    form_class = RegisterForm

    def get(self, request):
        if request.session.get('user_id'):
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                user = form.save()
                send_verification_email(request, user)
                messages.success(
                    request,
                    f'Добро пожаловать! Письмо с подтверждением отправлено на {user.email}'
                )
                return redirect('login')

            except Exception as e:
                messages.error(
                    request, 'Произошла ошибка при регистрации. Попробуйте позже.')
                print(f"Ошибка регистрации: {e}")

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'auth/login.html'
    form_class = LoginForm

    def get(self, request):
        if request.session.get('user_id'):
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
                if not user.is_verifired:
                    messages.warning(
                        request,
                        'Ваш email не подтвержден. Проверьте почту или запросите новое письмо.'
                    )
                    return render(request, self.template_name, {'form': form})

                user = authenticate(
                    request, username=user.username, password=password)

                if user:
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    request.session['email'] = user.email
                    request.session['first_name'] = user.first_name
                    request.session['is_authenticated'] = True
                    if user.groups.filter(name='User').exists():
                        assygn_role(user, 'User')
                    messages.success(
                        request, f'Добро пожаловать, {user.first_name or user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Неверный email или пароль')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')

        return render(request, self.template_name, {'form': form})


class ForgotPasswordView(View):
    template_name = 'auth/forgot_password.html'
    form_class = ForgotPasswordForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                user.reset_password_send_token()
                send_password_reset_email(request, user)

                messages.success(
                    request,
                    'Ссылка для сброса пароля отправлена на ваш email. Проверьте почту.'
                )
                return redirect('login')
            except User.DoesNotExist:
                messages.success(
                    request,
                    'Если пользователь с таким email существует, ссылка отправлена на почту.'
                )
                return redirect('login')

        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    template_name = 'auth/reset_password.html'
    form_class = ResetPasswordForm

    def get(self, request, token):
        try:
            user = User.objects.get(reset_password_token=token)

            if not user.reset_password_token_is_valid():
                messages.error(request, 'Ссылка для сброса пароля истекла.')
                return redirect('forgot_password')

            form = self.form_class()
            return render(request, self.template_name, {'form': form, 'token': token})
        except User.DoesNotExist:
            messages.error(request, 'Неверный токен сброса пароля.')
            return redirect('forgot_password')

    def post(self, request, token):
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                user = User.objects.get(reset_password_token=token)

                if not user.reset_password_token_is_valid():
                    messages.error(
                        request, 'Ссылка для сброса пароля истекла.')
                    return redirect('forgot_password')

                password = form.cleaned_data['password']
                user.set_password(password)
                user.confirm_reset_password_token()

                messages.success(
                    request, 'Пароль успешно изменен. Войдите в систему.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Неверный токен сброса пароля.')
                return redirect('forgot_password')

        return render(request, self.template_name, {'form': form, 'token': token})


class ViewMyListings(TemplateView):
    template_name = 'profile/car_listing.html'

    def get_context_data(self, **kwargs):
        user = User.objects.get(id=self.request.session.get("user_id", ''))
        cars = Car.objects.filter(user=user).prefetch_related(
            'brand', 'transmission', 'body_style').all()
        return super().get_context_data(cars=cars, **kwargs)


class AddCarListings(CreateView):
    template_name = 'core/sell_your_car.html'
    model = Car
    fields = ['brand', 'body_style', 'transmission', 'title', 'description',
              'price', 'speed', 'image_1', 'image_2', 'image_3', 'image_4']
    success_url = reverse_lazy('my_listings')

    def form_valid(self, form):
        user_id = self.request.session.get("user_id")
        if user_id:
            form.instance.user = User.objects.get(id=user_id)
        messages.success(self.request, 'Ваше объявление успешно опубликовано!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['body_styles'] = BodyStyle.objects.all()
        context['transmissions'] = Transmission.objects.all()
        return context


class EditCarListings(UpdateView):
    template_name = 'profile/edit_car_listing.html'
    model = Car
    success_url = reverse_lazy('my_listings')
    fields = ['brand', 'body_style', 'transmission', 'title', 'description',
              'price', 'speed', 'image_1', 'image_2', 'image_3', 'image_4']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['body_styles'] = BodyStyle.objects.all()
        context['transmissions'] = Transmission.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Автомобиль успешно обновлен!')
        return super().form_valid(form)


class QuickEditCar(UpdateView):
    model = Car
    fields = '__all__'
    success_url = reverse_lazy('my_listings')
    fields = ['title', 'price', 'description']


class SoftDeleteCarListings(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        car = get_object_or_404(Car.objects, id=pk, user_id=user_id)
        car.soft_delete()
        messages.success(
            request, f'Объявление "{car.title}" перемещено в корзину')
        return redirect('my_listings')


# ==================== RESTORE FROM TRASH ====================
class RestoreCarListing(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        car = get_object_or_404(Car.all_cars, id=pk,
                                user_id=user_id, is_deleted=True)
        car.restore()
        messages.success(request, f'Объявление "{car.title}" восстановлено')
        return redirect('trash_listings')


# ==================== PERMANENT DELETE ====================
class PermanentDeleteCar(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        car = get_object_or_404(Car.all_cars, id=pk,
                                user_id=user_id, is_deleted=True)
        title = car.title
        car.delete()  # Полное удаление из БД
        messages.success(request, f'Объявление "{title}" полностью удалено')
        return redirect('trash_listings')


class EmptyTrash(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        deleted_cars = Car.all_cars.filter(user_id=user_id, is_deleted=True)
        count = deleted_cars.count()
        deleted_cars.delete()
        messages.success(
            request, f'Корзина очищена. Удалено {count} объявлений.')
        return redirect('trash_listings')


class TrashCarListings(TemplateView):
    template_name = 'profile/trash_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')

        if user_id:
            context['deleted_cars'] = Car.all_cars.filter(
                user_id=user_id, is_deleted=True)
        else:
            context['deleted_cars'] = []

        return context


class ViewProfile(TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            active_listings = Car.objects.filter(user=user, is_deleted=False)
            completed_deals = Deal.objects.filter(
                seller=user, status='delivered').count()
            new_inquiries = Deal.objects.filter(
                seller=user, status='processing').count()
            favourites_count = Favourite.objects.filter(user=user).count()
            profile = Profile.objects.filter(user=user).first()

            context['user'] = user
            context['profile'] = profile
            context['active_listings'] = active_listings
            context['active_listings_count'] = active_listings.count()
            context['completed_deals'] = completed_deals
            context['new_inquiries'] = new_inquiries
            context['favourites_count'] = favourites_count
            context['profile_views'] = user.profile.avg_rating()
            context['views_percentage'] = '+12.5%'

        else:
            context['user'] = None
            context['profile'] = None
            context['active_listings'] = []
            context['active_listings_count'] = 0
            context['completed_deals'] = 0
            context['new_inquiries'] = 0
            context['favourites_count'] = 0
            context['profile_views'] = 0
            context['views_percentage'] = '0%'

        return context


class EditProfile(TemplateView):
    template_name = 'profile/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')

        if user_id:
            context['user'] = get_object_or_404(User, id=user_id)
            context['profile'] = Profile.objects.filter(user__id=user_id).first()

        return context

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        user = get_object_or_404(User, id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)

        # Update user fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        # Update profile fields
        phone = request.POST.get('phone')
        if phone:
            profile.phone = phone

        avatar = request.FILES.get('avatar')
        if avatar:
            if profile.avatar:
                profile.avatar.delete()
            profile.avatar = avatar

        profile.save()

        request.session['first_name'] = user.first_name

        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('edit_profile')


class AddReviewView(View):
    def post(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to leave a review')
            return redirect('login')

        to_user = get_object_or_404(User, id=pk)
        from_user = get_object_or_404(User, id=user_id)

        existing_review = Review.objects.filter(
            from_user=from_user, to_user=to_user).first()
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
            messages.success(
                request, 'Your review has been submitted successfully!')
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

        # Check if user is the author
        if review.from_user.id != user_id:
            messages.error(request, 'You can only delete your own reviews')
            return redirect('other_profile', pk=review.to_user.id)

        to_user_id = review.to_user.id
        review.delete()
        messages.success(request, 'Review deleted successfully')

        return redirect('other_profile', pk=to_user_id)


class ViewOtherProfile(TemplateView):
    template_name = 'core/other_user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            profile = Profile.objects.filter(user=user).first()

            # Active listings
            active_listings = Car.objects.filter(user=user, is_deleted=False)

            # Cars sold
            cars_sold = Deal.objects.filter(
                seller=user, status='delivered').count()

            # Reviews received
            reviews = Review.objects.filter(
                to_user=user).order_by('-created_at')

            # Average rating
            rating_data = reviews.aggregate(avg_rating=Avg('rating'))
            user_rating = rating_data['avg_rating'] or 0

            context['user'] = user
            context['other_profile'] = profile
            context['active_listings'] = active_listings
            context['active_listings_count'] = active_listings.count()
            context['cars_sold'] = cars_sold
            context['reviews'] = reviews
            context['user_rating'] = round(user_rating, 1)
            context['session_user_id'] = self.request.session.get('user_id')

        return context
