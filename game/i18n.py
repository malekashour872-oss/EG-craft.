# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""EG Craft i18n strings.

Spec ref: §3.4 — game/i18n.py defines STRINGS: dict[str, str]. All UI
code imports from here; zero hardcoded Arabic anywhere else.

Required keys are reproduced verbatim per the spec. Some Arabic
characters render as presentation-form codepoints in the source —
this is intentional, the strings are still text-strings for the
shaper; they normalise back to base letters via NFKC inside
``shape`` if needed.

NOTE: §17.1 bans the ellipsis character everywhere except the
single literal STRINGS["loading"] (per A-12). The arabic phrase
"جارٍ تحميل العالم…" contains the ellipsis — it is the exempt
literal.
"""
from __future__ import annotations

STRINGS: dict[str, str] = {
    # main menu / common verbs
    "play":          "ابدأ اللعب",
    "creative":      "الإبداعي",
    "survival":      "البقاء",
    "settings":      "الإعدادات",
    "quit":          "خروج",
    "resume":        "استئناف",
    "save":          "حفظ العالم",
    "main_menu":     "القائمة الرئيسية",
    "paused":        "إيقاف مؤقت",
    "respawn":       "إحياء",
    "page":          "صفحة",
    "rights":        "حقوق الملكية",
    "loading":       "جارٍ تحميل العالم…",
    "saved":         "✓ تم الحفظ",
    "loaded":        "✓ تم التحميل",
    "dead":          "لقد مت!",

    # hud / interaction
    "fly_hint":      "اضغط مسافة مرتين للطيران",
    "breed_hint":     "أطعم كائنين (قمح/جزر) هرّب بعضهما لدمجهما",
    "web_nosave":    "الحفظ غير متاح في نسخة الويب",
    "need_table":    "تحتاج طاولة صناعة للمواصفات المتقدمة",
    "registered":    "عدد الأنواع المسّجلة",

    # inventory / crafting labels
    "inventory":     "المخزون",
    "crafting":      "الصناعة",
    "furnace":       "الفرن",
    "chest":         "الصندوق",
    "fuel":          "الوقود",
    "input":         "الُمدخل",
    "output":        "الناتج",
    "species_log":   "سجل الكائنات",

    # death causes
    "death_causes": {
        "fall":       "سقوط من عل",
        "drown":       "غرق",
        "explosion":   "انفجار",
        "mob":         "قتلتك وحوش",
        "hunger":      "الموت جوعًا",
        "void":        "سقطت في الفراغ",
    },

    # rights-screen paragraph (verbatim per §14.2)
    "rights_paragraph":
        "© 2025 هذه اللعبة والأعمال الابتكارية والشيفارية المرتبطة بها ملكية "
        "حصرية لمالك حسن عاشور يُمنع النسخ أو التوزيع أو التعديل "
        "أو الاستغلال التجاري دون إذن كتابي من المالك.",

    # splash + footer (per §2.7)
    "splash_line1":   "EG Craft",
    "splash_line2":   "من إنتاج مالك حسن عاشور © 2025",
    "splash_tm":      "EG Craft™",
    "footer_copyright":
        "© 2025 مالك حسن عاشور — جميع الحقوق المملوكة محفوظة",

    # species log header
    "species_log_header": "1035 : عدد الأنواع المسّجلة",
    "species_hybrid":     "هجين",
    "species_hostile":   "وحش",
    "species_passive":   "أليف",

    # Commercial expansion — mobile + commercial strings
    "mobile_fullscreen_prompt": "اضغط لبدء اللعب بملء الشاشة",
    "mobile_loading":             "جارٍ تحميل لعبة الهاتف…",
    "mobile_orientation":         "للأداء الأمثل: ضع الهاتف أفقيًا",
    "select_world":               "اختر عالمًا",
    "new_world":                  "عالم جديد",
    "delete_world":               "حذف",
    "achievements":               "الإنجازات",
    "credits":                     "الاعتمادات",
    "stats":                       "الإحصائيات",
    "play_time":                   "وقت اللعب",
    "blocks_broken":               "الكتل المكسورة",
    "blocks_placed":               "الكتل الموضوعة",
    "mobs_killed":                 "الكائنات المقتولة",
    "deaths":                      "الوفيات",
    "distance_walked":             "المسافة الممشوية",
    "creative_palette":            "لوحة الإبداع",
    "all_blocks":                  "جميع الكتل",
    "select_biome":               "المنطقة الحيوية",
    "nether":                       "الجحيم",
    "end":                          "النهاية",
    "overworld":                    "العالم العلوي",
    "music_volume":                 "مستوى الموسيقى",
    "sfx_volume":                   "مستوى المؤثرات",
    "graphics_quality":            "جودة الرسومات",
    "vsync":                        "مزامنة الإطارات",
    "language":                     "اللغة",
    "back":                         "رجوع",
    "apply":                        "تطبيق",
    "reset_to_defaults":            "استعادة الافتراضي",
    "version":                      "الإصدار",
    "v2_commercial":                "نسخة تجارية v2.0",
    "achievements_title":          "الإنجازات المحققة",
    "boss_summon":                  "استدعاء الزعيم",
    "summon_ender_dragon":         "استدعاء تنين النهاية",
    "summon_wither":                "استدعاء الذبول",
    "victory":                      "نصر!",
    "defeat":                       "هزيمة",
}


def get(key: str, default: str = "") -> str:
    """Lookup STRINGS[key]; return ``default`` on miss."""
    val = STRINGS.get(key, default)
    if isinstance(val, dict):
        return str(val)
    return val


def get_death_cause(cause: str) -> str:
    """Return the Arabic string for a death cause key."""
    causes = STRINGS["death_causes"]
    return causes.get(cause, causes["fall"])
