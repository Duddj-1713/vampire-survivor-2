import pygame, math, random, os

pygame.init()

class Player: #플레이어 스탯 + 플레이어 버프 적용 시 스탯   
    def __init__(self):
        self.width, self.height = 50, 50
        # 플레이어 기본 스탯
        self.base_stat = {
            'hp' : 1000,
            'attack' : 20,
            'speed' : 10
        }
        #버프 관련 딕셔너리
        self.buff = {
            'hp' : 0,
            'attack' : 0,
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

    def attacking(self):
        pass

class Weapon:
    def __init__(self, attack_damage, attack_speed, attack_range):
        self.attack_damage = attack_damage
        self.attack_speed = attack_speed
        self.attack_range = attack_range
        self.last_attack = 0

    def detect_enemy(self, player_x, player_y, enemies, current_time):
        if current_time - self.last_attack < self.attack_speed or not enemies:
            return None

        # 가장 가까운 적 선택
        closest_enemy = min(
            enemies,
            key=lambda e: math.hypot(e.world_x - player_x, e.world_y - player_y)
        )
        distance = math.hypot(closest_enemy.world_x - player_x,
                              closest_enemy.world_y - player_y)

        if distance > self.attack_range:
            return None

        self.last_attack = current_time
        return closest_enemy 

import pygame, math

import pygame, math

import pygame, math

class Sword:
    def __init__(self, swing_images, attack_damage, attack_speed, attack_range):
        self.swing_images = swing_images
        self.attack_damage = attack_damage
        self.attack_speed = attack_speed
        self.attack_range = attack_range
        self.last_attack = 0

        self.attacking_flag = False
        self.swing_start_time = 0
        self.base_angle = 0
        self.target = None

        # 휘두르는 각도 구간 (0.5초 정도)
        self.angle_ranges = [(0, 35), (35, 90), (90, 150)]
        self.frame_times = [200, 170, 130]
        self.total_duration = sum(self.frame_times)

    def detect_enemy(self, player_x, player_y, enemies, current_time):
        if current_time - self.last_attack < self.attack_speed or not enemies:
            return None

        closest_enemy = min(
            enemies,
            key=lambda e: math.hypot(e.world_x - player_x, e.world_y - player_y)
        )
        distance = math.hypot(closest_enemy.world_x - player_x,
                              closest_enemy.world_y - player_y)

        if distance > self.attack_range:
            return None

        return closest_enemy

    def attack(self, player_world_x, player_world_y, enemies):
        current_time = pygame.time.get_ticks()
        if self.attacking_flag:
            return  # 이미 공격 중이면 무시

        target = self.detect_enemy(player_world_x, player_world_y, enemies, current_time)
        if target:
            # 공격 각도 (플레이어 → 적 방향)
            dx = target.world_x - player_world_x
            dy = target.world_y - player_world_y
            self.base_angle = math.degrees(math.atan2(-dy, dx))
            self.target = target
            target.take_damage(self.attack_damage)

            # 공격 시작
            self.attacking_flag = True
            self.swing_start_time = current_time
            self.last_attack = current_time

    def swing(self, screen, current_time, player_world_x, player_world_y, pov_x, pov_y):
        if not self.attacking_flag:
            return

        elapsed = current_time - self.swing_start_time
        if elapsed >= self.total_duration:
            self.attacking_flag = False
            return

        # 현재 프레임과 각도 계산
        frame_index = 0
        accumulated_time = 0
        for i, t in enumerate(self.frame_times):
            accumulated_time += t
            if elapsed <= accumulated_time:
                frame_index = i
                break

        frame_elapsed = elapsed - sum(self.frame_times[:frame_index])
        angle_start, angle_end = self.angle_ranges[frame_index]
        swing_angle = angle_start + (angle_end - angle_start) * (frame_elapsed / self.frame_times[frame_index])
        total_angle = self.base_angle - swing_angle

        current_image = self.swing_images[frame_index]
        rotated_image = pygame.transform.rotate(current_image, total_angle)

        # === 여기 중요 ===
        # 플레이어의 화면상 중심 좌표
        screen_x = player_world_x - pov_x
        screen_y = player_world_y - pov_y

        # 중심이 진짜 중앙에 맞는지 보기 위해 원 찍기
        pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)

        rect = rotated_image.get_rect(center=(screen_x, screen_y + 70))
        screen.blit(rotated_image, rect)

        # 이미지 영역 확인용 박스
        pygame.draw.rect(screen, (0, 255, 0), rect, 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, image):
        super().__init__()
        self.world_x = world_x
        self.world_y = world_y
        self.image = image
        self.rect = self.image.get_rect(topleft = (world_x, world_y))
        self.last_attack_time = 0
        self.state = 'moving'

        #적 기본 스탯
        self.base_stat = {
            'hp' : 50,
            'attack' : 20,
            'attack_speed' : 3000,
            'speed' : 7,
            'attack_range' : 80
        } 

        self.current_stat = self.calc_final_stats()
    
    def calc_final_stats(self):
        return(self.base_stat)
        #이후에 난이도, 버프, 고난 등 다양한 기능 추가시 업뎃할 예정

    def take_damage(self, attack_damage):
        self.current_stat['hp'] -= attack_damage
        if self.current_stat['hp'] <= 0:
            self.kill() #스스로 그룹에서 제거
    
    #플레이어한테 이동하는 로직 (+ 플레이어한테 돌진해서 공격하는 로직 추가)
    def move_toward(self, player_stat, player_world_x, player_world_y, current_time):
        dx = player_world_x - self.world_x
        dy = player_world_y - self.world_y
        length = math.hypot(dx, dy)
        stats = self.current_stat

        if length > stats['attack_range']:
            self.state = 'moving'
            dx /= length
            dy /= length
            self.world_x += dx * stats['speed']
            self.world_y += dy * stats['speed']

        elif length <= stats['attack_range']:
            self.state = 'attacking'
            if current_time - self.last_attack_time >= stats['attack_speed']:
                player_stat['hp'] -= stats['attack']
                self.last_attack_time = current_time

        #rect 업뎃
        self.rect.topleft = (self.world_x, self.world_y)

    #적이 여러명 있는 경우 서로 밀려나는 함수
    def sep_enemies(self, enemies, player_rect = None): #적의 종류가 늘어나면 나중에 수정 필요
        for other in enemies:
            if other is self: #감지되는 것이 자신인지 판단하기
                continue
            if self.rect.colliderect(other.rect): #서로 충돌했나 감지
                dx = self.world_x - other.world_x #서로 x, y가 얼마나 떨어졌는지 구하기
                dy = self.world_y - other.world_y
                length = math.hypot(dx, dy)
                if length != 0:
                    dx /= length #이동할 방향을  -1, 1로 구하기
                    dy /= length
                    self.world_x += dx * 2 #방향 * 2px 만큼 이동
                    self.world_y += dy * 2

        if player_rect and self.rect.colliderect(player_rect) and not(self.state == 'attacking'):
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
        if self.current_stat['hp'] > 0:
            screen_x = int(self.world_x - pov_x)
            screen_y = int(self.world_y - pov_y)
            screen.blit(self.image, (screen_x, screen_y))

