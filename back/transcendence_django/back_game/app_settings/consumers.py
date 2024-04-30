import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from back_game.monitor.monitor import monitor
from back_game.game_arena.arena import Arena
from back_game.game_settings.game_constants import *

log = logging.getLogger(__name__)

class PlayerConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channelID = None
        self.arena = None
        self.room_group_name = None
        self.joined = False
        self.username = None

    async def connect(self):
        self.channelID = self.scope['url_route']['kwargs']['channelID']
        self.room_group_name = f'game_{self.channelID}'
        log.info(f"User Connected to {self.room_group_name}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.leave(None)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        log.info(f"Disconnect with code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        content = json.loads(text_data)
        message_type, message = content['type'], content['message']
        message_binding = {
            'move_paddle': self.move_paddle,
            'join': self.join,
            'leave': self.leave,
            'give_up': self.give_up,
            'rematch': self.rematch
        }
        try:
            await message_binding[message_type](message)
        except KeyError as e:
            log.warning(f"Unknown message type: {message_type}")
            log.warning(f"Error: {e}")

    async def join(self, message: dict):
        self.username = message["username"]
        arenaID = message["arenaID"]
        self.arena = monitor.channels[self.channelID][arenaID]
        self.arena.game_update_callback = self.send_update
        self.arena.game_over_callback = self.send_game_over
        self.arena.enter_arena(self.username)
        self.joined = True
        self.send_message(f"{self.username} has joined the game.")
        self.send_update({"player_list": self.arena.players})

    async def leave(self, _):
        if not self.joined:
            log.error("Attempt to leave without joining.")
            return
        self.arena.disable_player(self.username)
        self.joined = False
        await self.send_message(f"{self.username} has left the game.")

    async def give_up(self, _):
        if not self.joined:
            log.error("Attempt to give up without joining.")
            return
        if self.arena.mode == LOCAL_MODE:
            self.arena.end_of_game()
        self.arena.player_gave_up(self.username)
        monitor.userGameTable.pop(self.username)
        self.joined = False
        await self.send_message(f"{self.username} has given up.")

    async def rematch(self, _):
        if not self.joined:
            log.error("Attempt to rematch without joining.")
            return
        arena_data = self.arena.rematch(self.username)
        if arena_data is None:
            await self.send_message(f"{self.username} asked for a rematch.")
        else:
            await self.send_update({"arena": arena_data})

    async def move_paddle(self, message: dict):
        if not self.joined:
            log.error("Attempt to move paddle without joining.")
            return
        player_name = message['player']
        direction = message['direction']
        paddle_data = self.arena.move_paddle(player_name, direction)
        await self.send_update({"paddle": paddle_data})
        log.info(f"{self.username} moved paddle to {paddle_data['position']}.")


    async def send_game_over(self, game_over_message):
        await self.send_update({
            "gameover": {
                'winner': f'{self.arena.get_winner()}',
                'message': game_over_message
                }
            })

    async def game_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': "game_message",
            'message': message
        }))

    async def game_update(self, event):
        message = event['update']
        await self.send(text_data=json.dumps({
            'type': "game_update",
            'update': message
        }))

    async def send_update(self, update):
        log.info(f"Sending update: {update}")
        await self.send_data({
            "type": "game_update",
            'update': update
        })

    async def send_message(self, message):
        log.info(f"Sending message: {message}")
        await self.send_data({
            "type": "game_message",
            'message': message
        })

    async def send_data(self, data):
        await self.channel_layer.group_send(
            self.room_group_name, data
        )
