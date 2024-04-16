import pygame, game    

if __name__ == '__main__':
    screen_width = 800
    screen_height = 500
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    playing_game = True
    debug = False

    timestep_per_episode = []
    reward_gained_per_episode = []

    # Game setup
    player_one = game.Player(0, game.Paddle(5,50,5), True)
    player_two = game.Player(1, game.Paddle(5,50,5), True)

    game = game.Game(player_one, player_two, game.Ball(1,6,6), (screen_width,screen_height), screen, debug)

    while running:
        for episode in range(100):
            playing_game = True
            timestep = 0
            reward = 0
            while playing_game:
            # Frame cap
                dt = clock.tick(0)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game.save_winner()
                        running = False
                
                # Clear screen
                screen.fill("black")
                playing_game, step_reward = game.calc_frame(dt)
                timestep += 1
                reward += step_reward
                pygame.display.flip()
            print('Game', episode + 1, 'finished')
            timestep_per_episode.append(timestep)
            reward_gained_per_episode.append(reward)
            if not running:
                break
        running = False
        best_reward = max(reward_gained_per_episode)
        max_timesetps = max(timestep_per_episode)
        print('p1 best reward:', best_reward, '; Game:', reward_gained_per_episode.index(best_reward) + 1)
        print('p1 longest game:', max_timesetps, 'frames ; Game:', timestep_per_episode.index(max_timesetps) + 1)
        game.save_winner()