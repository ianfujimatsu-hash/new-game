# -*- coding: utf-8 -*-
import pygame
import sys

from player import Player  # type: ignore
from attack import Attack  # type: ignore
from enemy import Enemy  # type: ignore
import math
import random

# Pygameの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ゲームメニュー")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# グリッドのサイズ
GRID_SIZE = 50

# フォント設定
try:
    font_path = "C:\\Windows\\Fonts\\msgothic"
    font = pygame.font.Font(font_path, 48)
    small_font = pygame.font.Font(font_path, 30)
except FileNotFoundError:
    # ファイルが見つからない場合は代替フォントを使う
    font = pygame.font.SysFont('meiryo', 48)
    small_font = pygame.font.SysFont('meiryo', 30)


def draw_text(text, font, color, surface, x, y):
    """画面にテキストを描画する関数"""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)
    return textrect


def main_menu():
    """メインメニュー画面のループ"""
    while True:
        # マウスの位置を取得
        mouse_pos = pygame.mouse.get_pos()

        # 画面を塗りつぶす
        screen.fill(WHITE)

        # タイトルテキストの描画
        draw_text('ゲームメニュー', font, BLACK, screen,
                  SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

        # ボタンの描画
        solo_button = draw_text(
            'ソロプレイ', small_font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        multi_button = draw_text(
            'マルチプレイ', small_font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)

        # ホバーエフェクト
        if solo_button.collidepoint(mouse_pos):
            draw_text('ソロプレイ', small_font, GRAY, screen,
                      SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        if multi_button.collidepoint(mouse_pos):
            draw_text('マルチプレイ', small_font, GRAY, screen,
                      SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)

        # イベント処理
        for event in pygame.event.get():
            # ループを終了して関数を抜ける
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if solo_button.collidepoint(event.pos):
                    # ここにソロプレイの開始処理を追加
                    print("ソロプレイが選択されました！")
                    start_solo_game()
                if multi_button.collidepoint(event.pos):
                    # ここにマルチプレイの開始処理を追加
                    print("マルチプレイが選択されました！")
                    start_multi_game()

        # 画面を更新
        pygame.display.update()


def start_solo_game():
    """ソロゲームの開始関数"""
    print("ソロゲームを開始します...")
    # キャラクター画像の読み込み
    try:
        player_img_orig = pygame.image.load("assets/bykin.png").convert_alpha()
        player_img_orig = pygame.transform.scale(player_img_orig, (150, 150))
        e_img_orig = pygame.image.load("assets/E.png").convert_alpha()
        e_img_orig = pygame.transform.scale(e_img_orig, (60, 60))
        q_img_orig = pygame.image.load("assets/Q.png").convert_alpha()
        q_img_orig = pygame.transform.scale(q_img_orig, (60, 60))

        # 敵画像の読み込み
        enemy_img = pygame.image.load("assets/enemy/star.png").convert_alpha()

        # クールダウンタイマー用のSurface
        cooldown_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
    except FileNotFoundError:
        print("エラー：assets/bykin.pngが見つかりません。")
        # 画像が見つからなければ関数を終了
        return

    player_img_dim = player_img_orig.copy()
    player_img_dim.set_alpha(100)  # プレイヤーの半透明画像

    # Playerオブジェクトを作成
    player = Player()
    # キャラクターの初期位置
    player.x = 0
    player.y = 0

    # 当たり判定のサイズを調整
    player_hitbox_width = 80
    player_hitbox_height = 80
    player_rect = pygame.Rect(0, 0, player_hitbox_width, player_hitbox_height)

    # 無敵時間の変数
    last_hit_time = 0
    invincibility_duration = 1000  # 1000ミリ秒（1秒）

    # 攻撃関連の変数
    attacks = []
    last_attack_time = 0
    attack_interval = 1000  # 1秒間隔

    # スキル関連の変数
    last_e_skill_time = 0
    e_cooldown = 3000  # 3秒のクールダウン
    e_img_dim = e_img_orig.copy()
    e_img_dim.fill((0, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)

    # 敵関連の変数
    enemies = []
    for _ in range(5):  # 5体の敵を生成
        enemy_x = random.randint(-1000, 1000)
        enemy_y = random.randint(-1000, 1000)
        enemies.append(Enemy(enemy_x, enemy_y))

    # キャラクターの初期位置と速度
    clock = pygame.time.Clock()

    running = True
    while running:
        # 　イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    current_time = pygame.time.get_ticks()
                    if current_time-last_e_skill_time >= e_cooldown:
                        print("スキルが発動しました！")
                        # ここにスキルの処理を追加
                        last_e_skill_time = current_time

        # キーの状態を取得してキャラクターを移動させる
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.y -= player.speed
        if keys[pygame.K_s]:
            player.y += player.speed
        if keys[pygame.K_a]:
            player.x -= player.speed
        if keys[pygame.K_d]:
            player.x += player.speed

        # 当たり判定の中心をプレイヤーの座標に合わせる
        player_rect.center = (player.x, player.y)

        # カメラオフセットを計算する
        # キャラクターが画面の中心に来るように調整
        camera_x = player.x - SCREEN_WIDTH / 2
        camera_y = player.y - SCREEN_HEIGHT / 2

        # 画面を塗りつぶす
        screen.fill(WHITE)

        # グリッドの描画
        # 横線
        for y in range(0, SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0 - camera_x % GRID_SIZE, y - camera_y %
                             GRID_SIZE), (SCREEN_WIDTH, y - camera_y % GRID_SIZE))

        # 縦線
        for x in range(0, SCREEN_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x - camera_x % GRID_SIZE, 0 - camera_y %
                             GRID_SIZE), (x - camera_x % GRID_SIZE, SCREEN_HEIGHT))

        # 攻撃の発射
        current_time = pygame.time.get_ticks()
        if current_time - last_attack_time > attack_interval:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # マウスの絶対座標を正しく計算する
            mouse_abs_x = mouse_x + (player.x - SCREEN_WIDTH / 2)
            mouse_abs_y = mouse_y + (player.y - SCREEN_HEIGHT / 2)

            # キャラクターの中心から発射
            player_center_x = player.x
            player_center_y = player.y

            # player.attackをAttackクラスに渡す
            new_attack = Attack(player_center_x, player_center_y,
                                mouse_abs_x, mouse_abs_y, 10, player.attack)
            attacks.append(new_attack)
            last_attack_time = current_time

        # 当たり判定処理
        attacks_to_remove = []
        enemies_to_remove = []
        for attack in attacks:
            for enemy in enemies:
                if attack.rect.colliderect(enemy.rect):
                    print("攻撃が敵に当たりました！")
                    # 敵の体力を減らす
                    enemy.health -= attack.damage

                    # 攻撃を削除リストに追加
                    attacks_to_remove.append(attack)

                    # 敵の体力が0以下になったら削除リストに追加
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)

        # 削除リストを適用
        for attack in attacks_to_remove:
            if attack in attacks:
                attacks.remove(attack)
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        # 攻撃の更新と描画
        for attack in attacks[:]:
            attack.update()
            attack.draw(screen, camera_x, camera_y)
            if attack.get_distance_from_start() > 500:
                attacks.remove(attack)

        # 敵とプレイヤーの当たり判定
        is_invincible = current_time - last_hit_time < invincibility_duration
        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)
            # 無敵時間中ではないかチェック
            if player_rect.colliderect(enemy.rect) and not is_invincible:
                print("プレイヤーが敵と衝突しました！")
                # プレイヤーの体力を減らす
                player.currentHp -= enemy.attack
                last_hit_time = current_time  # 最後にダメージを受けた時間を更新
                if player.currentHp <= 0:
                    print("ゲームオーバー")
                    pygame.quit()
                    sys.exit()

        # キャラクターの描画
        player_draw_x = SCREEN_WIDTH / 2 - player_img_orig.get_width() / 2
        player_draw_y = SCREEN_HEIGHT / 2 - player_img_orig.get_height() / 2

        # 無敵時間中は点滅
        if is_invincible and current_time % 400 < 200:
            screen.blit(player_img_dim, (player_draw_x, player_draw_y))
        else:
            screen.blit(player_img_orig, (player_draw_x, player_draw_y))

        # キャラクターの座標を左下に表示
        coords_text = f"X: {int(player.x)}, Y: {int(player.y)}"
        draw_text(coords_text, small_font, BLACK,
                  screen, 120, SCREEN_HEIGHT - 30)

        # HPバーの描画
        hp_bar_width = 200
        hp_bar_height = 20
        hp_bar_x = 20
        hp_bar_y = 20

        # HPの割合を計算
        hp_ratio = player.currentHp / player.maxHp
        current_hp_width = hp_bar_width * hp_ratio

        # HPバーの背景（赤）を描画
        pygame.draw.rect(screen, (255, 0, 0), (hp_bar_x,
                         hp_bar_y, hp_bar_width, hp_bar_height))

        # 現在のHPゲージ（緑）を描画
        pygame.draw.rect(screen, (0, 255, 0), (hp_bar_x,
                         hp_bar_y, current_hp_width, hp_bar_height))

        # HPテキストの描画
        hp_text = f"HP: {int(player.currentHp)}/{int(player.maxHp)}"
        text_x = hp_bar_x + hp_bar_width + 120
        text_y = hp_bar_y + hp_bar_height / 2

        draw_text(hp_text, small_font, BLACK, screen, text_x, text_y)

        # EとQの画像を座標の上に配置
        screen.blit(q_img_orig, (120, SCREEN_HEIGHT-120))
        screen.blit(e_img_orig, (40, SCREEN_HEIGHT-120))

        # クールタイム演出
        current_time = pygame.time.get_ticks()
        if current_time - last_e_skill_time < e_cooldown:
            cooldown_progress = (current_time - last_e_skill_time) / e_cooldown

            # クールダウン用のSurfaceをクリア
            cooldown_surface.fill((0, 0, 0, 0))

            # 半透明の薄いグレー
            overlay_color = (150, 150, 150, 150)

            # クールタイムの進行度に合わせて、円の開始角度と終了角度を計算
            angle_start_overlay = 90
            angle_end_overlay = 90 - (cooldown_progress * 360)

            # Surface上に円を描画
            pygame.draw.arc(cooldown_surface, overlay_color, (0, 0, 60, 60), math.radians(
                angle_start_overlay), math.radians(angle_end_overlay), 60)

            # 完成したSurfaceをメイン画面に貼り付け
            screen.blit(cooldown_surface, (40, SCREEN_HEIGHT - 120))

        # 画面を更新
        pygame.display.update()

        # フレームレートを固定
        clock.tick(60)
    pass


def start_multi_game():
    """マルチゲームの開始関数"""
    print("マルチゲームを開始します...")
    # 実際のマルチゲームのロジックをここに書く
    pass


# メインメニューの開始
if __name__ == '__main__':
    main_menu()
    # プログラム全体の終了時にPygameを終了
    pygame.quit()
    sys.exit()
