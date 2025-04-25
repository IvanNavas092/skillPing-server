import pusher
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime

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
      sender = data['sender']
      message = data['message']
      receptor = data['receptor']
      room_id = f"room-chat-{sorted([sender, receptor])[0]}_{sorted([sender, receptor])[1]}" 

      # disparamos el mensaje al canal especifico
      # envía un evento en tiempo real a todos los usuarios suscritos a esa sala de chat
      pusher_client.trigger(room_id, 'new-message', {
        'sender' : sender,
        'message' : message,
        'timestamp' : str(datetime.now())
      })
      return JsonResponse({'status': 'ok'})
    except Exception as e:
      return JsonResponse({'error': str(e)}, status = 400)
    
  return JsonResponse({'error'}, status = 405)