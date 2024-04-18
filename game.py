import random, agent, pickle, os, pygame

class Paddle:

    def __init__(self, speed: int, height: int, width: int) -> None:
        self.x_pos: int = 0
        self.y_pos: int = 0
        self.speed = speed
        self.height = height
        self.width = width
    
    def reset_paddle_position(self, screen_dimentions: tuple[int,int]):
        self.y_pos = int(screen_dimentions[1] / 2)

class Ball():

    def __init__(self, speed, height: int, width: int) -> None:
        self.pos = (0,0)
        self.speed = speed
        self.height = height
        self.width = width
        self.rect = pygame.Rect(self.pos, (self.width, self.height))
        self.direction = (0,0)

    def set_rect(self, ball_rect_pos:tuple[int,int]):
        self.rect.x = ball_rect_pos.x
        self.rect.y = ball_rect_pos.y

    def flip_ball_x(self):
        self.direction = (-self.direction[0], self.direction[1])
    
    def flip_ball_y(self):
        self.direction = (self.direction[0], -self.direction[1])
    
    def randomize_direction(self):
        self.direction = (1 if random.random() < 0.5 else -1, 1 if random.random() < 0.5 else -1)
    
    def reset_ball(self, screen_dimentions: tuple[int,int]):
        self.randomize_direction()
        self.rect.x = screen_dimentions[0] / 2
        self.rect.y = screen_dimentions[1] / 2
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.width, self.height)
    

class Player():

    def __init__(self, id: int, paddle: Paddle, ai: bool) -> None:
        # Maybe replace with agent
        self.id = id
        self.paddle = paddle
        self.rect = pygame.Rect(self.paddle.x_pos, self.paddle.y_pos, self.paddle.width, self.paddle.height)
        self.ai = ai
        
    def init_agent(self, screen_dimentions: tuple[int,int]):
        _max_actions = 3
        
        self.agent = agent.Agent(screen_dimentions[1], screen_dimentions[0], screen_dimentions[1], _max_actions)
        if os.path.exists("qtable.pickle"):
            with open("qtable.pickle", "rb") as f:
                self.agent.q_table = pickle.load(f)
            print('Loaded q_table for Player', self.id)
        else:
            self.agent.initialize_q_table()

    def set_rect(self):
        self.rect = pygame.Rect(self.paddle.x_pos, self.paddle.y_pos, self.paddle.width, self.paddle.height)

