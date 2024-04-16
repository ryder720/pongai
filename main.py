import pygame, game    

if __name__ == '__main__':
    screen_width = 800
    screen_height = 500
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    playing_game = True

    # Game setup
    player_one = game.Player(0, game.Paddle(5,50,5), True)
    player_two = game.Player(1, game.Paddle(5,50,5), True)

    game = game.Game(player_one, player_two, game.Ball(1,6,6), (screen_width,screen_height), screen, False)

    while running:
        for episode in range(200000):
            playing_game = True
            while playing_game:
            # Frame cap
                dt = clock.tick(0)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game.save_winner()
                        running = False
                
                # Clear screen
                screen.fill("black")
                playing_game = game.calc_frame(dt)
                pygame.display.flip()
            print('Game', episode + 1, 'finished')
            if not running:
                break
        running = False
        game.save_winner()