import pygame, math, random, os

pygame.init()

class Player: #플레이어 스탯 + 플레이어 버프 적용 시 스탯   
    def __init__(self, name):
        self.name = name
        self.width, self.height = 50, 50
        # 플레이어 기본 스탯
        self.base_stat = {
            'hp' : 1000,
            'attack' : 20,
            'attack_speed' : 1.0,
            'speed' : 10 
        }
        #버프 관련 딕셔너리
        self.buff = {
            'hp' : 0,
            'attack' : 0,
            'attack_speed' : 0.0,
            'speed' : 0 
        }

    def apply_buff(self, stat, value):
        self.buff[stat] += value

    def remove_buff(self, stat): #버프 제거 함수
        self.buff[stat] = 0

    def final_stats(self):
        final_stat = {}
        for key in self.base_stat:
            final_stat[key] = self.base_stat[key] + self.buff[key]
        return final_stat

class Enemy: #적 스탯 + 적 버프 적용 시 스탯 + 적 전용 AI or 로직
    def __init__(self, name, world_x, world_y, image):
        self.name = name
        self.world_x = world_x
        self.world_y = world_y
        self.image = image
        self.rect = self.image.get_rect(topleft = (world_x, world_y))
        #적 기본 스탯
        self.base_stat = {
            'hp' : 100,
            'attack' : 20,
            'attack_speed' : 1.0,
            'speed' : 7 
        }
        #적 버프 관련 딕셔너리
        self.buff = {
            'hp' : 0,
            'attack' : 0,
            'attack_speed' : 0.0,
            'speed' : 0 
        }
    def apply_buff(self, stat, value):
        self.buff[stat] += value

    def remove_buff(self, stat): #버프 제거 함수
        self.buff[stat] = 0

    def final_stats(self):
        final_stat = {}
        for key in self.base_stat:
            final_stat[key] = self.base_stat[key] + self.buff[key]
        return final_stat

    #플레이어한테 이동하는 로직
    def move_toward(self, player_world_x, player_world_y, distance):
        dx = player_world_x - self.world_x
        dy = player_world_y - self.world_y
        length = math.hypot(dx, dy) #플레이어와의 거리 계산

        if length > distance: #거리가 distance보다 멀리 있을 때
            dx /= length
            dy /= length
            stats = self.final_stats()
            self.world_x += dx * stats['speed']
            self.world_y += dy * stats['speed']


    #적이 여러명 있는 경우 서로 밀려나는 함수
    def sep_enemies(self, enemies, player_rect = None): #적의 종류가 늘어나면 나중에 수정 필요
        for other in enemies:
            if other is self: #감지되는 것이 자신인지 판단하기
                continue
            elif self.rect.colliderect(other.rect): #서로 충돌했나 감지
                dx = self.world_x - other.world_x #서로 x, y가 얼마나 떨어졌는지 구하기
                dy = self.world_y - other.world_y
                length = math.hypot(dx, dy)
                if length != 0:
                    dx /= length #이동할 방향을  -1, 1로 구하기
                    dy /= length
                    self.world_x += dx * 2 #방향 * 2px 만큼 이동
                    self.world_y += dy * 2

        if player_rect and self.rect.colliderect(player_rect):
                dx = self.world_x - player_rect.centerx   
                dy = self.world_y - player_rect.centery
                length = math.hypot(dx, dy)
                if length <= 100:
                    dx /= length #이동할 방향을  -1, 1로 구하기
                    dy /= length
                    self.world_x += dx * 2 #방향 * 2px 만큼 이동
                    self.world_y += dy * 2

        self.rect.topleft = (self.world_x, self.world_y) #x, y좌표 업데이트

    def draw_enemy(self, screen, pov_x, pov_y):
        screen_x = int(self.world_x - pov_x)
        screen_y = int(self.world_y - pov_y)
        screen.blit(self.image, (screen_x, screen_y))


BASE_DIR = os.path.dirname(__file__)

screen_w = 1200 #화면 가로
screen_h = 700 #화면 세로

