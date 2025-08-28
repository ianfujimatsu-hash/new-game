# -*- coding: utf-8 -*-
import pygame
import sys

from player import Player  # type: ignore
from attack import Attack  # type: ignore
from enemy import Enemy  # type: ignore
from aoe import AoE  # type: ignore
from pierce import PierceAttack # type: ignore
from scatter import ScatterAttack # type: ignore
import math
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SKILL_NONE, SKILL_AOE, SKILL_PIERCE, SKILL_SCATTER  # type: ignore

# Pygameの初期化
pygame.init()

# 画面設定
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
    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
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


# レベルアップ画面を表示する関数


def show_levelup_screen(screen, font, small_font, player, old_stats):
    # 背景の半透明な黒いオーバーレイを作成
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 半透明な黒色で塗りつぶす
    screen.blit(overlay, (0, 0))

    draw_text("レベルアップ！", font, WHITE, screen,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

    # 新しいステータスと古いステータスの差分を表示
    stats_x = SCREEN_WIDTH / 2
    stats_y = SCREEN_HEIGHT / 2 - 120

    current_stats = player.get_status()

    # レベル
    draw_text(f"レベル: {old_stats['level']} -> {current_stats['level']}",
              small_font, WHITE, screen, stats_x, stats_y)

    # 攻撃力
    draw_text(f"攻撃力: {old_stats['attack']} -> {current_stats['attack']}",
              small_font, WHITE, screen, stats_x, stats_y + 40)

    # 防御力
    draw_text(f"防御力: {old_stats['defense']} -> {current_stats['defense']}",
              small_font, WHITE, screen, stats_x, stats_y + 80)

    # スピード
    draw_text(f"スピード: {old_stats['speed']:.1f} -> {current_stats['speed']:.1f}",
              small_font, WHITE, screen, stats_x, stats_y + 120)

    # 最大HP
    draw_text(f"最大HP: {old_stats['maxHp']} -> {current_stats['maxHp']}",
              small_font, WHITE, screen, stats_x, stats_y + 160)

    # Enterキーで続行を促すメッセージ
    draw_text("Enterキーを押して続行", small_font, GRAY, screen,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

    pygame.display.update()

    # キー入力を待機してゲームを一時停止
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enterキーが押されたら
                    waiting_for_input = False

    # レベル2になったらスキル選択画面を表示
    if player.get_status()['level'] == 2:
        show_skill_selection_screen(screen, font, small_font, player)


def show_skill_selection_screen(screen, font, small_font, player):
    """スキル選択画面を表示する関数"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    draw_text("スキルを選択してください", font, WHITE, screen,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

    # 選択肢のボタンを作成
    aoe_button = draw_text("1. 範囲攻撃", small_font, WHITE,
                           screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    pierce_button = draw_text(
        "2. 貫通攻撃", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60)
    scatter_button = draw_text(
        "3. 拡散攻撃", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)

    pygame.display.update()

    waiting_for_selection = True
    while waiting_for_selection:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.skill = SKILL_AOE
                    print("範囲攻撃を選択しました。")
                    waiting_for_selection = False
                elif event.key == pygame.K_2:
                    player.skill = SKILL_PIERCE
                    print("貫通攻撃を選択しました。")
                    waiting_for_selection = False
                elif event.key == pygame.K_3:
                    player.skill = SKILL_SCATTER
                    print("拡散攻撃を選択しました。")
                    waiting_for_selection = False

# ダメージテキストを管理するクラス


class DamageText:
    def __init__(self, x, y, damage, start_time):
        self.x = x
        self.y = y
        self.damage = damage
        self.start_time = start_time
        self.lifetime = 1000  # 1000ミリ秒（1秒）表示

    def update(self, current_time):
        # 1秒後に消滅
        return current_time - self.start_time < self.lifetime

    def draw(self, screen, font, camera_x, camera_y):
        # カメラオフセットを考慮して描画
        text = str(int(self.damage))
        textobj = font.render(text, True, (255, 0, 0))  # 赤色でダメージ表示
        textrect = textobj.get_rect(
            center=(self.x - camera_x, self.y - camera_y - 20))
        self.y -= 1  # 1フレームごとに上に移動
        screen.blit(textobj, textrect)


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

def is_colliding(x, y, player_rect, enemies):
    """指定された座標がプレイヤーまたは他の敵と衝突しているか判定する"""
    new_enemy_rect = pygame.Rect(x, y, 120, 120) # 敵の画像サイズに合わせて調整
    
    # プレイヤーとの衝突判定
    if new_enemy_rect.colliderect(player_rect):
        return True
    
    # 他の敵との衝突判定
    for enemy in enemies:
        if new_enemy_rect.colliderect(enemy.rect):
            return True
            
    return False

def aoe_skill(player_x, player_y, attacks, player_attack):
    """範囲攻撃の処理"""
    # プレイヤーの中心座標
    center_x = player_x
    center_y = player_y
    radius = 150  # 範囲攻撃の半径
    lifetime = 3000     # 3秒で消滅
    damage = player_attack * 3  # 基本ダメージを攻撃力×3に設定

    new_aoe = AoE(center_x, center_y, radius, damage,
                  pygame.time.get_ticks(), lifetime)
    attacks.append(new_aoe)
    print("範囲攻撃が発動しました！")


def pierce_skill(player, attacks, camera_x, camera_y):
    """貫通攻撃の処理"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # マウスの絶対座標
    target_x = mouse_x + camera_x
    target_y = mouse_y + camera_y

    new_pierce = PierceAttack(
        player.x, player.y,
        target_x, target_y,
        speed=15,
        player_attack=player.attack,
        player_width=80,  # プレイヤーの当たり判定サイズと揃える
        player_height=80
    )
    attacks.append(new_pierce)
    print("貫通攻撃が発動しました！")

def scatter_skill(player, player_img_orig, attacks, mouse_x, mouse_y):
    """拡散攻撃の処理"""
    print("拡散攻撃が発動しました！")
    
    # 3つの攻撃を異なる角度で生成
    angles = [-0.1, 0, 0.1]  # ラジアンで角度をずらす（約5.7度ずつ）
    speed = 5
    
    player_center_x = player.x
    player_center_y = player.y
    
    base_angle = math.atan2(mouse_y - player_center_y, mouse_x - player_center_x)
    
    for angle_offset in angles:
        current_angle = base_angle + angle_offset
        
        # ターゲット座標を計算
        target_x = player_center_x + math.cos(current_angle) * 1000
        target_y = player_center_y + math.sin(current_angle) * 1000
        
        new_scatter = ScatterAttack(
            player_center_x, player_center_y,
            target_x, target_y,
            speed, player.attack
        )
        attacks.append(new_scatter)


def start_solo_game():
    """ソロゲームの開始関数"""
    print("ソロゲームを開始します...")
    # キャラクター画像の読み込み
    try:
        player_img_orig = pygame.image.load("assets/player.png").convert_alpha()
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
        print("エラー：assets/player.pngが見つかりません。")
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
    player_image_rect = player_img_orig.get_rect(center=(player.x, player.y))
    for _ in range(5):# 5体の敵を生成
        is_pos_found = False
        while not is_pos_found:
            enemy_x = random.randint(player.x - 1500, player.x + 1500)
            enemy_y = random.randint(player.y - 1500, player.y + 1500)
            
            # プレイヤーから200ピクセル以上離れているかチェック
            if math.hypot(enemy_x - player.x, enemy_y - player.y) > 200:
                is_pos_found = not is_colliding(enemy_x, enemy_y, player_image_rect, enemies)
        enemies.append(Enemy(enemy_x, enemy_y))

    # ダメージテキストを管理するリスト
    damage_texts = []

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
                        # スキルの種類に応じて異なる関数を呼び出す
                        if player.skill == SKILL_AOE:
                            aoe_skill(player.x, player.y,
                                      attacks, player.attack)
                        elif player.skill == SKILL_PIERCE:
                            pierce_skill(player, attacks, camera_x, camera_y)
                        elif player.skill == SKILL_SCATTER:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            mouse_abs_x = mouse_x + (player.x - SCREEN_WIDTH / 2)
                            mouse_abs_y = mouse_y + (player.y - SCREEN_HEIGHT / 2)
                            scatter_skill(player, player_img_orig, attacks, mouse_abs_x, mouse_abs_y)
                        else:
                            print("スキルが選択されていません。")
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
        screen.fill(GRAY)

        # グリッドの描画
        # 横線
        for y in range(0, SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, BLACK, (0 - camera_x % GRID_SIZE, y - camera_y %
                             GRID_SIZE), (SCREEN_WIDTH, y - camera_y % GRID_SIZE))

        # 縦線
        for x in range(0, SCREEN_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, BLACK, (x - camera_x % GRID_SIZE, 0 - camera_y %
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
                                mouse_abs_x, mouse_abs_y, 5, player.attack,current_time)
            attacks.append(new_attack)
            last_attack_time = current_time

        aoes_to_remove = []
        for aoe in [a for a in attacks if isinstance(a, AoE)]:
            if not aoe.update(current_time):  # 先に寿命判定
                aoes_to_remove.append(aoe)
            else:
                aoe.draw(screen, camera_x, camera_y)  # 生きてるときだけ描画

        # ここでAoEをattacksから削除する処理を追加
        attacks = [a for a in attacks if a not in aoes_to_remove]

        # 当たり判定処理
        attacks_to_remove = []
        enemies_to_remove = []
        for attack in attacks:
            if isinstance(attack, Attack):  # 通常攻撃の当たり判定
                for enemy in enemies:
                    if attack.rect.colliderect(enemy.rect):
                        print("攻撃が敵に当たりました！")
                        # ダメージテキストを生成
                        final_damage = attack.calculate_damage(enemy.defense)
                        if final_damage > 0:
                            damage_texts.append(DamageText(enemy.rect.centerx, enemy.rect.centery, final_damage, current_time))
                            # 敵の体力を減らす
                            enemy.health -= final_damage

                        # 攻撃を削除リストに追加
                        attacks_to_remove.append(attack)

                        # 敵の体力が0以下になったら削除リストに追加
                        if enemy.health <= 0:
                            enemies_to_remove.append(enemy)

            elif isinstance(attack, AoE):  # 範囲攻撃の当たり判定
                for enemy in enemies:
                    if attack.rect.colliderect(enemy.rect):
                        if not hasattr(attack, 'hit_enemies') or enemy not in attack.hit_enemies:
                            # ダメージ計算
                            final_damage = attack.damage - enemy.defense
                            if final_damage > 0:
                                damage_texts.append(DamageText(
                                    enemy.rect.centerx, enemy.rect.centery, final_damage, current_time))
                                enemy.health -= final_damage
                            if enemy.health <= 0:
                                enemies_to_remove.append(enemy)

                            # 同じAoEで二重ヒットしないよう記録
                            if not hasattr(attack, 'hit_enemies'):
                                attack.hit_enemies = [enemy]
                            else:
                                attack.hit_enemies.append(enemy)

            elif isinstance(attack, PierceAttack): # 貫通攻撃の当たり判定
                for enemy in enemies:
                    if attack.rect.colliderect(enemy.rect):
                        if not hasattr(attack, 'hit_enemies') or enemy not in attack.hit_enemies:
                            final_damage = attack.calculate_damage(enemy.defense)
                            if final_damage > 0:
                                damage_texts.append(DamageText(
                                    enemy.rect.centerx, enemy.rect.centery, final_damage, current_time))
                                enemy.health -= final_damage
                            if enemy.health <= 0:
                                enemies_to_remove.append(enemy)
                            if not hasattr(attack, 'hit_enemies'):
                                attack.hit_enemies = [enemy]
                            else:
                                attack.hit_enemies.append(enemy)

            elif isinstance(attack, ScatterAttack):  # 拡散攻撃の当たり判定
                for enemy in enemies:
                    if attack.rect.colliderect(enemy.rect):
                        if enemy not in attack.hit_enemies:
                            final_damage = attack.calculate_damage(enemy.defense)
                            if final_damage > 0:
                                damage_texts.append(DamageText(
                                    enemy.rect.centerx, enemy.rect.centery, final_damage, current_time))
                                enemy.health -= final_damage
                            if enemy.health <= 0:
                                enemies_to_remove.append(enemy)
                            attack.hit_enemies.append(enemy)
            
                            # 攻撃を削除リストに追加
                            attacks_to_remove.append(attack)
                            break  # ← 同じ弾で他の敵に当たらないようループ終了

        # 削除リストを適用
        attacks = [attack for attack in attacks if attack not in attacks_to_remove and attack not in aoes_to_remove]
        enemies = [enemy for enemy in enemies if enemy not in enemies_to_remove]
        
        # 経験値とレベルアップ処理
        old_stats = player.get_status()
        for enemy in enemies_to_remove:
            player.gain_experience(enemy.exp_drop)
            if player.get_status()['level'] > old_stats['level']:
                show_levelup_screen(
                    screen, font, small_font, player, old_stats)

       # 敵が倒されたら、新しい敵を生成
        if not enemies:
            for _ in range(5):
                enemy_x = random.randint(-500, 500)
                enemy_y = random.randint(-500, 500)
                enemies.append(Enemy(enemy_x, enemy_y))

        # 攻撃の更新と描画
        attacks_to_remove = []
        for attack in attacks:
            attack.update(current_time) if hasattr(attack, "update") else None
            attack.draw(screen, camera_x, camera_y)
            
            # 通常攻撃の射程距離による消去
            if isinstance(attack, Attack) and attack.get_distance_from_start() > 500:
                attacks_to_remove.append(attack)
            # AoEの寿命による消去
            if isinstance(attack, AoE) and not attack.update(current_time):
                attacks_to_remove.append(attack)
            # 貫通攻撃の射程距離による消去
            if isinstance(attack, PierceAttack) and attack.get_distance_from_start() > 1000:
                attacks_to_remove.append(attack)
            # 拡散攻撃の射程距離による消去
            if isinstance(attack, ScatterAttack) and attack.get_distance_from_start() > 500:
                attacks_to_remove.append(attack)
        # リストから削除
        attacks = [a for a in attacks if a not in attacks_to_remove]
        
        # 敵とプレイヤーの当たり判定
        is_invincible = current_time - last_hit_time < invincibility_duration
        for enemy in enemies:
            enemy.update(player.x, player.y, current_time)
            # 敵のHPバーを描画
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
                  screen, 140, SCREEN_HEIGHT - 30)

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

        # ダメージテキストの更新と描画
        damage_texts_to_remove = []
        for text in damage_texts:
            if text.update(current_time):
                text.draw(screen, small_font, camera_x, camera_y)
            else:
                damage_texts_to_remove.append(text)

        for text in damage_texts_to_remove:
            if text in damage_texts:
                damage_texts.remove(text)

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