class Game():
    
    def __init__(self, player_one: Player, player_two: Player, ball: Ball, screen_dimentions: tuple[int,int], screen: pygame.display, debug: bool) -> None:
        self.players = [player_one,player_two]
        self.screen_dimentions = screen_dimentions
        self.hasHuman = False
        self.ball = ball
        self.score = [0,0]
        self.screen = screen
        self.debug = debug
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
        self.ball.set_rect(self.ball.rect)
        
        self.ball.randomize_direction()

        for player in self.players:
            if player.ai:
                player.init_agent(screen_dimentions)

        self._draw_sprites()

    def save_winner(self):
        qtable = self.players[0].agent.q_table
        with open("qtable.pickle", "wb") as f:
            pickle.dump(qtable, f)
        print('Saved q_table')

    def calc_frame(self, dt):
        playing = True
        # One call to calculate movement, score, draw sprites, etc
        
        
        for player in self.players:
            if player.ai:
                state = (round(player.paddle.y_pos) - player.paddle.height, self.ball.rect.x, self.ball.rect.y)
                action = player.agent.choose_action(state, player.agent.q_table)
                self.move_paddle(player, action, dt)

        # Calculate the position of the ball relative to the paddle
        if self.ball.rect.y < player.paddle.y_pos:
            distance = player.paddle.y_pos - self.ball.rect.y
        elif player.paddle.y_pos <= self.ball.rect.y <= player.paddle.y_pos - player.paddle.height:
            distance = 0
        else:
            distance = self.ball.rect.y - (player.paddle.y_pos - player.paddle.height)

        # Calculate the percentage based on the distance
        max_distance = self.screen_dimentions[1]/ 2  # Assuming paddle height is the reference
        percentage = 1 - (distance / max_distance)

        # Calculate State and reward
        p1reward = 0
        p2reward = 0
        positive_reward = 0
        p1reward += max(0, min(percentage, .001))
        positive_reward += max(0, min(percentage, .001))
        if self.ball.rect.x <= self.ball.width / 2:
            p2reward += 10
            p1reward += -10
        if self.ball.rect.x >= self.screen_dimentions[0] - self.ball.width:
            p2reward += -10
            p1reward += 10
            positive_reward += 10
        if self.debug: print('Player 1 reward', p1reward, 'Player 2 reward', p2reward)
        
                
        
        _pressed = pygame.key.get_pressed()
        if not self.players[0].ai:
            if _pressed[pygame.K_w]:
                self.move_paddle(self.players[0], 1)
            if _pressed[pygame.K_s]:
                self.move_paddle(self.players[0], -1)
        if not self.players[1].ai:
            if _pressed[pygame.K_UP]:
                self.move_paddle(self.players[1], 1)
            if _pressed[pygame.K_DOWN]:
                self.move_paddle(self.players[1], -1)
        # Set collision for players
        self.players[0].set_rect()
        self.players[1].set_rect()
        
        playing = self._move_ball(dt)
        for player in self.players:
            if player.ai:
                if player.id == 0:
                    reward = p1reward
                elif player.id == 1:
                    reward = p2reward
                player.agent.update_q_table(state, action, reward, (round(player.paddle.y_pos) - player.paddle.height, self.ball.rect.x, self.ball.rect.y))
        self._draw_sprites()
        return playing, positive_reward
    
    def _draw_sprites(self):
        # Draw player one
        pygame.draw.rect(self.screen, (255,255,255), self.players[0].rect)
        # Draw player two
        pygame.draw.rect(self.screen, (255,255,255), self.players[1].rect)
        # Draw ball
        pygame.draw.rect(self.screen, (255,255,255), self.ball.rect)
    

    def _move_ball(self, dt):
        ball_rect_pos = self.ball.rect
        if not self._check_ball_collison(dt): return False

        # Move ball
        ball_rect_pos.x += self.ball.speed * self.ball.direction[0] * dt
        ball_rect_pos.y += self.ball.speed * self.ball.direction[1] * dt

        # Set new collision box
        self.ball.set_rect(ball_rect_pos)
        return True
    
    def move_paddle(self, player: Player, action: int, dt: float) -> None:
        y_pos = player.paddle.y_pos
        if action == 1 and y_pos > 0:
            y_pos -= player.paddle.speed * dt
        elif action == -1 and y_pos < self.screen_dimentions[1] - player.paddle.height:
            y_pos += player.paddle.speed * dt
        player.paddle.y_pos = max(0, min(y_pos, self.screen_dimentions[1] - player.paddle.height))
    
    def _check_paddle_collision(self):
        for player in self.players:
            if player.rect.colliderect(self.ball.rect):
                return player,True
        return None, False
    
    def _check_ball_collison(self, dt):
        _player, _paddle_collide = self._check_paddle_collision()
        if self.ball.rect.x + self.ball.direction[0] * self.ball.speed * dt >= self.screen_dimentions[0] - self.ball.width / 2:
            # Flip ball or reset it
            #self.ball.flip_ball_x()
            self.ball.reset_ball(self.screen_dimentions)
            self.players[0].paddle.reset_paddle_position(self.screen_dimentions)
            self.players[1].paddle.reset_paddle_position(self.screen_dimentions)
            # Score for p1
            self.score[0] += 1
            # Will print when working
            self.print_scores()
            return False

            

        if self.ball.rect.x + self.ball.direction[0] * self.ball.speed * dt <= -self.ball.width / 2:
            # Flip ball or reset it
            #self.ball.flip_ball_x()
            self.ball.reset_ball(self.screen_dimentions)
            self.players[0].paddle.reset_paddle_position(self.screen_dimentions)
            self.players[1].paddle.reset_paddle_position(self.screen_dimentions)
            # Score for p2
            self.score[1] += 1
            self.print_scores()
            return False

        if self.ball.rect.y + self.ball.direction[1] * self.ball.speed * dt > self.screen_dimentions[1] - self.ball.height:
            self.ball.direction = (self.ball.direction[0], -abs(self.ball.direction[1]))
        if self.ball.rect.y + self.ball.direction[1] * self.ball.speed * dt <= self.ball.height:
            self.ball.direction = (self.ball.direction[0], abs(self.ball.direction[1]))
        
        if _paddle_collide:
            # Might move this to own method and just return true so I can add reward for hitting
                self.ball.flip_ball_x()
                _height = self.ball.rect.y - _player.paddle.y_pos
                _percent = _height/_player.paddle.height
                # Change y direction based off of location hit
                if _percent <= .4:
                    _new_dir = -1
                if _percent > .4 and _percent < .6:
                    _new_dir = 0
                if _percent >= .6:
                    _new_dir = 1
                self.ball.direction = (self.ball.direction[0], _new_dir)
        return True
            

    def print_scores(self):
        player_one_score = self.score[0]
        player_two_score = self.score[1]
        score_message = f"Player One: {player_one_score} | Player Two: {player_two_score}"
        print(score_message)