# 플레이어 좌표 (화면 중앙)
player_x = screen_w // 2 - 50
player_y = screen_h // 2 - 50

#플레이어한테 기본 스탯 부여
player = Player('플레이어')
player_stats = player.final_stats()

#플레이어의 실제 월드 좌표
player_world_x = screen_w // 2
player_world_y = screen_h // 2

enemies = []
enemy_spawn_timer = 0 #2초(2000ms)마다 적 생성
enemy_spawn_range = {'min' : 150, 'max' : 600} #플레이어 주변 150 ~600픽셀 이내 거리에서 생성
enemy_max_amount = 10 #적의 최대수

screen = pygame.display.set_mode((screen_w, screen_h))

background = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Background.PNG'))
player_image = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Player.PNG'))
enemy_image = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Enemy.PNG'))

pygame.display.set_caption('Vampire Survivor 2') #게임 이름, 나중에 변경

clock = pygame.time.Clock() #프레임 조절

game_running = True
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #창 닫기 이벤트 발생
            game_running = False
    
    dt = clock.tick(60) #매 프레임마다 지나는 시간 체크(ms)
    enemy_spawn_timer += dt

    key_press = pygame.key.get_pressed() #WASD로 이동

    dx, dy = 0, 0 #x, y축 방향으로 이동하는 방향 저장하는 변수
    
    if key_press[pygame.K_w]:
        dy -= 1
    if key_press[pygame.K_s]:
        dy += 1
    if key_press[pygame.K_a]:
        dx -= 1
    if key_press[pygame.K_d]:
        dx += 1

    if dx != 0 or dy != 0: #대각선으로 이동시에 루트2로 나눔
        length = (dx**2 + dy**2) ** 0.5
        dx /= length
        dy /= length

    player_world_x += dx * player_stats['speed'] #방향 + 속도
    player_world_y += dy * player_stats['speed']

    pov_x = player_world_x - screen_w // 2 + 25
    pov_y = player_world_y - screen_h // 2 + 25

    if enemy_spawn_timer >= 200 and len(enemies) < enemy_max_amount: #적의 최대치보다 적을시, 적이 스폰되는 지점 정하기
        enemy_spawn_timer = 0 #타이머 리셋

        #플레이어로부터 x축 방향으로 100 ~ 300px만큼 떨어진 위치로 x좌표 설정
        enemy_x = player_world_x + random.choice([-1, 1]) * random.randint(enemy_spawn_range['min'], enemy_spawn_range['max'])
        #플레이어로부터 y축 방향으로 100 ~ 300px만큼 떨어진 위치로 y좌표 설정
        enemy_y = player_world_y + random.choice([-1, 1]) * random.randint(enemy_spawn_range['min'], enemy_spawn_range['max'])

        enemies.append(Enemy('적', enemy_x, enemy_y, enemy_image)) #enemies 리스트에 적 추가

    # 무한 반복하는 배경 그리기
    for x in range(-screen_w, screen_w + screen_w, screen_w):
        for y in range(-screen_h, screen_h + screen_h, screen_h):
            screen.blit(background, (x - (pov_x % screen_w), y - (pov_y % screen_h)))

    # 플레이어 그리기 (화면 중앙)
    screen.blit(player_image, (screen_w // 2 - 25, screen_h // 2 - 25))

    player_rect = pygame.Rect(player_world_x, player_world_y, player.width, player.height) #플레이어의 좌표, 너비, 높이가 담긴 직사각형 정보
    #모든 적 그리기
    for enemy in enemies:
        enemy.move_toward(player_world_x, player_world_y, 50 * math.sqrt(2)) #플레이어한테 이동하는 함수 모든 적에게 실행
        enemy.draw_enemy(screen, pov_x, pov_y) #적 그리는 함수 실행
        enemy.sep_enemies(enemies, player_rect) #적끼리 서로 충돌할때 서로 멀어지는 함수 실행

    #화면 전체 새로고침
    pygame.display.flip()

    clock.tick(60) #60프레임 고정

pygame.quit()