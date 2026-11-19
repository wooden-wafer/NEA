# Import Libraries
import pygame
import math
import random
import tkinter
from tkinter import messagebox
import sqlite3

#Button class: Creates a button that executes a function upon being clicked
class Button:
    #Intialising the button
    def __init__(self, size = (100, 50), position = (0, 0), colour = (0, 0, 0)):
        self.width = size[0]
        self.height = size[1]
        self.x = position[0]
        self.y = position[1]
        self.colour = colour
        self.locked = False

    #Displaying the button on the screen
    def draw(self, screen):
        pygame.draw.rect(screen, (self.colour), (self.x, self.y, self.width, self.height))

    #Checking for mouse click on button
    def collision(self, mouse_pos):
        if self.locked == False:
            if self.x <= mouse_pos[0] <= self.x + self.width:
                if self.y <= mouse_pos[1] <= self.y + self.height:
                    return True
        return False

#Text button class: Button that can have text
class TextButton(Button):
    #Intialising the button
    def __init__(self, size, position, colour, text = "", font_size = 20, font_colour = (255, 255, 255)):
        super().__init__(size, position, colour)
        self.text = text
        self.font_size = font_size
        self.font_colour = font_colour

    #Displaying the button on the screen
    def draw(self, screen):
        pygame.draw.rect(screen, (self.colour), (self.x, self.y, self.width, self.height))
        if self.text != "":
            font = pygame.font.SysFont("Tahoma", self.font_size)
            text = font.render(self.text, 1, self.font_colour)
            screen.blit(text, (self.x+(self.width/2-text.get_width()/2), self.y+(self.height/2-text.get_height()/2)))

#Icon button class: Button that can have an icon
class IconButton(Button):
    #Intialising the button
    def __init__(self, size, position, colour, icon = ""):
        super().__init__(size, position, colour)
        self.icon = icon

    #Displaying the button on the screen
    def draw(self, screen):
        pygame.draw.rect(screen, (self.colour), (self.x, self.y, self.width, self.height))
        if self.icon != "":
            image = pygame.image.load(self.icon)
            image = pygame.transform.scale(image, (self.width-2, self.height-2))
            screen.blit(image, (self.x + 1, self.y + 1))

#Toggle button class: Button that can toggle between three different states
class ToggleButton(TextButton):
    def __init__(self, size, position, colour1, colour2, colour3, text1 = "", text2 = "", text3 = "", font_size = 20, font_colour = (255, 255, 255)):
        super().__init__(size, position, colour1, text1, font_size, font_colour)
        self.colour1 = colour1
        self.text1 = text1
        self.colour2 = colour2
        self.text2 = text2
        self.colour3 = colour3
        self.text3 = text3
        self.toggle_state = 0

    #Toggles between states
    def toggle(self):
        self.toggle_state += 1
        self.toggle_state = self.toggle_state % 3

        if self.toggle_state == 0:
            self.colour = self.colour1
            self.text = self.text1
        if self.toggle_state == 1:
            self.colour = self.colour2
            self.text = self.text2
        if self.toggle_state == 2:
            self.colour = self.colour3
            self.text = self.text3

        return self.toggle_state

#Slider class: Range slider
class Slider:
    #Initialising the slider
    def __init__(self, x, y, percent):
        self.x = x
        self.y = y
        self.min = x
        self.max = x + 300

        self.percent = percent
        self.backgroundRect = pygame.Rect(x, y, 300, 20)
        self.thumb_x = self.x + 3*self.percent
        self.thumb_y = self.y + 10
        self.changing = False
        self.font = pygame.font.SysFont("Tahoma", 15)

    #Displaying the slider and its value on the screen
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.backgroundRect)
        pygame.draw.rect(screen, (150, 150, 150), pygame.Rect(self.x, self.y, self.thumb_x - self.x, 20))
        pygame.draw.circle(screen, (150, 150, 150), (self.thumb_x, self.thumb_y), 15)

        screen.blit(self.font.render(f"{self.percent:.0f}%", 1, (0, 0, 0)), (self.x + 320, self.y))

    #Checking for mouse click on the slider
    def collision(self, mouse_pos):
        if self.thumb_x -15 <= mouse_pos[0] <= self.thumb_x + 15:
            if self.thumb_y - 15 <= mouse_pos[1] <= self.thumb_y + 15:
                self.changing = True

    #Moving the slider to the mouse if it is in bounds of the slider
    def move(self, mouse_x):
        if mouse_x < self.min:
            mouse_x = self.min
        if mouse_x > self.max:
            mouse_x = self.max

        self.thumb_x = mouse_x
        self.percent = ((self.thumb_x - self.x) / 3 ) // 1

    #Returns the percent attribute as a decimal
    def return_percentage(self):
        return self.percent / 100

#Melee attack class: Perform a melee attack with specified damage and range.
class MeleeAttack:
    #Initialising the melee attack
    def __init__(self, damage, range):
        self.damage = damage
        self.range = range
        self.hitlist = []
        self.melee_image = pygame.image.load("Sprites/melee_image.png").convert_alpha()
        self.weapon_rect = pygame.Rect(0, 0, 0, 0)

    #Displaying the attack on the screen
    def draw(self, screen, mouse_pos, player_pos):
        vector = [mouse_pos[0] - player_pos[0], (mouse_pos[1] - player_pos[1])]
        hyp = math.sqrt((vector[0])**2 + (vector[1])**2)
        if hyp > 0:
            vector = [self.range*vector[0]/hyp, self.range*vector[1]/hyp]
            angle = math.acos(vector[0]/self.range)
            if vector[1] > 0:
                angle *= -1
            rot_img = pygame.transform.rotate(self.melee_image, 90+(angle*180/math.pi))
            rot_img.set_colorkey((0, 0, 0))
            screen.blit(rot_img, (player_pos[0] + vector[0] - rot_img.get_width()/2, player_pos[1] + vector[1] - rot_img.get_height()/2))

            self.weapon_rect = rot_img.get_rect()
            self.weapon_rect.x = player_pos[0] + vector[0] - rot_img.get_width()/2
            self.weapon_rect.y = player_pos[1] + vector[1] - rot_img.get_height()/2

    #Detecting if the melee attack has hit an enemy
    def detect_collision(self, enemy):
        if enemy not in self.hitlist:
            if self.weapon_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                self.hitlist.append(enemy)
                enemy.take_damage(self.damage)

#Spell1 class: Perform the first spell
class Spell1:
    #initialising the first spell
    def __init__(self, damage, mouse_pos, player_pos):
        self.damage = damage
        self.hitlist = []
        self.spell_image = pygame.image.load("Sprites/spell.png").convert_alpha()
        self.spell_image = pygame.transform.scale(self.spell_image, (90, 90))

        vector = [mouse_pos[0] - player_pos[0], (mouse_pos[1] - player_pos[1])]
        hyp = math.sqrt((vector[0])**2 + (vector[1])**2)
        if hyp > 0:
            self.vector = [20*vector[0]/hyp, 20*vector[1]/hyp]
            angle = math.acos(self.vector[0]/20)
            if self.vector[1] > 0:
                angle *= -1
            self.rot_img = pygame.transform.rotate(self.spell_image, -90 + (angle*180/math.pi))
            self.rot_img.set_colorkey((0, 0, 0))
            self.initial_x = player_pos[0] + self.vector[0] - self.rot_img.get_width()/2
            self.initial_y = player_pos[1] + self.vector[1] - self.rot_img.get_height()/2

        self.weapon_rect = pygame.Rect(0, 0, 0, 0)

    #Displaying the first spell on the screen
    def draw(self, screen, current_tick):
        screen.blit(self.rot_img, (self.initial_x + current_tick * self.vector[0], self.initial_y + current_tick * self.vector[1]))
        self.weapon_rect = pygame.Rect(self.initial_x + current_tick * self.vector[0], self.initial_y + current_tick * self.vector[1], self.rot_img.get_width(), self.rot_img.get_height())

    #Detecting if the first spell has hit an enemy
    def detect_collision(self, enemy):
        if enemy not in self.hitlist:
            if self.weapon_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                self.hitlist.append(enemy)
                enemy.take_damage(self.damage)