class game:
    def __init__(self):
        self.screen = screen
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.clock = pygame.time.Clock()
        self.current_time = 0

        self.background = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Background.PNG'))
        self.player_image = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Player.PNG'))
        self.enemy_image = pygame.image.load(os.path.join(BASE_DIR, 'images', 'Enemy.PNG'))
        self.swing_images = [
        pygame.transform.scale(
            pygame.image.load(os.path.join(BASE_DIR, 'images', 'sword1.PNG')).convert_alpha(),
            (280, 280)
        ),
        pygame.transform.scale(
            pygame.image.load(os.path.join(BASE_DIR, 'images', 'sword2.PNG')).convert_alpha(),
            (280, 280)
        ),
        pygame.transform.scale(
            pygame.image.load(os.path.join(BASE_DIR, 'images', 'sword3.PNG')).convert_alpha(),
            (280, 280)
        )
        ]


        self.player = Player()
        self.player_stats = self.player.final_stats()
        self.player_world_x = screen_w//2
        self.player_world_y = screen_h//2

        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_range = {'min':150,'max':600}
        self.enemy_max_amount = 10 #적의 최대수

        self.sword = Sword(self.swing_images, attack_damage=20, attack_speed=500, attack_range=150)


    def start(self):
        global current_state

        start_button_rect = pygame.Rect(400, 400, 400, 50)

        pygame.draw.rect(self.screen, (0, 0, 0), [0, 0, 1200, 700])

        if start_button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (255, 255, 255), [400, 400, 400, 50])
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_state = 'running'

        else:
            pygame.draw.rect(self.screen, (255, 255, 255), [450, 410, 300, 30])

    def update(self, dt):
        dt = self.clock.tick(60) #매 프레임마다 지나는 시간 체크(ms)
        self.current_time += dt
        self.enemy_spawn_timer += dt

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

        self.player_world_x += dx * self.player_stats['speed'] #방향 + 속도
        self.player_world_y += dy * self.player_stats['speed']

        self.pov_x = self.player_world_x - screen_w // 2 + 25
        self.pov_y = self.player_world_y - screen_h // 2 + 25

        if self.enemy_spawn_timer >= 200 and len(self.enemies) < self.enemy_max_amount: #적의 최대치보다 적을시, 적이 스폰되는 지점 정하기
            self.enemy_spawn_timer = 0 #타이머 리셋

            #플레이어로부터 x축 방향으로 100 ~ 300px만큼 떨어진 위치로 x좌표 설정
            enemy_x = self.player_world_x + random.choice([-1, 1]) * random.randint(self.enemy_spawn_range['min'], self.enemy_spawn_range['max'])
            #플레이어로부터 y축 방향으로 100 ~ 300px만큼 떨어진 위치로 y좌표 설정
            enemy_y = self.player_world_y + random.choice([-1, 1]) * random.randint(self.enemy_spawn_range['min'], self.enemy_spawn_range['max'])

            self.enemies.append(Enemy(enemy_x, enemy_y, self.enemy_image)) #enemies 리스트에 적 추가

    def player_attack(self):
        self.sword.attack(self.player_world_x, self.player_world_y, self.enemies)
        self.sword.swing(
            self.screen,
            pygame.time.get_ticks(),
            self.player_world_x,
            self.player_world_y,
            self.pov_x,
            self.pov_y
            )



    def draw(self):
        # 무한 반복하는 배경 그리기
        for x in range(-screen_w, screen_w + screen_w, screen_w):
            for y in range(-screen_h, screen_h + screen_h, screen_h):
                self.screen.blit(self.background, (x - (self.pov_x % screen_w), y - (self.pov_y % screen_h)))

        # 플레이어 그리기 (화면 중앙)
        self.screen.blit(self.player_image, (screen_w // 2 - 25, screen_h // 2 - 25))

        player_rect = pygame.Rect(self.player_world_x, self.player_world_y, self.player.width, self.player.height) #플레이어의 좌표, 너비, 높이가 담긴 직사각형 정보
        #모든 적 그리기
        for enemy in self.enemies:
            enemy.move_toward(self.player_stats, self.player_world_x, self.player_world_y, self.current_time) #플레이어한테 이동하는 함수 모든 적에게 실행
            enemy.draw_enemy(self.screen, self.pov_x, self.pov_y) #적 그리는 함수 실행
            enemy.sep_enemies(self.enemies, player_rect) #적끼리 서로 충돌할때 서로 멀어지는 함수 실행

        pygame.draw.rect(self.screen, (255, 0, 0), [0, 0, self.player_stats['hp'], 50]) #hp바 생성

BASE_DIR = os.path.dirname(__file__)

current_state = 'start'

screen_w = 1200 #화면 가로
screen_h = 700 #화면 세로

# 플레이어 좌표 (화면 중앙)
player_x = screen_w // 2 - 50
player_y = screen_h // 2 - 50

#플레이어한테 기본 스탯 부여
player = Player()
player_stats = player.final_stats()

#플레이어의 실제 월드 좌표
player_world_x = screen_w // 2
player_world_y = screen_h // 2

enemies = []
enemy_spawn_timer = 0 #2초(2000ms)마다 적 생성
enemy_spawn_range = {'min' : 150, 'max' : 600} #플레이어 주변 150 ~600픽셀 이내 거리에서 생성
enemy_max_amount = 10 #적의 최대수

screen = pygame.display.set_mode((screen_w, screen_h))

current_time = 0
pygame.display.set_caption('Vampire Survivor 2') #게임 이름, 나중에 변경

clock = pygame.time.Clock() #프레임 조절
Game = game()

running = True

while running:
    dt = Game.clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if current_state == 'start':
        Game.start()
    elif current_state == 'running':
        Game.update(dt)
        Game.player_attack()
        Game.draw()

    pygame.display.flip()

pygame.quit()