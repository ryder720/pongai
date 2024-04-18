import pygame, game, time  

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

    # Game setup
    player_one = game.Player(0, game.Paddle(600,50,5), True)
    player_two = game.Player(1, game.Paddle(600,50,5), True)

    game = game.Game(player_one, player_two, game.Ball(500,6,6), (screen_width,screen_height), screen, debug)

    while running:
            episodes = 200000
            episodes_ran = 0
            start_time = time.time()
            for episode in range(episodes):
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
                print('Game', episode + 1, 'out of', episodes ,'finished with reward: ', reward)
                episodes_ran += 1
                timestep_per_episode.append(timestep)
                reward_gained_per_episode.append(reward)
                if not running:
                    break
            end_time = time.time()
            total_time = end_time - start_time
            total_time_hours = 0
            if total_time > 3600:
                total_time_hours = total_time / 3600
            print(episodes_ran, 'episodes finished in', int(total_time_hours), 'hours', round(total_time - int(total_time_hours) * 3600), 'seconds')
            running = False
            game.save_winner()