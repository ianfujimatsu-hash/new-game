# aoe.py
import pygame


class AoE:
    def __init__(self, x, y, radius, damage, start_time, lifetime):
        """範囲攻撃の初期設定"""
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.start_time = start_time
        self.lifetime = lifetime
        self.rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self, current_time):
        """攻撃の生存時間を更新する"""
        return current_time - self.start_time < self.lifetime

    def draw(self, screen, camera_x, camera_y):
        """範囲攻撃を画面に描画する（円形のエフェクト）"""
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 100, 100, 100), (self.radius, self.radius), self.radius)
        screen.blit(surf, (int(self.x - camera_x - self.radius), int(self.y - camera_y - self.radius)))
