import pygame
import math


class Attack:
    def __init__(self, x, y, target_x, target_y, speed, damage):
        """攻撃の初期設定"""
        self.image = pygame.image.load("assets/attack.png").convert_alpha()

        # サイズを調整
        self.image = pygame.transform.scale(self.image, (20, 20))

        # 攻撃の初期位置を渡された中心座標に設定
        self.rect = self.image.get_rect(center=(x, y))

        # 発射時の位置を記録
        self.start_pos = (x, y)
        self.damage = damage

        # 攻撃の角度を計算
        angle = math.atan2(target_y - y, target_x - x)

        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed

    def update(self):
        """攻撃の位置を更新する"""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def draw(self, screen, camera_x, camera_y):
        """攻撃を画面に描画する"""
        screen.blit(self.image, (self.rect.x -
                                 camera_x, self.rect.y - camera_y))

    def get_distance_from_start(self):
        """発射地点からの距離を計算する"""
        dx = self.rect.centerx - self.start_pos[0]
        dy = self.rect.centery - self.start_pos[1]
        return (dx**2 + dy**2)**0.5
