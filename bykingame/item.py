# item.py
import pygame
import os

class Item:
    def __init__(self, name, item_type, image_path=None):
        self.name = name
        self.item_type = item_type
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40)) # 画像サイズを調整

# アイテムのタイプを定数として定義
ITEM_TYPE_EQUIPMENT = "装備"
ITEM_TYPE_MATERIAL = "素材"
ITEM_TYPE_CONSUMABLE = "消耗品"