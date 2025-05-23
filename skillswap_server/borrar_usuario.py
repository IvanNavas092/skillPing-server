import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillping_server.settings')
django.setup()

from marketplace.models import User

username = input("Introduce el nombre de usuario que deseas eliminar: ")

try:
    user = User.objects.get(username=username)
    confirm = input(f"¿Estás seguro de que quieres eliminar al usuario '{username}'? (s/n): ").lower()
    if confirm == 's':
        user.delete()
        print(f"✅ Usuario '{username}' eliminado correctamente.")
    else:
        print("❌ Cancelado.")
except User.DoesNotExist:
    print(f"⚠️ El usuario '{username}' no existe.")



