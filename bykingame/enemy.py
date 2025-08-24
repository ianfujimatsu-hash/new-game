# enemy.py
import pygame
import random
import math


class Enemy:
    def __init__(self, x, y):
        """敵キャラクターの初期設定"""
        self.image_orig = pygame.image.load(
            "assets/enemy/star.png").convert_alpha()
        self.image_orig = pygame.transform.scale(self.image_orig, (120, 120))
        self.image = self.image_orig.copy()
        # 座標は変数で管理
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed = 0.5
        self.max_health = 100
        self.health = self.max_health
        self.attack = 5
        self.defense = 2
        self.last_move_time = pygame.time.get_ticks()
        self.move_interval = 4000  # 4秒
        self.move_direction = (0, 0)  # (x方向, y方向)
        self.angle = 0
        self.rotation_speed = 1  # 回転の速さ
        self.exp_drop = 20  # 敵を倒したときに得られる経験値

    def update(self, player_x, player_y, current_time):
        """敵の位置を更新する"""
        current_time = pygame.time.get_ticks()

        # 2秒ごとに移動方向を変更
        if current_time - self.last_move_time > self.move_interval:
            # ランダムな角度を生成
            angle = random.uniform(0, 2 * math.pi)

            # 角度から移動方向を計算
            self.move_direction = (math.cos(angle), math.sin(angle))
            self.last_move_time = current_time

        # 敵の座標を更新
        self.x += self.move_direction[0] * self.speed
        self.y += self.move_direction[1] * self.speed

        # 回転処理
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.image_orig, self.angle)

        # 回転後の画像用に rect を更新（座標は self.x, self.y 基準）
        self.rect = self.image.get_rect(center=(self.x, self.y))

        pass

    def draw(self, screen, camera_x, camera_y):
        """敵を画面に描画する"""
        # 敵の描画
        screen.blit(self.image, (self.rect.x -
                    camera_x, self.rect.y - camera_y))

        # HPバーの描画
        hp_bar_width = 80
        hp_bar_height = 5
        hp_ratio = self.health / self.max_health

        if hp_ratio > 0:
            # HPバーの位置は "元の中心座標" を基準にする
            center_x, center_y = self.rect.center

            hp_bar_x = center_x - hp_bar_width / 2
            hp_bar_y = center_y - 70  # キャラの頭上に固定（調整可能）

            # HPバーの背景（赤）
            pygame.draw.rect(screen, (255, 0, 0),
                             (hp_bar_x - camera_x, hp_bar_y - camera_y,
                             hp_bar_width, hp_bar_height))

            # HPゲージ（緑）
            pygame.draw.rect(screen, (0, 255, 0),
                             (hp_bar_x - camera_x, hp_bar_y - camera_y,
                             hp_bar_width * hp_ratio, hp_bar_height))