#Spell2 class: Perform the second spell
class Spell2:
    #Initialising the second spell
    def __init__(self, damage, diameter, player_pos):
        self.damage = damage
        self.diameter = diameter
        self.hitlist = []
        self.bomb_image = pygame.image.load("Sprites/bomb.png").convert_alpha()
        self.bomb_image = pygame.transform.scale(self.bomb_image, (60, 60))
        self.bomb_image.set_colorkey((0, 0, 0))
        self.bomb_width = self.bomb_image.get_width()
        self.blast_image = pygame.image.load("Sprites/blast.png").convert_alpha()
        self.blast_image = pygame.transform.scale(self.blast_image, (diameter, diameter))
        self.blast_image.set_colorkey((0, 0, 0))
        self.x = player_pos[0]
        self.y = player_pos[1]
        self.timer = 0
        self.length = 120
        self.exploding = False
        self.weapon_rect = pygame.Rect(self.x - self.diameter/2, self.y - self.diameter/2, self.diameter, self.diameter)

    #Displaying the second spell on the screen
    def draw(self, screen, current_tick):
        if current_tick < self.length:
            screen.blit(self.bomb_image, (self.x - self.bomb_width/2, self.y - self.bomb_width/2))
        else:
            if self.exploding == False:
                pygame.mixer.Sound("Audios/spell2.mp3").play()
            self.exploding = True
            if self.timer < 30:
                screen.blit(self.blast_image, (self.x - self.diameter/2, self.y - self.diameter/2))
                self.timer += 1

    #Detecting if the second spell has hit an enemy
    def detect_collision(self, enemy):
        if self.exploding:
            if enemy not in self.hitlist:
                if self.weapon_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                    self.hitlist.append(enemy)
                    enemy.take_damage(self.damage)

#Level class: Creates a level where each tile is 60x60, creating a tile map of 32x18
class LevelScreen:
    #Initialises the level screen
    def __init__(self, x, y):
        self.level = pygame.Surface((1920, 1080))
        grassTileImage = pygame.image.load("Sprites/grassTile.png")
        self.enemies = []
        self.levelTileMap = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                ]

        row_index = 0
        for row in self.levelTileMap:
            column_index = 0
            for tile in row:
                if tile == 0:
                    self.level.blit(grassTileImage, (column_index * 60, row_index * 60))

                column_index += 1
            row_index += 1

        numberOfEnemies = random.randint(1, 8)
        numberOfTanks = random.randint(1, 3)

        for i in range(numberOfEnemies):
            self.enemies.append(Enemy(x = random.randint(300, 1620), y = random.randint(300, 780)))
        for i in range(numberOfTanks):
            self.enemies.append(Tank(x = random.randint(300, 1620), y = random.randint(300, 780)))

        self.top = False
        self.left = False
        self.bottom = False
        self.right = False

        self.x = x
        self.y = y

        self.locked = True
        self.discovered = False
        self.type = "normal"

    #Draws all of the tiles
    def drawtiles(self, screen):
        screen.blit(self.level, (0, 0))

    #Representation of the level
    def __repr__(self):
        return "1"

#First room in a game
class StartLevelScreen(LevelScreen):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.enemies = []
        self.locked = False
        self.type = "start"
        self.discovered = True

    def __repr__(self):
        return "2"

#Final room in a game
class EndLevelScreen(LevelScreen):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "end"

    def __repr__(self):
        return "3"

#Class that creates a new world
class World:
    #Constructor for world class
    def __init__(self):
        self.tileMap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.numberOfTiles = 1

        self.map = pygame.image.load("Sprites/map_background.png")
        pygame.Surface.set_alpha(self.map, 225)
        self.void_tile = pygame.image.load("Sprites/void_map_tile.png")
        self.locked_tile = pygame.image.load("Sprites/locked_map_tile.png")
        self.normal_tile = pygame.image.load("Sprites/normal_map_tile.png")
        self.start_tile = pygame.image.load("Sprites/start_map_tile.png")
        self.end_tile = pygame.image.load("Sprites/end_map_tile.png")
        self.player_indicator = pygame.image.load("Sprites/player_indicator.png")
        pygame.Surface.set_colorkey(self.player_indicator,  (255, 255, 255))
        
        self.map_enabled = False

        self.firstX = 0
        self.firstY = 0

    #Generate new world
    def generate(self):
        firstRoomX = random.randint(1, 6)
        firstRoomY = 6
        self.tileMap[firstRoomY][firstRoomX] = StartLevelScreen(firstRoomX, firstRoomY)
        self.firstRoom = (firstRoomX, firstRoomY)
        self.currentX = firstRoomX
        self.currentY = firstRoomY
        self.previousX = firstRoomX
        self.previousY = firstRoomY

        stopGenerating = False
        while stopGenerating == False:
            for i in range(len(self.tileMap)):
                for j in range(len(self.tileMap)):
                    if self.tileMap[i][j] != 0:
                        numberOfNeighbours = 0
                        skip = False
                        top = False
                        left = False
                        bottom = False
                        right = False

                        if stopGenerating == False and skip == False:
                            newTileX = 0
                            newTileY = 0
                            while newTileX == 0 and newTileY == 0:
                                newTileX = random.randint(-1, 1)
                                newTileY = random.randint(-1, 1)
                            if abs(newTileX) == abs(newTileY):
                                skip = True
                            newTileX += j
                            newTileY += i
                            if self.tileMap[newTileY][newTileX] != 0:
                                skip = True
                            if newTileX < 1 or newTileX > 6 or newTileY < 1 or newTileY > 6:
                                skip = True
                            else:
                                if self.tileMap[newTileY - 1][newTileX - 1] != 0:
                                    numberOfNeighbours += 1
                                if self.tileMap[newTileY - 1][newTileX] != 0:
                                    numberOfNeighbours += 1
                                    top = True
                                if self.tileMap[newTileY - 1][newTileX + 1] != 0:
                                    numberOfNeighbours += 1
                                if self.tileMap[newTileY][newTileX - 1] != 0:
                                    numberOfNeighbours += 1
                                    left = True
                                if self.tileMap[newTileY][newTileX + 1] != 0:
                                    numberOfNeighbours += 1
                                    right = True
                                if self.tileMap[newTileY + 1][newTileX - 1] != 0:
                                    numberOfNeighbours += 1
                                if self.tileMap[newTileY + 1][newTileX] != 0:
                                    numberOfNeighbours += 1
                                    bottom = True
                                if self.tileMap[newTileY + 1][newTileX + 1] != 0:
                                    numberOfNeighbours += 1
                                if numberOfNeighbours > 2:
                                    skip = True

                            if skip == False:
                                if self.numberOfTiles < 18:
                                    self.tileMap[newTileY][newTileX] = LevelScreen(newTileX, newTileY)
                                else:
                                    self.tileMap[newTileY][newTileX] = EndLevelScreen(newTileX, newTileY)
                                    self.lastRoom = (newTileX, newTileY)
                                self.numberOfTiles += 1
                                self.tileMap[newTileY][newTileX].top = top
                                self.tileMap[newTileY][newTileX].left = left
                                self.tileMap[newTileY][newTileX].bottom = bottom
                                self.tileMap[newTileY][newTileX].right = right
   
                        if self.numberOfTiles >= 19:
                            stopGenerating = True

        for y in range(len(self.tileMap)):
            for x in range(len(self.tileMap[y])):
                if self.tileMap[y][x] != 0:
                    if self.tileMap[y][x - 1] != 0:
                        self.tileMap[y][x].left = True
                    if self.tileMap[y][x + 1] != 0:
                        self.tileMap[y][x].right = True
                    if self.tileMap[y - 1][x] != 0:
                        self.tileMap[y][x].top = True
                    if self.tileMap[y + 1][x] != 0:
                        self.tileMap[y][x].bottom = True

    #Create and update map
    def createMap(self):    
        for i in range(len(self.tileMap)):
            for j in range(len(self.tileMap)):
                if self.tileMap[i][j] == 0:
                    self.map.blit(self.void_tile, (j*100, i*100))
                elif self.tileMap[i][j].discovered == False:
                    self.map.blit(self.locked_tile, (j*100, i*100))
                elif self.tileMap[i][j].type == "normal":
                    self.map.blit(self.normal_tile, (j*100, i*100))
                elif self.tileMap[i][j].type == "start":
                    self.map.blit(self.start_tile, (j*100, i*100))
                elif self.tileMap[i][j].type == "end":
                    self.map.blit(self.end_tile, (j*100, i*100))

        self.map.blit(self.player_indicator, (self.currentX*100, self.currentY*100))

    #Draw map on screen
    def drawMap(self, screen):
        screen.blit(self.map, (560, 140))

