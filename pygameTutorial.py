from random import randint
from sys import exit
import pygame

SCREENWIDTH = 800
SCREENHEIGHT = 400
SKYX, SKYY = 0, 0
GROUNDX, GROUNDY = 0, 300
TEXTX, TEXTY = 300, 50
TEXTCOLOR = (64, 64, 64)
TEXTBOXCOLOR = '#c0e8ec'
GAMEOVER_COLOR = (94, 129, 162)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        playerWalk1 = pygame.image.load(
            'graphics/player/player_walk_1.png').convert_alpha()
        playerWalk2 = pygame.image.load(
            'graphics/player/player_walk_2.png').convert_alpha()
        self.playerWalk = [playerWalk1, playerWalk2]
        self.playerIndex = 0
        self.playerJump = pygame.image.load(
            'graphics/player/jump.png').convert_alpha()

        self.image = self.playerWalk[1]
        self.rect = self.image.get_rect(midbottom=(80, GROUNDY))
        self.gravity = 0

        self.jumpSound = pygame.mixer.Sound('audio/jump.wav')
        self.jumpSound.set_volume(0.3)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= GROUNDY:
            self.gravity = -20
            self.jumpSound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= GROUNDY:
            self.rect.bottom = GROUNDY

    def animate(self):
        if self.rect.bottom < GROUNDY:
            self.image = self.playerJump
        else:
            self.playerIndex += 0.1
            if self.playerIndex >= len(self.playerWalk):
                self.playerIndex = 0
            self.image = self.playerWalk[int(self.playerIndex)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animate()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'fly':
            fly1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly1, fly2]
            yPos = GROUNDY - 90
            self.animationSpeed = 0.4
        else:
            snail1 = pygame.image.load(
                'graphics/snail/snail1.png').convert_alpha()
            snail2 = pygame.image.load(
                'graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail1, snail2]
            yPos = GROUNDY
            self.animationSpeed = 0.04

        self.animationIndex = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(
            midbottom=(randint(900, 1100), yPos))

    def animate(self):
        self.animationIndex += self.animationSpeed
        if self.animationIndex >= len(self.frames):
            self.animationIndex = 0
        self.image = self.frames[int(self.animationIndex)]

    def update(self):
        self.rect.x -= 5
        self.destroy()
        self.animate()

    def destroy(self):
        if self.rect.right <= 0:
            self.kill()


def displayScore(score=''):
    currentTime = pygame.time.get_ticks()
    if score == '':
        score = (currentTime - startTime)//1000
    scoreSurface = TextFont.render(f'Score: {score}', False, TEXTCOLOR)
    scoreRect = scoreSurface.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT/8))
    screen.blit(scoreSurface, scoreRect)


def displayGameOverScreen(score):
    screen.fill(GAMEOVER_COLOR)
    displayScore(score)
    screen.blit(playerStand, playerStandRect)
    screen.blit(gameName, gameNameRect)
    instructionSurface = TextFont.render(
        'Press space to start', False, TEXTCOLOR)
    instructionRect = instructionSurface.get_rect(
        center=(SCREENWIDTH/2, 7 * SCREENHEIGHT/8))
    screen.blit(instructionSurface, instructionRect)


def collisionSprite():
    global finalScore
    if pygame.sprite.spritecollide(player.sprite, obstacleGroup, False):
        currentTime = pygame.time.get_ticks()
        finalScore = (currentTime - startTime) // 1000
        obstacleGroup.empty()
        return False
    return True


pygame.init()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
TextFont = pygame.font.Font('font/Pixeltype.ttf', 50)
pygame.display.set_caption('Runner')  # changes caption @ top of window
clock = pygame.time.Clock()
startTime = 0
finalScore = 0
gameActive = False
backgroundMusic = pygame.mixer.Sound('audio/music.wav')
backgroundMusic.play(loops=-1)

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())
obstacleGroup = pygame.sprite.Group()

skySurface = pygame.image.load('graphics/Sky.png').convert()
groundSurface = pygame.image.load('graphics/ground.png').convert()

# intro screen
playerStand = pygame.image.load(
    'graphics/player/player_stand.png').convert_alpha()
playerStand = pygame.transform.rotozoom(playerStand, 0, 2)
playerStandRect = playerStand.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT/2))

gameName = TextFont.render('Pixel Runner', False, (111, 196, 169))
gameNameRect = gameName.get_rect(center=(400, 80))

# Timer
obstacleTimer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacleTimer, 1500)

# GAME LOOP
while(True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if gameActive:
            if event.type == obstacleTimer:
                if randint(0, 4):
                    obstacleGroup.add(Obstacle('snail'))
                else:
                    obstacleGroup.add(Obstacle('fly'))
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                gameActive = True
                startTime = pygame.time.get_ticks()

    if gameActive:
        # draw all elements
        screen.blit(skySurface, (SKYX, SKYY))  # block image transfer
        screen.blit(groundSurface, (GROUNDX, GROUNDY))

        displayScore()

        player.update()
        player.draw(screen)

        obstacleGroup.update()
        obstacleGroup.draw(screen)

        gameActive = collisionSprite()
    else:
        playerGravity = 0
        displayGameOverScreen(finalScore)

    # update all
    pygame.display.update()
    clock.tick(60)  # set maximum framerate
