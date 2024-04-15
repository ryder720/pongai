import pygame, game    

if __name__ == '__main__':
    screen_width = 800
    screen_height = 500
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    playing_game = False

    # Game setup
    player_one = game.Player(0, game.Paddle(5,50,5), True)
    player_two = game.Player(1, game.Paddle(5,50,5), True)

    game = game.Game(player_one, player_two, game.Ball(1,6,6), (screen_width,screen_height), screen)

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