#Enemy class: Creates a default enemy that chases the player with a sword
class Enemy:
    #Initialising the enemy
    def __init__(self, x = 0, y = 0, vel = 3, width = 60, height = 60, damage = 1, hp = 20, range = 50, attack_length = 12, cooldown_length = 72, img = "Sprites/enemy_outline.png"):
        self.x = x
        self.y = y
        self.vel = vel
        self.width = width
        self.height = height
        self.damage = damage
        self.max_hp = hp
        self.hp = hp
        self.range = range
        
        self.melee_image = pygame.image.load("Sprites/melee_image.png")
        self.enemy_image = pygame.image.load(img)
        self.enemy_image = pygame.transform.scale(self.enemy_image, (self.width, self.height))

        self.player_hit = False
        self.attack_cooldown = True
        self.attack_cooldown_timer = random.randint(cooldown_length, 2 * cooldown_length)
        self.attack_timer = attack_length
        self.oact = cooldown_length
        self.oat = attack_length

        self.leniency_factor = 0.75

        self.type = "enemy"

    #Returns a vector that points towards the player and the angle it makes with the positive horizontal
    def returnTrigValues(self, player_pos):
        vector = [player_pos[0] - self.x, (player_pos[1] - self.y)]
        hyp = math.sqrt((vector[0])**2 + (vector[1])**2)
        if hyp > 0:
            vector = [vector[0]/hyp, vector[1]/hyp]
            angle = math.acos(vector[0])
            if vector[1] > 0:
                angle *= -1
        return (vector, angle)
    
    #Moves the enemy towards the player using the vector from the method above
    def move(self, screen, trigValues):
        vector = [trigValues[0][0]*self.vel, trigValues[0][1]*self.vel]
        self.x += vector[0]
        self.y += vector[1]
        screen.blit(self.enemy_image, (self.x, self.y))

    #Attacks the player periodically
    def attack(self, screen, trigValues, player_rect):
        collision = False
        
        if self.player_hit == True and self.attack_cooldown == False:
            vector = [trigValues[0][0]*self.range, trigValues[0][1]*self.range]
            angle = trigValues[1]
            rot_img = pygame.transform.rotate(self.melee_image, 90+(angle*180/math.pi))
            rot_img.set_colorkey((0, 0, 0))
            weapon_x = self.x + self.width/2 + vector[0] - rot_img.get_width()/2
            weapon_y = self.y + self.height/2 + vector[1] - rot_img.get_height()/2
            screen.blit(rot_img, (weapon_x, weapon_y))
            self.attack_timer -= 1
            
            weapon_rect = pygame.Rect(weapon_x, weapon_y, rot_img.get_width()*self.leniency_factor, rot_img.get_height()*self.leniency_factor)
            if weapon_rect.colliderect(player_rect):
                collision = True

        if self.attack_timer <= 0:
            self.player_hit = False
            self.attack_cooldown = True
            self.attack_timer = self.oat

        if self.attack_cooldown == True:
            self.attack_cooldown_timer -= 1

        if self.attack_cooldown_timer <= 0:
            self.attack_cooldown = False
            self.attack_cooldown_timer = self.oact

        return collision
    
    #Display the health of an enemy above it
    def display_health(self, screen):
        empty_bar = pygame.Rect(self.x, self.y - 25, self.width, 15)
        health_bar = pygame.Rect(self.x, self.y - 25, (self.hp/self.max_hp)*self.width, 15)
        pygame.draw.rect(screen, (255, 0, 0), empty_bar)
        pygame.draw.rect(screen, (0, 255, 0), health_bar)

    #Decrease hp attribute by damage parameter
    def take_damage(self, damage):
        self.hp -= damage
    
#Tank class: Class inherited from the enemy class
class Tank(Enemy):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y, vel = 1, width = 100, height = 100, damage = 2, hp = 50, range = 125, attack_length = 24, cooldown_length = 150)
        self.melee_image = pygame.transform.scale(self.melee_image, (140, 140))
        self.leniency_factor = 0.7

        self.type = "tank"

#Boss class: Class inherited from the enemy class
class Boss(Enemy):
    #Constructor for boss enemy
    def __init__(self, minion_countdown, difficulty):
        if difficulty == "easy":
            hp = 300
        if difficulty == "normal":
            hp = 500
        if difficulty == "hard":
            hp = 700

        super().__init__(x = 760, y = 340, vel = 1, width = 200, height = 200, damage = 3, hp = hp, range = 180, attack_length = 30, cooldown_length = 150)
        self.melee_image = pygame.transform.scale(self.melee_image, (200, 200))
        self.leniency_factor = 0.5
        
        self.timer = minion_countdown // 2
        self.minion_countdown = minion_countdown

        self.type = "boss"

    #Spawns minions
    def spawn_minions(self):
        self.timer -= 1
        minions = []

        if self.timer <= 0:
            number_of_minions = random.randint(3, 6)
            for x in range(number_of_minions):
                minion_x = random.randint(0, 1920)
                minion_y = random.randint(0, 1080)
                minion = Enemy(x = minion_x, y = minion_y, vel = 2)
                minions.append(minion)
            self.timer = self.minion_countdown

        return minions

#Player class: Creates a player object
class Player:
    #Initialise player
    def __init__(self, x = 935, y = 1000, width = 60, height = 60, hp = 5):
        self.x = x
        self.y = y
        self.vel = 5
        self.width = width
        self.height = height
        
        self.max_hp = hp
        self.hp = hp
        self.heal_amount = 1
        self.heal_triggered = False
        self.heal_cooldown = False
        self.heal_cooldown_timer = 3600

        self.is_up = False
        self.is_left = False
        self.is_down = False
        self.is_right = False

        image = pygame.image.load("Sprites/player_outline.png")
        self.image = pygame.transform.scale(image, (self.width, self.height))

        self.dash_up = False
        self.dash_left = False
        self.dash_down = False
        self.dash_right = False

        self.dash_cooldown = False
        self.dash_cooldown_timer = 120
        self.dash_timer = 12
        self.is_dashing = False

        self.melee = None
        self.melee_pressed = False
        self.melee_cooldown = True
        self.melee_cooldown_timer = 36
        self.melee_timer = 12

        self.immunity = False
        self.immunityTimer = 60

        self.mana = 100
        self.max_mana = 100

        self.spell1 = None
        self.spell1_trigger = False
        self.spell1_cooldown = False
        self.spell1_mana_cost = 25
        self.spell1_length = 180
        self.spell1_tick = 0

        self.spell2 = None
        self.spell2_trigger = False
        self.spell2_cooldown = False
        self.spell2_mana_cost = 30
        self.spell2_length = 150
        self.spell2_tick = 0

        self.mbRect = pygame.Rect(10, 100, 75, 300)

    #Move player if player inputs movement keys
    def move(self):
        if self.is_dashing == False:
            if self.is_up and self.y > 0:
                self.y -= self.vel
            if self.is_left and self.x > 0:
                self.x -= self.vel
            if self.is_down and self.y + self.height < 1080:
                self.y += self.vel
            if self.is_right and self.x + self.width < 1920:
                self.x += self.vel

    #Player dashes if they press the dash keybind and it is not on cooldown
    def dash(self):
        if self.is_dashing == True and self.dash_cooldown == False:
            if self.dash_timer == 12:
                self.dash_up = self.is_up
                self.dash_left = self.is_left
                self.dash_down = self.is_down
                self.dash_right = self.is_right
            if self.dash_up and self.y > 0:
                self.y -= self.vel*4
            if self.y < 0:
                self.y = 0
            if self.dash_left and self.x > 0:
                self.x -= self.vel*4
            if self.x < 0:
                self.x = 0
            if self.dash_down and self.y + self.height < 1080:
                self.y += self.vel*4
            if self.y + self.height > 1080:
                self.y = 1080 - self.height
            if self.dash_right and self.x + self.width < 1920:
                self.x += self.vel*4
            if self.x + self.width > 1920:
                self.x = 1920 - self.width
            self.dash_timer -= 1

            self.setImmunity()

        else:
            self.is_dashing = False

        if self.dash_timer <= 0:
            self.is_dashing = False
            self.dash_cooldown = True
            self.dash_timer = 12

            # TEST CODE
            print("DASH COOLDOWN ACTIVATED")

        if self.dash_cooldown == True:
            self.dash_cooldown_timer -= 1

        if self.dash_cooldown_timer <= 0:
            self.dash_cooldown = False
            self.dash_cooldown_timer = 120
            # TEST CODE
            print("DASH COOLDOWN DEACTIVATED")

    #Increments the player's hp if conditions are met
    def heal(self):
        if self.hp + self.heal_amount <= self.max_hp and self.heal_triggered == True and self.heal_cooldown == False:
            self.hp += self.heal_amount
            self.heal_triggered = False
            self.heal_cooldown = True
            # TEST CODE
            print("HEAL COOLDOWN ACTIVATED")
            if self.hp + self.heal_amount > self.max_hp:
                print("CANNOT HEAL. HEALTH ALREADY FULL")

        if self.heal_cooldown == True:
            self.heal_cooldown_timer -= 1

        if self.heal_cooldown_timer <= 0:
            self.heal_cooldown = False
            self.heal_cooldown_timer = 3600
            # TEST CODE
            print("HEAL COOLDOWN DEACTIVATED")

    #Performs melee attack if left click is pressed
    def meleePressed(self, screen):
        if self.melee_pressed == True and self.melee_cooldown == False:
            self.melee.draw(screen, pygame.mouse.get_pos(), (self.x + (self.width/2), self.y + (self.height/2)))
            self.melee_timer -= 1

        if self.melee_timer <= 0:
            self.melee_pressed = False
            self.melee_cooldown = True
            self.melee_timer = 12
            self.melee = None

        if self.melee_cooldown == True:
            self.melee_cooldown_timer -= 1

        if self.melee_cooldown_timer <= 0:
            self.melee_cooldown = False
            self.melee_cooldown_timer = 36

    #Performs first spell if 1 is pressed
    def spell1Pressed(self, screen):
        if self.spell1_trigger == True:
            self.spell1.draw(screen, self.spell1_tick)
            self.spell1_tick += 1
            self.spell1_cooldown = True

        if self.spell1_tick >= self.spell1_length:
            self.spell1_trigger = False
            self.spell1_tick = 0
            self.spell1_cooldown = False
            self.spell1 = None

    #Performs second spell if 2 is pressed
    def spell2Pressed(self, screen):
        if self.spell2_trigger == True:
            self.spell2.draw(screen, self.spell2_tick)
            self.spell2_tick += 1
            self.spell2_cooldown = True

        if self.spell2_tick >= self.spell2_length:
            self.spell2_trigger = False
            self.spell2_tick = 0
            self.spell2_cooldown = False
            self.spell2 = None

    #Sets player's immunity value to true, negating any damage for a small period of time
    def setImmunity(self):
        if self.immunityTimer > 0:
            self.immunity = True
            self.immunityTimer -= 1

        if self.immunityTimer <= 0:
            self.immunity = False
            self.immunityTimer = 60

    #Increases player mana every frame
    def increaseMana(self, amount):
        if self.mana < self.max_mana:
            self.mana += amount

        if self.mana > self.max_mana:
            self.mana = self.max_mana

    #Displays player mana
    def displayMana(self, screen):
        pygame.draw.rect(screen, (99, 99, 99), self.mbRect)
        pygame.draw.rect(screen, (32,41,167), pygame.Rect(10, 400-self.mana*3, 75, self.mana*3))

    #Displays player onto game window
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

