import logging
import math
from typing import Any

from back_game.game_entities.ball import Ball
from back_game.game_entities.paddle import Paddle
from back_game.game_physics.ball_collider import BallCollider
from back_game.game_physics.edges import Edges
from back_game.game_physics.paddle_collider import PaddleCollider
from back_game.game_physics.position import Position
from back_game.game_settings.dict_keys import BALL, POSITION

logger = logging.getLogger(__name__)


class Collision:

    @staticmethod
    def is_paddle_collision(ball: Ball, paddle: Paddle) -> bool:
        """
        Checks if the ball collides with a paddle.
        """
        collision_point: Position = PaddleCollider.get_collision_point(ball, paddle)
        distance_x: float = ball.position.x - collision_point.x
        distance_y: float = ball.position.y - collision_point.y
        distance: float = math.sqrt(distance_x**2 + distance_y**2)
        return distance < ball.radius

    @staticmethod
    def collide_with_paddle(ball: Ball, paddle: Paddle):
        BallCollider.push_ball(ball, paddle)
        collision_point = PaddleCollider.get_collision_point(ball, paddle)
        ball.speed = PaddleCollider.get_ball_speed_after_paddle_collision(
            paddle, collision_point
        )
        logger.info("New speed is: %s", ball.speed.__dict__)

    @staticmethod
    def handle_collision(new_position: Position, ball: Ball):
        for paddle in ball.paddles.values():
            if Collision.is_paddle_collision(ball, paddle):
                Collision.collide_with_paddle(ball, paddle)
                return None
        score_update = BallCollider.ball_collide_with_wall(new_position, ball)
        return score_update

    @staticmethod
    def detect_collision(new_position: Position, ball: Ball) -> dict[str, Any]:
        update = Collision.handle_collision(new_position, ball)
        ball_position_update = {BALL: {POSITION: ball.position.__dict__}}
        return (
            {**update, **ball_position_update}
            if update is not None
            else ball_position_update
        )
