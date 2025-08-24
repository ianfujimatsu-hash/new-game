# player.py
from constants import SKILL_NONE


class Player:
    def __init__(self):
        """プレイヤーキャラクターのステータスを初期化する"""
        self.level = 1
        self.attack = 100
        self.defense = 5
        self.speed = 10
        self.maxHp = 100
        self.currentHp = self.maxHp
        self.experience = 0
        self.experienceToNextLevel = 10

        # キャラクターの座標
        self.x = 0
        self.y = 0
        # スキルを初期化
        self.skill = SKILL_NONE

    def gain_experience(self, exp):
        """経験値を獲得する"""
        self.experience += exp
        if self.experience >= self.experienceToNextLevel:
            self.level_up()

    def level_up(self):
        """レベルアップ処理"""
        self.level += 1
        self.experience -= self.experienceToNextLevel
        self.experienceToNextLevel = int(
            self.experienceToNextLevel * 1.5)  # 次のレベルまでの経験値を増やす

        # ステータスを上昇させる
        self.attack += 2
        self.defense += 1
        self.speed += 0.2
        self.maxHp += 10
        self.currentHp = self.maxHp  # HPを全回復

        print(f"レベルアップ！レベル {self.level} になりました！")

    def get_status(self):
        """現在のステータスを返す"""
        return {
            "level": self.level,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "maxHp": self.maxHp,
            "currentHp": self.currentHp,
            "experience": self.experience,
            "experienceToNextLevel": self.experienceToNextLevel,
        }
        pass
