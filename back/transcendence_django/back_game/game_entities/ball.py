from back_game.game_settings.game_constants import  GAME_WIDTH, GAME_HEIGHT, BALL_RADIUS, INITIAL_SPEEDX, INITIAL_SPEEDY
from back_game.game_physics.position import Position
from back_game.game_physics.vector import Vector
import math

import logging
logger = logging.getLogger(__name__)

class Ball:
   def __init__(self, paddles):
      self.position = Position(GAME_WIDTH / 2, GAME_HEIGHT / 2)
      self.speed = Vector(INITIAL_SPEEDX, INITIAL_SPEEDY)
      self.radius = BALL_RADIUS
      self.paddles = paddles
      self.hasCollided = {paddle.slot : False for paddle in paddles}

   def update(self, newPosition, newSpeed, newRadius):
      self.position.setCoordinates(newPosition.x, newPosition.y)
      self.speed.setCoordinates(newSpeed.x, newSpeed.y)
      self.radius = newRadius

   def to_dict(self):
      return {
         'position': self.position.to_dict(),
         'speed': self.speed.to_dict(),
         'radius': self.radius
      }

   def set_position(self, position):
      x = position.x
      y = position.y
      if x < self.radius or x > GAME_WIDTH - self.radius:
         raise ValueError("Ball x-coordinate is out of bounds.")
      elif y < self.radius or y > GAME_HEIGHT - self.radius:
         raise ValueError("Ball y-coordinate is out of bounds.")
      self.position.setCoordinates(x, y)

   def move(self):
      new_position = Position(
         self.position.x + self.speed.x,
         self.position.y + self.speed.y)
      self.update_position(new_position)

   def update_collision(self, paddle):
      if self.is_paddle_collision(self.position, paddle):
         self.update_position(self.position)

   def update_position(self, new_position):
      for paddle in self.paddles:
         if self.is_paddle_collision(self.position, paddle):
            self.__push_ball(paddle)
            new_position = self.position
            break
            # return # Exit the function after handling the collision

      # If no collision with paddles, proceed with the normal update
      self.__update_wall_collision(new_position)

   def __push_ball(self, paddle):
      side = self.get_collision_side(self.position, paddle)
      push_position = Position(self.position.x, self.position.y)
      if side == "top":
         push_position.y = paddle.top - self.radius
      elif side == "bottom":
         push_position.y = paddle.bottom + self.radius
      elif side == "left":
         push_position.x = paddle.left - self.radius
      elif side == "right":
         push_position.x = paddle.right + self.radius
      self.set_position(push_position)
      # Adjust the ball's position based on the collision point
      if side == "top" or side == "bottom":
         # Ball hits the top of the paddle
         self.speed.y *= -1
      if side == "left" or side == "right":
         # Ball hits the left or right side of the paddle
         self.speed.x *= -1
      logger.info(f"Ball collided with paddle {paddle.slot} on the {side} side.")

   def is_paddle_collision(self, position, paddle):
      """
      Checks if the ball collides with a paddle.
      """
      # Calculate the distance from the ball's center to the closest point on the paddle
      closest_x = max(min(position.x, paddle.right), paddle.left)
      closest_y = max(min(position.y, paddle.bottom), paddle.top)
      distance_x = position.x - closest_x
      distance_y = position.y - closest_y
      distance = math.sqrt(distance_x**2 + distance_y**2)

      # Check if the distance is less than or equal to the ball's radius
      return distance < self.radius

   def get_collision_side(self, position, paddle):
      """
      Determines which side of the paddle the ball collides with, accurately considering the ball's radius.
      """
      # Calculate the distance from the ball's center to the closest point on the paddle's edge
      closest_x = max(min(position.x, paddle.right), paddle.left)
      closest_y = max(min(position.y, paddle.bottom), paddle.top)
      distance_x = position.x - closest_x
      distance_y = position.y - closest_y

      # Determine which side of the paddle the ball hits
      if abs(distance_x) > abs(distance_y):
         # The ball hits the left or right side of the paddle
         if distance_x > 0:
               return "right"
         else:
               return "left"
      else:
         # The ball hits the top or bottom side of the paddle
         if distance_y > 0:
               return "bottom"
         else:
               return "top"

   def __update_wall_collision(self, new_position):
      if new_position.x <= self.radius or new_position.x >= GAME_WIDTH - self.radius:
         self.speed.x *= -1
      if new_position.y <= self.radius or new_position.y >= GAME_HEIGHT - self.radius:
         self.speed.y *= -1
      else:
         self.position = new_position

   def reset(self):
      self.position = Position(GAME_WIDTH / 2, GAME_HEIGHT / 2)
      self.speed = Vector(5, 5)
