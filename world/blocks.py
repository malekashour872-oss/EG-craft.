# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Block table and item IDs.

Spec ref: §6.2 — 21 block IDs (0–20) and items 101–117 (per A-16
iron_ore=116, gold_ore=117). Tools 120+ per §8.1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Block IDs (0–20)
# ─────────────────────────────────────────────────────────────
ID_AIR = 0
ID_GRASS = 1
ID_DIRT = 2
ID_STONE = 3
ID_COBBLE = 4
ID_SAND = 5
ID_GRAVEL = 6
ID_LOG = 7
ID_LEAVES = 8
ID_PLANKS = 9
ID_GLASS = 10
ID_WATER = 11
ID_BEDROCK = 12
ID_COAL_ORE = 13
ID_IRON_ORE = 14
ID_GOLD_ORE = 15
ID_DIAMOND_ORE = 16
ID_CRAFTING_TABLE = 17
ID_FURNACE = 18
ID_CHEST = 19
ID_TORCH = 20

# Item IDs (101+) per §6.2 + A-16
ITEM_STICK = 101
ITEM_COAL = 102
ITEM_IRON_INGOT = 103
ITEM_GOLD_INGOT = 104
ITEM_DIAMOND = 105
ITEM_WHEAT = 106
ITEM_CARROT = 107
ITEM_RAW_MEAT = 108
ITEM_COOKED_MEAT = 109
ITEM_LEATHER = 110
ITEM_FEATHER = 111
ITEM_BONE = 112
ITEM_STRING = 113
ITEM_GUNPOWDER = 114
ITEM_ARROW = 115
ITEM_IRON_ORE = 116  # A-16
ITEM_GOLD_ORE = 117  # A-16

# ─────────────────────────────────────────────────────────────
# Commercial item expansion (IDs 200+). Extends the §6.2 item table
# without conflicting with TOOL_BASE=120..139 (5 materials × 4 tools).
# Documented in DECISIONS.md → L-2.
# ─────────────────────────────────────────────────────────────
ITEM_NETHERITE_INGOT  = 200
ITEM_NETHERITE_SCRAP  = 201
ITEM_EMERALD          = 202
ITEM_QUARTZ           = 203
ITEM_AMETHYST_SHARD   = 204
ITEM_BUCKET            = 205
ITEM_WATER_BUCKET      = 206
ITEM_LAVA_BUCKET        = 207
ITEM_MILK_BUCKET        = 208
ITEM_COD               = 209
ITEM_SALMON             = 210
ITEM_TROPICAL_FISH      = 211
ITEM_PUFFERFISH         = 212
ITEM_COOKED_COD         = 213
ITEM_COOKED_SALMON      = 214
ITEM_MELON_SLICE        = 215
ITEM_BAKED_POTATO       = 216
ITEM_POTATO             = 217
ITEM_BREAD              = 218
ITEM_COOKIE             = 219
ITEM_CAKE               = 220
ITEM_PUMPKIN_PIE        = 221
ITEM_APPLE              = 222
ITEM_GOLDEN_APPLE       = 223
ITEM_ENCHANTED_GOLDEN_APPLE = 224
ITEM_SUGAR              = 225
ITEM_PAPER              = 226
ITEM_BOOK               = 227
ITEM_ENCHANTED_BOOK     = 228
ITEM_WRITABLE_BOOK      = 229
ITEM_WRITTEN_BOOK       = 230
ITEM_MAP                = 231
ITEM_COMPASS            = 232
ITEM_CLOCK              = 233
ITEM_SPYGLASS            = 234
ITEM_ENDER_PEARL        = 235
ITEM_ENDER_EYE          = 236
ITEM_EYE_OF_ENDER       = 237
ITEM_BLAZE_ROD          = 238
ITEM_GHAST_TEAR         = 239
ITEM_NETHER_STAR        = 240
ITEM_PRISMARINE_SHARD   = 241
ITEM_PRISMARINE_CRYSTALS = 242
ITEM_SHULKER_SHELL       = 243
ITEM_TURTLE_SCUTE        = 244
ITEM_PHANTOM_MEMBRANE    = 245
ITEM_HEART_OF_THE_SEA   = 246
ITEM_NAUTILUS_SHELL     = 247
ITEM_CONDUIT             = 248
ITEM_DRAGON_BREATH       = 249
ITEM_ELDER_GUARDIAN_SPIKE = 250
ITEM_TOTEM_OF_UNDYING    = 251
ITEM_SHULKER_BOX         = 252
ITEM_FLOWER_POT          = 253
ITEM_NAME_TAG            = 254
ITEM_SADDLE              = 255
ITEM_LEAD                = 256
ITEM_HORSE_ARMOR_IRON    = 257
ITEM_HORSE_ARMOR_GOLD    = 258
ITEM_HORSE_ARMOR_DIAMOND = 259
ITEM_SHEARS              = 260
ITEM_FLINT_AND_STEEL     = 261
ITEM_FLINT               = 262
ITEM_FIRE_CHARGE         = 263
ITEM_END_CRYSTAL         = 264
ITEM_DRAGON_HEAD         = 265
ITEM_TURTLE_HELMET       = 266
ITEM_TRIDENT             = 267
ITEM_SHIELD              = 268
ITEM_BOW                 = 269
ITEM_CROSSBOW            = 270
ITEM_ARROW_TIPPED         = 271
ITEM_FIREWORK_ROCKET      = 272
ITEM_FIREWORK_STAR         = 273
ITEM_ENCHANTED_CARROT_ON_STICK = 274
ITEM_WARPED_FUNGUS_ON_STICK    = 275
ITEM_CARROT_ON_STICK           = 276
ITEM_GLOW_INK_SAC              = 277
ITEM_INK_SAC                   = 278
ITEM_LAPIS_LAZULI               = 279
ITEM_HONEY_BOTTLE              = 280
ITEM_HONEYCOMB                  = 281
ITEM_HONEY_BLOCK                 = 282

