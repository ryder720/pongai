import pygame, random, agent, pickle, os


class Paddle:

    def __init__(self, speed: int, height: int, width: int) -> None:
        self.x_pos: int = 0
        self.y_pos: int = 0
        self.speed = speed
        self.height = height
        self.width = width
    
    def reset_paddle_position(self, screen_dimentions: tuple[int,int]):
        self.y_pos = int(screen_dimentions[1] / 2)


class Player():

    def __init__(self, id: int, paddle: Paddle, ai: bool) -> None:
        # Maybe replace with agent
        self.id = id
        self.paddle = paddle
        self.rect = pygame.Rect(self.paddle.x_pos, self.paddle.y_pos, self.paddle.width, self.paddle.height)
        self.ai = ai
        
    def init_agent(self, screen_width, screen_height, rows, columns):
        _max_actions = 3
        
        self.agent = agent.Agent(rows, rows, columns, _max_actions)
        if os.path.exists("qtable.pickle"):
            with open("qtable.pickle", "rb") as f:
                self.agent.q_table = pickle.load(f)
            print('Loaded q_table for Player', self.id)
        else:
            self.agent.initialize_q_table()

    def set_rect(self):
        self.rect = pygame.Rect(self.paddle.x_pos, self.paddle.y_pos, self.paddle.width, self.paddle.height)

class Ball():

    def __init__(self, speed, height: int, width: int) -> None:
        self.x_pos = 0
        self.y_pos = 0
        self.speed = speed
        self.height = height
        self.width = width
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)
        self.direction = (0,0)

    def set_rect(self):
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)

    def flip_ball_x(self):
        self.direction = (-self.direction[0], self.direction[1])
    
    def flip_ball_y(self):
        self.direction = (self.direction[0], -self.direction[1])
    
    def randomize_direction(self):
        self.direction = (1 if random.random() < 0.5 else -1, 1 if random.random() < 0.5 else -1)
    
    def reset_ball(self, screen_dimentions: tuple[int,int]):
        self.randomize_direction()
        self.x_pos = screen_dimentions[0] / 2
        self.y_pos = screen_dimentions[1] / 2
    
