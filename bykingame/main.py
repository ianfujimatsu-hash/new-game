# -*- coding: utf-8 -*-
import pygame
import sys

from player import Player  # type: ignore
from attack import Attack  # type: ignore
from enemy import Enemy  # type: ignore
from aoe import AoE  # type: ignore
from pierce import PierceAttack  # type: ignore
from scatter import ScatterAttack  # type: ignore
import math
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SKILL_NONE, SKILL_AOE, SKILL_PIERCE, SKILL_SCATTER  # type: ignore
from item import Item, ITEM_TYPE_EQUIPMENT, ITEM_TYPE_MATERIAL, ITEM_TYPE_CONSUMABLE  # type: ignore
from item_data import RECIPES, ITEMS  # type: ignore

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

settings_img = pygame.image.load("assets/Settings.png").convert_alpha()
settings_img = pygame.transform.scale(settings_img, (60, 60))

# フォント設定
try:
    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    font = pygame.font.Font(font_path, 48)
    small_font = pygame.font.Font(font_path, 30)
    tiny_font = pygame.font.Font(font_path, 18)
except FileNotFoundError:
    # ファイルが見つからない場合は代替フォントを使う
    font = pygame.font.SysFont('meiryo', 48)
    small_font = pygame.font.SysFont('meiryo', 30)
    tiny_font = pygame.font.SysFont('meiryo', 18)


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
    draw_text("Spaceキーを押して続行", small_font, GRAY, screen,
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
                if event.key == pygame.K_SPACE:  # SPACEキーが押されたら
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
    new_enemy_rect = pygame.Rect(x, y, 120, 120)  # 敵の画像サイズに合わせて調整

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
    angles = [-0.3, 0, 0.3]  # ラジアンで角度をずらす（約5.7度ずつ）
    speed = 5

    player_center_x = player.x
    player_center_y = player.y

    base_angle = math.atan2(mouse_y - player_center_y,
                            mouse_x - player_center_x)

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


def show_inventory_screen(screen, font, small_font, player):
    """インベントリ画面を表示する関数"""

    # インベントリ時はカーソルを見えるように
    pygame.mouse.set_visible(True)

    # 今の画面をコピーして保存
    background = screen.copy()

    # --- インベントリ枠の描画（10x10グリッド） ---
    slots_cols = 10
    slots_rows = 10
    slot_size = 40
    slot_margin = 8
    slots_start_x = SCREEN_WIDTH / 20
    slots_start_y = SCREEN_HEIGHT / 10 + 60
    waiting_for_close = True
    clock = pygame.time.Clock()
    craft_selected_index = 0  # クラフト対象レシピのインデックス

    # --- クラフト関連ヘルパ ---
    def player_has_any_material_for_recipe(recipe, player):
        for mat in recipe["materials"]:
            for inv in player.inventory:
                if inv["item"].name == mat["name"]:
                    return True
        return False

    def get_silhouette(img):
        arr = pygame.surfarray.pixels3d(img).copy()
        gray = arr.mean(axis=2)
        arr[:, :, 0] = gray
        arr[:, :, 1] = gray
        arr[:, :, 2] = gray
        new_img = pygame.surfarray.make_surface(arr)
        new_img.set_alpha(100)
        return new_img

    while waiting_for_close:
        # 入力イベントを処理
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    waiting_for_close = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gear_rect.collidepoint(event.pos):
                    result = show_settings_menu(screen, font, small_font)
                    if result == "resume":
                        pass  # 何もしない（インベントリ再開）
                    elif result == "main_menu":
                        return "main_menu"  # 呼び出し元でmain_menu()を呼ぶ
                    elif result == "quit":
                        pygame.quit()
                        sys.exit()

        # 直前のゲーム画面を再描画
        screen.blit(background, (0, 0))

        # 画面クリア＆オーバーレイ
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        draw_text("インベントリ", font, WHITE, screen,
                  SCREEN_WIDTH / 8, SCREEN_HEIGHT / 10)

        # マウス座標を毎フレーム取得
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_index = None

        # --- インベントリスロット描画＆マウス選択判定 ---
        for row in range(slots_rows):
            for col in range(slots_cols):
                rect_x = slots_start_x + col * (slot_size + slot_margin)
                rect_y = slots_start_y + row * (slot_size + slot_margin)
                slot_rect = pygame.Rect(rect_x, rect_y, slot_size, slot_size)
                idx = row * slots_cols + col
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    hovered_index = idx
                # ハイライト
                if hovered_index == idx:
                    pygame.draw.rect(screen, (255, 255, 0), slot_rect, 3)
                else:
                    pygame.draw.rect(screen, (255, 255, 255), slot_rect, 2)
                # アイテムと個数
                if hasattr(player, "inventory") and idx < len(player.inventory):
                    inv = player.inventory[idx]
                    item = inv["item"]
                    count = inv["count"]
                    if item.image:
                        img_x = rect_x + \
                            (slot_size - item.image.get_width()) // 2
                        img_y = rect_y + \
                            (slot_size - item.image.get_height()) // 2
                        screen.blit(item.image, (img_x, img_y))
                        count_text = str(count)
                        count_surface = small_font.render(
                            count_text, True, (255, 255, 255))
                        screen.blit(count_surface, (rect_x +
                                    slot_size - 20, rect_y + slot_size - 26))

        # 右の詳細欄
        info_x = slots_start_x + slots_cols * (slot_size + slot_margin) + 160
        info_y = slots_start_y
        if (hasattr(player, "inventory")
            and player.inventory
            and hovered_index is not None
                and hovered_index < len(player.inventory)):
            selected_item = player.inventory[hovered_index]["item"]
            selected_count = player.inventory[hovered_index]["count"]
            # item_dataから情報取得
            item_info = ITEMS.get(selected_item.name)
            if item_info:
                draw_text(f"名前: {item_info['name']}", small_font,
                          (255, 255, 255), screen, info_x + 100, info_y + 20)
                draw_text(f"種別: {item_info['item_type']}", small_font,
                          (255, 255, 255), screen, info_x + 100, info_y + 60)
                draw_text(f"個数: {selected_count}", small_font,
                          (255, 255, 255), screen, info_x + 100, info_y + 100)
                draw_text(f"説明: {item_info['description']}", small_font,
                          (255, 255, 255), screen, info_x + 120, info_y + 160)
            else:
                # 万一item_dataになければ…
                draw_text("アイテム情報なし", small_font, (255, 255, 255),
                          screen, info_x + 100, info_y + 40)
        else:
            draw_text("アイテムがありません", small_font, (255, 255, 255),
                      screen, info_x + 100, info_y + 40)

        # --- クラフトUI ---
        craft_ui_x = 40
        craft_ui_y = SCREEN_HEIGHT - 180
        craft_ui_width = 360
        craft_ui_height = 120

        unlocked_indices = [i for i, r in enumerate(
            RECIPES) if player_has_any_material_for_recipe(r, player)]
        if unlocked_indices:
            craft_selected_index = unlocked_indices[craft_selected_index % len(
                unlocked_indices)]
        else:
            craft_selected_index = 0

        recipe = RECIPES[craft_selected_index]
        result_info = recipe["result"]
        mat_info_list = recipe["materials"]

        # クラフト枠
        pygame.draw.rect(
            screen, (60, 60, 60),
            (craft_ui_x, craft_ui_y, craft_ui_width, craft_ui_height),
            border_radius=12
        )
        draw_text("クラフト", tiny_font, WHITE, screen,
                  craft_ui_x+44, craft_ui_y+18)

        # 完成品画像・名前
        try:
            img = pygame.image.load(result_info["image_path"]).convert_alpha()
            img = pygame.transform.smoothscale(img, (32, 32))
        except:
            img = pygame.Surface((32, 32), pygame.SRCALPHA)
            img.fill((100, 100, 100, 100))
        player_has_all = all(
            any(inv["item"].name == mat["name"] and inv["count"]
                >= mat["count"] for inv in player.inventory)
            for mat in mat_info_list
        )
        player_has_any = player_has_any_material_for_recipe(recipe, player)
        img_surf = img if player_has_all else get_silhouette(img)
        screen.blit(img_surf, (craft_ui_x+12, craft_ui_y+36))

        # 素材リスト：縦並び・画像小さく・文字も小さく
        mat_base_x = craft_ui_x + 112
        mat_base_y = craft_ui_y + 32
        mat_line_height = 30

        mouse_pos = pygame.mouse.get_pos()
        tooltip_text = None  # ツールチップ用

        for i, mat in enumerate(mat_info_list):
            mat_item = ITEMS.get(mat["name"])
            try:
                mat_img = pygame.image.load(
                    mat_item["image_path"]).convert_alpha()
                mat_img = pygame.transform.smoothscale(mat_img, (24, 24))
            except:
                mat_img = pygame.Surface((24, 24), pygame.SRCALPHA)
                mat_img.fill((120, 120, 120, 120))

            inv_count = 0
            for inv in player.inventory:
                if inv["item"].name == mat["name"]:
                    inv_count = inv["count"]
                    break
            enough = inv_count >= mat["count"]
            mat_img_disp = mat_img if enough else get_silhouette(mat_img)
            y = mat_base_y + i * mat_line_height

            # 描画
            screen.blit(mat_img_disp, (mat_base_x, y))

            # --- ホバー判定 ---
            rect = pygame.Rect(mat_base_x, y, 24, 24)
            if rect.collidepoint(mouse_pos):
                tooltip_text = f"{mat['name']} : 所持 {inv_count}"

        # --- ツールチップを描画 ---
        if tooltip_text:
            tx, ty = mouse_pos
            # 背景の小さな矩形
            tooltip_surf = tiny_font.render(tooltip_text, True, WHITE)
            tw, th = tooltip_surf.get_size()
            pygame.draw.rect(screen, (30, 30, 30),
                             (tx+16, ty, tw+8, th+4), border_radius=4)
            screen.blit(tooltip_surf, (tx+20, ty+2))

        # --- クラフトUIの操作判定もここでまとめて ---
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if unlocked_indices:
                    craft_selected_index = (
                        craft_selected_index + event.y) % len(unlocked_indices)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if craft_ui_x <= mx <= craft_ui_x+craft_ui_width and craft_ui_y <= my <= craft_ui_y+craft_ui_height:
                    if player_has_all:
                        # 素材消費
                        for mat in mat_info_list:
                            for inv in player.inventory:
                                if inv["item"].name == mat["name"]:
                                    inv["count"] -= mat["count"]
                                    if inv["count"] <= 0:
                                        player.inventory.remove(inv)
                                    break
                        # 作成アイテムを追加
                        made = False
                        for inv in player.inventory:
                            if inv["item"].name == result_info["name"]:
                                inv["count"] += 1
                                made = True
                                break
                        if not made:
                            item = Item(
                                result_info["name"], result_info["item_type"], result_info["image_path"])
                            player.inventory.append({"item": item, "count": 1})

        # プレイヤーの現在のステータスを表示
        current_stats = player.get_status()
        stats_x = SCREEN_WIDTH - 200
        stats_y = SCREEN_HEIGHT / 10

        draw_text(f"レベル: {current_stats['level']}",
                  small_font, WHITE, screen, stats_x, stats_y)
        draw_text(f"攻撃力: {current_stats['attack']}",
                  small_font, WHITE, screen, stats_x, stats_y + 40)
        draw_text(f"防御力: {current_stats['defense']}",
                  small_font, WHITE, screen, stats_x, stats_y + 80)
        draw_text(f"スピード: {current_stats['speed']:.1f}",
                  small_font, WHITE, screen, stats_x, stats_y + 120)
        draw_text(f"HP: {current_stats['currentHp']}/{current_stats['maxHp']}",
                  small_font, WHITE, screen, stats_x, stats_y + 160)
        draw_text(f"経験値: {current_stats['experience']}/{current_stats['experienceToNextLevel']}",
                  small_font, WHITE, screen, stats_x, stats_y + 200)

        # 歯車アイコンの座標
        gear_x = SCREEN_WIDTH - 60
        gear_y = SCREEN_HEIGHT - 60
        screen.blit(settings_img, (gear_x, gear_y))
        gear_rect = pygame.Rect(
            gear_x, gear_y, settings_img.get_width(), settings_img.get_height())

        # 閉じるためのメッセージ
        draw_text("Tabキーを押してゲームに戻る", small_font, GRAY, screen,
                  SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

        pygame.display.update()
        clock.tick(60)   # ← ここでFPSを制御


def show_settings_menu(screen, font, small_font):
    # メニュー内容
    options = ["ゲーム再開", "メインメニューに戻る", "ゲームを終了"]
    selected = 0
    clock = pygame.time.Clock()
    while True:
        # 背景の半透明
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # メニュー描画
        for i, text in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            draw_text(text, font, color, screen, SCREEN_WIDTH /
                      2, SCREEN_HEIGHT / 2 + i * 80)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        return "resume"
                    elif selected == 1:
                        return "main_menu"
                    elif selected == 2:
                        return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, text in enumerate(options):
                    tx, ty = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 80
                    rect = pygame.Rect(tx-150, ty-30, 300, 60)
                    if rect.collidepoint(mx, my):
                        if i == 0:
                            return "resume"
                        elif i == 1:
                            return "main_menu"
                        elif i == 2:
                            return "quit"


def start_solo_game():
    """ソロゲームの開始関数"""
    print("ソロゲームを開始します...")
    # キャラクター画像の読み込み
    try:
        player_img_orig = pygame.image.load(
            "assets/player.png").convert_alpha()
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
    for _ in range(5):  # 5体の敵を生成
        is_pos_found = False
        while not is_pos_found:
            # 極座標で円周内をランダムに選ぶ（より均等な分布）
            theta = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, 500)
            enemy_x = math.cos(theta) * r
            enemy_y = math.sin(theta) * r

            # プレイヤーから200ピクセル以上離れているか
            if math.hypot(enemy_x - player.x, enemy_y - player.y) > 200:
                # 他の敵・プレイヤーと重なっていないか
                if not is_colliding(enemy_x, enemy_y, player_image_rect, enemies):
                    is_pos_found = True
        enemies.append(Enemy(enemy_x, enemy_y))

    # アイテムドロップ用リスト
    dropped_items = []

    # インベントリ（アイテムリスト）
    player.inventory = []

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
                            mouse_abs_x = mouse_x + \
                                (player.x - SCREEN_WIDTH / 2)
                            mouse_abs_y = mouse_y + \
                                (player.y - SCREEN_HEIGHT / 2)
                            scatter_skill(player, player_img_orig,
                                          attacks, mouse_abs_x, mouse_abs_y)
                        else:
                            print("スキルが選択されていません。")
                        last_e_skill_time = current_time

                # Tabキーが押されたらインベントリを開く
                if event.key == pygame.K_TAB:
                    show_inventory_screen(screen, font, small_font, player)

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
                                mouse_abs_x, mouse_abs_y, 5, player.attack, current_time)
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
                            damage_texts.append(DamageText(
                                enemy.rect.centerx, enemy.rect.centery, final_damage, current_time))
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

            elif isinstance(attack, PierceAttack):  # 貫通攻撃の当たり判定
                for enemy in enemies:
                    if attack.rect.colliderect(enemy.rect):
                        if not hasattr(attack, 'hit_enemies') or enemy not in attack.hit_enemies:
                            final_damage = attack.calculate_damage(
                                enemy.defense)
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
                            final_damage = attack.calculate_damage(
                                enemy.defense)
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
        attacks = [
            attack for attack in attacks if attack not in attacks_to_remove and attack not in aoes_to_remove]
        enemies = [enemy for enemy in enemies if enemy not in enemies_to_remove]

        # 経験値とレベルアップ処理
        old_stats = player.get_status()
        for enemy in enemies_to_remove:
            # アイテムのドロップ処理
            for item_name, item_info in ITEMS.items():
                if random.random() < item_info["drop_rate"]:
                    item = Item(
                        item_info["name"], item_info["item_type"], item_info["image_path"])
                    dropped_items.append({
                        "item": item,
                        "x": enemy.rect.centerx,
                        "y": enemy.rect.centery
                    })
            # 経験値の取得処理
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

        # --- ドロップアイテムの取得判定 ---
        items_to_remove = []
        for dropped in dropped_items:
            item_rect = pygame.Rect(
                dropped["x"] - 20,  # 32x32画像なら中心合わせ
                dropped["y"] - 20,
                40,
                40
            )
            if player_rect.colliderect(item_rect):
                # 既に同じアイテムがある場合はカウントを増やす
                found = False
                for inv in player.inventory:
                    if inv["item"].name == dropped["item"].name:
                        inv["count"] += 1
                        found = True
                        break
                if not found:
                    player.inventory.append(
                        {"item": dropped["item"], "count": 1})
                items_to_remove.append(dropped)
                # 取得演出やSEなどが必要ならここで追加
        for dropped in items_to_remove:
            dropped_items.remove(dropped)

        # --- ドロップアイテムの描画 ---
        for dropped in dropped_items:
            item = dropped["item"]
            x = dropped["x"] - camera_x - (item.image.get_width() // 2)
            y = dropped["y"] - camera_y - (item.image.get_height() // 2)
            if item.image:
                screen.blit(item.image, (x, y))

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
