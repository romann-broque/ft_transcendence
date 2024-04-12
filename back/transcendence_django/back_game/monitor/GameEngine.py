import asyncio
import logging
from back_game.game_settings.game_constants import *

log = logging.getLogger(__name__)

class GameEngine:
    def __init__(self):
        self.arenas = []
        self.game_loop_task = None
        self.started = False

    def addArena(self, arena):
        self.arenas.append(arena)

    def removeArena(self, arena):
        self.arenas.remove(arena)

    async def start(self):
        if not self.started:
            self.game_loop_task = asyncio.create_task(self.run_game_loop())
            self.started = True

    async def run_game_loop(self):
        while any(arena.status != OVER for arena in self.arenas):
            self.update_game_states()
            await asyncio.sleep(1)
        self.started = False

    def update_game_states(self):
        for arena in self.arenas:
            if (arena.status == STARTED and arena.isEmpty())\
                or arena.status == OVER:
                self.gameOver(arena)

    def gameOver(self, arena):
        arena.status = OVER
        self.removeArena(arena)
        # send the end of game stats via the consumer.
        # room_name = arena.id