# Potion IDs (300+)
ITEM_POTION = 300
ITEM_SPLASH_POTION = 301
ITEM_LINGERING_POTION = 302
ITEM_POTION_WATER      = 303
ITEM_POTION_MUNDANE    = 304
ITEM_POTION_THICK      = 305
ITEM_POTION_REGENERATION   = 306
ITEM_POTION_SWIFTNESS      = 307
ITEM_POTION_FIRE_RESISTANCE = 308
ITEM_POTION_HEALING         = 309
ITEM_POTION_NIGHT_VISION    = 310
ITEM_POTION_STRENGTH        = 311
ITEM_POTION_LEAPING          = 312
ITEM_POTION_WATER_BREATHING = 313
ITEM_POTION_INVISIBILITY     = 314
ITEM_POTION_SLOW_FALLING    = 315
ITEM_POTION_SLOWNESS        = 316
ITEM_POTION_WEAKNESS         = 317
ITEM_POTION_POISON           = 318
ITEM_POTION_HARMING          = 319
ITEM_POTION_LUCK             = 320
ITEM_POTION_TURTLE_MASTER    = 321
ITEM_POTION_SLOWNESS_LONG     = 322

# Spawn eggs (350+)
ITEM_SPAWN_EGG_BASE = 350

# Music discs (380+)
ITEM_DISC_13 = 380
ITEM_DISC_CAT = 381
ITEM_DISC_BLOCKS = 382
ITEM_DISC_CHIRP = 383
ITEM_DISC_FAR = 384
ITEM_DISC_MALL = 385
ITEM_DISC_MELLOHI = 386
ITEM_DISC_STAL = 387
ITEM_DISC_STRAD = 388
ITEM_DISC_WARD = 389
ITEM_DISC_11 = 390
ITEM_DISC_WAIT = 391
ITEM_DISC_OTHERSIDE = 392
ITEM_DISC_5 = 393
ITEM_DISC_PIGSTEP = 394

# Tool base per §8.1 (materials × 4 types)
TOOL_BASE = 120

from world.blocks_expansion import *  # noqa: F401,F403 — re-export expansion

@dataclass
class BlockDef:
    id: int
    identifier: str
    name_ar: str
    hardness: float
    tool: str            # "any" | "pickaxe" | "axe" | "shovel"
    min_tier: int        # 0 = none
    drop: Optional[int]  # block id or item id; None = none
    tiles: tuple[int, int, int]  # top, side, bottom
    cross_mesh: bool = False
    light_radius: int = 0
    solid: bool = True
    swimmable: bool = False

