# scatter.py
import pygame
import math


class ScatterAttack:
    def __init__(self, center_x, center_y, target_x, target_y, speed, player_attack):
        """拡散攻撃の初期設定"""
        self.image = pygame.image.load("assets/attack01.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # サイズを調整

        # キャラクターの中心座標から発射
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.start_pos = (center_x, center_y)
        self.player_attack = player_attack

        # 攻撃の角度を計算
        angle = math.atan2(target_y - center_y, target_x - center_x)
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed

        # 攻撃が消えたかどうかのフラグ
        self.active = True
        self.hit_enemies = []
        
    def update(self, current_time=None):
        """攻撃の位置を更新する"""
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

    def draw(self, screen, camera_x, camera_y):
        """攻撃を画面に描画する"""
        if self.active:
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

    def get_distance_from_start(self):
        """発射地点からの距離を計算する"""
        dx = self.rect.centerx - self.start_pos[0]
        dy = self.rect.centery - self.start_pos[1]
        return (dx**2 + dy**2)**0.5

    def calculate_damage(self, enemy_defense):
        """敵の防御力を考慮してダメージを計算する"""
        damage = self.player_attack - enemy_defense
        return max(0, damage)