from django.http import JsonResponse
from datetime import datetime
from .models import User, Message
from django.db.models import Count
import json
from marketplace.pusher import pusher_client
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chat(request):
    if request.method == "POST":
        # prepare data
        try:
            data = json.loads(request.body)
            sender_username = data["sender"]
            receptor_username = data["receptor"]
            message_content = data["message"]

            # Obtener los objetos User por username
            sender = User.objects.get(username=sender_username)
            receptor = User.objects.get(username=receptor_username)

            # Guardar en la base de datos
            new_message = Message.objects.create(
                sender=sender, receptor=receptor, message=message_content, is_read=False
            )

            # count messages between these two users (one way and the other)
            message_count = Message.objects.filter(
                sender__in=[sender, receptor], receptor__in=[sender, receptor]
            ).count()

            # count messages no read by receptor
            message_no_read_count = Message.objects.filter(
                receptor=receptor, is_read=False
            ).count()

            # If they reach 11 messages, it is considered a new "interaction"
            if message_count == 11:
                sender.interactions += 1
                sender.save(update_fields=["interactions"])

            # Crear room con los nombres ordenados alfabéticamente
            usernames = sorted([sender_username, receptor_username])
            room_id = f"room-chat-{usernames[0]}_{usernames[1]}"

            # Enviar mensaje a Pusher
            pusher_client.trigger(
                room_id,
                "new-message",
                {
                    "sender": sender_username,
                    "receptor": receptor_username,
                    "message": message_content,
                    "timestamp": str(datetime.now()),
                },
            )
            # send private notification to receptor with the message_no_read_count
            pusher_client.trigger(
                f"notifications-{receptor_username}",  # channel for receptor
                "unread-messages",
                {
                    "unread_counts": message_no_read_count,
                    "sender": sender_username,  # who is sending the message
                },
            )
            return JsonResponse(
                {
                    "status": "ok",
                    "message_id": new_message.id,
                    "unread_count": message_no_read_count
                }
            )

        except User.DoesNotExist as e:
            return JsonResponse(
                {"error": f"Usuario no encontrado: {str(e)}"}, status=400
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


# mark messages as read 
@csrf_exempt
def mark_messages_as_read(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_user = data["current_user"]  # Quién está marcando como leídos
            sender_username = data["sender"]  # De quién son los mensajes
            
            current_user_obj = User.objects.get(username=current_user)
            sender_obj = User.objects.get(username=sender_username)
            
            # Marcar como leídos los mensajes de este sender
            Message.objects.filter(
                sender=sender_obj,
                receptor=current_user_obj,
                is_read=False
            ).update(is_read=True)
            
            # Obtener nuevo conteo de no leídos
            new_unread_count = Message.objects.filter(
                receptor=current_user_obj,
                is_read=False
            ).count()
            
            # Notificar al usuario sobre el cambio
            pusher_client.trigger( #channel, event, data
                f"notifications-{current_user}", # channel
                "unread-messages", # event
                { # data
                    "unread_counts": new_unread_count,
                    "sender": sender_username
                }
            )
            
            return JsonResponse({
                "status": "success",
                "new_unread_count": new_unread_count
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

# obbtain unread counts for a user
@csrf_exempt
def get_unread_counts(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data["username"]
            
            user = User.objects.get(username=username)
            
            # Obtener conteo total de no leídos
            total_unread = Message.objects.filter(
                receptor=user,
                is_read=False
            ).count()
            
            # Obtener conteo por cada remitente
            senders_unread = Message.objects.filter(
                receptor=user,
                is_read=False
            ).values('sender__username').annotate(count=Count('id'))
            
            return JsonResponse({
                "status": "success",
                "total_unread": total_unread,
                "by_sender": list(senders_unread)
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)