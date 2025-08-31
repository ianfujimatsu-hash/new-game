import pygame

# Pygameの初期化（もし他の場所でやるならここは消してOK）
pygame.init()

# スキルの種類を定義
SKILL_NONE = 0
SKILL_AOE = 1   # 範囲攻撃
SKILL_PIERCE = 2  # 貫通攻撃
SKILL_SCATTER = 3  # 拡散攻撃

# ディスプレイサイズを取得
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
