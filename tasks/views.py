from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Task
from .emails import send_welcome_email, send_password_reset_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


@login_required
def task_list(request):
    tasks = Task.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title:
            Task.objects.create(title=title, description=description, owner=request.user)
        return redirect('task_list')
    return render(request, 'tasks/task_form.html')


@login_required
def task_toggle_done(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.done = not task.done
    task.save()
    return redirect('task_list')


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.delete()
    return redirect('task_list')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_welcome_email(user)
            login(request, user)
            return redirect('task_list')
    else:
        form = CustomUserCreationForm()

    input_class = 'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400'
    for field in form.fields.values():
        field.widget.attrs.update({'class': input_class})

    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('task_list')
        else:
            return render(request, 'tasks/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'tasks/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def update_photo_view(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        request.user.profile.photo = request.FILES['photo']
        request.user.profile.save()
    return redirect('task_list')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
            send_password_reset_email(user, reset_url)
        except User.DoesNotExist:
            pass
        return render(request, 'tasks/forgot_password.html', {'sent': True})
    return render(request, 'tasks/forgot_password.html')


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'tasks/reset_password.html', {'invalid': True})

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 and password1 == password2:
            user.password = make_password(password1)
            user.save()
            return redirect('login')
        else:
            return render(request, 'tasks/reset_password.html', {'error': 'Les mots de passe ne correspondent pas'})

    return render(request, 'tasks/reset_password.html')