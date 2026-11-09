# -*- coding: utf-8 -*-

# 整个Mod的绑定配置
ModVersion = "1.0.0"
ModName = "demoCompoundBow"
ClientSystemName = "demoCompoundBowBeh"
ClientSystemClsPath = "compoundBowScript.compoundBowClientSystem.CompoundBowClientSystem"
ServerSystemName = "demoCompoundBowDev"
ServerSystemClsPath = "compoundBowScript.compoundBowServerSystem.CompoundBowServerSystem"

# 引擎事件
AddServerPlayerEvent = "AddServerPlayerEvent"
ItemReleaseUsingServerEvent = "ItemReleaseUsingServerEvent"
OnLocalPlayerStopLoading = "OnLocalPlayerStopLoading"
ClientItemTryUseEvent = "ClientItemTryUseEvent"
ItemReleaseUsingClientEvent = "ItemReleaseUsingClientEvent"
StopUsingItemClientEvent = "StopUsingItemClientEvent"
OnCarriedNewItemChangedClientEvent = "OnCarriedNewItemChangedClientEvent"
OnScriptTickClient = "OnScriptTickClient"

# 物品与实体
BOW_NAME = "demo:compound_bow"
AMMO_NAME = "demo:compound_arrow"
# 想退回原版箭时，把这里改成 "minecraft:arrow" 即可
ARROW_ENTITY = "demo:compound_arrow_entity"

# 进世界补给
BOW_SLOT = 0
AMMO_SLOT = 1
AMMO_COUNT = 32

# 蓄力。durationLeft 是剩余时间，held = maxUseDuration - durationLeft
FULL_CHARGE_SECONDS = 1.0
TICKS_PER_SECOND = 20
MIN_CHARGE = 0.15

# 发射参数。短蓄力和满蓄力的区别都在这两组值里
MIN_POWER = 0.8
MAX_POWER = 3.0
MIN_DAMAGE = 2.0
MAX_DAMAGE = 12.0
GRAVITY = 0.05
SPAWN_FORWARD = 1.2
SPAWN_UP = 1.5

# 客户端表现
DEFAULT_FOV = 70.0
FOV_ZOOM = 15.0
FOV_MIN = 30.0
DRAW_TICKS = 30
SHOOT_ANIM_TICKS = 6

# 自定义 Molang 节点，动画里用 q.mod.xxx 读取
MOLANG_BREATHE = "query.mod.compound_bow_breathe"
MOLANG_AIM = "query.mod.compound_bow_aim"
MOLANG_SHOOT = "query.mod.compound_bow_shoot"
MOLANG_FIX_X = "query.mod.compound_bow_fix_offset_x"
MOLANG_FIX_Z = "query.mod.compound_bow_fix_offset_z"
MOLANG_SPEED = "query.mod.compound_bow_speed_amplifier"

# 弓的“展开/配件”状态：默认只留弓身、弦、箭，其余配件收起来
# arrow_loaded=1 显示搭好的箭；reload=0 隐藏换箭；transition=0；sight/torch/core/assist 都收起
DEPLOY_DEFAULTS = (
    ("query.mod.compound_bow_arrow_loaded", 1.0),
    ("query.mod.compound_bow_reload", 0.0),
    ("query.mod.compound_bow_transition", 0.0),
    ("query.mod.compound_bow_deployment_torch", 0.0),
    ("query.mod.compound_bow_deployment_sight", 0.0),
    ("query.mod.compound_bow_deployment_core", 0.0),
    ("query.mod.compound_bow_deployment_shelf", 0.0),
    ("query.mod.compound_bow_deployment_string", 0.0),
    ("query.mod.compound_bow_deployment_assist", 0.0),
)

# 第一人称手臂：和小地图/combatDrone 一样，把手部模型挂到玩家上
ARM_GEOMETRY_KEY = "compound_bow_arm"
ARM_RENDER_CONTROLLER = "controller.render.compound_bow_arm"
ARM_CONTROLLER_KEY = "compound_bow_controller"
ARM_CONTROLLER_NAME = "controller.animation.compound_bow.general"
BOW_ITEM_CONDITION = "query.get_equipped_item_full_name('main_hand') == '{}'".format(BOW_NAME)
ARM_ANIM_MAP = (
    ("compound_bow_1st_idle", "animation.compound_bow.1st_idle"),
    ("compound_bow_3rd_idle", "animation.compound_bow.3rd_idle"),
    ("compound_bow_1st_aim", "animation.compound_bow.1st_aim"),
    ("compound_bow_3rd_aim", "animation.compound_bow.3rd_aim"),
    ("compound_bow_1st_shoot", "animation.compound_bow.1st_shoot"),
    ("compound_bow_3rd_shoot", "animation.compound_bow.3rd_shoot"),
)

# 第一人称横向修正：与 combatDrone 的 GetFixOffset 一致
FIX_OFFSET_FACTOR = 7.5
FIX_OFFSET_MAX_RATE = 1.6
SLIM_FIX_OFFSET_Z = -0.5
