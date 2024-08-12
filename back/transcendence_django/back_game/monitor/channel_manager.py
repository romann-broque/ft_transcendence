import logging
import random
import string
from typing import Any

from back_game.game_arena.arena import Arena
from back_game.game_arena.game import GameStatus
from back_game.game_arena.player import Player
from back_game.game_settings.game_constants import CREATED, DEAD, TOURNAMENT_ARENA_COUNT, WAITING
from transcendence_django.dict_keys import ID

logger = logging.getLogger(__name__)


class ChannelManager:
    def __init__(self):
        self.channels: dict[str, dict[str, Arena]] = {}
        self.user_game_table: dict[int, dict[str, Any]] = {}

    def can_channel_be_joined(self, channel_id: str, user_id: int) -> bool:
        if channel_id not in self.channels or self.is_tournament(channel_id):
            return False
        channel: dict[str, Any] = self.channels[channel_id]
        arena: Arena = self.get_available_arena(channel_id)
        return arena.get_status() in [GameStatus(CREATED), GameStatus(WAITING)]

    async def join_channel(
        self, user_id: int, channel_id: str
    ) -> dict[str, Any] | None:
        if not self.can_channel_be_joined(channel_id, user_id):
            return None
        arena: Arena = self.get_available_arena(channel_id)
        logger.info("Arena id: %s", arena.id)
        self.add_user_to_channel(user_id, channel_id, arena.id)
        return self.get_channel_from_user_id(user_id)

    def join_already_created_channel(
        self, user_id: int, is_remote: bool, is_tournament: bool
    ) -> dict[str, Any] | None:
        channel = self.get_channel_from_user_id(user_id)
        if channel is None and is_remote:
            channel = self.__get_available_channel(is_tournament)
        if channel is None:
            return None
        return channel

    async def create_new_channel(
        self, user_id: int, players_specs: dict[str, int], is_tournament: bool = False
    ) -> dict[str, Any]:
        arena_count = 1
        if is_tournament:
            arena_count = TOURNAMENT_ARENA_COUNT
        arenas = []
        for _ in range(arena_count):
            new_arena: Arena = Arena(players_specs)
            arenas.append(new_arena)
        channel_id: str = self.__generate_random_id(10)
        self.channels[channel_id] = {
            "is_tournament": is_tournament,
            "arenas": {arena.id: arena for arena in arenas}
        }
        self.add_user_to_channel(user_id, channel_id)
        logger.info("New arenas: %s", arenas)
        return self.user_game_table[user_id]

    def get_channel_from_user_id(self, user_id: int) -> dict[str, Any] | None:
        channel: dict[str, Any] | None = self.user_game_table.get(user_id)
        if channel is None:
            return None
        return channel

    def get_available_arena(self, channel_id: str) -> Arena | None:
        arenas = self.get_arenas(channel_id)
        for arena in arenas.values():
            if arena.is_full():
                continue
            if arena.get_status() in [GameStatus(CREATED), GameStatus(WAITING)]:
                return arena
        return None

    def is_user_in_channel(self, user_id: int) -> bool:
        user_data = self.user_game_table.get(user_id)
        if user_data is None:
            return False
        return user_data["arena"] is not None

    def add_user_to_channel(self, user_id: int, channel_id: str, arena_id: str = None):
        logger.info("Adding user %s to channel %s in arena %s", user_id, channel_id, arena_id)
        arena = self.get_arena(channel_id, arena_id)
        self.user_game_table[user_id] = {
            "channel_id": channel_id,
            "arena": arena.to_dict() if arena else None,
        }

    def get_players_from_channel(self, channel_id: str) -> list[dict[str, Any]]:
        players = []
        logger.info("Getting players from channel %s", channel_id)
        for user_id, user_data in self.user_game_table.items():
            if user_data["channel_id"] == channel_id:
                players.append({"user_id": user_id, "arena": user_data["arena"]})
        return players

    def get_channel_capacity(self, channel_id: str) -> int:
        arenas = self.get_arenas(channel_id)
        return sum(arena.game.nb_players for arena in arenas.values())

    def are_all_arenas_ready(self, channel_id: str) -> bool:
        arenas = self.get_arenas(channel_id)
        return all(arena.is_full()
            for arena in arenas.values())

    def are_all_arenas_over(self, channel_id: str) -> bool:
        arenas = self.get_arenas(channel_id)
        return len(arenas) == 0

    def is_tournament(self, channel_id: str) -> bool:
        return self.channels[channel_id]["is_tournament"]

    def delete_arena(self, channel_id: str, arena_id: str):
        arenas = self.get_arenas(channel_id)
        arena = self.get_arena(channel_id, arena_id)
        logger.info("Deleting arena %s in channel %s (%s)", arena_id, channel_id, arena)
        arena.set_status(GameStatus(DEAD))
        logger.info("Arena %s is dead", arena.id)
        player_list: dict[str, Player] = arena.get_players()
        for player in player_list.values():
            self.delete_user(player.user_id, arena_id)
        arenas.pop(arena_id)

    def get_arena(self, channel_id: str, arena_id: str | None) -> Arena | None:
        logger.info("Trying to get arena %s in channel %s", arena_id, channel_id)
        channel = self.channels.get(channel_id)
        if channel:
            return channel["arenas"].get(arena_id)
        return None

    def get_arenas(self, channel_id: str) -> dict[str, Arena] | None:
        return self.channels[channel_id].get("arenas")

    def leave_arena(self, user_id: int, channel_id: str, arena_id: str):
        arena = self.get_arena(channel_id, arena_id)
        if arena is None:
            return
        if arena and not arena.did_player_give_up(user_id):
            if arena.get_status() == WAITING:
                arena.player_gave_up(user_id)
            else:
                arena.player_leave(user_id)

    def is_user_active_in_game(
        self, user_id: int, channel_id: str, arena_id: str
    ) -> bool:
        if self.user_game_table.get(user_id) == {
            "channel_id": channel_id,
            "arena": arena_id,
        }:
            arena = self.get_arena(channel_id, arena_id)
            return arena.is_user_active_in_game(user_id)
        return False

    def delete_channel(self, channel_id: str):
        del self.channels[channel_id]

    def delete_user(self, user_id: int, arena_id: str):
        try:
            user_data = self.user_game_table[user_id]
            if user_data["arena"][ID] == arena_id:
                self.user_game_table.pop(user_id)
                logger.info("User %s deleted from user_game_table", user_id)
        except KeyError:
            pass

    def __get_available_channel(self, is_tournament: bool) -> dict[str, Any] | None:
        channels = {
            channel_id: channel
            for channel_id, channel in self.channels.items()
            if self.is_tournament(channel_id) == is_tournament
        }
        for channel_id, channel in channels.items():
            arenas = self.get_arenas(channel_id)
            for arena in arenas.values():
                if arena.is_private() or arena.is_full():
                    continue
                if arena.get_status() in [GameStatus(CREATED), GameStatus(WAITING)]:
                    return {"channel_id": channel_id, "arena": arena.to_dict()}
        return None

    def __generate_random_id(self, length: int) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return "".join(random.choice(letters_and_digits) for _ in range(length))
