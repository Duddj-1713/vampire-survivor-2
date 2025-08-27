import pygame, math, random, os

pygame.init()

class Player: #플레이어 스탯 + 플레이어 버프 적용 시 스탯   
    def __init__(self, name):
        self.name = name
        # 플레이어 기본 스탯
        self.base_stat = {
            'hp' : 1000,
            'attack' : 20,
            'attack_speed' : 1.0,
            'speed' : 2 
        }
        self.buff = {
            'hp'    : 0,
            'attack' : 0,
            'attack_speed' : 0.0,
            'speed' : 0 
        }

    def apply_buff(self, stat, value):
        self.buff[stat] += value

    def remove_buff(self, stat):
        self.buff[stat] = 0

    def final_stats(self):
        final_stat = {}
        for key in self.base_stat:
            final_stat[key] = self.base_stat[key] + self.buff[key]
        return final_stat


BASE_DIR = os.path.dirname(__file__)

screen_w = 1200 #화면 가로
screen_h = 700 #화면 세로

# 플레이어 좌표
player_x = screen_w // 2 - 50
player_y = screen_h // 2 - 50   

player = Player('플레이어')
player_stats = player.final_stats()

screen = pygame.display.set_mode((screen_w, screen_h))
background = pygame.image.load(os.path.join(BASE_DIR, 'images', '임시 배경.PNG'))
player_image = pygame.image.load(os.path.join(BASE_DIR, 'images', '플레이어.PNG'))
pygame.display.set_caption('Vampire Survivor 2') #게임 이름, 나중에 변경

game_running = True
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #창 닫기 이벤트 발생
            game_running = False
    
    key_press = pygame.key.get_pressed() #WASD로 이동
    if not(key_press[pygame.K_w] or key_press[pygame.K_s] and key_press[pygame.K_a] and key_press[pygame.K_d]):
        if key_press[pygame.K_w]:
            player_y -= player_stats['speed']
        if key_press[pygame.K_s]:
            player_y += player_stats['speed']
        if key_press[pygame.K_a]:
            player_x -= player_stats['speed']
        if key_press[pygame.K_d]:
            player_x += player_stats['speed']
    else:
        if key_press[pygame.K_w]:
            player_y -= player_stats['speed']**0.5
        if key_press[pygame.K_s]:
            player_y += player_stats['speed']**0.5
        if key_press[pygame.K_a]:
            player_x -= player_stats['speed']**0.5
        if key_press[pygame.K_d]:
            player_x += player_stats['speed']**0.5

    pov_x = player_x - screen_w // 2
    pov_y = player_y - screen_h // 2

    # 무한 반복하는 배경 그리기
    for x in range(-screen_w, screen_w + screen_w, screen_w):
        for y in range(-screen_h, screen_h + screen_h, screen_h):
            screen.blit(background, (x - (pov_x % screen_w), y - (pov_y % screen_h)))

    # 플레이어 그리기
    screen.blit(player_image, (screen_w // 2 - 50, screen_h // 2))

    pygame.display.flip()

pygame.quit()
