# SkillPing - Backend Django

Este es el backend de **SkillPing**, una plataforma para el intercambio de habilidades entre usuarios. Desarrollado con Django y Django REST Framework, ofrece una API RESTful que se comunica con un frontend (como Angular).

---

## 🚀 Tecnologías utilizadas

- Python 3.11+
- Django 5.1.5
- Django REST Framework 3.15.2
- PostgreSQL (NeonDB)
- `django-cors-headers` 4.7.0
- `django-extensions` 4.1
- `python-dotenv` 1.1.0
- `pusher` 3.3.3
- `requests` 2.32.3

---

## ⚙️ Requisitos

- Python 3.11+ instalado
- `pip` o Conda
- PostgreSQL (o conexión externa tipo NeonDB)
- (Recomendado) entorno virtual

---

## 🛠️ Instalación del proyecto

### Opción A: Usando pip

```bash
# 1. Clona el repositorio
git clone 
cd skillping-backend

# 2. Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate

# 3. Instala los paquetes
pip install -r requirements.txt

# 4. Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# 5. Ejecuta el servidor
python manage.py runserver
```
### Opción B: Usando Anaconda
```bash
# 1. Clona el repositorio

git clone
cd skillping-backend

# 2. Crea el entorno desde el archivo environment.yml
conda env create -f environment.yml

# 3. Activa el entorno
conda activate entorno_skillping

# 4. Migraciones y superusuario
python manage.py migrate

# 5. Ejecuta el servidor
python manage.py runserver
```
