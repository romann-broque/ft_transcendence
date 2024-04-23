# Game area dimensions
GAME_HEIGHT = 600
GAME_WIDTH = 1000

# Game arena
MIN_PLAYER = 2
MAX_PLAYER = 10

# # Ball parameters
INITIAL_SPEEDX = 5
INITIAL_SPEEDY = 5
BALL_RADIUS = 15

# Paddle parameters
PADDLE_INITIAL_SPEED_RATE = 0.025
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_OFFSET = 60

# Game mode
LOCAL_MODE = 0
ONLINE_MODE = 1

# Game status
WAITING = 0
STARTED = 1
OVER = 2
# When all arenas are DEAD, the corresponding channel can be deleted
DEAD = 3

# Other states
LISTENING = 4
