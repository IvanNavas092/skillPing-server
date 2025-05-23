# Archivo para cargar los datos de la base de datos en un archivo JSON (forzado a UTF-8 para que los emojis carguen)
import django
import os
import sys
import io

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skillping_server.settings")
django.setup()

from django.core.management import call_command

out = io.StringIO()
call_command('dumpdata', 
    exclude=['auth.permission', 'contenttypes'],
    use_natural_foreign_keys=True,
    use_natural_primary_keys=True,
    stdout=out)

with open('backup_data.json', 'w', encoding='utf-8') as f:
    f.write(out.getvalue())

print("✅ Datos exportados con emojis correctamente")
