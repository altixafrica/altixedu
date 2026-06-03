import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.notifications.models import Message
from apps.accounts.models import User


class MessageConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time messaging.
    
    Handles:
    - New messages (broadcast to recipient)
    - Typing indicators
    - Read receipts
    - Online/offline status
    """
    
    async def connect(self):
        self.user = self.scope['user']
        self.user_id = self.user.id if self.user.is_authenticated else None
        self.room_group_name = f'messages_{self.user_id}'
        
        # Only allow authenticated users
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user's message group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Broadcast user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user_id,
                'status': 'online',
            }
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        if not self.user_id:
            return
        
        # Broadcast user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user_id,
                'status': 'offline',
            }
        )
        
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'message':
                await self.handle_new_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            elif message_type == 'ping':
                # Keep-alive ping
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            pass

    async def handle_new_message(self, data):
        """Handle new message from sender"""
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not receiver_id or not content:
            return
        
        # Save message to database
        message = await self.save_message(
            sender_id=self.user_id,
            receiver_id=receiver_id,
            content=content
        )
        
        if message:
            # Send to both sender and receiver
            message_data = {
                'type': 'new_message',
                'id': message.id,
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'content': message.content,
                'sent_at': message.sent_at.isoformat(),
                'read': message.read,
            }
            
            # Send to receiver
            await self.channel_layer.group_send(
                f'messages_{receiver_id}',
                message_data
            )
            
            # Confirm to sender
            await self.send(text_data=json.dumps({
                'type': 'message_sent',
                'id': message.id,
            }))

    async def handle_typing(self, data):
        """Handle typing indicator"""
        recipient_id = data.get('recipient_id')
        is_typing = data.get('is_typing', False)
        
        if recipient_id:
            await self.channel_layer.group_send(
                f'messages_{recipient_id}',
                {
                    'type': 'typing_indicator',
                    'user_id': self.user_id,
                    'is_typing': is_typing,
                }
            )

    async def handle_read_receipt(self, data):
        """Handle read receipt"""
        message_id = data.get('message_id')
        
        if message_id:
            message = await self.mark_message_read(message_id)
            if message:
                # Notify sender that message was read
                await self.channel_layer.group_send(
                    f'messages_{message.sender_id}',
                    {
                        'type': 'read_receipt',
                        'message_id': message_id,
                        'read_by_user_id': self.user_id,
                    }
                )

    # Channel layer handlers
    async def new_message(self, event):
        """Broadcast new message to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def typing_indicator(self, event):
        """Broadcast typing indicator"""
        await self.send(text_data=json.dumps(event))

    async def read_receipt(self, event):
        """Broadcast read receipt"""
        await self.send(text_data=json.dumps(event))

    async def user_status(self, event):
        """Broadcast user online/offline status"""
        await self.send(text_data=json.dumps(event))

    # Database operations
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        """Save message to database"""
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                school=sender.school,
            )
            return message
        except (User.DoesNotExist, Message.DoesNotExist):
            return None

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark message as read"""
        try:
            message = Message.objects.get(id=message_id)
            message.read = True
            message.save()
            return message
        except Message.DoesNotExist:
            return None
