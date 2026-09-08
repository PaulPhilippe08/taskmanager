import requests
from django.conf import settings

def send_welcome_email(user):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"email": settings.BREVO_SENDER_EMAIL, "name": "Task Manager"},
        "to": [{"email": user.email, "name": user.username}],
        "subject": "Bienvenue sur Task Manager",
        "htmlContent": f"<p>Bonjour {user.username},</p><p>Ton compte a bien été créé. Bienvenue !</p>",
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
    except requests.RequestException as e:
        print("ERREUR RESEAU:", e)

def send_password_reset_email(user, reset_url):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"email": settings.BREVO_SENDER_EMAIL, "name": "Task Manager"},
        "to": [{"email": user.email, "name": user.username}],
        "subject": "Réinitialisation de ton mot de passe",
        "htmlContent": f"<p>Bonjour {user.username},</p><p>Clique ici pour réinitialiser ton mot de passe : <a href='{reset_url}'>{reset_url}</a></p>",
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException:
        pass