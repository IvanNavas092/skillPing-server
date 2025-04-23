import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillswap_server.settings')
django.setup()

from marketplace.models import User

# OPCIÓN A: Borrar un solo usuario por username ===
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


# === OPCIÓN B (comentada): Borrar todos los usuarios (¡Peligroso!) ===

# confirm_all = input("¿Estás seguro de que quieres eliminar TODOS los usuarios? (s/n): ").lower()
# if confirm_all == 's':
#     deleted, _ = User.objects.all().delete()
#     print(f"✅ Se eliminaron {deleted} usuarios.")
# else:
#     print("❌ Cancelado.")

