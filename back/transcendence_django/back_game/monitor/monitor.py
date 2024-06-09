import asyncio
import logging
import random
import string
from typing import Any

from back_game.game_arena.arena import Arena
from back_game.game_arena.game import GameStatus
from back_game.game_arena.player import Player
from back_game.game_settings.dict_keys import ARENA, ID
from back_game.game_settings.game_constants import (
    DEAD,
    DYING,
    MONITOR_LOOP_INTERVAL,
    OVER,
    RUN_LOOP_INTERVAL,
    STARTED,
    TIMEOUT_GAME_OVER,
    TIMEOUT_INTERVAL,
    WAITING,
)

logger = logging.getLogger(__name__)


class Monitor:

    def __init__(self):
        self.channels: dict[str, Any] = {}
        self.user_game_table: dict[int, dict[str, Any]] = {}

    def generate_random_id(self, length: int) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return "".join(random.choice(letters_and_digits) for _ in range(length))

    async def create_channel(self, user_id: int, players_specs: dict[str, int]) -> dict[str, Any] | None:
        channel = self.get_channel_from_user_id(user_id)
        if channel is None:
            return await self.get_new_channel(user_id, players_specs)
        return None

    async def join_channel(self, user_id: int, channel_id: str) -> dict[str, Any]:
        channel = self.get_channel_from_user_id(user_id)
        if self.channels[channel_id] is None:
            return None
        arena_id: int = self.channels[channel_id].keys()[0]
        self.add_user_to_channel(user_id, channel_id, arena_id)
        return channel

    def join_already_created_channel(self, user_id: int, is_remote: bool) -> dict[str, Any] | None:
        channel = self.get_channel_from_user_id(user_id)
        if channel is None and is_remote:
            channel = self.get_available_channel()
        if channel is None:
            return None
        return channel

    def get_available_channel(self) -> dict[str, Any] | None:
        for channel_id, channel in self.channels.items():
            arena_id = list(channel.keys())[0]
            arena = channel[arena_id]
            if arena.get_status() == GameStatus(WAITING):
                return {"channel_id": channel_id, "arena_id": arena_id, "arena": arena.to_dict()}
        return None

    async def get_new_channel(
        self, user_id: int, players_specs: dict[str, int]
    ) -> dict[str, Any]:
        new_arena: Arena = Arena(players_specs)
        channel_id = self.generate_random_id(10)
        self.channels[channel_id] = {new_arena.id: new_arena}
        asyncio.create_task(
            self.monitor_arenas_loop(channel_id, self.channels[channel_id])
        )
        asyncio.create_task(self.run_game_loop(self.channels[channel_id]))
        self.add_user_to_channel(user_id, channel_id, new_arena.id)
        logger.info("New arena: %s", new_arena.to_dict())
        return self.user_game_table[user_id]

    def get_channel_from_user_id(self, user_id: int) -> dict[str, Any] | None:
        channel: dict[str, Any] | None = self.user_game_table.get(user_id)
        if channel is None:
            return None
        return channel

    def add_user_to_channel(self, user_id: int, channel_id: str, arena_id: int):
        arena: Arena = self.channels[channel_id][arena_id]
        self.user_game_table[user_id] = {
            "channel_id": channel_id,
            "arena": arena.to_dict(),
        }

    def delete_arena(self, arenas: dict[str, Arena], arena_id: str):
        arena = arenas[arena_id]
        arena.set_status(GameStatus(DEAD))
        logger.info("Arena %s is dead", arena.id)
        player_list: dict[str, Player] = arena.get_players()
        for player in player_list.values():
            self.delete_user(player.user_id)
        arenas.pop(arena_id)

    def delete_user(self, user_id: int):
        try:
            self.user_game_table.pop(user_id)
            logger.info("User %s deleted from user_game_table", user_id)
        except KeyError:
            pass

    def leave_arena(self, user_id: int, channel_id: int, arena_id: int):
        channel = self.channels.get(channel_id)
        if channel is None:
            return
        arena = channel.get(arena_id)
        if arena is None:
            return
        if arena and not arena.did_player_give_up(user_id):
            if arena.get_status() == WAITING:
                arena.player_gave_up(user_id)
            else:
                arena.player_leave(user_id)

    def get_arena_from_user_id(self, user_id: int) -> dict[str, Any] | None:
        user_channel: dict[str, Any] | None = self.user_game_table.get(user_id)
        if user_channel is None:
            return None
        return user_channel["arena"]

    def is_user_active_in_game(self, user_id: int, channel_id: str, arena_id: int) -> bool:
        if self.user_game_table.get(user_id) == {"channel_id": channel_id, "arena": arena_id}:
            arena: Arena = self.channels[channel_id][arena_id]
            return arena.is_user_active_in_game(user_id)
        return False

    def delete_channel(self, channel_id: str):
        del self.channels[channel_id]

    async def monitor_arenas_loop(self, channel_id: str, arenas: dict[str, Arena]):
        while arenas:
            await self.update_game_states(arenas)
            await asyncio.sleep(MONITOR_LOOP_INTERVAL)
        self.delete_channel(channel_id)

    async def update_game_states(self, arenas: dict[str, Arena]):
        for arena in arenas.values():
            arena_status = arena.get_status()
            if arena_status == GameStatus(WAITING) and arena.has_enough_players(): # can_be_started method to implement
                await arena.start_game()
            elif arena.can_be_over():
                arena.conclude_game()
                if arena_status != GameStatus(STARTED):
                    self.delete_arena(arenas, arena.id)
                    break
            elif arena_status == GameStatus(OVER):
                logger.info("Game over in arena %s", arena.id)
                await self.game_over(arenas, arena)
                break

    async def run_game_loop(self, arenas: dict[str, Arena]):
        while arenas:
            for arena in arenas.values():
                if arena.get_status() == GameStatus(STARTED):
                    update_message = arena.update_game()
                    if arena.game_update_callback is not None:
                        await arena.game_update_callback(update_message)
            await asyncio.sleep(RUN_LOOP_INTERVAL)

    async def game_over(self, arenas: dict[str, Arena], arena: Arena):
        arena.set_status(GameStatus(DYING))
        if arena.game_update_callback is not None:
            logger.info("Sending game over message to arena %s", arena.id)
            await arena.game_update_callback({ARENA: arena.to_dict()})
        time = TIMEOUT_GAME_OVER + 1
        while arena.get_status() in [GameStatus(DYING), GameStatus(WAITING)] and time > 0:
            time -= TIMEOUT_INTERVAL
            if arena.game_over_callback is not None:
                await arena.game_over_callback(
                    "Game Over! Thank you for playing.", time
                )
            if time == 0 and arena.get_status() == GameStatus(DYING):
                self.delete_arena(arenas, arena.id)
            else:
                await asyncio.sleep(TIMEOUT_INTERVAL)


monitor = Monitor()
