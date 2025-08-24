# enemy.py
import pygame


class Enemy:
    def __init__(self, x, y):
        """敵キャラクターの初期設定"""
        self.image = pygame.image.load("assets/enemy/star.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.health = 10
        self.attack = 5
        self.defense = 2

    def update(self):
        """敵の位置を更新する（ここでは何もしません）"""
        pass

    def draw(self, screen, camera_x, camera_y):
        """敵を画面に描画する"""
        screen.blit(self.image, (self.rect.x -
                    camera_x, self.rect.y - camera_y))