#Game class: Manages all logic including game states, player, enemies and the world
class Game:
    #Initialising the game
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
    
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("Roguelike")
        self.screen.fill((176, 196, 222))

        self.clock = pygame.time.Clock()

        self.controls = {}

        try:
            with open("settings.txt", "r") as file:
                contents = file.read().split("\n")
                self.master_volume = float(contents[0])
                self.game_volume = float(contents[1])
                self.music_volume = float(contents[2])
                self.difficulty = contents[3]
                self.controls["ctrl_up"] = pygame.key.key_code(contents[4])
                self.controls["ctrl_left"] = pygame.key.key_code(contents[5])
                self.controls["ctrl_down"] = pygame.key.key_code(contents[6])
                self.controls["ctrl_right"] = pygame.key.key_code(contents[7])
                self.controls["ctrl_dash"] = pygame.key.key_code(contents[8])
                self.controls["ctrl_heal"] = pygame.key.key_code(contents[9])
                self.controls["ctrl_spell1"] = pygame.key.key_code(contents[10])
                self.controls["ctrl_spell2"] = pygame.key.key_code(contents[11])
                self.controls["ctrl_map"] = pygame.key.key_code(contents[12])
        
        except:
            self.master_volume = 1
            self.game_volume = 1
            self.music_volume = 1
            self.difficulty = "normal"
            self.controls["ctrl_up"] = pygame.K_w
            self.controls["ctrl_left"] = pygame.K_a
            self.controls["ctrl_down"] = pygame.K_s
            self.controls["ctrl_right"] = pygame.K_d
            self.controls["ctrl_dash"] = pygame.K_SPACE
            self.controls["ctrl_heal"] = pygame.K_h
            self.controls["ctrl_spell1"] = pygame.K_1
            self.controls["ctrl_spell2"] = pygame.K_2
            self.controls["ctrl_map"] = pygame.K_m

        self.allowed_controls = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, 
                                 pygame.K_o, pygame.K_p, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, 
                                 pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, 
                                 pygame.K_n, pygame.K_m, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, 
                                 pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_BACKSLASH, pygame.K_SLASH, pygame.K_BACKQUOTE, 
                                 pygame.K_SPACE, pygame.K_SEMICOLON, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET, pygame.K_LSHIFT, 
                                 pygame.K_RSHIFT, pygame.K_HASH, pygame.K_MINUS, pygame.K_EQUALS, pygame.K_COMMA, pygame.K_PERIOD, 
                                 pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]

        self.setting_control = ""

        self.colours = {
            "lime_green": (50, 205, 50),
            "light_steel_blue": (176, 196, 222),
            "red": (255, 0, 0),
            "forest_green": (34, 139, 34),
            "black": (0, 0, 0),
            "light_grey": (211, 211, 211),
            "dark_grey": (45, 45, 45),
            "lime": (0, 255, 0),
            "white": (255, 255, 255),
            "yellow": (255, 191, 0),
        }

        self.buttons = {
            "title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "ROGUELIKE", 75, self.colours["black"]),
            "settings_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "SETTINGS", 75, self.colours["black"]),
            "audio_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "AUDIO SETTINGS", 75, self.colours["black"]),
            "controls_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "CONTROLS", 75, self.colours["black"]),
            "game_settings_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "GAME SETTINGS", 75, self.colours["black"]),
            "lose_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "YOU LOSE", 75, self.colours["black"]),
            "win_title": TextButton((1000, 200), (460, 125), self.colours["light_steel_blue"], "YOU WIN", 75, self.colours["black"]),
            "leaderboard_title": TextButton((1000, 200), (450, 125), self.colours["light_steel_blue"], "LEADERBOARD", 75, self.colours["black"]),
            "master_volume": TextButton((400, 50), (500, 332.5), self.colours["light_steel_blue"], "MASTER VOLUME", 35, self.colours["black"]),
            "game_volume": TextButton((400, 50), (500, 482.5), self.colours["light_steel_blue"], "GAME VOLUME", 35, self.colours["black"]),
            "music_volume": TextButton((400, 50), (500, 632.5), self.colours["light_steel_blue"], "MUSIC VOLUME", 35, self.colours["black"]),
            "up_label": TextButton((70, 70), (1025, 325), self.colours["light_steel_blue"], "MOVE UP", 35, self.colours["black"]),
            "left_label": TextButton((70, 70), (1025, 405), self.colours["light_steel_blue"], "MOVE LEFT", 35, self.colours["black"]),
            "down_label": TextButton((70, 70), (1025, 485), self.colours["light_steel_blue"], "MOVE DOWN", 35, self.colours["black"]),
            "right_label": TextButton((70, 70), (1025, 565), self.colours["light_steel_blue"], "MOVE RIGHT", 35, self.colours["black"]),
            "dash_label": TextButton((70, 70), (1025, 645), self.colours["light_steel_blue"], "DASH", 35, self.colours["black"]),
            "heal_label": TextButton((70, 70), (1025, 725), self.colours["light_steel_blue"], "HEAL", 35, self.colours["black"]),
            "spell1_label": TextButton((70, 70), (1025, 805), self.colours["light_steel_blue"], "SPELL 1", 35, self.colours["black"]),
            "spell2_label": TextButton((70, 70), (1025, 885), self.colours["light_steel_blue"], "SPELL 2", 35, self.colours["black"]),
            "map_label": TextButton((70, 70), (1025, 965), self.colours["light_steel_blue"], "MAP", 35, self.colours["black"]),
            "difficulty_label": TextButton((400, 50), (625, 340), self.colours["light_steel_blue"], "DIFFICULTY", 40, self.colours["black"]),
            "score_label": TextButton((400, 50), (650, 550), self.colours["light_steel_blue"], "YOUR SCORE", 35, self.colours["black"]),
            "play": TextButton((250, 100), (835, 350), self.colours["lime_green"], "PLAY", 40),
            "play_again": TextButton((250, 100), (835, 350), self.colours["lime_green"], "PLAY AGAIN", 40),
            "quit": IconButton((25, 25), (1885, 10), self.colours["red"], "Sprites/x.png"),
            "settings": IconButton((25, 25), (10, 10), self.colours["light_grey"], "Sprites/cog.png"),
            "audio": TextButton((320, 100), (800, 350), self.colours["black"], "AUDIO", 40),
            "controls": TextButton((320, 100), (800, 475), self.colours["black"], "CONTROLS", 40),
            "game_settings": TextButton((320, 100), (800, 600), self.colours["black"], "GAME SETTINGS", 40),
            "register": TextButton((250, 100), (835, 600), self.colours["dark_grey"], "REGISTER", 40),
            "login": TextButton((250, 100), (835, 725), self.colours["dark_grey"], "LOGIN", 40),
            "logout": TextButton((250, 100), (835, 950), self.colours["dark_grey"], "LOGOUT", 40),
            "leaderboard": TextButton((250, 100), (835, 475), self.colours["yellow"], "LEADERBOARD", 36),
            "leaderboard_easy": TextButton((250, 100), (535, 350), self.colours["lime_green"], "EASY", 40),
            "leaderboard_normal": TextButton((250, 100), (835, 350), self.colours["yellow"], "NORMAL", 40),
            "leaderboard_hard": TextButton((250, 100), (1135, 350), self.colours["red"], "HARD", 40),
            "test_audio_1": TextButton((240, 70), (700, 750), self.colours["black"], "TEST 1", 40),
            "test_audio_2": TextButton((240, 70), (950, 750), self.colours["black"], "TEST 2", 40),
            "difficulty_toggle": ToggleButton((200, 70), (1000, 332.5), self.colours["yellow"], self.colours["red"], self.colours["lime"], "NORMAL", "HARD", "EASY", 25, self.colours["white"]),
            "score": TextButton((80, 50), (1100, 550), self.colours["light_steel_blue"], "0", 35, self.colours["black"])
        }

        self.sliders = {
            "master_volume": Slider(1000, 350, self.master_volume*100),
            "game_volume": Slider(1000, 500, self.game_volume*100),
            "music_volume": Slider(1000, 650, self.music_volume*100),
        }

        self.control_buttons = {
            "ctrl_up": TextButton((150, 70), (750, 325), self.colours["lime"], pygame.key.name(self.controls["ctrl_up"]).upper(), 25, self.colours["white"]),
            "ctrl_left": TextButton((150, 70), (750, 405), self.colours["lime"], pygame.key.name(self.controls["ctrl_left"]).upper(), 25, self.colours["white"]),
            "ctrl_down": TextButton((150, 70), (750, 485), self.colours["lime"], pygame.key.name(self.controls["ctrl_down"]).upper(), 25, self.colours["white"]),
            "ctrl_right": TextButton((150, 70), (750, 565), self.colours["lime"], pygame.key.name(self.controls["ctrl_right"]).upper(), 25, self.colours["white"]),
            "ctrl_dash": TextButton((150, 70), (750, 645), self.colours["lime"], pygame.key.name(self.controls["ctrl_dash"]).upper(), 25, self.colours["white"]),
            "ctrl_heal": TextButton((150, 70), (750, 725), self.colours["lime"], pygame.key.name(self.controls["ctrl_heal"]).upper(), 25, self.colours["white"]),
            "ctrl_spell1": TextButton((150, 70), (750, 805), self.colours["lime"], pygame.key.name(self.controls["ctrl_spell1"]).upper(), 25, self.colours["white"]),
            "ctrl_spell2": TextButton((150, 70), (750, 885), self.colours["lime"], pygame.key.name(self.controls["ctrl_spell2"]).upper(), 25, self.colours["white"]),
            "ctrl_map": TextButton((150, 70), (750, 965), self.colours["lime"], pygame.key.name(self.controls["ctrl_map"]).upper(), 25, self.colours["white"]),
        }

        if self.difficulty == "hard":
            self.buttons["difficulty_toggle"].toggle()
        if self.difficulty == "easy":
            self.buttons["difficulty_toggle"].toggle()
            self.buttons["difficulty_toggle"].toggle()

        self.game_state = "main_menu"

        self.full_heart = pygame.image.load("Sprites/full_heart.png")
        self.full_heart = pygame.transform.scale(self.full_heart, (75, 75))
        self.empty_heart = pygame.image.load("Sprites/empty_heart.png")
        self.empty_heart = pygame.transform.scale(self.empty_heart, (75, 75))
        self.cooldown_heart = pygame.image.load("Sprites/cooldown_heart.png")
        self.cooldown_heart = pygame.transform.scale(self.cooldown_heart, (75, 75))

        self.test_audio_1 = pygame.mixer.Sound('Audios/test1.mp3')
        self.test_audio_2 = pygame.mixer.Sound('Audios/test2.mp3')
        self.swing_audio = pygame.mixer.Sound('Audios/swing.mp3')
        self.spell1_audio = pygame.mixer.Sound('Audios/spell1.mp3')
        self.spell2_audio = pygame.mixer.Sound('Audios/spell2.mp3')
        self.win_audio = pygame.mixer.Sound('Audios/win.mp3')
        self.menu_music = pygame.mixer.Sound('Audios/menu.mp3')

        self.game_sounds = [
            self.test_audio_1,
            self.test_audio_2,
            self.swing_audio,
            self.spell1_audio,
            self.spell2_audio,
            self.win_audio,
        ]

        self.music = [
            self.menu_music,
        ]

        if len(self.game_sounds) > 0:
            for sound in self.game_sounds:
                sound.set_volume(self.game_volume * self.master_volume)

        if len(self.music) > 0:
            for sound in self.music:
                sound.set_volume(self.music_volume * self.master_volume)

        self.player_melee_damage = 6
        self.player_spell1_damage = 25
        self.player_spell2_damage = 30

        self.time = 0
        self.kills = 0
        self.clears = 0

        self.logged_in = False
        self.username = ""
        
        self.chars = ['!', '£', '$', '%', '&', '*', '#', '@', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
                      'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
                      'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.key = ['2', '9', 'e', 'r', 'Y', 'A', '#', 'S', 'L', '1', '4', '$', 'O', '@', 'W', 'q', 'V', 'D', '3', 'C', 'o', '%', 'y', 'E', '£', 'd', '5', 
                    'h', '*', 'j', 'M', 'B', 'U', 'F', 'N', 'u', '!', 'X', 'w', '7', 's', 'g', 'x', '6', 'I', '0', 'c', 'l', 'v', 'z', 'b', 'H', 'J', 'm', 
                    'f', 'G', 'n', '8', 'Z', 'a', 'p', 'i', 'P', 'R', 'k', 't', '&', 'Q', 'T', 'K']
        
        self.connection = sqlite3.connect('leaderboard.db')

        self.test_mode = False

    #Method for game state: main menu
    def main_menu(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["title"].draw(self.screen)

        self.buttons["play"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
        self.buttons["settings"].draw(self.screen)
        self.buttons["leaderboard"].draw(self.screen)

        if self.logged_in == False:
            self.buttons["register"].draw(self.screen)
            self.buttons["login"].draw(self.screen)
        if self.logged_in == True:
            self.buttons["logout"].draw(self.screen)

        self.menu_music.play(-1)

    #Method for game state: settings menu
    def settings_menu(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["settings_title"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)

        self.buttons["audio"].draw(self.screen)
        self.buttons["controls"].draw(self.screen)
        self.buttons["game_settings"].draw(self.screen)

    #Method for game state: audio menu
    def audio_menu(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["audio_title"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
        self.buttons["master_volume"].draw(self.screen)
        self.buttons["game_volume"].draw(self.screen)
        self.buttons["music_volume"].draw(self.screen)
        self.buttons["test_audio_1"].draw(self.screen)
        self.buttons["test_audio_2"].draw(self.screen)

        self.sliders["master_volume"].draw(self.screen)
        self.sliders["game_volume"].draw(self.screen)
        self.sliders["music_volume"].draw(self.screen)
        if self.sliders["master_volume"].changing == True:
            self.sliders["master_volume"].move(self.mouse_pos[0])
        if self.sliders["game_volume"].changing == True:
            self.sliders["game_volume"].move(self.mouse_pos[0])
        if self.sliders["music_volume"].changing == True:
            self.sliders["music_volume"].move(self.mouse_pos[0])

    #Method for game state: controls menu
    def controls_menu(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["controls_title"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
        self.buttons["up_label"].draw(self.screen)
        self.buttons["left_label"].draw(self.screen)
        self.buttons["down_label"].draw(self.screen)
        self.buttons["right_label"].draw(self.screen)
        self.buttons["dash_label"].draw(self.screen)
        self.buttons["heal_label"].draw(self.screen)
        self.buttons["spell1_label"].draw(self.screen)
        self.buttons["spell2_label"].draw(self.screen)
        self.buttons["map_label"].draw(self.screen)
        self.control_buttons["ctrl_up"].draw(self.screen)
        self.control_buttons["ctrl_left"].draw(self.screen)
        self.control_buttons["ctrl_down"].draw(self.screen)
        self.control_buttons["ctrl_right"].draw(self.screen)
        self.control_buttons["ctrl_dash"].draw(self.screen)
        self.control_buttons["ctrl_heal"].draw(self.screen)
        self.control_buttons["ctrl_spell1"].draw(self.screen)
        self.control_buttons["ctrl_spell2"].draw(self.screen)
        self.control_buttons["ctrl_map"].draw(self.screen)

    #UI for registering
    def register_screen(self):
        self.window = tkinter.Tk()
        self.window.title("REGISTER")
        self.window.geometry("500x500")
        self.window.configure(bg = '#303030')
        frame = tkinter.Frame(bg = '#303030')

        register_label = tkinter.Label(frame, text = "REGISTER", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 30))
        username_label = tkinter.Label(frame, text = "USERNAME", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 16))
        password_label = tkinter.Label(frame, text = "PASSWORD", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 16))
        self.username_entry = tkinter.Entry(frame, font = ("Arial", 16))
        self.password_entry = tkinter.Entry(frame, show = "*", font = ("Arial", 16))
        register_button = tkinter.Button(frame, text = "REGISTER", bg = '#6667AB', fg = '#FFFFFF', font = ("Arial", 16), command = self.register)
        
        register_label.grid(row = 0, column = 0, columnspan = 2, pady = 50)
        username_label.grid(row = 1, column = 0, pady = 20)
        password_label.grid(row = 2, column = 0, pady = 20)
        self.username_entry.grid(row = 1, column = 1)
        self.password_entry.grid(row = 2, column = 1)
        register_button.grid(row = 3, column = 0, columnspan = 2, pady = 30)
        
        frame.pack()

        self.window.mainloop()

    #Registers user account
    def register(self):
        self.connection = sqlite3.connect('leaderboard.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")
        
        username = str(self.username_entry.get())
        password = str(self.password_entry.get())
        username_check = False
        password_check = False
        symbol_check = False
        repeat_check = False
        invalid_char = False
        
        symbols = "!£$%&*#@"
        
        for letter in password:
            if letter in symbols:
                symbol_check = True
            if letter not in self.chars:
                invalid_char = True

        for letter in username:
            if letter not in self.chars:
                invalid_char = True

        self.cursor.execute("SELECT username FROM users")
        results = self.cursor.fetchall()
        for row in results:
            if str(row[0]) == username:
                repeat_check = True

        if 1 <= len(username) <= 15 and repeat_check == False and invalid_char == False:
            username_check = True
        if username == "":
            messagebox.showinfo(title = "Registration Unsuccessful", message = "Username field cannot be empty")
        if len(username) > 15:
            messagebox.showinfo(title = "Registration Unsuccessful", message = "Username field cannot be longer than 15 characters")
        if repeat_check == True:
            messagebox.showinfo(title = "Registration Unsuccessful", message = "This username already exists")
        
        if 8 <= len(password) <= 15 and symbol_check == True:
            password_check = True
        if len(password) < 8 or len(password) > 15:
            messagebox.showinfo(title = "Registration Unsuccessful", message = "Password field must be between 8 and 15 characters")
        if symbol_check == False:
            messagebox.showinfo(title = "Registration Unsuccessful", message = "Password field must contain at least one symbol from '!£$%&*#@'")

        if invalid_char == True:
            messagebox.showinfo(title = "Registration Unsuccessful", message = "Invalid character detected")

        if username_check == True and password_check == True:
            messagebox.showinfo(title = "Registration Successful", message = "You have successfully created an account")

            self.logged_in = True
            self.username = username

            encrypted_password = self.encryptPassword(password)

            self.cursor.execute("INSERT INTO users (username, password, easy, normal, hard) VALUES (?, ?, ?, ?, ?)", (username, encrypted_password, 0, 0, 0))
            self.connection.commit()

            self.window.destroy()

        self.connection.close()

    #UI for login
    def login_screen(self):
        self.window = tkinter.Tk()
        self.window.title("LOGIN")
        self.window.geometry("500x500")
        self.window.configure(bg = '#303030')
        frame = tkinter.Frame(bg = '#303030')

        login_label = tkinter.Label(frame, text = "LOGIN", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 30))
        username_label = tkinter.Label(frame, text = "USERNAME", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 16))
        password_label = tkinter.Label(frame, text = "PASSWORD", bg = '#303030', fg = '#FFFFFF', font = ("Arial", 16))
        self.username_entry = tkinter.Entry(frame, font = ("Arial", 16))
        self.password_entry = tkinter.Entry(frame, show = "*", font = ("Arial", 16))
        login_button = tkinter.Button(frame, text = "LOGIN", bg = '#6667AB', fg = '#FFFFFF', font = ("Arial", 16), command = self.login)
        
        login_label.grid(row = 0, column = 0, columnspan = 2, pady = 50)
        username_label.grid(row = 1, column = 0, pady = 20)
        password_label.grid(row = 2, column = 0, pady = 20)
        self.username_entry.grid(row = 1, column = 1)
        self.password_entry.grid(row = 2, column = 1)
        login_button.grid(row = 3, column = 0, columnspan = 2, pady = 30)
        
        frame.pack()

        self.window.mainloop()

    #Logs user in
    def login(self):
        self.connection = sqlite3.connect('leaderboard.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")
        
        username = str(self.username_entry.get())
        password = str(self.password_entry.get())
        encrypted_password = self.encryptPassword(password)

        self.cursor.execute("SELECT username, password FROM users")
        for row in self.cursor.fetchall():
            if str(row[0]) == username and str(row[1]) == encrypted_password:
                messagebox.showinfo(title = "Logged in Succesfully", message = "You have logged in succesfully")
                self.logged_in = True
                self.username = username
                self.window.destroy()

        if self.logged_in == False:
            messagebox.showinfo(title = "Logged in Unsuccessfully", message = "Your username and password do not match")

        self.connection.close()

    #Logs user out
    def logout(self):
        messagebox.showinfo(title = "Logged Out", message = "You have been logged out successfully")
        self.logged_in = False
        self.username = ""

    #Method for game state: game settings menu
    def game_settings_menu(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["game_settings_title"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
        self.buttons["difficulty_label"].draw(self.screen)
        self.buttons["difficulty_toggle"].draw(self.screen)

    #Method for game state: gameplay
    def gameplay(self):
        self.screen.fill(self.colours["black"])  
        self.currentLevel.drawtiles(self.screen)
        
        self.player.draw(self.screen)
        self.player.move()
        self.player.dash()
        self.player.heal()
        self.player.increaseMana(0.005)

        for enemy in self.enemies:
            if enemy.hp <= 0:
                self.kills += 1

                if enemy.type == "boss":
                    self.game_state = "game_over_win"
                    current_score = self.calculateScore()
                    self.buttons["score"].text = str(current_score)
                    self.saveResults(current_score)
                    self.win_audio.play()
                
                self.enemies.remove(enemy)
                self.player.increaseMana(10)
                self.player.heal_cooldown_timer -= 60

            if enemy.type == "boss":
                for minion in enemy.spawn_minions():
                    self.enemies.append(minion)
            
            trigValues = enemy.returnTrigValues((self.player.x, self.player.y))
            enemy.move(self.screen, trigValues)
            if enemy.player_hit:
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                enemy_strike = enemy.attack(self.screen, trigValues, player_rect)
                if enemy_strike and self.player.immunity == False:
                    self.player.hp -= enemy.damage
                    self.player.setImmunity()
            else:
                enemy.player_hit = True
            
            enemy.display_health(self.screen)
            
            if self.player.spell1 != None:
                self.player.spell1.detect_collision(enemy)

            if self.player.spell2 != None:
                self.player.spell2.detect_collision(enemy)

            if self.player.melee != None:
                self.player.melee.detect_collision(enemy)

        if self.player.immunity:
            self.player.setImmunity()

        self.player.meleePressed(self.screen)
        self.player.spell1Pressed(self.screen)
        self.player.spell2Pressed(self.screen)

        for i in range(self.player.max_hp):
            heart_pos = (10 + (i*80), 0)
            if i + 1 <= self.player.hp:
                self.screen.blit(self.full_heart, heart_pos)
            elif self.player.heal_cooldown == True:
                self.screen.blit(self.cooldown_heart, heart_pos)
            else:
                self.screen.blit(self.empty_heart, heart_pos)

        self.player.displayMana(self.screen)

        if self.player.hp <= 0:
            self.game_state = "game_over_lose"

        if len(self.currentLevel.enemies) == 0:
            self.currentLevel.locked = False

        if self.currentLevel.locked == False:
            if self.player.x == 1920 - self.player.width:
                self.change_room("right")
            if self.player.x == 0:
                self.change_room("left")
            if self.player.y == 1080 - self.player.height:
                self.change_room("down")
            if self.player.y == 0:
                self.change_room("up")

        self.buttons["quit"].draw(self.screen)

        if self.world.map_enabled == True:
            self.world.drawMap(self.screen)

        self.time += 1

    #Lose menu
    def game_over_lose(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["lose_title"].draw(self.screen)
        self.buttons["play_again"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)

    #Win menu
    def game_over_win(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["win_title"].draw(self.screen)
        self.buttons["play_again"].draw(self.screen)
        self.buttons["score_label"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
        self.buttons["score"].draw(self.screen)

    #Leaderboard menu
    def leaderboard_menu(self):        
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["quit"].draw(self.screen)
        self.buttons["leaderboard_title"].draw(self.screen)
        self.buttons["leaderboard_easy"].draw(self.screen)
        self.buttons["leaderboard_normal"].draw(self.screen)
        self.buttons["leaderboard_hard"].draw(self.screen)
        
    #Easy mode leaderboard
    def leaderboard_easy(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["quit"].draw(self.screen)
        self.buttons["leaderboard_title"].draw(self.screen)

        self.connection = sqlite3.connect('leaderboard.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")
        
        self.cursor.execute("SELECT username, easy FROM users ORDER BY easy DESC, username ASC;")
        results = self.cursor.fetchall()
        if len(results) >= 10:
            results = results[0:10]

        frame = pygame.Surface((480, 640))
        frame.fill(self.colours["light_steel_blue"])
        font = pygame.font.SysFont("Tahoma", 30)
        for i in range(len(results)):
            if str(results[i][0]) != "":
                frame.blit(font.render(f"{i+1:<3}. {results[i][0]:<35} {results[i][1]:<1}", 1, self.colours["black"]), (0, i*60))

        if self.logged_in == True:
            self.cursor.execute("SELECT username, easy FROM users WHERE username = ?;", (str(self.username),))
            results = self.cursor.fetchall()
            frame.blit(font.render(f"You. {results[0][0]:<35} {results[0][1]:<1}", 1, self.colours["black"]), (0, 600))
        
        self.screen.blit(frame, (710, 350))

    #Normal mode leaderboard
    def leaderboard_normal(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["quit"].draw(self.screen)
        self.buttons["leaderboard_title"].draw(self.screen)

        self.connection = sqlite3.connect('leaderboard.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")
        
        self.cursor.execute("SELECT username, normal FROM users ORDER BY normal DESC, username ASC;")
        results = self.cursor.fetchall()
        if len(results) >= 10:
            results = results[0:9]

        frame = pygame.Surface((480, 640))
        frame.fill(self.colours["light_steel_blue"])
        font = pygame.font.SysFont("Tahoma", 30)
        for i in range(len(results)):
            if str(results[i][0]) != "":
                frame.blit(font.render(f"{i+1} . {results[i][0]:<16} {results[i][1]:>25}", 1, self.colours["black"]), (0, i*60))

        if self.logged_in == True:
            self.cursor.execute("SELECT username, normal FROM users WHERE username = ?;", (str(self.username),))
            results = self.cursor.fetchall()
            frame.blit(font.render(f"You {results[0][0]:<16} {results[0][1]:>20}", 1, self.colours["black"]), (0, 600))
        
        self.screen.blit(frame, (710, 350))

    #Hard mode leaderboard
    def leaderboard_hard(self):
        self.screen.fill(self.colours["light_steel_blue"])
        self.buttons["quit"].draw(self.screen)
        self.buttons["leaderboard_title"].draw(self.screen)

        self.connection = sqlite3.connect('leaderboard.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")
        
        self.cursor.execute("SELECT username, hard FROM users ORDER BY hard DESC, username ASC;")
        results = self.cursor.fetchall()
        if len(results) > 10:
            results = results[0:10]

        frame = pygame.Surface((480, 640))
        frame.fill(self.colours["light_steel_blue"])
        font = pygame.font.SysFont("Tahoma", 30)
        for i in range(len(results)):
            if str(results[i][0]) != "":
                frame.blit(font.render(f"{i+1} . {results[i][0]:<16} {results[i][1]:>25}", 1, self.colours["black"]), (0, i*60))

        if self.logged_in == True:
            self.cursor.execute("SELECT username, hard FROM users WHERE username = ?;", (str(self.username),))
            results = self.cursor.fetchall()
            frame.blit(font.render(f"You {results[0][0]:<16} {results[0][1]:>20}", 1, self.colours["black"]), (0, 600))
        
        self.screen.blit(frame, (710, 350))
    
    #Method for managing audio volume
    def audio_manager(self):
        self.master_volume = self.sliders["master_volume"].return_percentage()
        self.game_volume = self.sliders["game_volume"].return_percentage()
        self.music_volume = self.sliders["music_volume"].return_percentage()
        
        if len(self.game_sounds) > 0:
            for sound in self.game_sounds:
                sound.set_volume(self.game_volume * self.master_volume)
        
        if len(self.music) > 0:
            for sound in self.music:
                sound.set_volume(self.music_volume * self.master_volume)

    #Method for activating the changing controls procedure
    def change_controls(self, control):
        if self.control_buttons[control].collision(self.mouse_pos):
            for key, value in self.control_buttons.items():
                value.locked = True
            self.buttons["quit"].locked = True
            self.buttons["quit"].colour = self.colours["light_grey"]
            self.control_buttons[control].colour = self.colours["red"]
            self.control_buttons[control].text = "..."
            self.setting_control = control

    #Method for beginning a new game
    def new_game(self):
        if self.difficulty == "easy":
            player_hp = 8
            self.player_melee_damage = 8
            self.player_spell1_damage = 25
            self.player_spell2_damage = 30
        if self.difficulty == "normal":
            player_hp = 6
            self.player_melee_damage = 6
            self.player_spell1_damage = 15
            self.player_spell2_damage = 20
        if self.difficulty == "hard":
            player_hp = 4
            self.player_melee_damage = 4
            self.player_spell1_damage = 10
            self.player_spell2_damage = 15

        self.world = World()
        self.world.generate()
        self.world.createMap()
        
        if self.test_mode:
            self.currentLevel = self.world.tileMap[self.world.lastRoom[1]][self.world.lastRoom[0]]
            self.enemies = self.currentLevel.enemies
            self.enemies.append(Boss(1200, self.difficulty))
        else:
            self.currentLevel = self.world.tileMap[self.world.currentY][self.world.currentX]
        
        self.enemies = self.currentLevel.enemies
        
        self.player = Player(hp = player_hp)

    #Changing Room
    def change_room(self, direction):
        if direction == "up" and self.currentLevel.top == True:
            self.world.currentY -= 1
            self.player.y = 1050 - self.player.height
        if direction == "left" and self.currentLevel.left == True:
            self.world.currentX -= 1
            self.player.x = 1890 - self.player.width
        if direction == "down" and self.currentLevel.bottom == True:
            self.world.currentY += 1
            self.player.y = 30
        if direction == "right" and self.currentLevel.right == True:
            self.world.currentX += 1
            self.player.x = 30

        self.currentLevel = self.world.tileMap[self.world.currentY][self.world.currentX]
        self.enemies = self.currentLevel.enemies

        if self.currentLevel.type == "end":
            self.enemies.append(Boss(1200, self.difficulty))
            
        if self.currentLevel.locked == True:
            self.clears += 1

        self.world.tileMap[self.world.currentY][self.world.currentX].discovered = True
        self.world.createMap()

    def calculateScore(self):
        return int((self.kills + (20 * self.clears)) / (self.time / 10800))
    
    #Saving new high scores
    def saveResults(self, score):
        if self.logged_in:
            self.connection = sqlite3.connect('leaderboard.db')
            self.cursor = self.connection.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                       users(username STRING PRIMARY KEY, password STRING, easy INTEGER, normal INTEGER, hard INTEGER)""")

            if self.difficulty == "easy":
                self.cursor.execute("SELECT username, easy FROM users")
                for row in self.cursor.fetchall():
                    if str(row[0]) == self.username:
                        high_score = row[1]

                if score > high_score:
                    self.cursor.execute("UPDATE users SET easy = ? WHERE username = ?", (score, self.username))

            if self.difficulty == "normal":
                self.cursor.execute("SELECT username, normal FROM users")
                for row in self.cursor.fetchall():
                    if str(row[0]) == self.username:
                        high_score = row[1]

                if score > high_score:
                    self.cursor.execute("UPDATE users SET normal = ? WHERE username = ?", (score, self.username))

            if self.difficulty == "hard":
                self.cursor.execute("SELECT username, hard FROM users")
                for row in self.cursor.fetchall():
                    if str(row[0]) == self.username:
                        high_score = row[1]

                if score > high_score:
                    self.cursor.execute("UPDATE users SET hard = ? WHERE username = ?", (score, self.username))

            self.connection.commit()
            self.connection.close()

    #Encrypting the password
    def encryptPassword(self, password):
        encrypted_password = ""
        for character in password:
            index = self.chars.index(character)
            encrypted_password += self.key[index]

        return encrypted_password
    
    #Saving the settings
    def saveSettings(self):
        with open("settings.txt", "w") as file:
            file.write(str(self.master_volume) + '\n')
            file.write(str(self.game_volume) + '\n')
            file.write(str(self.music_volume) + '\n')
            file.write(self.difficulty + '\n')
            file.write(pygame.key.name(self.controls["ctrl_up"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_left"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_down"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_right"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_dash"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_heal"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_spell1"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_spell2"]) + '\n')
            file.write(pygame.key.name(self.controls["ctrl_map"]))

    #Managing pygame events
    def events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.connection.close()
                self.saveSettings()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # TEST CODE
                if event.button == 1:
                    print("LEFT CLICK PRESSED")
                if event.button == 3:
                    print("RIGHT CLICK PRESSED")

                if event.button == 1:
                    if self.game_state == "main_menu":
                        if self.buttons["play"].collision(self.mouse_pos):
                            self.new_game()
                            self.game_state = "game"
                            self.menu_music.stop()
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.connection.close()
                            self.saveSettings()
                            exit()
                        if self.buttons["settings"].collision(self.mouse_pos):
                            self.game_state = "settings_menu"
                        if self.logged_in == False:
                            if self.buttons["register"].collision(self.mouse_pos):
                                self.register_screen()
                            if self.buttons["login"].collision(self.mouse_pos):
                                self.login_screen()
                        if self.logged_in == True:
                            if self.buttons["logout"].collision(self.mouse_pos):
                                self.logout()
                        if self.buttons["leaderboard"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_menu"

                    if self.game_state == "game":
                        if self.player.melee_cooldown == False and self.player.melee == None:
                            self.player.melee = MeleeAttack(self.player_melee_damage, 75)
                            self.player.melee_pressed = True
                            self.swing_audio.play()

                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "main_menu"

                    if self.game_state == "game_over_lose":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "main_menu"
                        if self.buttons["play_again"].collision(self.mouse_pos):
                            self.new_game()
                            self.game_state = "game"

                    if self.game_state == "game_over_win":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "main_menu"
                        if self.buttons["play_again"].collision(self.mouse_pos):
                            self.new_game()
                            self.game_state = "game"

                    if self.game_state == "settings_menu":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "main_menu"
                        if self.buttons["audio"].collision(self.mouse_pos):
                            self.game_state = "audio_menu"
                            self.menu_music.stop()
                        if self.buttons["controls"].collision(self.mouse_pos):
                            self.game_state = "controls_menu"
                        if self.buttons["game_settings"].collision(self.mouse_pos):
                            self.game_state = "game_settings_menu"

                    if self.game_state == "audio_menu":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "settings_menu"
                            self.menu_music.play(-1)
                        if self.buttons["test_audio_1"].collision(self.mouse_pos):
                            self.test_audio_1.play()
                        if self.buttons["test_audio_2"].collision(self.mouse_pos):
                            self.test_audio_2.play()

                        self.sliders["master_volume"].collision(self.mouse_pos)
                        self.sliders["game_volume"].collision(self.mouse_pos)
                        self.sliders["music_volume"].collision(self.mouse_pos)

                    if self.game_state == "controls_menu":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "settings_menu"

                        self.change_controls("ctrl_up")
                        self.change_controls("ctrl_left")
                        self.change_controls("ctrl_down")
                        self.change_controls("ctrl_right")
                        self.change_controls("ctrl_dash")
                        self.change_controls("ctrl_heal")
                        self.change_controls("ctrl_spell1")
                        self.change_controls("ctrl_spell2")
                        self.change_controls("ctrl_map")

                    if self.game_state == "game_settings_menu":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "settings_menu"

                        if self.buttons["difficulty_toggle"].collision(self.mouse_pos):
                            state = self.buttons["difficulty_toggle"].toggle()
                            if state == 0:
                                self.difficulty = "normal"
                            if state == 1:
                                self.difficulty = "hard"
                            if state == 2:
                                self.difficulty = "easy"

                    if self.game_state == "leaderboard_menu":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "main_menu"

                        if self.buttons["leaderboard_easy"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_easy"
                        if self.buttons["leaderboard_normal"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_normal"
                        if self.buttons["leaderboard_hard"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_hard"

                    if self.game_state == "leaderboard_easy":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_menu"

                    if self.game_state == "leaderboard_normal":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_menu"

                    if self.game_state == "leaderboard_hard":
                        if self.buttons["quit"].collision(self.mouse_pos):
                            self.game_state = "leaderboard_menu"

            if event.type == pygame.MOUSEBUTTONUP:
                self.audio_manager()
                self.sliders["master_volume"].changing = False
                self.sliders["game_volume"].changing = False
                self.sliders["music_volume"].changing = False

            if event.type == pygame.KEYDOWN:
                # TEST CODE
                print(f"{pygame.key.name(event.key)} PRESSED")
                
                # TEST CODE
                if self.game_state == "main_menu":
                    if event.key == pygame.key.key_code("="):
                        self.test_mode = not self.test_mode
                        print(f"test mode: {self.test_mode}")

                # TEST CODE

                if self.game_state == "game":
                    if event.key == self.controls["ctrl_up"]:
                        self.player.is_up = True
                        print("UP PRESSED")
                    if event.key == self.controls["ctrl_left"]:
                        self.player.is_left = True
                        print("LEFT PRESSED")
                    if event.key == self.controls["ctrl_down"]:
                        self.player.is_down = True
                        print("DOWN PRESSED")
                    if event.key == self.controls["ctrl_right"]:
                        self.player.is_right = True
                        print("RIGHT PRESSED")
                    if event.key == self.controls["ctrl_dash"]:
                        self.player.is_dashing = True
                        print("DASH PRESSED")
                    if event.key == self.controls["ctrl_heal"]:
                        self.player.heal_triggered = True
                        print("HEAL PRESSED")
                    if event.key == self.controls["ctrl_spell1"]:
                        if self.player.mana >= self.player.spell1_mana_cost and self.player.spell1_cooldown == False:
                            self.player.spell1 = Spell1(self.player_spell1_damage, pygame.mouse.get_pos(), (self.player.x + self.player.width/2, self.player.y + self.player.height/2))
                            self.player.mana -= self.player.spell1_mana_cost
                            self.player.spell1_trigger = True
                            self.spell1_audio.play()
                        print("SPELL 1 PRESSED")
                    if event.key == self.controls["ctrl_spell2"]:
                        if self.player.mana >= self.player.spell2_mana_cost and self.player.spell2_cooldown == False:
                            self.player.spell2 = Spell2(self.player_spell2_damage, 200, (self.player.x + self.player.width/2, self.player.y + self.player.height/2))
                            self.player.mana -= self.player.spell2_mana_cost
                            self.player.spell2_trigger = True
                        print("SPELL 2 PRESSED")
                    if event.key == self.controls["ctrl_map"]:
                        self.world.map_enabled = True
                        print("MAP PRESSED")

                if self.game_state == "controls_menu":
                    if self.setting_control != "":
                        rejected_key = False
                        for key, value in self.controls.items():
                            if event.key == value:
                                rejected_key = True
                        if event.key not in self.allowed_controls:
                            rejected_key = True
                        if rejected_key == False:
                            self.controls[self.setting_control] = event.key
                            self.control_buttons[self.setting_control].text = pygame.key.name(event.key).upper()
                            self.control_buttons[self.setting_control].colour = self.colours["lime"]
                            self.buttons["quit"].colour = self.colours["red"]
                            self.buttons["quit"].locked = False
                            for key, value in self.control_buttons.items():
                                value.locked = False
                            self.setting_control = ""
                        rejected_key = False

            if event.type == pygame.KEYUP:
                if self.game_state == "game":
                    if event.key == self.controls["ctrl_up"]:
                        self.player.is_up = False
                    if event.key == self.controls["ctrl_left"]:
                        self.player.is_left = False
                    if event.key == self.controls["ctrl_down"]:
                        self.player.is_down = False
                    if event.key == self.controls["ctrl_right"]:
                        self.player.is_right = False
                    
                    if event.key == self.controls["ctrl_map"]:
                        self.world.map_enabled = False

    #The code that is executed after initialisation every frame
    def execute(self):
        while True:
            self.events()
            
            if self.game_state == "main_menu":
                self.main_menu()

            if self.game_state == "settings_menu":
                self.settings_menu()

            if self.game_state == "audio_menu":
                self.audio_menu()

            if self.game_state == "controls_menu":
                self.controls_menu()

            if self.game_state == "game_settings_menu":
                self.game_settings_menu()

            if self.game_state == "game":
                self.gameplay()

            if self.game_state == "game_over_lose":
                self.game_over_lose()

            if self.game_state == "game_over_win":
                self.game_over_win()

            if self.game_state == "leaderboard_menu":
                self.leaderboard_menu()

            if self.game_state == "leaderboard_easy":
                self.leaderboard_easy()

            if self.game_state == "leaderboard_normal":
                self.leaderboard_normal()

            if self.game_state == "leaderboard_hard":
                self.leaderboard_hard()

            pygame.display.flip()
            self.clock.tick(60)

#Creating an instance of the game class and executing it
Game().execute()