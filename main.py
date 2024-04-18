import pygame, game    

if __name__ == '__main__':
    screen_width = 500
    screen_height = 300
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    playing_game = True
    debug = False

    timestep_per_episode = []
    reward_gained_per_episode = []
    learning_rate = [0.1, 0.5, 0.9, 1]


    # Game setup
    player_one = game.Player(0, game.Paddle(600,50,5), True)
    player_two = game.Player(1, game.Paddle(600,50,5), True)

    game = game.Game(player_one, player_two, game.Ball(500,6,6), (screen_width,screen_height), screen, debug)

while running:
        for episode in range(200):
            timestep_per_episode = []
            reward_gained_per_episode = []
            playing_game = True
            timestep = 0
            reward = 0
            while playing_game:
                # Frame cap
                dt = clock.tick(120) / 1000
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                # Clear screen
                screen.fill("black")
                playing_game, step_reward = game.calc_frame(dt)
                timestep += 1
                reward += step_reward
                pygame.display.flip()
                if not running:
                    break
            print('Game', episode + 1, 'finished with reward: ', reward)
            timestep_per_episode.append(timestep)
            reward_gained_per_episode.append(reward)
            if not running:
                break
        running = False
        game.save_winner()