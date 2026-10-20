# -*- coding: utf-8 -*-

# 整个Mod的一些绑定配置
ModVersion = "1.0.0"
ModName = "demoPotion"
ClientSystemName = "demoPotionBeh"
ClientSystemClsPath = "demoPotionScript.potionClientSystem.PotionClientSystem"
ServerSystemName = "demoPotionDev"
ServerSystemClsPath = "demoPotionScript.potionServerSystem.PotionServerSystem"

# 引擎事件
UiInitFinishedEvent = "UiInitFinished"
AddServerPlayerEvent = "AddServerPlayerEvent"
ServerItemTryUseEvent = "ServerItemTryUseEvent"
ServerItemUseOnEvent = "ServerItemUseOnEvent"
ProjectileDoHitEffectEvent = "ProjectileDoHitEffectEvent"

# 服务端 -> 客户端
ShowCloudVisualEvent = "ShowLingeringCloud"
ClearCloudVisualEvent = "ClearLingeringCloud"

ITEM_NAME = "demo:lingering_potion"
# 用原版滞留药水抛射物，空中才能看到瓶子。自定义实体没有这套模型。
PROJECTILE_NAME = "minecraft:lingering_potion"
PLAYER_IDENTIFIER = "minecraft:player"
AOI_NAME = "lingering"
PARTICLE_NAME = "demo:lingering_cloud"

# 右键丢出的瓶子。power 是出手速度，gravity 越大落得越快
THROW_POWER = 1.4
THROW_GRAVITY = 0.08
THROW_SPAWN_UP = 1.5
THROW_SPAWN_FORWARD = 1.0

# 落点左右前后各伸出 2 格，向上 2 格。粒子盒子和这个范围对齐
HALF_XZ = 2.0
HEIGHT = 2.0
# 判定区再往下扩 1 格，避免脚底刚好贴在盒子底面时不算进入
FOOT_PAD = 1.0
# 单位秒。与 particles/lingering_cloud.json 里的 active_time 保持一致
CLOUD_SECONDS = 30

EFFECT_SPEED = ("speed", CLOUD_SECONDS, 1, True)
EFFECT_JUMP = ("jump_boost", CLOUD_SECONDS, 1, True)
EFFECT_REGEN = ("regeneration", CLOUD_SECONDS, 0, True)
EFFECTS = (EFFECT_SPEED, EFFECT_JUMP, EFFECT_REGEN)