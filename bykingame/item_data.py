ITEMS = {
    "バイオゲル": {
        "name": "バイオゲル",
        "item_type": "消耗品",
        "image_path": "assets/Biogel_consumable.png",
        "description": "HPを10%回復",
        "drop_rate": 0.5
    },
    "スターライトパーティクル": {
        "name": "スターライトパーティクル",
        "item_type": "素材",
        "image_path": "assets/Starlightparticles_material.png",
        "description": "希少な星の粒子。合成素材。",
        "drop_rate": 0.1
    },
    "オーダーセル膜": {
        "name": "オーダーセル膜",
        "item_type": "素材",
        "image_path": "assets/Ordercellmembrane_material.png",
        "description": "秩序細胞の膜。合成素材。",
        "drop_rate": 0.2
    }
}

RECIPES = [
    {
        "result": {
            "name": "フラグメント・オブ・ザ・ライトコア",
            "item_type": "素材",
            "image_path": "assets/FragmentsoftheLightCore_material.png",
            "description": "光核のかけら。強力なクラフト素材。",
        },
        "materials": [
            {"name": "スターライトパーティクル", "count": 1},
            {"name": "オーダーセル膜", "count": 1}
        ]
    },
    # ここに他レシピも追加できます
]