class Game():
    
    def __init__(self, player_one: Player, player_two: Player, ball: Ball, screen_dimentions: tuple[int,int]) -> None:
        self.players = [player_one,player_two]
        self.screen_dimentions = screen_dimentions
        self.hasHuman = False
        self.ball = ball
        self.score = [0,0]
        self.grid_rows = 15
        self.grid_columns = 15
        if not player_one.ai or not player_two.ai:
            self.hasHuman = True
        
        


        # Set up game
        self.players[0].paddle.x_pos = 0
        self.players[0].paddle.y_pos = (int) (screen_dimentions[1] / 2)

        self.players[1].paddle.x_pos = screen_dimentions[0] - self.players[1].paddle.width
        self.players[1].paddle.y_pos = (int) (screen_dimentions[1] / 2)

        self.ball.reset_ball(screen_dimentions)

        # Set collision box
        self.players[0].set_rect()
        self.players[1].set_rect()
        self.ball.set_rect()
        
        self.ball.randomize_direction()

        for player in self.players:
            if player.ai:
                player.init_agent(self.screen_dimentions[0], self.screen_dimentions[1], self.grid_rows, self.grid_columns)

        self._draw_sprites()

    def save_winner(self):
        if self.score[0] > self.score[1]:
            qtable = self.players[0].agent.q_table
        else:
            qtable = self.players[0].agent.q_table
        with open("qtable.pickle", "wb") as f:
            pickle.dump(qtable, f)

    def calc_frame(self, dt):

        # One call to calculate movement, score, draw sprites, etc
        ball_row = (self.grid_rows * self.ball.y_pos) / self.screen_dimentions[1]
        ball_col = (self.grid_columns * self.ball.x_pos) / self.screen_dimentions[0]
        
        for player in self.players:
            if player.ai:
                paddle_row = (self.grid_rows * player.paddle.y_pos) / self.screen_dimentions[1]
                state = (int(paddle_row), int(ball_row), int(ball_col), int(self.ball.direction[0]), int(self.ball.direction[1]))
                action = player.agent.choose_action(state, player.agent.q_table)
                self._move_paddle(player, action, dt)
                _player, _paddle_collide = self._check_paddle_collision()
                # Calculate State and reward
                reward = 0
                if player == _player and _paddle_collide:
                    reward += 10
                    print('Reward: Player', player.id, '+', reward)
                
                if player.id == 0:
                    if self.ball.x_pos == screen_width - self.ball.width:
                        reward += 10
                        print('Reward: Player', player.id, '+', reward)
                    if self.ball.x_pos == 0:
                        reward += -15
                        print('Reward: Player', player.id, '+', reward)
                if player.id == 1:
                    if self.ball.x_pos == 0:
                        reward += 10
                        print('Reward: Player', player.id, '+', reward)
                    if self.ball.x_pos == screen_width - self.ball.width:
                        reward += -15
                        print('Reward: Player', player.id, '+', reward)
                
                
        
        _pressed = pygame.key.get_pressed()
        if not self.players[0].ai:
            if _pressed[pygame.K_w]:
                self._move_paddle(self.players[0], 1)
            if _pressed[pygame.K_s]:
                self._move_paddle(self.players[0], -1)
        if not self.players[1].ai:
            if _pressed[pygame.K_UP]:
                self._move_paddle(self.players[1], 1)
            if _pressed[pygame.K_DOWN]:
                self._move_paddle(self.players[1], -1)
        # Set collision for players
        self.players[0].set_rect()
        self.players[1].set_rect()

        
        self._move_ball(dt)
        ball_row = (self.grid_rows * self.ball.y_pos) / self.screen_dimentions[1]
        
        ball_col = (self.grid_columns * self.ball.x_pos) / self.screen_dimentions[0]
        for player in self.players:
            if player.ai:
                paddle_row = (self.grid_rows * player.paddle.y_pos) / self.screen_dimentions[1]
                player.agent.update_q_table(state, action, reward, (int(paddle_row), int(ball_row), int(ball_col), int(self.ball.direction[0]), int(self.ball.direction[1])))
        self._draw_sprites()
    
    def _draw_sprites(self):
        # Draw player one
        pygame.draw.rect(screen, (255,255,255), self.players[0].rect)
        # Draw player two
        pygame.draw.rect(screen, (255,255,255), self.players[1].rect)
        # Draw ball
        pygame.draw.rect(screen, (255,255,255), self.ball.rect)

    def _move_ball(self, dt):
        
        self._check_ball_collison()

        # Move ball
        self.ball.x_pos += self.ball.direction[0] * dt
        self.ball.y_pos += self.ball.direction[1] * dt

        # Set new collision box
        self.ball.set_rect()
    
    def _move_paddle(self, player:Player, action: int, dt):
        if action == 1:
            if not player.paddle.y_pos < 0:
                player.paddle.y_pos -= player.paddle.speed * dt
        elif action == -1:
            if not player.paddle.y_pos > screen_height - player.paddle.height:
                player.paddle.y_pos += player.paddle.speed * dt
    
    def _check_paddle_collision(self):
        for player in self.players:
            if player.rect.colliderect(self.ball.rect):
                return player,True
        return None, False
    def _check_ball_collison(self):
        _player, _paddle_collide = self._check_paddle_collision()
        if self.ball.x_pos + self.ball.direction[0] > screen_width - self.ball.width:
            # Score for p1
            self.score[0] += 1
            self._print_score()

            # Flip ball or reset it
            #self.ball.flip_ball_x()
            self.ball.reset_ball(self.screen_dimentions)
            self.players[0].paddle.reset_paddle_position(self.screen_dimentions)
            self.players[1].paddle.reset_paddle_position(self.screen_dimentions)

        if self.ball.x_pos + self.ball.direction[0] < 0:
            # Score for p2
            self.score[1] += 1
            self._print_score()

            # Flip ball or reset it
            #self.ball.flip_ball_x()
            self.ball.reset_ball(self.screen_dimentions)
            self.players[0].paddle.reset_paddle_position(self.screen_dimentions)
            self.players[1].paddle.reset_paddle_position(self.screen_dimentions)

        if self.ball.y_pos + self.ball.direction[1] > screen_height or self.ball.y_pos + self.ball.direction[1] <= 0:
            # Bounce ball
            self.ball.flip_ball_y()
        
        if _paddle_collide:
            # Might move this to own method and just return true so I can add reward for hitting
                self.ball.flip_ball_x()
                _height = self.ball.y_pos - _player.paddle.y_pos
                _percent = _height/_player.paddle.height
                # Change y direction based off of location hit
                if _percent <= .4:
                    _new_dir = -1
                if _percent > .4 and _percent < .6:
                    _new_dir = 0
                if _percent >= .6:
                    _new_dir = 1
                self.ball.direction = (self.ball.direction[0], _new_dir)
            

    def _print_score(self):
        print('Player One: ' + repr(self.score[0]) + ' | Player Two: ' + repr(self.score[1]))

        

if __name__ == '__main__':
    screen_width = 800
    screen_height = 500
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    playing_game = False

    # Game setup
    player_one = Player(0, Paddle(3,50,5), True)
    player_two = Player(1, Paddle(3,50,5), True)

    game = Game(player_one, player_two, Ball(.25,6,6), (screen_width,screen_height))

    while running:
        # Frame cap
        dt = clock.tick(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.save_winner()
                running = False
        
        # Clear screen
        screen.fill("black")
        game.calc_frame(dt)

        # Start game
        if playing_game:
            pass
        
        pygame.display.flip()