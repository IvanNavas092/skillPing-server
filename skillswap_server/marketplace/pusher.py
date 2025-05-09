import pusher
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
from .models import User, Message

pusher_client = pusher.Pusher(
  app_id='1980276',
  key='682407f9d91aaf86de6f',
  secret='aefab4c4834cff4aaf9a',
  cluster='eu',
  ssl=True
)
# example
# pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sender_username = data['sender']
            receptor_username = data['receptor']
            message_content = data['message']

            # Obtener los objetos User por username
            sender = User.objects.get(username=sender_username)
            receptor = User.objects.get(username=receptor_username)

            # Guardar en la base de datos
            new_message = Message.objects.create(
                sender=sender, 
                receptor=receptor, 
                message=message_content
            )
            
            # Contar mensajes entre estos dos usuarios (ida y vuelta)
            message_count = Message.objects.filter(
                sender__in=[sender, receptor],
                receptor__in=[sender, receptor]
            ).count()

            # Si alcanzan los 11 mensajes, se considera una nueva "interacción"
            if message_count == 11:
                sender.interactions += 1
                sender.save(update_fields=['interactions'])

            # Crear room con los nombres ordenados alfabéticamente
            usernames = sorted([sender_username, receptor_username])
            room_id = f"room-chat-{usernames[0]}_{usernames[1]}"

            # Enviar mensaje a Pusher
            pusher_client.trigger(room_id, 'new-message', {
                'sender': sender_username,
                'receptor': receptor_username,
                'message': message_content,
                'timestamp': str(datetime.now())
            })
            
            return JsonResponse({'status': 'ok', 'message_id': new_message.id})
        
        except User.DoesNotExist as e:
            return JsonResponse({'error': f'Usuario no encontrado: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)