# Hardness "—" → -1.0 (unbreakable)
_BLOCKS: dict[int, BlockDef] = {
    ID_AIR:             BlockDef(ID_AIR,             "air",            "هواء",          -1.0, "any", 0, None, (0, 0, 0), solid=False),
    ID_GRASS:           BlockDef(ID_GRASS,           "grass",          "عشب",            0.6, "shovel", 0, ID_DIRT, (0, 1, 2)),
    ID_DIRT:            BlockDef(ID_DIRT,            "dirt",           "تراب",           0.5, "shovel", 0, ID_DIRT, (2, 2, 2)),
    ID_STONE:           BlockDef(ID_STONE,           "stone",          "حجر",            1.5, "pickaxe", 1, ID_COBBLE, (3, 3, 3)),
    ID_COBBLE:          BlockDef(ID_COBBLE,          "cobble",         "حجر مرصوف",     2.0, "pickaxe", 1, ID_COBBLE, (4, 4, 4)),
    ID_SAND:            BlockDef(ID_SAND,            "sand",           "رمل",            0.5, "shovel", 0, ID_SAND, (5, 5, 5)),
    ID_GRAVEL:          BlockDef(ID_GRAVEL,          "gravel",         "حصى",            0.6, "shovel", 0, ID_GRAVEL, (6, 6, 6)),
    ID_LOG:             BlockDef(ID_LOG,             "log",            "جذع شجرة",      2.0, "axe", 0, ID_LOG, (8, 7, 8)),
    ID_LEAVES:          BlockDef(ID_LEAVES,           "leaves",         "أوراق شجر",      0.2, "any", 0, None, (10, 10, 10)),
    ID_PLANKS:          BlockDef(ID_PLANKS,          "planks",         "ألواح خشب",     2.0, "axe", 0, ID_PLANKS, (9, 9, 9)),
    ID_GLASS:           BlockDef(ID_GLASS,           "glass",          "زجاج",           0.3, "any", 0, None, (12, 12, 12)),
    ID_WATER:           BlockDef(ID_WATER,           "water",          "ماء",            -1.0, "any", 0, None, (11, 11, 11), solid=False, swimmable=True),
    ID_BEDROCK:         BlockDef(ID_BEDROCK,          "bedrock",        "صخر الأساس",     -1.0, "any", 0, None, (17, 17, 17)),
    ID_COAL_ORE:        BlockDef(ID_COAL_ORE,        "coal_ore",       "خام الفحم",      3.0, "pickaxe", 1, ITEM_COAL, (13, 13, 13)),
    ID_IRON_ORE:        BlockDef(ID_IRON_ORE,        "iron_ore",       "خام الحديد",     3.0, "pickaxe", 2, ITEM_IRON_ORE, (14, 14, 14)),
    ID_GOLD_ORE:        BlockDef(ID_GOLD_ORE,        "gold_ore",       "خام الذهب",      3.0, "pickaxe", 3, ITEM_GOLD_ORE, (15, 15, 15)),
    ID_DIAMOND_ORE:     BlockDef(ID_DIAMOND_ORE,     "diamond_ore",    "خام الألماس",    3.0, "pickaxe", 3, ITEM_DIAMOND, (16, 16, 16)),
    ID_CRAFTING_TABLE:  BlockDef(ID_CRAFTING_TABLE,  "crafting_table", "طاولة صناعة",    2.5, "axe", 0, ID_CRAFTING_TABLE, (18, 19, 9)),
    ID_FURNACE:         BlockDef(ID_FURNACE,         "furnace",        "الفرن",          3.5, "pickaxe", 1, ID_FURNACE, (21, 20, 21)),
    ID_CHEST:           BlockDef(ID_CHEST,           "chest",          "الصندوق",        2.5, "axe", 0, ID_CHEST, (22, 22, 22)),
    ID_TORCH:           BlockDef(ID_TORCH,           "torch",          "المشعل",         0.1, "any", 0, ID_TORCH, (23, 23, 23), cross_mesh=True, light_radius=8, solid=False),
    # ── Commercial expansion (IDs 21+). DECISIONS.md L-2.
    ID_OBSIDIAN:        BlockDef(ID_OBSIDIAN,       "obsidian",       "زجاج بركاني",     50.0, "pickaxe", 3, ID_OBSIDIAN, (24, 24, 24)),
    ID_NETHERRACK:      BlockDef(ID_NETHERRACK,     "netherrack",     "صخر الجحيم",       0.4, "pickaxe", 0, ID_NETHERRACK, (25, 25, 25)),
    ID_END_STONE:        BlockDef(ID_END_STONE,     "end_stone",      "حجر النهاية",      3.0, "pickaxe", 1, ID_END_STONE, (26, 26, 26)),
    ID_GLOWSTONE:        BlockDef(ID_GLOWSTONE,     "glowstone",      "حجر الضوء",        0.3, "pickaxe", 0, ITEM_QUARTZ, (27, 27, 27), light_radius=15),
    ID_SOUL_SAND:        BlockDef(ID_SOUL_SAND,      "soul_sand",      "رمل الأرواح",      0.5, "shovel", 0, ID_SOUL_SAND, (28, 28, 28)),
    ID_BRICKS:           BlockDef(ID_BRICKS,         "bricks",         "طوب",              2.0, "pickaxe", 1, ID_BRICKS, (29, 29, 29)),
    ID_SANDSTONE:        BlockDef(ID_SANDSTONE,     "sandstone",      "حجر رملي",         0.8, "pickaxe", 0, ID_SANDSTONE, (30, 30, 30)),
    ID_SNOW:             BlockDef(ID_SNOW,           "snow",           "ثلج",              0.2, "shovel", 0, ID_SNOW, (31, 31, 31), solid=False),
    ID_ICE:              BlockDef(ID_ICE,            "ice",            "جليد",             0.5, "pickaxe", 0, None, (32, 32, 32)),
    ID_CACTUS:           BlockDef(ID_CACTUS,         "cactus",         "صبار",             0.4, "any", 0, ID_CACTUS, (33, 33, 33), solid=False),
    ID_PUMPKIN:          BlockDef(ID_PUMPKIN,        "pumpkin",        "يقطين",            1.0, "axe", 0, ID_PUMPKIN, (34, 34, 34)),
    ID_BOOKSHELF:        BlockDef(ID_BOOKSHELF,     "bookshelf",      "مكتبة كتب",        1.5, "axe", 0, ITEM_BOOK, (35, 35, 35)),
    ID_JUKEBOX:          BlockDef(ID_JUKEBOX,        "jukebox",        "مشغل الأقراص",     2.0, "axe", 0, ID_JUKEBOX, (36, 36, 36)),
    ID_BREWING_STAND:    BlockDef(ID_BREWING_STAND, "brewing_stand",  "حامل التقطير",     0.5, "pickaxe", 0, ID_BREWING_STAND, (37, 37, 37), solid=False),
    ID_ENCHANTING_TABLE: BlockDef(ID_ENCHANTING_TABLE, "enchanting_table", "طاولة السحر", 5.0, "pickaxe", 2, ID_ENCHANTING_TABLE, (38, 38, 38), light_radius=7),
    ID_LEVER:            BlockDef(ID_LEVER,           "lever",          "رافعة",            0.5, "any", 0, ID_LEVER, (39, 39, 39), solid=False),
    ID_REDSTONE_LAMP:    BlockDef(ID_REDSTONE_LAMP, "redstone_lamp",  "مصباح الريدستون",  0.3, "any", 0, ID_REDSTONE_LAMP, (40, 40, 40)),
    ID_REDSTONE_TORCH:   BlockDef(ID_REDSTONE_TORCH, "redstone_torch", "مشعل الريدستون",   0.1, "any", 0, ID_REDSTONE_TORCH, (41, 41, 41), cross_mesh=True, solid=False),
    ID_REPEATER:         BlockDef(ID_REPEATER,       "repeater",       "مكرر الريدستون",   0.1, "any", 0, ID_REPEATER, (42, 42, 42), solid=False),
    ID_PISTON:           BlockDef(ID_PISTON,         "piston",         "مكبس",             1.5, "any", 0, ID_PISTON, (43, 43, 43)),
    ID_STICKY_PISTON:    BlockDef(ID_STICKY_PISTON, "sticky_piston",  "مكبس لزج",         1.5, "any", 0, ID_STICKY_PISTON, (44, 44, 44)),
    ID_FURNACE_LIT:      BlockDef(ID_FURNACE_LIT,   "furnace_lit",    "فرن مشتعل",        3.5, "pickaxe", 1, ID_FURNACE, (45, 45, 45), light_radius=13),
    ID_ANVIL:            BlockDef(ID_ANVIL,          "anvil",          "سندان",            5.0, "pickaxe", 2, ID_ANVIL, (46, 46, 46)),
    ID_CAULDRON:         BlockDef(ID_CAULDRON,       "cauldron",       "مرجل",             2.0, "pickaxe", 1, ID_CAULDRON, (47, 47, 47)),
    ID_LANTERN:          BlockDef(ID_LANTERN,        "lantern",        "فانوس",            0.3, "any", 0, ID_LANTERN, (48, 48, 48), light_radius=15, solid=False),
    ID_DRAGON_EGG:       BlockDef(ID_DRAGON_EGG,    "dragon_egg",     "بيضة التنين",      3.0, "any", 0, ID_DRAGON_EGG, (49, 49, 49)),
    ID_LAVA:             BlockDef(ID_LAVA,           "lava",           "حمم",              -1.0, "any", 0, None, (50, 50, 50), solid=False, swimmable=True, light_radius=15),
    ID_MAGMA_BLOCK:      BlockDef(ID_MAGMA_BLOCK,   "magma_block",    "حجر الحمم",        0.5, "pickaxe", 0, ID_MAGMA_BLOCK, (51, 51, 51), light_radius=3),
    ID_EMERALD_ORE:      BlockDef(ID_EMERALD_ORE,   "emerald_ore",    "خام الزمرد",       3.0, "pickaxe", 3, ITEM_EMERALD, (52, 52, 52)),
    ID_EMERALD_BLOCK:    BlockDef(ID_EMERALD_BLOCK, "emerald_block",  "مكعب الزمرد",      5.0, "pickaxe", 3, ID_EMERALD_BLOCK, (53, 53, 53)),
    ID_DEEPSLATE:        BlockDef(ID_DEEPSLATE,      "deepslate",      "الصخر العميق",     3.0, "pickaxe", 1, ID_DEEPSLATE, (54, 54, 54)),
    ID_DEEPSLATE_COAL_ORE:    BlockDef(ID_DEEPSLATE_COAL_ORE,    "deepslate_coal_ore",    "خام الفحم العميق",   4.5, "pickaxe", 1, ITEM_COAL, (55, 55, 55)),
    ID_DEEPSLATE_IRON_ORE:   BlockDef(ID_DEEPSLATE_IRON_ORE, "deepslate_iron_ore", "خام الحديد العميق",   4.5, "pickaxe", 2, ITEM_IRON_ORE, (56, 56, 56)),
    ID_DEEPSLATE_GOLD_ORE:   BlockDef(ID_DEEPSLATE_GOLD_ORE, "deepslate_gold_ore", "خام الذهب العميق",   4.5, "pickaxe", 3, ITEM_GOLD_ORE, (57, 57, 57)),
    ID_DEEPSLATE_DIAMOND_ORE: BlockDef(ID_DEEPSLATE_DIAMOND_ORE, "deepslate_diamond_ore", "خام الألماس العميق",  4.5, "pickaxe", 3, ITEM_DIAMOND, (58, 58, 58)),
    ID_DEEPSLATE_EMERALD_ORE: BlockDef(ID_DEEPSLATE_EMERALD_ORE, "deepslate_emerald_ore", "خام الزمرد العميق",   4.5, "pickaxe", 3, ITEM_EMERALD, (59, 59, 59)),
    ID_MOSS_BLOCK:       BlockDef(ID_MOSS_BLOCK,    "moss_block",     "مكعب الطحلب",      0.1, "any", 0, ID_MOSS_BLOCK, (60, 60, 60)),
    ID_AZALEA:           BlockDef(ID_AZALEA,         "azalea",         "أزاليا",           0.1, "any", 0, ID_AZALEA, (61, 61, 61), solid=False),
    ID_FLOWERING_AZALEA: BlockDef(ID_FLOWERING_AZALEA, "flowering_azalea", "أزاليا مزهرة", 0.1, "any", 0, ID_FLOWERING_AZALEA, (62, 62, 62), solid=False),
    ID_CALCITE:          BlockDef(ID_CALCITE,        "calcite",        "كالسيت",           0.75, "pickaxe", 0, ID_CALCITE, (63, 63, 63)),
    ID_TUFF:             BlockDef(ID_TUFF,           "tuff",           "توف",              1.25, "pickaxe", 0, ID_TUFF, (64, 64, 64)),
    ID_BASALT:           BlockDef(ID_BASALT,         "basalt",         "بازلت",            1.25, "pickaxe", 1, ID_BASALT, (65, 65, 65)),
    ID_BLACKSTONE:       BlockDef(ID_BLACKSTONE,    "blackstone",     "حجر أسود",         1.5, "pickaxe", 1, ID_BLACKSTONE, (66, 66, 66)),
    ID_POLISHED_BLACKSTONE: BlockDef(ID_POLISHED_BLACKSTONE, "polished_blackstone", "حجر أسود مصقول", 1.5, "pickaxe", 1, ID_POLISHED_BLACKSTONE, (67, 67, 67)),
    ID_NETHER_GOLD_ORE:  BlockDef(ID_NETHER_GOLD_ORE, "nether_gold_ore", "خام ذهب الجحيم", 3.0, "pickaxe", 2, ITEM_GOLD_INGOT, (68, 68, 68)),
    ID_QUARTZ_ORE:       BlockDef(ID_QUARTZ_ORE,    "quartz_ore",     "خام الكوارتز",      3.0, "pickaxe", 2, ITEM_QUARTZ, (69, 69, 69)),
    ID_NETHERITE_BLOCK: BlockDef(ID_NETHERITE_BLOCK, "netherite_block","مكعب النثرايت",    50.0, "pickaxe", 4, ID_NETHERITE_BLOCK, (70, 70, 70)),
    ID_CRYING_OBSIDIAN:  BlockDef(ID_CRYING_OBSIDIAN, "crying_obsidian","زجاج بركاني باك", 50.0, "pickaxe", 3, ID_CRYING_OBSIDIAN, (71, 71, 71), light_radius=3),
    ID_RESPAWN_ANCHOR:   BlockDef(ID_RESPAWN_ANCHOR, "respawn_anchor", "مرساة الإحياء",    50.0, "pickaxe", 3, ID_RESPAWN_ANCHOR, (72, 72, 72)),
    ID_AMETHYST:         BlockDef(ID_AMETHYST,       "amethyst",       "جمري",             1.5, "pickaxe", 1, ITEM_AMETHYST_SHARD, (73, 73, 73)),
    ID_BUDDING_AMETHYST: BlockDef(ID_BUDDING_AMETHYST, "budding_amethyst", "جمري متبرعم", 1.5, "pickaxe", 1, ID_BUDDING_AMETHYST, (74, 74, 74)),
    ID_DRIPSTONE:        BlockDef(ID_DRIPSTONE,      "dripstone",      "حجر التنقيط",      1.5, "pickaxe", 0, ID_DRIPSTONE, (75, 75, 75)),
    ID_POWDER_SNOW:      BlockDef(ID_POWDER_SNOW,    "powder_snow",    "ثلج متطاير",        0.1, "any", 0, None, (76, 76, 76), solid=False),
    ID_NOTE_BLOCK:       BlockDef(ID_NOTE_BLOCK,    "note_block",     "مكعب النغم",        1.0, "axe", 0, ID_NOTE_BLOCK, (77, 77, 77)),
    ID_TARGET:           BlockDef(ID_TARGET,         "target",         "هدف",              0.5, "any", 0, ID_TARGET, (78, 78, 78)),
    ID_GLASS_PANE:       BlockDef(ID_GLASS_PANE,    "glass_pane",     "لوح زجاج",          0.3, "any", 0, None, (79, 79, 79)),
    ID_IRON_BARS:        BlockDef(ID_IRON_BARS,     "iron_bars",      "قضبان حديد",        5.0, "pickaxe", 1, ITEM_IRON_INGOT, (80, 80, 80), solid=False),
    ID_OAK_DOOR:         BlockDef(ID_OAK_DOOR,      "oak_door",       "باب خشب",           1.0, "axe", 0, ID_OAK_DOOR, (81, 81, 81), solid=False),
    ID_IRON_DOOR:        BlockDef(ID_IRON_DOOR,     "iron_door",      "باب حديد",          5.0, "pickaxe", 1, ID_IRON_DOOR, (82, 82, 82), solid=False),
    ID_OAK_FENCE:        BlockDef(ID_OAK_FENCE,     "oak_fence",      "سور خشب",           1.0, "axe", 0, ID_OAK_FENCE, (83, 83, 83), solid=False),
    ID_OAK_SLAB:         BlockDef(ID_OAK_SLAB,      "oak_slab",       "لوح خشبي",          1.0, "axe", 0, ID_OAK_SLAB, (84, 84, 84)),
    ID_STONE_SLAB:       BlockDef(ID_STONE_SLAB,    "stone_slab",     "لوح حجري",          2.0, "pickaxe", 1, ID_STONE_SLAB, (85, 85, 85)),
    ID_COBBLE_SLAB:      BlockDef(ID_COBBLE_SLAB,   "cobble_slab",    "لوح حصى",           2.0, "pickaxe", 1, ID_COBBLE_SLAB, (86, 86, 86)),
    ID_BRICK_SLAB:       BlockDef(ID_BRICK_SLAB,    "brick_slab",     "لوح طوب",           2.0, "pickaxe", 1, ID_BRICK_SLAB, (87, 87, 87)),
    ID_OAK_STAIRS:       BlockDef(ID_OAK_STAIRS,    "oak_stairs",     "درج خشب",           1.0, "axe", 0, ID_OAK_STAIRS, (88, 88, 88)),
    ID_STONE_STAIRS:     BlockDef(ID_STONE_STAIRS,  "stone_stairs",   "درج حجري",          2.0, "pickaxe", 1, ID_STONE_STAIRS, (89, 89, 89)),
    ID_COBBLE_STAIRS:    BlockDef(ID_COBBLE_STAIRS, "cobble_stairs",  "درج حصى",           2.0, "pickaxe", 1, ID_COBBLE_STAIRS, (90, 90, 90)),
    ID_BRICK_STAIRS:     BlockDef(ID_BRICK_STAIRS,  "brick_stairs",   "درج طوب",           2.0, "pickaxe", 1, ID_BRICK_STAIRS, (91, 91, 91)),
    ID_STONE_BUTTON:     BlockDef(ID_STONE_BUTTON,  "stone_button",   "زر حجر",            0.5, "any", 0, ID_STONE_BUTTON, (92, 92, 92), solid=False),
    ID_OAK_BUTTON:       BlockDef(ID_OAK_BUTTON,    "oak_button",     "زر خشب",            0.5, "any", 0, ID_OAK_BUTTON, (93, 93, 93), solid=False),
    ID_STONE_PRESSURE_PLATE: BlockDef(ID_STONE_PRESSURE_PLATE, "stone_pressure_plate", "صفيحة ضغط حجر", 0.5, "any", 0, ID_STONE_PRESSURE_PLATE, (94, 94, 94), solid=False),
    ID_OAK_PRESSURE_PLATE:   BlockDef(ID_OAK_PRESSURE_PLATE, "oak_pressure_plate", "صفيحة ضغط خشب", 0.5, "any", 0, ID_OAK_PRESSURE_PLATE, (95, 95, 95), solid=False),
    ID_RAIL:             BlockDef(ID_RAIL,          "rail",           "سكة",               0.7, "pickaxe", 0, ID_RAIL, (96, 96, 96), solid=False),
    ID_FLOWER_RED:       BlockDef(ID_FLOWER_RED,    "flower_red",     "وردة",              0.1, "any", 0, ID_FLOWER_RED, (97, 97, 97), cross_mesh=True, solid=False),
    ID_FLOWER_YELLOW:    BlockDef(ID_FLOWER_YELLOW, "flower_yellow",  "زهرة صفراء",        0.1, "any", 0, ID_FLOWER_YELLOW, (98, 98, 98), cross_mesh=True, solid=False),
    ID_FLOWER_BLUE:      BlockDef(ID_FLOWER_BLUE,   "flower_blue",    "زهرة زرقاء",        0.1, "any", 0, ID_FLOWER_BLUE, (99, 99, 99), cross_mesh=True, solid=False),
    ID_TALL_GRASS:       BlockDef(ID_TALL_GRASS,    "tall_grass",     "عشب طويل",          0.1, "any", 0, None, (100, 100, 100), cross_mesh=True, solid=False),
    ID_MUSHROOM_RED:     BlockDef(ID_MUSHROOM_RED,  "mushroom_red",   "فطر أحمر",          0.1, "any", 0, ID_MUSHROOM_RED, (101, 101, 101), cross_mesh=True, solid=False),
    ID_MUSHROOM_BROWN:   BlockDef(ID_MUSHROOM_BROWN, "mushroom_brown", "فطر بني",           0.1, "any", 0, ID_MUSHROOM_BROWN, (102, 102, 102), cross_mesh=True, solid=False),
    ID_VINE:             BlockDef(ID_VINE,          "vine",           "كرمة",              0.2, "any", 0, ID_VINE, (103, 103, 103), solid=False),
    ID_LILY_PAD:         BlockDef(ID_LILY_PAD,     "lily_pad",       "زنبقة",             0.1, "any", 0, ID_LILY_PAD, (104, 104, 104), solid=False),
    ID_DEAD_BUSH:        BlockDef(ID_DEAD_BUSH,     "dead_bush",      "شجيرة ميتة",        0.1, "any", 0, ID_DEAD_BUSH, (105, 105, 105), cross_mesh=True, solid=False),
    ID_FERN:             BlockDef(ID_FERN,          "fern",           "سرخس",              0.1, "any", 0, ID_FERN, (106, 106, 106), cross_mesh=True, solid=False),
}

