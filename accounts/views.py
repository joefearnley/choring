from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # create inactive user until email verification
            user.is_active = False
            user.save()
            token = signing.dumps({'user_id': user.id})
            activation_link = request.build_absolute_uri(
                '/accounts/activate/{token}/'.format(token=token)
            )
            send_mail(
                'Activate your account',
                f'Follow this link to activate your account: {activation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            messages.success(request, 'Registration successful. Check your email to activate your account.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate_view(request, token):
    try:
        data = signing.loads(token, max_age=60 * 60 * 24)
        user_id = data.get('user_id')
    except signing.BadSignature:
        return render(request, 'accounts/activation_invalid.html')
    except signing.SignatureExpired:
        return render(request, 'accounts/activation_invalid.html')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'accounts/activation_invalid.html')
    user.is_active = True
    user.save()
    login(request, user)
    return render(request, 'accounts/activation_complete.html')