# Tile reserved 24–31 (per §5.5; 25 = sun, 26 = moon per A-9)
TILE_SUN = 25
TILE_MOON = 26

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def is_solid(block_id: int) -> bool:
    """Per §6.4: id not in {0, 11, 20}."""
    return block_id not in (ID_AIR, ID_WATER, ID_TORCH)

def is_transparent(block_id: int) -> bool:
    """Per §6.4: id in {0, 8, 10, 11, 20}."""
    return block_id in (ID_AIR, ID_LEAVES, ID_GLASS, ID_WATER, ID_TORCH)

def get(block_id: int) -> BlockDef:
    """Return the BlockDef for an id (air if unknown)."""
    return _BLOCKS.get(block_id, _BLOCKS[ID_AIR])

def tile_for_face(block_id: int, face: int) -> int:
    """face ∈ 0..5 (top, bottom, side)."""
    bdef = get(block_id)
    if face == 0:  # top
        return bdef.tiles[0]
    if face == 1:  # bottom
        return bdef.tiles[2]
    return bdef.tiles[1]  # side

# Item labels (for inventory display names) per §6.2
ITEM_NAMES_AR: dict[int, str] = {
    ITEM_STICK:        "عصا",
    ITEM_COAL:         "فحم",
    ITEM_IRON_INGOT:   "سبيكة حديد",
    ITEM_GOLD_INGOT:   "سبيكة ذهب",
    ITEM_DIAMOND:      "ألماسة",
    ITEM_WHEAT:        "قمح",
    ITEM_CARROT:       "جزر",
    ITEM_RAW_MEAT:     "لحم نيء",
    ITEM_COOKED_MEAT:  "لحم مطبوخ",
    ITEM_LEATHER:      "جلد",
    ITEM_FEATHER:      "ريشة",
    ITEM_BONE:         "عظمة",
    ITEM_STRING:       "خيط",
    ITEM_GUNPOWDER:    "بارود",
    ITEM_ARROW:        "سهم",
    ITEM_IRON_ORE:     "خام الحديد",
    ITEM_GOLD_ORE:     "خام الذهب",
}

# Tool materials per §8.1
TOOL_MATERIALS = [
    # (id_offset, key, arabic, speed_mult, durability, sword_dmg, tier)
    (0,  "wooden",  "خشبي",   2,   60,   4, 1),
    (4,  "stone",   "حجري",   4,   132,  5, 2),
    (8,  "iron",    "حديدي",  6,   251,  6, 3),
    (12, "golden",  "ذهبي",   12,  33,   4, 2),
    (16, "diamond", "ماسِي",   8,   1562, 7, 4),
]

TOOL_TYPES = [
    # (id_offset, key, arabic)
    (0, "pickaxe", "معول"),
    (1, "axe",     "فأس"),
    (2, "shovel",  "مجرفة"),
    (3, "sword",   "سيف"),
]

def tool_id(material_offset: int, type_offset: int) -> int:
    """Return the item ID for a (material, type) combo."""
    return TOOL_BASE + material_offset + type_offset

def tool_material_tier(material_key: str) -> int:
    for _, key, _, _, _, _, tier in TOOL_MATERIALS:
        if key == material_key:
            return tier
    return 0
