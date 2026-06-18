#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGNALIS TRPG Adjudicator - Kivy Android Version
================================================
Converted from tkinter desktop app to Kivy mobile app.
Target: Android landscape mode, 2772x1280 resolution.

Core game logic preserved from v2.0 desktop version.
"""

# =============================================================================
# 1. 导入 (Imports)
# =============================================================================
import json
import random
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty, DictProperty
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle

# =============================================================================
# 2. 常量定义 (Constants) - Copied from original
# =============================================================================

# 全局中文字体路径（在 build() 中被设置为 Android 系统字体）
_CHINESE_FONT = None
_FONT_REGISTERED = False

class CharacterType(Enum):
    """角色类型枚举"""
    REPLIKA = "仿形体"
    HUMAN = "人类"


class SuccessLevel(Enum):
    """成功等级枚举"""
    FAILURE = (0, "失败", "事情变糟了，可能承受后果")
    SUCCESS = (1, "成功", "你做到了，但刚好勉强")
    GOOD_SUCCESS = (2, "出色成功", "你做得很好，获得额外收益")
    GREAT_SUCCESS = (3, "卓越成功", "超出预期的完美成果")


class ResonanceStage(Enum):
    """生物共振阶段枚举"""
    SILENCE = (0, "静默", "无共振能力")
    WHISPER = (1, "低语", "感知信号、直觉增强")
    ECHO = (2, "回声", "投射意念、心灵感应")
    RESONANCE = (3, "共鸣", "现实扭曲、物质操控")
    CHORUS = (4, "合唱", "大规模现实改写(极度危险)")


# ---------------------------------------------------------------------------
# 属性定义 (Attributes) - v2: 6项属性, 范围1-5
# ---------------------------------------------------------------------------
ATTRIBUTES = {
    "phy": ("体格", "PHY", "身体素质、力量、耐力、生命值相关"),
    "agi": ("敏捷", "AGI", "速度、协调性、闪避、反应"),
    "per": ("感知", "PER", "察觉隐藏事物、听力、视觉、直觉"),
    "int": ("智力", "INT", "逻辑推理、知识、技术操作、分析"),
    "wil": ("意志", "WIL", "心理抵抗、压力承受、精神专注"),
    "res": ("共振", "RES", "生物共振潜力、信号敏感度"),
}

ATTRIBUTE_POINTS_REPLIKA = 25
ATTRIBUTE_POINTS_HUMAN = 28
ATTRIBUTE_MIN = 1
ATTRIBUTE_MAX = 5

# ---------------------------------------------------------------------------
# 技能定义 (Skills) - v2: 30技能点, 5个类别
# ---------------------------------------------------------------------------
SKILLS = {
    "melee":        ("近战武器",  "phy", "武器", "棍棒、刀刃、徒手格斗"),
    "firearms":     ("枪械",      "per", "武器", "手枪、步枪、霰弹枪射击"),
    "dodge":        ("闪避",      "agi", "武器", "躲避攻击、寻找掩体"),
    "tactics":      ("战术",      "int", "武器", "战斗策略、团队配合、战场分析"),
    "heavy":        ("重武器",    "phy", "武器", "重型枪械、爆炸物操作"),
    "throw":        ("投掷",      "agi", "武器", "投掷武器、投掷物精准度"),
    "mechanical":   ("机械维修",  "int", "技术", "修理设备、开锁、机械操作"),
    "electronics":  ("电子技术",  "int", "技术", "电子设备操控、数据恢复"),
    "medical":      ("医疗",      "int", "技术", "急救、手术、制药、护理"),
    "hacking":      ("骇入",      "int", "技术", "网络入侵、系统破解、数据窃取"),
    "stealth":      ("潜行",      "agi", "生存", "隐藏行踪、静默移动"),
    "search":       ("搜索",      "per", "生存", "搜寻物品、调查现场、搜集线索(v2新增)"),
    "perception_sk":("感知",      "per", "生存", "环境感知、危险预警、直觉判断(v2新增)"),
    "tracking":     ("追踪",      "per", "生存", "追踪目标、寻找痕迹、路径分析"),
    "negotiation":  ("交涉",      "wil", "社交", "说服、谈判、协商"),
    "deception":    ("欺骗",      "int", "社交", "说谎、伪装、误导"),
    "leadership":   ("领导力",    "wil", "社交", "指挥、激励、团队管理"),
    "empathy":      ("共情",      "res", "社交", "理解他人情绪、建立情感连接"),
    "resonance_theory": ("共振理论", "int", "共振", "理解生物共振的科学原理"),
    "signal_decode":    ("信号解读", "per", "共振", "解读共振信号、翻译频率"),
    "freq_tuning":      ("频率调谐", "res", "共振", "调谐共振频率、信号放大/过滤"),
    "reality_sense":    ("现实感知", "res", "共振", "感知现实扭曲、预知危险"),
}

SKILL_CATEGORIES = {
    "武器": ["melee", "firearms", "dodge", "tactics", "heavy", "throw"],
    "技术": ["mechanical", "electronics", "medical", "hacking"],
    "生存": ["stealth", "search", "perception_sk", "tracking"],
    "社交": ["negotiation", "deception", "leadership", "empathy"],
    "共振": ["resonance_theory", "signal_decode", "freq_tuning", "reality_sense"],
}

TOTAL_SKILL_POINTS = 30
SKILL_MAX = 4

# ---------------------------------------------------------------------------
# 武器定义 (Weapons)
# ---------------------------------------------------------------------------
WEAPONS = {
    "unarmed":      ("徒手",        1, None),
    "melee":        ("近战武器",    2, None),
    "pistol":       ("手枪",        2, "近距离(10m内)+1骰"),
    "rifle":        ("步枪",        3, "可瞄准(花费1轮,+1成功)"),
    "shotgun":      ("霰弹枪",      3, "近距离伤害+2"),
    "heavy":        ("重型武器",    4, "需要PHY>=3"),
    "flamethrower": ("火焰喷射器",  3, "无视护甲,持续燃烧"),
    "resonance":    ("共振武器",    0, "造成压力伤害而非物理伤害"),
}

# ---------------------------------------------------------------------------
# 护甲定义 (Armors)
# ---------------------------------------------------------------------------
ARMORS = {
    "none":     ("无",           0, 0,  "无"),
    "light":    ("轻型护甲",     1, 0,  "无"),
    "medium":   ("中型护甲",     2, -1, "AGI检定-1骰"),
    "heavy":    ("重型护甲",     3, -2, "AGI检定-2骰,不能奔跑"),
    "replika":  ("仿形体装甲",   2, 0,  "仿形体专用"),
}

# ---------------------------------------------------------------------------
# 恐怖等级定义 (Horror Levels)
# ---------------------------------------------------------------------------
HORROR_LEVELS = {
    "unease":   ("不安",  5, 1),
    "fear":     ("恐惧",  5, 2),
    "despair":  ("绝望",  5, 3),
    "madness":  ("疯狂",  5, 5),
}

# ---------------------------------------------------------------------------
# 压力系统定义 (Stress System)
# ---------------------------------------------------------------------------
STRESS_EFFECTS = {
    (0, 2):     ("正常",    0, 0,  "无影响"),
    (3, 4):     ("紧张",   -1, 0,  "-1骰"),
    (5, 6):     ("焦虑",   -1, 1,  "-1骰, 阈值+1"),
    (7, 8):     ("恐慌",   -2, 1,  "-2骰, 阈值+1"),
    (9, 10):    ("崩溃",   -3, 99, "-3骰, 仅6失败; 强制理智检定"),
}

# ---------------------------------------------------------------------------
# 贴贴机制定义 (Intimacy System)
# ---------------------------------------------------------------------------
INTIMACY_ACTIONS = {
    "emotional_bond":   ("情感连接",    -2, "一次/场景", "拥抱、安慰、鼓励等"),
    "deep_intimacy":    ("深度亲密",    -3, "一次/游戏", "贴贴、心灵共鸣、深层信任"),
}

# ---------------------------------------------------------------------------
# PCD消耗
# ---------------------------------------------------------------------------
PCD_COSTS = {
    "reroll":   1,
    "add_die":  2,
    "overload": 3,
}

# ---------------------------------------------------------------------------
# 共振能力中文映射
# ---------------------------------------------------------------------------
RESONANCE_ABILITIES = {
    "telekinesis":       "念力",
    "psychic_blast":     "心灵冲击",
    "reality_fold":      "现实折叠",
    "mech_interference": "机械干扰",
    "frequency_rebuild": "频率重建",
    "memory_read":       "记忆读取",
    "resonance_scan":    "共振扫描",
    "empathic_wave":     "共情波",
}

# ---------------------------------------------------------------------------
# 中文显示映射 (Display Mappings) - All placed AFTER their data definitions
# ---------------------------------------------------------------------------
ATTR_DISPLAY_NAMES = [f"{v[1]}({v[0]})" for v in ATTRIBUTES.values()]
ATTR_KEY_MAP = {f"{v[1]}({v[0]})": k for k, v in ATTRIBUTES.items()}
ATTR_DISPLAY_MAP = {k: f"{v[1]}({v[0]})" for k, v in ATTRIBUTES.items()}

SKILL_DISPLAY_NAMES = [f"{k}({v[0]})" for k, v in SKILLS.items()]
SKILL_KEY_MAP = {f"{k}({v[0]})": k for k, v in SKILLS.items()}
SKILL_DISPLAY_MAP = {k: f"{k}({v[0]})" for k, v in SKILLS.items()}

ARMOR_DISPLAY_NAMES = [f"{k}({v[0]})" for k, v in ARMORS.items()]
ARMOR_KEY_MAP = {f"{k}({v[0]})": k for k, v in ARMORS.items()}
ARMOR_DISPLAY_MAP = {k: f"{k}({v[0]})" for k, v in ARMORS.items()}

WEAPON_DISPLAY_NAMES = [f"{k}({v[0]})" for k, v in WEAPONS.items()]
WEAPON_KEY_MAP = {f"{k}({v[0]})": k for k, v in WEAPONS.items()}
WEAPON_DISPLAY_MAP = {k: f"{k}({v[0]})" for k, v in WEAPONS.items()}

HORROR_DISPLAY_NAMES = [f"{k}({v[0]})" for k, v in HORROR_LEVELS.items()]
HORROR_KEY_MAP = {f"{k}({v[0]})": k for k, v in HORROR_LEVELS.items()}
HORROR_DISPLAY_MAP = {k: f"{k}({v[0]})" for k, v in HORROR_LEVELS.items()}

RESONANCE_DISPLAY_NAMES = [f"{k}({v})" for k, v in RESONANCE_ABILITIES.items()]
RESONANCE_KEY_MAP = {f"{k}({v})": k for k, v in RESONANCE_ABILITIES.items()}

# =============================================================================
# 3. 核心逻辑类 (Core Logic Classes) - Copied from original
# =============================================================================

class DiceEngine:
    """骰子引擎 - 处理所有骰子投掷和判定逻辑"""

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    def roll_d6(self) -> int:
        return random.randint(1, 6)

    def roll_pool(self, pool_size: int) -> List[int]:
        if pool_size < 1:
            pool_size = 1
        rolls = [self.roll_d6() for _ in range(pool_size)]
        rolls.sort(reverse=True)
        return rolls

    def count_successes(self, rolls: List[int], threshold: int = 4) -> int:
        return sum(1 for r in rolls if r >= threshold)

    def get_success_level(self, successes: int) -> SuccessLevel:
        if successes == 0:
            return SuccessLevel.FAILURE
        elif successes == 1:
            return SuccessLevel.SUCCESS
        elif successes == 2:
            return SuccessLevel.GOOD_SUCCESS
        else:
            return SuccessLevel.GREAT_SUCCESS

    def roll_with_threshold(self, pool_size: int, threshold: int = 4) -> dict:
        rolls = self.roll_pool(pool_size)
        successes = self.count_successes(rolls, threshold)
        level = self.get_success_level(successes)
        return {
            "rolls": rolls,
            "successes": successes,
            "level": level,
            "threshold": threshold,
            "pool_size": pool_size,
        }

    def opposed_roll(self, atk_pool: int, def_pool: int,
                     atk_threshold: int = 4, def_threshold: int = 4) -> dict:
        atk_rolls = self.roll_pool(atk_pool)
        def_rolls = self.roll_pool(def_pool)
        atk_successes = self.count_successes(atk_rolls, atk_threshold)
        def_successes = self.count_successes(def_rolls, def_threshold)
        margin = atk_successes - def_successes
        if margin > 0:
            result = "hit"
            description = f"命中! 额外伤害 +{margin}"
        elif margin == 0:
            result = "graze"
            description = "擦伤(伤害减半,向下取整)"
        else:
            result = "miss"
            description = "完全闪避"
        return {
            "attack_rolls": atk_rolls,
            "defense_rolls": def_rolls,
            "attack_successes": atk_successes,
            "defense_successes": def_successes,
            "margin": margin,
            "result": result,
            "description": description,
        }

    def pcd_depletion_check(self) -> dict:
        roll = self.roll_d6()
        if roll <= 2:
            result = "服从模式"
            desc = "24小时内将听从任何权威命令，如同初始启动状态"
        elif roll <= 4:
            result = "记忆碎片化"
            desc = "失去最高等级技能1级，若有多项则随机选择"
        else:
            result = "人格撕裂"
            desc = "获得1点人格不稳定标记，永久降低最大PCD 1点"
        return {"roll": roll, "result": result, "description": desc}

    def resonance_burst_die(self) -> dict:
        roll = self.roll_d6()
        effects = {
            1: ("共振反噬", "压力+2，能力失控，可能伤害盟友"),
            2: ("信号干扰", "本场景所有检定-1骰，感知混乱"),
            3: ("稳定共振", "正常获得骰池加成"),
            4: ("共鸣强化", "获得1点额外PCD/意志点数"),
            5: ("超频共振", "骰池加成翻倍，但压力额外+1"),
            6: ("谐波爆发", "自动获得3成功，但获得1点临时创伤"),
        }
        name, desc = effects.get(roll, ("未知", ""))
        return {"roll": roll, "name": name, "description": desc}


# =============================================================================
# 角色类 (Character)
# =============================================================================

class Character:
    """角色基类 - v2版本"""

    def __init__(self, name: str = "", char_type: CharacterType = CharacterType.HUMAN):
        self.name = name
        self.char_type = char_type
        self.description = ""
        self.attributes = {"phy": 4, "agi": 4, "per": 4, "int": 4, "wil": 4, "res": 4}
        self.skills = {key: 0 for key in SKILLS.keys()}
        self.max_hp = 12
        self.current_hp = 12
        self.stress = 0
        self.max_stress = 10
        self.pcd_points = 3
        self.max_pcd = 5
        self.resonance_stage = 0
        self.armor = "none"
        self.equipped_weapon = "unarmed"
        self.temp_traumas = 0
        self.perm_traumas = 0
        self.personality_instability = 0
        self.notes = ""
        self.used_emotional_bond = False
        self.used_deep_intimacy = False
        self.sedative_active = False

    def get_threshold(self) -> int:
        if self.char_type == CharacterType.REPLIKA:
            return 4
        return 5

    def get_stress_effects(self) -> Tuple[str, int, int, str]:
        s = self.stress
        for (low, high), effects in STRESS_EFFECTS.items():
            if low <= s <= high:
                return effects
        return ("未知", 0, 0, "")

    def get_pool_modifier(self) -> int:
        modifier = 0
        modifier += self.get_health_modifier()
        stress_name, stress_mod, stress_thresh, _ = self.get_stress_effects()
        modifier += stress_mod
        return modifier

    def get_effective_threshold(self) -> int:
        base = self.get_threshold()
        stress_name, stress_mod, thresh_mod, special = self.get_stress_effects()
        if thresh_mod == 99:
            return 6
        return base + thresh_mod

    def get_health_modifier(self) -> int:
        ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        if ratio > 0.75:
            return 0
        elif ratio > 0.50:
            return -1
        elif ratio > 0.25:
            return -2
        else:
            return -3

    def get_health_status(self) -> str:
        ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        if ratio > 0.75:
            return "绿色(健康)"
        elif ratio > 0.50:
            return "黄色(受伤)"
        elif ratio > 0.25:
            return "红色(重伤)"
        else:
            return "黑色(濒死)"

    def get_stress_level_name(self) -> str:
        name, _, _, _ = self.get_stress_effects()
        return name

    def get_attribute_name(self, attr_key: str) -> str:
        return ATTRIBUTES.get(attr_key, (attr_key, attr_key, ""))[0]

    def get_attribute_abbr(self, attr_key: str) -> str:
        return ATTRIBUTES.get(attr_key, ("", attr_key, ""))[1]

    def get_attribute_display(self, attr_key: str) -> str:
        return ATTR_DISPLAY_MAP.get(attr_key, attr_key)

    def get_skill_name(self, skill_key: str) -> str:
        name = SKILLS.get(skill_key, ("", "", "", ""))[0]
        return f"{skill_key}({name})"

    def get_skill_attr(self, skill_key: str) -> str:
        return SKILLS.get(skill_key, ("", "", "", ""))[1]

    def get_skill_category(self, skill_key: str) -> str:
        return SKILLS.get(skill_key, ("", "", "", ""))[2]

    def calculate_pool(self, attr: str, skill: str, situational: int = 0) -> int:
        attr_val = self.attributes.get(attr, 0)
        skill_val = self.skills.get(skill, 0)
        modifier = self.get_pool_modifier()
        pool = attr_val + skill_val + modifier + situational
        return max(1, pool)

    def calculate_hp(self) -> int:
        phy = self.attributes.get("phy", 4)
        return phy * 2 + 4

    def update_max_hp(self):
        old_max = self.max_hp
        self.max_hp = self.calculate_hp()
        if old_max > 0:
            ratio = self.current_hp / old_max
            self.current_hp = min(int(self.max_hp * ratio), self.max_hp)
        else:
            self.current_hp = self.max_hp

    def take_damage(self, damage: int) -> dict:
        self.current_hp = max(0, self.current_hp - damage)
        stress_gain = 0
        if damage >= 3:
            stress_gain = 2
        elif damage >= 1:
            stress_gain = 1
        old_stress = self.stress
        self.stress = min(self.max_stress, self.stress + stress_gain)
        return {
            "damage_taken": damage,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "health_status": self.get_health_status(),
            "stress_gained": self.stress - old_stress,
            "current_stress": self.stress,
        }

    def heal(self, amount: int) -> int:
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def replika_fast_heal(self, has_repair_kit: bool = True) -> dict:
        if self.char_type != CharacterType.REPLIKA:
            return {"success": False, "reason": "只有仿形体可以使用此恢复方式"}
        if not has_repair_kit:
            return {"success": False, "reason": "需要维修工具"}
        healed = self.heal(4)
        return {"success": True, "healed": healed, "method": "维修工具快速修复", "current_hp": self.current_hp}

    def human_natural_heal(self, resonance_energy: int) -> dict:
        if self.char_type != CharacterType.HUMAN:
            return {"success": False, "reason": "只有人类可以使用此恢复方式"}
        max_heal = min(2, resonance_energy)
        actual_cost = min(max_heal, resonance_energy)
        healed = self.heal(max_heal)
        return {"success": True, "healed": healed, "resonance_cost": actual_cost,
                "method": "自然恢复(消耗共振能量)", "current_hp": self.current_hp}

    def replika_nanobot_injection(self) -> dict:
        if self.char_type != CharacterType.REPLIKA:
            return {"success": False, "reason": "只有仿形体可以使用此恢复方式"}
        heal_amount = self.max_hp // 2
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + heal_amount)
        actual_healed = self.current_hp - old_hp
        was_dying = self.current_hp <= 0 or self.get_health_status() == "黑色(濒死)"
        return {"success": True, "healed": actual_healed, "method": "强效恢复纳米机器人针剂",
                "revived": was_dying, "current_hp": self.current_hp}

    def add_stress(self, amount: int):
        self.stress = min(self.max_stress, self.stress + amount)

    def reduce_stress(self, amount: int):
        self.stress = max(0, self.stress - amount)

    def intimacy_stress_relief(self, action_key: str) -> dict:
        action_info = INTIMACY_ACTIONS.get(action_key)
        if not action_info:
            return {"success": False, "reason": "未知的亲密交互类型"}
        name, stress_relief, limit, desc = action_info
        if action_key == "emotional_bond" and self.used_emotional_bond:
            return {"success": False, "reason": "本场景已使用过情感连接"}
        if action_key == "deep_intimacy" and self.used_deep_intimacy:
            return {"success": False, "reason": "本游戏已使用过深度亲密交互"}
        old_stress = self.stress
        self.reduce_stress(abs(stress_relief))
        actual_relief = old_stress - self.stress
        if action_key == "emotional_bond":
            self.used_emotional_bond = True
        elif action_key == "deep_intimacy":
            self.used_deep_intimacy = True
        return {"success": True, "action": name, "relief": actual_relief,
                "old_stress": old_stress, "new_stress": self.stress,
                "limit": limit, "description": desc}

    def reset_scene_intimacy(self):
        self.used_emotional_bond = False

    def check_temp_trauma(self) -> dict:
        if self.temp_traumas <= 0:
            return {"has_temp_trauma": False}
        if self.stress < 4:
            removed = self.temp_traumas
            self.temp_traumas = 0
            return {"has_temp_trauma": False, "auto_removed": True,
                    "removed_count": removed, "reason": "压力降至4以下，临时创伤自动消除"}
        return {"has_temp_trauma": True, "count": self.temp_traumas,
                "note": "v2: 临时创伤不会造成噩梦，降至4压力以下即可消除"}

    def apply_sedative(self) -> dict:
        if self.perm_traumas <= 0:
            return {"success": False, "reason": "没有永久创伤需要缓解"}
        self.sedative_active = True
        return {"success": True, "effect": "永久创伤效果减半", "duration": "1场景",
                "note": "镇定剂仅能缓解症状，无法治愈永久创伤"}

    def get_perm_trauma_modifier(self) -> int:
        base_penalty = -self.perm_traumas
        if self.sedative_active:
            return math.ceil(base_penalty / 2)
        return base_penalty

    def consume_pcd(self, cost: int) -> bool:
        if self.pcd_points >= cost:
            self.pcd_points -= cost
            return True
        return False

    def use_pcd_reroll(self) -> dict:
        if self.consume_pcd(1):
            return {"success": True, "cost": 1, "effect": "可重掷任意一次骰池"}
        return {"success": False, "reason": "PCD不足"}

    def use_pcd_add_die(self) -> dict:
        if self.consume_pcd(2):
            return {"success": True, "cost": 2, "effect": "检定骰池+1"}
        return {"success": False, "reason": "PCD不足(需要2点)"}

    def use_pcd_overload(self) -> dict:
        if self.consume_pcd(3):
            return {"success": True, "cost": 3, "effect": "检定骰池+2，但压力+1"}
        return {"success": False, "reason": "PCD不足(需要3点)"}

    def to_dict(self) -> dict:
        return {
            "version": 2, "name": self.name, "char_type": self.char_type.name,
            "description": self.description, "attributes": self.attributes.copy(),
            "skills": self.skills.copy(), "max_hp": self.max_hp,
            "current_hp": self.current_hp, "stress": self.stress,
            "max_stress": self.max_stress, "pcd_points": self.pcd_points,
            "max_pcd": self.max_pcd, "resonance_stage": self.resonance_stage,
            "armor": self.armor, "equipped_weapon": self.equipped_weapon,
            "temp_traumas": self.temp_traumas, "perm_traumas": self.perm_traumas,
            "personality_instability": self.personality_instability,
            "notes": self.notes, "used_emotional_bond": self.used_emotional_bond,
            "used_deep_intimacy": self.used_deep_intimacy,
            "sedative_active": self.sedative_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        char_type = CharacterType[data.get("char_type", "HUMAN")]
        char = cls(data.get("name", ""), char_type)
        char.description = data.get("description", "")
        char.attributes.update(data.get("attributes", {}))
        char.skills.update(data.get("skills", {}))
        char.max_hp = data.get("max_hp", char.calculate_hp())
        char.current_hp = data.get("current_hp", char.max_hp)
        char.stress = data.get("stress", 0)
        char.max_stress = data.get("max_stress", 10)
        char.pcd_points = data.get("pcd_points", data.get("resource_points", 3))
        char.max_pcd = data.get("max_pcd", data.get("max_resource", 5))
        char.resonance_stage = data.get("resonance_stage", 0)
        char.armor = data.get("armor", "none")
        char.equipped_weapon = data.get("equipped_weapon", "unarmed")
        char.temp_traumas = data.get("temp_traumas", 0)
        char.perm_traumas = data.get("perm_traumas", 0)
        char.personality_instability = data.get("personality_instability", 0)
        char.notes = data.get("notes", "")
        char.used_emotional_bond = data.get("used_emotional_bond", False)
        char.used_deep_intimacy = data.get("used_deep_intimacy", False)
        char.sedative_active = data.get("sedative_active", False)
        return char

    def __str__(self) -> str:
        return f"{self.name} [{self.char_type.value}] HP:{self.current_hp}/{self.max_hp} 压力:{self.stress}"


# =============================================================================
# 判定引擎 (Adjudicator Engine)
# =============================================================================

class AdjudicatorEngine:
    """判定引擎 - 处理所有游戏判定"""

    def __init__(self):
        self.dice = DiceEngine()
        self.log_entries: List[str] = []

    def log(self, entry: str) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {entry}"
        self.log_entries.append(log_entry)
        return log_entry

    def get_logs(self) -> List[str]:
        return self.log_entries.copy()

    def clear_logs(self):
        self.log_entries.clear()

    def basic_check(self, character: Character, attr: str, skill: str,
                    situational: int = 0, description: str = "") -> dict:
        pool = character.calculate_pool(attr, skill, situational)
        threshold = character.get_effective_threshold()
        result = self.dice.roll_with_threshold(pool, threshold)
        attr_name = character.get_attribute_display(attr)
        skill_name = character.get_skill_name(skill)
        attr_val = character.attributes.get(attr, 0)
        skill_val = character.skills.get(skill, 0)
        stress_name, stress_mod, thresh_mod, special = character.get_stress_effects()
        details = f"【{description or '基础检定'}】\n"
        details += f"角色: {character.name} [{character.char_type.value}]\n"
        details += f"检定: {attr_name}({attr_val}) + {skill_name}({skill_val})\n"
        if situational != 0:
            details += f"情境调整: {situational:+d}\n"
        details += f"状态修正: {character.get_pool_modifier():+d}\n"
        details += f"压力状态: {stress_name} ({character.stress}/10)\n"
        details += f"骰池: {pool} | 阈值: {threshold}+\n"
        details += f"投掷: {result['rolls']}\n"
        details += f"成功数: {result['successes']} | 结果: {result['level'].value[1]}\n"
        details += f"{result['level'].value[2]}"
        self.log(details)
        result["details"] = details
        result["attr_name"] = attr_name
        result["skill_name"] = skill_name
        result["character"] = character.name
        return result

    def opposed_check(self, char1: Character, attr1: str, skill1: str,
                      char2: Character, attr2: str, skill2: str,
                      situational1: int = 0, situational2: int = 0,
                      description: str = "") -> dict:
        pool1 = char1.calculate_pool(attr1, skill1, situational1)
        pool2 = char2.calculate_pool(attr2, skill2, situational2)
        threshold1 = char1.get_effective_threshold()
        threshold2 = char2.get_effective_threshold()
        opposed = self.dice.opposed_roll(pool1, pool2, threshold1, threshold2)
        attr1_name = char1.get_attribute_display(attr1)
        skill1_name = char1.get_skill_name(skill1)
        attr2_name = char2.get_attribute_display(attr2)
        skill2_name = char2.get_skill_name(skill2)
        details = f"【{description or '对抗检定'}】\n"
        details += f"{char1.name} [{char1.char_type.value}]: {attr1_name}({char1.attributes.get(attr1,0)}) + {skill1_name}({char1.skills.get(skill1,0)}) = 骰池{pool1}\n"
        details += f"  投掷: {opposed['attack_rolls']} = {opposed['attack_successes']}成功 (阈值{threshold1}+)\n"
        details += f"{char2.name} [{char2.char_type.value}]: {attr2_name}({char2.attributes.get(attr2,0)}) + {skill2_name}({char2.skills.get(skill2,0)}) = 骰池{pool2}\n"
        details += f"  投掷: {opposed['defense_rolls']} = {opposed['defense_successes']}成功 (阈值{threshold2}+)\n"
        details += f"结果: {opposed['description']}"
        self.log(details)
        opposed["details"] = details
        opposed["pool1"] = pool1
        opposed["pool2"] = pool2
        return opposed

    def combat_attack(self, attacker: Character, defender: Character,
                      weapon_key: str = None, situational: int = 0,
                      called_shot: str = None) -> dict:
        weapon = weapon_key or attacker.equipped_weapon
        weapon_info = WEAPONS.get(weapon, WEAPONS["unarmed"])
        attr = "agi"
        skill = "firearms" if weapon in ["pistol", "rifle", "shotgun", "heavy"] else "melee"
        atk_pool = attacker.calculate_pool(attr, skill, situational)
        damage_mult = 1
        if called_shot == "head":
            atk_pool -= 2
            damage_mult = 2
        elif called_shot == "arm":
            atk_pool -= 1
        elif called_shot == "leg":
            atk_pool -= 1
        atk_pool = max(1, atk_pool)
        def_pool = defender.calculate_pool("agi", "dodge")
        atk_threshold = attacker.get_effective_threshold()
        def_threshold = defender.get_effective_threshold()
        atk_rolls = self.dice.roll_pool(atk_pool)
        def_rolls = self.dice.roll_pool(def_pool)
        atk_successes = self.dice.count_successes(atk_rolls, atk_threshold)
        def_successes = self.dice.count_successes(def_rolls, def_threshold)
        armor_info = ARMORS.get(defender.armor, ARMORS["none"])
        armor_value = armor_info[1]
        margin = atk_successes - def_successes
        details = f"【战斗攻击】{attacker.name} -> {defender.name}\n"
        details += f"武器: {weapon_info[0]} (基础伤害{weapon_info[1]})\n"
        if called_shot:
            details += f"瞄准部位: {called_shot}\n"
        details += f"{attacker.name}: {attacker.get_attribute_display('agi')}({attacker.attributes.get('agi',0)}) + {attacker.get_skill_name(skill)}({attacker.skills.get(skill,0)}) = 骰池{atk_pool}\n"
        details += f"  投掷: {atk_rolls} = {atk_successes}成功 (阈值{atk_threshold}+)\n"
        details += f"{defender.name}: {defender.get_attribute_display('agi')}({defender.attributes.get('agi',0)}) + {defender.get_skill_name('dodge')}({defender.skills.get('dodge',0)}) = 骰池{def_pool}\n"
        details += f"  投掷: {def_rolls} = {def_successes}成功 (阈值{def_threshold}+)\n"
        details += f"护甲: {armor_info[0]} (减值{armor_value})\n"
        if margin > 0:
            base_damage = weapon_info[1]
            extra_damage = max(0, margin - 1)
            armor_absorbed = min(extra_damage + base_damage, armor_value)
            total_damage = base_damage + extra_damage - armor_absorbed
            total_damage = max(1, total_damage)
            if called_shot == "head":
                total_damage *= damage_mult
                details += f"头部命中! 伤害x2\n"
            elif called_shot == "arm":
                details += f"命中手臂! 对方武器检定-1骰\n"
            elif called_shot == "leg":
                details += f"命中腿部! 对方移动减半\n"
            defender.take_damage(total_damage)
            details += f"命中! 基础:{base_damage} + 额外:{extra_damage} - 护甲:{armor_absorbed} = 总伤害:{total_damage}\n"
            details += f"{defender.name} HP: {defender.current_hp}/{defender.max_hp} [{defender.get_health_status()}]"
            result = {"result": "hit", "damage": total_damage, "base_damage": base_damage,
                      "extra_damage": extra_damage, "armor_absorbed": armor_absorbed}
        elif margin == 0:
            damage = max(1, weapon_info[1] // 2)
            defender.take_damage(damage)
            details += f"擦伤! 伤害减半: {damage}\n"
            details += f"{defender.name} HP: {defender.current_hp}/{defender.max_hp} [{defender.get_health_status()}]"
            result = {"result": "graze", "damage": damage}
        else:
            details += f"未命中!"
            result = {"result": "miss", "damage": 0}
        self.log(details)
        result["details"] = details
        result["attack_rolls"] = atk_rolls
        result["defense_rolls"] = def_rolls
        result["attack_successes"] = atk_successes
        result["defense_successes"] = def_successes
        result["margin"] = margin
        result["attacker"] = attacker.name
        result["defender"] = defender.name
        return result

    def horror_check(self, character: Character, level: str = "fear") -> dict:
        horror_info = HORROR_LEVELS.get(level, HORROR_LEVELS["fear"])
        name, threshold, stress_on_fail = horror_info
        pool = character.calculate_pool("wil", "perception_sk")
        result = self.dice.roll_with_threshold(pool, threshold)
        details = f"【恐怖检定 - {name}】{character.name}\n"
        details += f"阈值: {threshold}+ | 骰池: {pool}\n"
        details += f"投掷: {result['rolls']} = {result['successes']}成功\n"
        if result["successes"] > 0:
            character.add_stress(1)
            details += f"抵抗成功! 勉强保持理智。压力+1(当前{character.stress})"
            result["stress_gained"] = 1
        else:
            old_stress = character.stress
            character.add_stress(stress_on_fail)
            gained = character.stress - old_stress
            details += f"抵抗失败! 压力+{gained}(当前{character.stress})"
            result["stress_gained"] = gained
        self.log(details)
        result["details"] = details
        return result

    def resonance_check(self, character: Character, ability: str,
                        situational: int = 0) -> dict:
        stage = character.resonance_stage
        if stage == 0:
            return {"success": False, "details": f"{character.name}处于静默阶段，无法使用共振能力。"}
        ability_map = {
            "telekinesis":      ("res", "resonance_theory"),
            "psychic_blast":    ("res", "reality_sense"),
            "reality_fold":     ("res", "freq_tuning"),
            "mech_interference":("res", "electronics"),
            "frequency_rebuild":("res", "signal_decode"),
            "memory_read":      ("res", "int"),
            "resonance_scan":   ("res", "signal_decode"),
            "empathic_wave":    ("res", "empathy"),
        }
        attr, skill = ability_map.get(ability, ("res", "resonance_theory"))
        pool = character.calculate_pool(attr, skill, situational)
        if stage >= 4:
            threshold = 3
        elif stage >= 3:
            threshold = 4
        else:
            threshold = character.get_effective_threshold()
        result = self.dice.roll_with_threshold(pool, threshold)
        stress_cost = {1: 0, 2: 1, 3: 2, 4: 3}.get(stage, 0)
        if stress_cost > 0:
            character.add_stress(stress_cost)
        ability_cn = RESONANCE_ABILITIES.get(ability, ability)
        details = f"【生物共振 - {ability_cn}】{character.name}\n"
        details += f"共振阶段: {stage} | 能力: {ability_cn}\n"
        details += f"骰池: {pool} | 阈值: {threshold}+\n"
        details += f"投掷: {result['rolls']} = {result['successes']}成功\n"
        if stress_cost > 0:
            details += f"压力成本: +{stress_cost}(当前{character.stress})"
        self.log(details)
        result["details"] = details
        result["stress_cost"] = stress_cost
        result["stage"] = stage
        return result

    def resonance_surge(self, character: Character) -> dict:
        stress = character.stress
        if stress < 5:
            return {"success": False, "details": "压力不足5，无法触发共振爆发。"}
        bonus = (stress + 1) // 2
        new_stress = min(10, stress + 1)
        character.stress = new_stress
        res_die = self.dice.resonance_burst_die()
        if res_die["roll"] == 1:
            character.add_stress(2)
        elif res_die["roll"] == 4:
            character.pcd_points = min(character.max_pcd, character.pcd_points + 1)
        elif res_die["roll"] == 5:
            bonus *= 2
            character.add_stress(1)
        elif res_die["roll"] == 6:
            character.temp_traumas += 1
        details = f"【共振爆发】{character.name}\n"
        details += f"当前压力: {stress} -> 爆发后: {character.stress}\n"
        details += f"骰池加成: +{bonus}\n"
        details += f"共振骰[{res_die['roll']}]: {res_die['name']} - {res_die['description']}"
        self.log(details)
        return {"bonus": bonus, "stress_before": stress, "stress_after": character.stress,
                "resonance_die": res_die, "details": details}

    def sanity_check(self, character: Character) -> dict:
        pool = character.attributes.get("wil", 2)
        threshold = 5
        result = self.dice.roll_with_threshold(pool, threshold)
        details = f"【理智检定(强制)】{character.name}\n"
        details += f"骰池: {pool} (仅WIL) | 阈值: {threshold}+\n"
        details += f"投掷: {result['rolls']} = {result['successes']}成功\n"
        if result["successes"] > 0:
            character.stress = 7
            character.temp_traumas += 1
            details += f"成功! 压力降至7，获得1点临时创伤。"
            result["outcome"] = "success"
        else:
            character.stress = 10
            character.perm_traumas += 1
            details += f"失败! 压力保持10，获得1点永久创伤，进入崩溃状态!"
            result["outcome"] = "failure"
        self.log(details)
        result["details"] = details
        return result

    def use_pcd(self, character: Character, action: str) -> dict:
        if character.char_type != CharacterType.REPLIKA:
            return {"success": False, "reason": "只有仿形体拥有PCD"}
        if action == "reroll":
            result = character.use_pcd_reroll()
        elif action == "add_die":
            result = character.use_pcd_add_die()
        elif action == "overload":
            result = character.use_pcd_overload()
            if result["success"]:
                character.add_stress(1)
        else:
            return {"success": False, "reason": "未知的PCD操作"}
        if character.pcd_points <= 0:
            depletion = self.dice.pcd_depletion_check()
            self.log(f"【PCD耗尽检定】{character.name}: {depletion['result']} - {depletion['description']}")
            result["pcd_depletion"] = depletion
        details = f"【PCD使用】{character.name} - {action}\n"
        details += f"PCD剩余: {character.pcd_points}/{character.max_pcd}\n"
        details += f"效果: {result.get('effect', result.get('reason', ''))}"
        self.log(details)
        result["details"] = details
        return result

    def intimacy_action(self, character: Character, action_key: str) -> dict:
        result = character.intimacy_stress_relief(action_key)
        if result["success"]:
            action_name = result["action"]
            details = f"【贴贴 - {action_name}】{character.name}\n"
            details += f"压力减少: -{result['relief']} ({result['old_stress']} -> {result['new_stress']})\n"
            details += f"限制: {result['limit']}\n"
            details += f"描述: {result['description']}"
            self.log(details)
            result["details"] = details
        else:
            details = f"【贴贴失败】{character.name}: {result['reason']}"
            self.log(details)
            result["details"] = details
        return result

    def heal_replika(self, character: Character, has_kit: bool = True) -> dict:
        result = character.replika_fast_heal(has_kit)
        if result["success"]:
            details = f"【仿形体恢复】{character.name}\n"
            details += f"方法: {result['method']}\n"
            details += f"恢复: +{result['healed']} HP (当前{result['current_hp']})"
            self.log(details)
            result["details"] = details
        else:
            result["details"] = f"恢复失败: {result['reason']}"
        return result

    def heal_human(self, character: Character, resonance_energy: int) -> dict:
        result = character.human_natural_heal(resonance_energy)
        if result["success"]:
            details = f"【人类恢复】{character.name}\n"
            details += f"方法: {result['method']}\n"
            details += f"恢复: +{result['healed']} HP (当前{result['current_hp']})\n"
            details += f"消耗共振能量: {result['resonance_cost']}"
            self.log(details)
            result["details"] = details
        else:
            result["details"] = f"恢复失败: {result['reason']}"
        return result

    def revive_replika(self, character: Character) -> dict:
        result = character.replika_nanobot_injection()
        if result["success"]:
            details = f"【仿形体濒死恢复】{character.name}\n"
            details += f"方法: {result['method']}\n"
            details += f"恢复: +{result['healed']} HP (当前{result['current_hp']})\n"
            if result["revived"]:
                details += "已从濒死状态苏醒!"
            self.log(details)
            result["details"] = details
        else:
            result["details"] = f"濒死恢复失败: {result['reason']}"
        return result

    def check_trauma(self, character: Character) -> dict:
        result = {}
        temp_result = character.check_temp_trauma()
        if temp_result.get("auto_removed"):
            details = f"【临时创伤消除】{character.name}: {temp_result['reason']}"
            self.log(details)
            result["temp_trauma"] = temp_result
        if character.perm_traumas > 0:
            result["perm_trauma"] = {
                "count": character.perm_traumas,
                "modifier": character.get_perm_trauma_modifier(),
                "sedative_active": character.sedative_active,
                "note": "镇定剂可减半永久创伤效果(1场景)" if not character.sedative_active else "镇定剂效果生效中",
            }
        return result

    def apply_sedative(self, character: Character) -> dict:
        result = character.apply_sedative()
        if result["success"]:
            details = f"【镇定剂】{character.name}\n"
            details += f"效果: {result['effect']}\n"
            details += f"持续时间: {result['duration']}\n"
            details += f"{result['note']}"
            self.log(details)
            result["details"] = details
        return result

    def new_scene(self, characters: List[Character]):
        for char in characters:
            char.reset_scene_intimacy()
            if char.sedative_active:
                char.sedative_active = False
                self.log(f"【场景切换】{char.name}的镇定剂效果已消退")
        self.log("【场景切换】所有角色的场景级状态已重置")


# =============================================================================
# 敌人模板 (Enemy Templates)
# =============================================================================

DEFAULT_ENEMY_TEMPLATES = [
    {
        "name": "感染仿形体", "template_key": "infected_replika",
        "description": "被未知信号感染的仿形体，行为狂暴且具有攻击性。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 3, "per": 2, "int": 1, "wil": 2, "res": 0},
        "skills": {"melee": 2, "firearms": 1, "dodge": 1, "stealth": 1},
        "armor": "replika", "equipped_weapon": "melee", "stress": 5,
        "resonance_stage": 0, "pcd_points": 0, "threat_level": "中等",
        "special_abilities": ["狂暴(伤害+1)", "感染撕咬(命中可能传播感染)"],
    },
    {
        "name": "BCC士兵", "template_key": "bcc_soldier",
        "description": "边境控制委员会的制式士兵，装备精良，训练有素。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 3, "per": 3, "int": 2, "wil": 3, "res": 0},
        "skills": {"firearms": 3, "dodge": 2, "tactics": 2, "melee": 1},
        "armor": "medium", "equipped_weapon": "rifle", "stress": 2,
        "resonance_stage": 0, "pcd_points": 2, "threat_level": "中等",
        "special_abilities": ["战术配合(附近有友军时+1骰)", "掩护射击(保护盟友)"],
    },
    {
        "name": "信号幽灵", "template_key": "signal_ghost",
        "description": "由纯粹共振能量构成的幽灵实体，物理攻击效果有限。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 1, "agi": 4, "per": 4, "int": 2, "wil": 4, "res": 3},
        "skills": {"dodge": 3, "stealth": 3, "resonance_theory": 2, "freq_tuning": 2},
        "armor": "none", "equipped_weapon": "resonance", "stress": 8,
        "resonance_stage": 2, "pcd_points": 0, "threat_level": "困难",
        "special_abilities": ["相位移动(物理攻击-2骰)", "共振攻击(造成压力伤害)", "无形(免疫物理伤害50%)"],
    },
    {
        "name": "变异体", "template_key": "mutant",
        "description": "受到共振辐射影响的变异生物，形态扭曲且极具攻击性。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 4, "agi": 2, "per": 2, "int": 1, "wil": 2, "res": 1},
        "skills": {"melee": 3, "dodge": 1, "tracking": 2},
        "armor": "light", "equipped_weapon": "melee", "stress": 6,
        "resonance_stage": 0, "pcd_points": 0, "threat_level": "困难",
        "special_abilities": ["再生(每轮恢复1HP)", "猛击(命中造成额外压力)", "恐怖嚎叫(范围内压力+1)"],
    },
    {
        "name": "猎手", "template_key": "hunter",
        "description": "专门猎杀目标的精英仿形体，速度快且致命。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 4, "per": 3, "int": 2, "wil": 3, "res": 0},
        "skills": {"firearms": 3, "dodge": 3, "stealth": 3, "melee": 2, "tactics": 2},
        "armor": "light", "equipped_weapon": "pistol", "stress": 3,
        "resonance_stage": 0, "pcd_points": 3, "threat_level": "困难",
        "special_abilities": ["闪避大师(闪避+1骰)", "致命精准(头部攻击无惩罚)", "追踪(无法被潜行摆脱)"],
    },
    {
        "name": "观测者", "template_key": "observer",
        "description": "来自维度之外的宇宙恐怖存在。无法被击败，只能逃避。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 5, "agi": 3, "per": 5, "int": 5, "wil": 5, "res": 5},
        "skills": {"melee": 4, "dodge": 4, "stealth": 4, "tactics": 4,
                   "resonance_theory": 5, "freq_tuning": 4, "reality_sense": 4},
        "armor": "heavy", "equipped_weapon": "resonance", "stress": 10,
        "resonance_stage": 4, "pcd_points": 5, "threat_level": "极端",
        "special_abilities": ["现实扭曲(改变战场环境)", "心灵恐惧(自动恐惧检定)",
                             "不可名状(直视者压力+3)", "绝对压制(所有检定-2骰)"],
    },
    {
        "name": "仿形体哨兵", "template_key": "replika_sentry",
        "description": "标准的仿形体巡逻单位，警戒区域内任何异常。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 3, "per": 3, "int": 2, "wil": 2, "res": 0},
        "skills": {"firearms": 2, "dodge": 2, "tactics": 1, "melee": 1},
        "armor": "replika", "equipped_weapon": "rifle", "stress": 2,
        "resonance_stage": 0, "pcd_points": 2, "threat_level": "轻微",
        "special_abilities": ["警戒(察觉检定+1骰)", "通讯呼叫(发现敌人后召唤增援)"],
    },
    {
        "name": "污染体", "template_key": "contaminated",
        "description": "受到轻度共振污染的工作人员，神智不清但仍保有部分本能。",
        "char_type": "HUMAN",
        "attributes": {"phy": 2, "agi": 2, "per": 2, "int": 1, "wil": 1, "res": 1},
        "skills": {"melee": 1, "dodge": 1, "stealth": 1},
        "armor": "none", "equipped_weapon": "melee", "stress": 7,
        "resonance_stage": 0, "pcd_points": 0, "threat_level": "轻微",
        "special_abilities": ["感染抓挠(命中需抵抗感染)", "不稳定行为(随机行动)"],
    },
    {
        "name": "侦察无人机群", "template_key": "drone_swarm",
        "description": "由数十个小型侦察无人机组成的蜂群，可覆盖大片区域。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 1, "agi": 4, "per": 4, "int": 1, "wil": 1, "res": 0},
        "skills": {"perception_sk": 3, "stealth": 2, "dodge": 3},
        "armor": "none", "equipped_weapon": "resonance", "stress": 0,
        "resonance_stage": 0, "pcd_points": 0, "threat_level": "轻微",
        "special_abilities": ["群体意识(单次攻击只能消灭部分)", "广域扫描(感知范围翻倍)", "自爆(接近时造成范围压力伤害)"],
    },
    {
        "name": "共振畸变体", "template_key": "resonance_aberration",
        "description": "被共振能量彻底扭曲的存在，介于物质与能量之间。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 3, "per": 4, "int": 2, "wil": 3, "res": 4},
        "skills": {"resonance_theory": 3, "freq_tuning": 3, "dodge": 2, "melee": 2},
        "armor": "none", "equipped_weapon": "resonance", "stress": 8,
        "resonance_stage": 3, "pcd_points": 0, "threat_level": "困难",
        "special_abilities": ["共振吸收(共振伤害转化为HP恢复)", "频率干扰(附近角色共振检定-2骰)", "相位攻击(无视50%护甲)"],
    },
]


# =============================================================================
# 角色预设模板 (Character Templates)
# =============================================================================

DEFAULT_CHARACTER_TEMPLATES = [
    {
        "name": "护卫型仿形体(Protektor)", "template_key": "protektor",
        "description": "专为战斗和保护任务设计的仿形体，拥有强健的体格和战斗技能。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 5, "agi": 3, "per": 3, "int": 2, "wil": 4, "res": 0},
        "skills": {"melee": 3, "firearms": 2, "dodge": 2, "tactics": 2, "heavy": 2},
        "armor": "replika", "equipped_weapon": "rifle", "stress": 1,
        "resonance_stage": 0, "pcd_points": 4,
    },
    {
        "name": "侦察型仿形体(Storch)", "template_key": "storch",
        "description": "感知能力出众的仿形体，擅长侦查和情报收集。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 2, "agi": 4, "per": 5, "int": 3, "wil": 3, "res": 0},
        "skills": {"stealth": 3, "firearms": 2, "dodge": 2, "search": 2, "perception_sk": 2, "tactics": 1},
        "armor": "light", "equipped_weapon": "pistol", "stress": 1,
        "resonance_stage": 0, "pcd_points": 3,
    },
    {
        "name": "战斗型仿形体(STAR)", "template_key": "star",
        "description": "为正面战斗而设计的仿形体，火力凶猛，装甲厚重。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 5, "agi": 2, "per": 3, "int": 2, "wil": 4, "res": 0},
        "skills": {"firearms": 3, "melee": 2, "dodge": 1, "tactics": 2, "heavy": 3},
        "armor": "heavy", "equipped_weapon": "heavy", "stress": 1,
        "resonance_stage": 0, "pcd_points": 4,
    },
    {
        "name": "技术型仿形体(Kolibri)", "template_key": "kolibri",
        "description": "精通各种技术的仿形体，擅长hacking和设备操作。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 2, "agi": 3, "per": 3, "int": 5, "wil": 3, "res": 0},
        "skills": {"electronics": 3, "mechanical": 3, "hacking": 2, "firearms": 1, "dodge": 1, "medical": 1},
        "armor": "light", "equipped_weapon": "pistol", "stress": 1,
        "resonance_stage": 0, "pcd_points": 3,
    },
    {
        "name": "殖民地调查员", "template_key": "investigator",
        "description": "来自殖民地的人类调查员，拥有敏锐的直觉和生物共振潜力。",
        "char_type": "HUMAN",
        "attributes": {"phy": 2, "agi": 3, "per": 4, "int": 3, "wil": 4, "res": 3},
        "skills": {"firearms": 2, "dodge": 2, "resonance_theory": 2, "search": 2, "empathy": 2, "negotiation": 1},
        "armor": "light", "equipped_weapon": "pistol", "stress": 2,
        "resonance_stage": 1, "pcd_points": 0,
    },
    {
        "name": "前BCC军官", "template_key": "ex_officer",
        "description": "曾服役于边境控制委员会的前军官，经验丰富但心怀创伤。",
        "char_type": "HUMAN",
        "attributes": {"phy": 3, "agi": 2, "per": 3, "int": 3, "wil": 5, "res": 1},
        "skills": {"firearms": 3, "tactics": 3, "dodge": 2, "melee": 2, "leadership": 2},
        "armor": "medium", "equipped_weapon": "rifle", "stress": 4,
        "resonance_stage": 0, "pcd_points": 0,
    },
    {
        "name": "仿形体医护兵", "template_key": "medic",
        "description": "专职医疗救护的仿形体，也具备一定的战斗能力。",
        "char_type": "REPLIKA",
        "attributes": {"phy": 3, "agi": 3, "per": 4, "int": 4, "wil": 3, "res": 0},
        "skills": {"medical": 4, "dodge": 2, "firearms": 1, "mechanical": 2, "empathy": 2},
        "armor": "light", "equipped_weapon": "pistol", "stress": 1,
        "resonance_stage": 0, "pcd_points": 3,
    },
]


# =============================================================================
# 敌人类 (Enemy)
# =============================================================================

class Enemy(Character):
    """敌人角色类 - 继承自Character"""

    def __init__(self, name: str = "", template_key: str = ""):
        super().__init__(name, CharacterType.REPLIKA)
        self.template_key = template_key
        self.threat_level = "轻微"
        self.special_abilities: List[str] = []

    @classmethod
    def from_template(cls, template: dict) -> "Enemy":
        enemy = cls(template.get("name", ""), template.get("template_key", ""))
        enemy.description = template.get("description", "")
        enemy.char_type = CharacterType[template.get("char_type", "REPLIKA")]
        enemy.attributes.update(template.get("attributes", {}))
        enemy.skills.update(template.get("skills", {}))
        enemy.max_hp = enemy.calculate_hp()
        enemy.current_hp = enemy.max_hp
        enemy.stress = template.get("stress", 0)
        enemy.resonance_stage = template.get("resonance_stage", 0)
        enemy.armor = template.get("armor", "none")
        enemy.equipped_weapon = template.get("equipped_weapon", "unarmed")
        enemy.pcd_points = template.get("pcd_points", 0)
        enemy.max_pcd = template.get("pcd_points", 5)
        enemy.threat_level = template.get("threat_level", "轻微")
        enemy.special_abilities = template.get("special_abilities", [])
        return enemy

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["template_key"] = self.template_key
        data["threat_level"] = self.threat_level
        data["special_abilities"] = self.special_abilities.copy()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        char_type = CharacterType[data.get("char_type", "REPLIKA")]
        enemy = cls(data.get("name", ""), data.get("template_key", ""))
        enemy.description = data.get("description", "")
        enemy.char_type = char_type
        enemy.attributes.update(data.get("attributes", {}))
        enemy.skills.update(data.get("skills", {}))
        enemy.max_hp = data.get("max_hp", enemy.calculate_hp())
        enemy.current_hp = data.get("current_hp", enemy.max_hp)
        enemy.stress = data.get("stress", 0)
        enemy.max_stress = data.get("max_stress", 10)
        enemy.pcd_points = data.get("pcd_points", 0)
        enemy.max_pcd = data.get("max_pcd", 5)
        enemy.resonance_stage = data.get("resonance_stage", 0)
        enemy.armor = data.get("armor", "none")
        enemy.equipped_weapon = data.get("equipped_weapon", "unarmed")
        enemy.temp_traumas = data.get("temp_traumas", 0)
        enemy.perm_traumas = data.get("perm_traumas", 0)
        enemy.personality_instability = data.get("personality_instability", 0)
        enemy.notes = data.get("notes", "")
        enemy.threat_level = data.get("threat_level", "轻微")
        enemy.special_abilities = data.get("special_abilities", [])
        return enemy


# =============================================================================
# 数据管理器 (Data Manager)
# =============================================================================

class DataManager:
    """数据管理器 - 处理所有数据导入导出"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def save_character(self, character: Character, filename: str = None) -> str:
        if filename is None:
            filename = f"{character.name or 'unnamed'}_char.json"
        if not filename.endswith('.json'):
            filename += '.json'
        filepath = self.get_data_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(character.to_dict(), f, ensure_ascii=False, indent=2)
        return filepath

    def load_character(self, filepath: str) -> Character:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Character.from_dict(data)

    def save_enemy(self, enemy: Enemy, filename: str = None) -> str:
        if filename is None:
            filename = f"{enemy.name or 'unnamed'}_enemy.json"
        if not filename.endswith('.json'):
            filename += '.json'
        filepath = self.get_data_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(enemy.to_dict(), f, ensure_ascii=False, indent=2)
        return filepath

    def load_enemy(self, filepath: str) -> Enemy:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Enemy.from_dict(data)

    def export_log(self, log_entries: list, filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adjudication_log_{timestamp}.txt"
        filepath = self.get_data_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("SIGNALIS TRPG 判定日志 v2.0\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for entry in log_entries:
                f.write(entry + "\n\n")
        return filepath

    @staticmethod
    def import_character_from_json(filepath: str) -> Character:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Character.from_dict(data)

    @staticmethod
    def import_enemy_from_json(filepath: str) -> Enemy:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Enemy.from_dict(data)


# =============================================================================
# 4. Kivy UI类 (Kivy UI Classes)
# =============================================================================

# ---------------------------------------------------------------------------
# 颜色主题 (Color Theme) - SIGNALIS dark style
# ---------------------------------------------------------------------------
BG_COLOR =          (0.08, 0.06, 0.06, 1)
PANEL_COLOR =       (0.12, 0.10, 0.10, 1)
ACCENT_COLOR =      (0.72, 0.45, 0.20, 1)
TEXT_COLOR =        (0.9,  0.88, 0.85, 1)
DIM_TEXT =          (0.55, 0.50, 0.48, 1)
SUCCESS_COLOR =     (0.36, 0.55, 0.36, 1)
FAILURE_COLOR =     (0.72, 0.25, 0.20, 1)
BUTTON_BG =         (0.20, 0.17, 0.15, 1)
BUTTON_BG_ACTIVE =  (0.30, 0.25, 0.22, 1)
INPUT_BG =          (0.18, 0.15, 0.14, 1)

# ---------------------------------------------------------------------------
# 工具函数 (Utility functions)
# ---------------------------------------------------------------------------
def make_spinner(text: str, values: list, font_size=None, **kwargs):
    """Create a themed Spinner widget with canvas background for Android compatibility."""
    if font_size is None:
        font_size = sp(13)
    spinner = Spinner(
        text=text, values=values,
        color=TEXT_COLOR,
        font_size=font_size,
        font_name=_font(),
        background_normal='',
        background_down='',
        **kwargs
    )
    # Use canvas to draw background - avoids black box on Android
    with spinner.canvas.before:
        Color(*INPUT_BG)
        spinner._bg_rect = Rectangle(pos=spinner.pos, size=spinner.size)
    spinner.bind(pos=lambda obj, val: setattr(spinner._bg_rect, 'pos', val))
    spinner.bind(size=lambda obj, val: setattr(spinner._bg_rect, 'size', val))
    return spinner


def _font():
    """返回已注册的中文字体名（Android 优先系统字体，回退 Roboto）"""
    if _FONT_REGISTERED and _CHINESE_FONT:
        return 'chinese'
    return 'Roboto'


def make_button(text: str, callback=None, font_size=None, **kwargs):
    """Create a themed Button widget."""
    if font_size is None:
        font_size = sp(12)
    btn = Button(
        text=text,
        background_color=BUTTON_BG,
        color=TEXT_COLOR,
        font_size=font_size,
        font_name=_font(),
        **kwargs
    )
    if callback:
        btn.bind(on_press=callback)
    return btn


def make_label(text: str, font_size=14, color=TEXT_COLOR, bold=False, **kwargs):
    """Create a themed Label widget."""
    if 'size_hint_y' not in kwargs:
        kwargs['size_hint_y'] = None
    return Label(
        text=text, font_size=sp(font_size),
        color=color, bold=bold,
        font_name=_font(),
        **kwargs
    )


def add_panel_bg(widget, color=PANEL_COLOR):
    """为 widget 添加 canvas.before 背景绘制，避免 Android 黑屏"""
    with widget.canvas.before:
        Color(*color)
        widget._bg_rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda obj, val: setattr(widget._bg_rect, 'pos', val))
    widget.bind(size=lambda obj, val: setattr(widget._bg_rect, 'size', val))


# ---------------------------------------------------------------------------
# 确认对话框 (Confirmation Popup)
# ---------------------------------------------------------------------------
class ConfirmPopup(Popup):
    """通用确认对话框"""
    def __init__(self, title, message, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = _font()
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = True
        self.background_color = PANEL_COLOR
        self.on_confirm = on_confirm

        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        add_panel_bg(layout)
        layout.add_widget(make_label(message, font_size=14))

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_box.add_widget(make_button("确认", self._on_confirm))
        btn_box.add_widget(make_button("取消", self._on_dismiss))
        layout.add_widget(btn_box)

        self.content = layout

    def _on_confirm(self, instance):
        self.on_confirm()
        self.dismiss()

    def _on_dismiss(self, instance):
        self.dismiss()


# ---------------------------------------------------------------------------
# 角色编辑器弹窗 (Character Editor Popup)
# ---------------------------------------------------------------------------
class CharacterEditorPopup(Popup):
    """角色创建/编辑弹窗"""

    def __init__(self, character=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "创建角色" if character is None else f"编辑角色 - {character.name}"
        self.title_font = _font()
        self.size_hint = (0.95, 0.95)
        self.auto_dismiss = False
        self.background_color = PANEL_COLOR
        self.on_save = on_save

        if character is None:
            self.character = Character("新角色")
        else:
            self.character = character

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        main_layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        add_panel_bg(main_layout)

        # 滚动区域
        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        form = GridLayout(cols=1, spacing=dp(8), padding=dp(5), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # 名称
        form.add_widget(make_label("名称:", font_size=13))
        self.name_input = TextInput(
            text=self.character.name, multiline=False,
            background_color=INPUT_BG, foreground_color=TEXT_COLOR,
            font_size=sp(13), size_hint_y=None, height=dp(40),
            font_name=_font()
        )
        form.add_widget(self.name_input)

        # 类型
        form.add_widget(make_label("类型:", font_size=13))
        self.type_spinner = make_spinner(
            self.character.char_type.name,
            ["HUMAN", "REPLIKA"],
            font_size=sp(13),
            size_hint_y=None, height=dp(40)
        )
        form.add_widget(self.type_spinner)

        # 描述
        form.add_widget(make_label("描述:", font_size=13))
        self.desc_input = TextInput(
            text=self.character.description, multiline=True,
            background_color=INPUT_BG, foreground_color=TEXT_COLOR,
            font_size=sp(12), size_hint_y=None, height=dp(60),
            font_name=_font()
        )
        form.add_widget(self.desc_input)

        # 属性
        form.add_widget(make_label("--- 属性 ---", font_size=14, color=ACCENT_COLOR, bold=True))

        self.attr_inputs = {}
        for key, (name, abbr, desc) in ATTRIBUTES.items():
            form.add_widget(make_label(f"{abbr}({name}):", font_size=12))
            inp = TextInput(
                text=str(self.character.attributes.get(key, 4)),
                multiline=False, input_filter="int",
                background_color=INPUT_BG, foreground_color=TEXT_COLOR,
                font_size=sp(12), size_hint_y=None, height=dp(36),
                font_name=_font()
            )
            self.attr_inputs[key] = inp
            form.add_widget(inp)

        # 技能 (按类别分组)
        form.add_widget(make_label("--- 技能 ---", font_size=14, color=ACCENT_COLOR, bold=True))

        self.skill_inputs = {}
        for cat_name, skill_keys in SKILL_CATEGORIES.items():
            form.add_widget(make_label(f"[{cat_name}]", font_size=12, color=DIM_TEXT))
            for sk in skill_keys:
                name = SKILLS[sk][0]
                form.add_widget(make_label(f"{name}:", font_size=11))
                inp = TextInput(
                    text=str(self.character.skills.get(sk, 0)),
                    multiline=False, input_filter="int",
                    background_color=INPUT_BG, foreground_color=TEXT_COLOR,
                    font_size=sp(11), size_hint_y=None, height=dp(32),
                    font_name=_font()
                )
                self.skill_inputs[sk] = inp
                form.add_widget(inp)

        # 状态
        form.add_widget(make_label("--- 状态 ---", font_size=14, color=ACCENT_COLOR, bold=True))

        status_fields = [
            ("HP:", "current_hp", str(self.character.current_hp)),
            ("压力:", "stress", str(self.character.stress)),
            ("PCD:", "pcd_points", str(self.character.pcd_points)),
            ("共振阶段:", "resonance_stage", str(self.character.resonance_stage)),
        ]
        self.status_inputs = {}
        for label, key, default in status_fields:
            form.add_widget(make_label(label, font_size=12))
            inp = TextInput(
                text=default, multiline=False, input_filter="int",
                background_color=INPUT_BG, foreground_color=TEXT_COLOR,
                font_size=sp(12), size_hint_y=None, height=dp(36),
                font_name=_font()
            )
            self.status_inputs[key] = inp
            form.add_widget(inp)

        # 护甲
        form.add_widget(make_label("护甲:", font_size=12))
        self.armor_spinner = make_spinner(
            ARMOR_DISPLAY_MAP.get(self.character.armor, self.character.armor),
            ARMOR_DISPLAY_NAMES,
            font_size=sp(12),
            size_hint_y=None, height=dp(36)
        )
        form.add_widget(self.armor_spinner)

        # 武器
        form.add_widget(make_label("武器:", font_size=12))
        self.weapon_spinner = make_spinner(
            WEAPON_DISPLAY_MAP.get(self.character.equipped_weapon, self.character.equipped_weapon),
            WEAPON_DISPLAY_NAMES,
            font_size=sp(12),
            size_hint_y=None, height=dp(36)
        )
        form.add_widget(self.weapon_spinner)

        scroll.add_widget(form)
        main_layout.add_widget(scroll)

        # 底部按钮
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_box.add_widget(make_button("保存", self._on_save))
        btn_box.add_widget(make_button("取消", self._on_cancel))
        btn_box.add_widget(make_button("应用模板", self._on_template))
        main_layout.add_widget(btn_box)

        self.content = main_layout

    def _load_data(self):
        pass  # 数据已在_build_ui中加载

    def _on_save(self, instance):
        try:
            self.character.name = self.name_input.text or "未命名"
            self.character.char_type = CharacterType[self.type_spinner.text]
            self.character.description = self.desc_input.text

            for key, inp in self.attr_inputs.items():
                val = int(inp.text) if inp.text else 4
                self.character.attributes[key] = max(ATTRIBUTE_MIN, min(ATTRIBUTE_MAX, val))

            for key, inp in self.skill_inputs.items():
                val = int(inp.text) if inp.text else 0
                self.character.skills[key] = max(0, min(SKILL_MAX, val))

            self.character.current_hp = int(self.status_inputs["current_hp"].text) if self.status_inputs["current_hp"].text else self.character.current_hp
            self.character.stress = int(self.status_inputs["stress"].text) if self.status_inputs["stress"].text else 0
            self.character.pcd_points = int(self.status_inputs["pcd_points"].text) if self.status_inputs["pcd_points"].text else 3
            self.character.resonance_stage = int(self.status_inputs["resonance_stage"].text) if self.status_inputs["resonance_stage"].text else 0

            self.character.armor = ARMOR_KEY_MAP.get(self.armor_spinner.text, self.armor_spinner.text)
            self.character.equipped_weapon = WEAPON_KEY_MAP.get(self.weapon_spinner.text, self.weapon_spinner.text)
            self.character.max_hp = self.character.calculate_hp()

            if self.on_save:
                self.on_save(self.character)
            self.dismiss()
        except Exception as e:
            popup = Popup(title="错误", title_font=_font(), content=make_label(f"保存失败: {str(e)}", font_size=14),
                          size_hint=(0.5, 0.3), background_color=PANEL_COLOR)
            popup.open()

    def _on_cancel(self, instance):
        self.dismiss()

    def _on_template(self, instance):
        popup = TemplateSelectorPopup(on_select=self._apply_template)
        popup.open()

    def _apply_template(self, template):
        self.name_input.text = template.get("name", "新角色")
        self.type_spinner.text = template.get("char_type", "HUMAN")
        self.desc_input.text = template.get("description", "")

        for key, val in template.get("attributes", {}).items():
            if key in self.attr_inputs:
                self.attr_inputs[key].text = str(val)

        for key, val in template.get("skills", {}).items():
            if key in self.skill_inputs:
                self.skill_inputs[key].text = str(val)

        armor_key = template.get("armor", "none")
        self.armor_spinner.text = ARMOR_DISPLAY_MAP.get(armor_key, armor_key)
        weapon_key = template.get("equipped_weapon", "unarmed")
        self.weapon_spinner.text = WEAPON_DISPLAY_MAP.get(weapon_key, weapon_key)
        self.status_inputs["resonance_stage"].text = str(template.get("resonance_stage", 0))
        self.status_inputs["pcd_points"].text = str(template.get("pcd_points", 3))
        phy = template.get("attributes", {}).get("phy", 4)
        self.status_inputs["current_hp"].text = str(phy * 2 + 4)


# ---------------------------------------------------------------------------
# 模板选择弹窗 (Template Selector Popup)
# ---------------------------------------------------------------------------
class TemplateSelectorPopup(Popup):
    """角色模板选择弹窗"""

    def __init__(self, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "选择模板"
        self.title_font = _font()
        self.size_hint = (0.9, 0.8)
        self.background_color = PANEL_COLOR
        self.on_select = on_select

        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        add_panel_bg(layout)

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        self.btn_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(5)
        )
        self.btn_container.bind(minimum_height=self.btn_container.setter('height'))

        for template in DEFAULT_CHARACTER_TEMPLATES:
            btn = Button(
                text=f"{template['name']} [{template['char_type']}]\n{template['description'][:40]}...",
                halign="center", size_hint_y=None, height=dp(60),
                background_color=BUTTON_BG, color=TEXT_COLOR,
                font_size=sp(11)
            )
            btn.bind(on_press=lambda inst, t=template: self._select(t))
            self.btn_container.add_widget(btn)

        scroll.add_widget(self.btn_container)
        layout.add_widget(scroll)
        layout.add_widget(make_button("取消", self._dismiss, size_hint_y=None, height=dp(45)))

        self.content = layout

    def _select(self, template):
        self.on_select(template)
        self.dismiss()

    def _dismiss(self, instance):
        self.dismiss()


# ---------------------------------------------------------------------------
# 敌人模板选择弹窗 (Enemy Template Selector Popup)
# ---------------------------------------------------------------------------
class EnemyTemplateSelectorPopup(Popup):
    """敌人模板选择弹窗"""

    def __init__(self, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "选择敌人模板"
        self.title_font = _font()
        self.size_hint = (0.9, 0.8)
        self.background_color = PANEL_COLOR
        self.on_select = on_select

        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        add_panel_bg(layout)

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        self.btn_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(5)
        )
        self.btn_container.bind(minimum_height=self.btn_container.setter('height'))

        for template in DEFAULT_ENEMY_TEMPLATES:
            btn = Button(
                text=f"{template['name']} [{template['threat_level']}]\n{template['description'][:40]}...",
                halign="center", size_hint_y=None, height=dp(60),
                background_color=BUTTON_BG, color=TEXT_COLOR,
                font_size=sp(11)
            )
            btn.bind(on_press=lambda inst, t=template: self._select(t))
            self.btn_container.add_widget(btn)

        scroll.add_widget(self.btn_container)
        layout.add_widget(scroll)
        layout.add_widget(make_button("取消", self._dismiss, size_hint_y=None, height=dp(45)))

        self.content = layout

    def _select(self, template):
        self.on_select(template)
        self.dismiss()

    def _dismiss(self, instance):
        self.dismiss()


# ---------------------------------------------------------------------------
# 人类恢复弹窗 (Human Heal Popup)
# ---------------------------------------------------------------------------
class HumanHealPopup(Popup):
    """人类恢复 - 输入共振能量"""

    def __init__(self, on_confirm=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "人类自然恢复"
        self.title_font = _font()
        self.size_hint = (0.5, 0.35)
        self.background_color = PANEL_COLOR
        self.on_confirm = on_confirm

        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        add_panel_bg(layout)
        layout.add_widget(make_label("每1HP消耗1共振能量\n每天最多恢复2HP", font_size=13))

        layout.add_widget(make_label("可用共振能量:", font_size=12))
        self.energy_input = TextInput(
            text="5", multiline=False, input_filter="int",
            background_color=INPUT_BG, foreground_color=TEXT_COLOR,
            font_size=sp(14), size_hint_y=None, height=dp(40), halign="center",
            font_name=_font()
        )
        layout.add_widget(self.energy_input)

        btn_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_box.add_widget(make_button("恢复", self._confirm))
        btn_box.add_widget(make_button("取消", self._dismiss))
        layout.add_widget(btn_box)

        self.content = layout

    def _confirm(self, instance):
        try:
            energy = int(self.energy_input.text) if self.energy_input.text else 0
            self.on_confirm(energy)
            self.dismiss()
        except:
            self.dismiss()

    def _dismiss(self, instance):
        self.dismiss()


# ---------------------------------------------------------------------------
# 信息弹窗 (Info Popup)
# ---------------------------------------------------------------------------
class InfoPopup(Popup):
    """通用信息弹窗"""

    def __init__(self, title, message, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = _font()
        self.size_hint = (0.9, 0.8)
        self.background_color = PANEL_COLOR

        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        add_panel_bg(layout)

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        label = Label(
            text=message, font_size=sp(12), color=TEXT_COLOR,
            size_hint_y=None, markup=True,
            font_name=_font()
        )
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)
        layout.add_widget(scroll)

        layout.add_widget(make_button("关闭", self._dismiss, size_hint_y=None, height=dp(45)))

        self.content = layout

    def _dismiss(self, instance):
        self.dismiss()


# ---------------------------------------------------------------------------
# 左侧面板 - 角色管理 (Left Panel)
# ---------------------------------------------------------------------------
class LeftPanel(BoxLayout):
    """左栏 - 角色和敌人管理"""

    characters = DictProperty({})
    enemies = DictProperty({})

    def __init__(self, app, **kwargs):
        import traceback
        print("[SIGNALIS] LeftPanel.__init__ start")
        try:
            super().__init__(**kwargs)
            self.app = app
            self.orientation = "vertical"
            self.padding = dp(5)
            self.spacing = dp(5)
            self._build_ui()
            print("[SIGNALIS] LeftPanel.__init__ done")
        except Exception as e:
            print(f"[SIGNALIS] CRASH in LeftPanel.__init__: {e}")
            print(f"[SIGNALIS] TRACEBACK: {traceback.format_exc()}")
            raise

    def _build_ui(self):
        # 标题
        self.add_widget(make_label("角色 / 敌人", font_size=18, color=ACCENT_COLOR, bold=True,
                                   size_hint_y=None, height=dp(35)))

        # 攻击方/防御方显示
        self.attacker_label = make_label("攻击方: 无", font_size=11, color=SUCCESS_COLOR,
                                          size_hint_y=None, height=dp(25))
        self.add_widget(self.attacker_label)
        self.defender_label = make_label("防御方: 无", font_size=11, color=FAILURE_COLOR,
                                          size_hint_y=None, height=dp(25))
        self.add_widget(self.defender_label)

        # 设为攻击方/防御方按钮
        target_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        target_box.add_widget(make_button("设为攻击方", self._set_attacker, font_size=sp(10)))
        target_box.add_widget(make_button("设为防御方", self._set_defender, font_size=sp(10)))
        self.add_widget(target_box)

        # --- 角色列表 ---
        self.add_widget(make_label("--- 角色 ---", font_size=13, color=DIM_TEXT,
                                   size_hint_y=None, height=dp(22)))

        char_scroll = ScrollView(size_hint=(1, 0.25), do_scroll_x=False, scroll_type=['content'])
        self.char_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.char_list.bind(minimum_height=self.char_list.setter('height'))
        char_scroll.add_widget(self.char_list)
        self.add_widget(char_scroll)

        char_btn_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(3))
        char_btn_box.add_widget(make_button("新建", self._new_character, font_size=sp(10)))
        char_btn_box.add_widget(make_button("编辑", self._edit_character, font_size=sp(10)))
        char_btn_box.add_widget(make_button("删除", self._delete_character, font_size=sp(10)))
        self.add_widget(char_btn_box)

        # --- 敌人列表 ---
        self.add_widget(make_label("--- 敌人 ---", font_size=13, color=DIM_TEXT,
                                   size_hint_y=None, height=dp(22)))

        enemy_scroll = ScrollView(size_hint=(1, 0.25), do_scroll_x=False, scroll_type=['content'])
        self.enemy_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.enemy_list.bind(minimum_height=self.enemy_list.setter('height'))
        enemy_scroll.add_widget(self.enemy_list)
        self.add_widget(enemy_scroll)

        enemy_btn_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(3))
        enemy_btn_box.add_widget(make_button("添加(模板)", self._add_enemy, font_size=sp(10)))
        enemy_btn_box.add_widget(make_button("删除", self._delete_enemy, font_size=sp(10)))
        self.add_widget(enemy_btn_box)

        # --- 角色详情 ---
        self.add_widget(make_label("--- 详情 ---", font_size=13, color=DIM_TEXT,
                                   size_hint_y=None, height=dp(22)))

        detail_scroll = ScrollView(size_hint=(1, 0.3), do_scroll_x=False, scroll_type=['content'])
        self.detail_label = Label(
            text="选择一个角色查看详情", font_size=sp(11),
            color=TEXT_COLOR, size_hint_y=None, markup=True,
            font_name=_font()
        )
        self.detail_label.bind(texture_size=self.detail_label.setter('size'))
        self.detail_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        detail_scroll.add_widget(self.detail_label)
        self.add_widget(detail_scroll)

        # 场景切换按钮
        self.add_widget(make_button("场景切换(重置效果)", self._new_scene,
                                     size_hint_y=None, height=dp(40), font_size=sp(12)))

    def _make_char_button(self, entity, is_enemy=False):
        """创建角色/敌人按钮"""
        if is_enemy:
            display = f"{entity.name} [{entity.threat_level}] HP:{entity.current_hp}"
        else:
            display = f"{entity.name} [{entity.char_type.value}] HP:{entity.current_hp}"
        btn = Button(
            text=display, halign="left", font_size=sp(11),
            background_color=BUTTON_BG, color=TEXT_COLOR,
            size_hint_y=None, height=dp(36),
            font_name=_font()
        )
        btn.entity = entity
        btn.is_enemy = is_enemy
        btn.bind(on_press=self._on_entity_select)
        return btn

    def _on_entity_select(self, instance):
        """选中角色/敌人"""
        self.selected_entity = instance.entity
        self.selected_is_enemy = instance.is_enemy
        self._update_detail(instance.entity)
        # 高亮选中
        for child in list(self.char_list.children) + list(self.enemy_list.children):
            if hasattr(child, 'background_color'):
                child.background_color = BUTTON_BG
        instance.background_color = BUTTON_BG_ACTIVE

    def _update_detail(self, entity):
        """更新详情显示"""
        if isinstance(entity, Character):
            text = f"[b]{entity.name}[/b] [{entity.char_type.value}]\n"
            text += f"HP: {entity.current_hp}/{entity.max_hp} [{entity.get_health_status()}]\n"
            stress_name, _, _, _ = entity.get_stress_effects()
            text += f"压力: {entity.stress}/10 ({stress_name})\n"
            if entity.char_type == CharacterType.REPLIKA:
                text += f"PCD: {entity.pcd_points}/{entity.max_pcd}\n"
            text += f"共振阶段: {entity.resonance_stage}\n"
            text += f"创伤: 临时{entity.temp_traumas}/永久{entity.perm_traumas}\n"
            text += "\n[b]属性[/b]\n"
            for key, val in entity.attributes.items():
                text += f"  {entity.get_attribute_display(key)}: {val}\n"
            text += "\n[b]技能[/b]\n"
            for cat_name, skill_keys in SKILL_CATEGORIES.items():
                cat_skills = []
                for sk in skill_keys:
                    sv = entity.skills.get(sk, 0)
                    if sv > 0:
                        cat_skills.append(f"{entity.get_skill_name(sk)}:{sv}")
                if cat_skills:
                    text += f"  [{cat_name}] {', '.join(cat_skills)}\n"
            if isinstance(entity, Enemy):
                text += f"\n威胁等级: {entity.threat_level}\n"
                if entity.special_abilities:
                    for ab in entity.special_abilities:
                        text += f"  - {ab}\n"
            self.detail_label.text = text
        else:
            self.detail_label.text = "未选择"

    def add_character(self, character):
        """添加角色"""
        char_id = f"char_{len(self.characters)}"
        self.characters[char_id] = character
        self._refresh_char_list()
        return char_id

    def add_enemy(self, enemy):
        """添加敌人"""
        enemy_id = f"enemy_{len(self.enemies)}"
        self.enemies[enemy_id] = enemy
        self._refresh_enemy_list()
        return enemy_id

    def _refresh_char_list(self):
        self.char_list.clear_widgets()
        for char_id, char in self.characters.items():
            self.char_list.add_widget(self._make_char_button(char, is_enemy=False))

    def _refresh_enemy_list(self):
        self.enemy_list.clear_widgets()
        for enemy_id, enemy in self.enemies.items():
            self.enemy_list.add_widget(self._make_char_button(enemy, is_enemy=True))

    def get_selected_entity(self):
        """获取当前选中的实体"""
        return getattr(self, 'selected_entity', None)

    def _set_attacker(self, instance):
        entity = self.get_selected_entity()
        if entity:
            self.app.current_attacker = entity
            self.attacker_label.text = f"攻击方: {entity.name} [{entity.char_type.value}]"
            self.app.engine.log(f"设定攻击方: {entity.name}")
            self.app.add_log(f"设定攻击方: {entity.name}")
        else:
            self._show_info("提示", "请先选择一个角色或敌人")

    def _set_defender(self, instance):
        entity = self.get_selected_entity()
        if entity:
            self.app.current_defender = entity
            self.defender_label.text = f"防御方: {entity.name} [{entity.char_type.value}]"
            self.app.engine.log(f"设定防御方: {entity.name}")
            self.app.add_log(f"设定防御方: {entity.name}")
        else:
            self._show_info("提示", "请先选择一个角色或敌人")

    def _new_character(self, instance):
        def on_save(char):
            self.add_character(char)
        popup = CharacterEditorPopup(on_save=on_save)
        popup.open()

    def _edit_character(self, instance):
        entity = self.get_selected_entity()
        if entity and not getattr(self, 'selected_is_enemy', False):
            def on_save(updated_char):
                for char_id, c in self.characters.items():
                    if c is entity:
                        self.characters[char_id] = updated_char
                        break
                self._refresh_char_list()
                self._update_detail(updated_char)
            popup = CharacterEditorPopup(character=entity, on_save=on_save)
            popup.open()
        else:
            self._show_info("提示", "请选择一个角色(不是敌人)")

    def _delete_character(self, instance):
        if hasattr(self, 'selected_entity') and self.selected_entity:
            if not getattr(self, 'selected_is_enemy', False):
                for char_id, c in list(self.characters.items()):
                    if c is self.selected_entity:
                        del self.characters[char_id]
                        break
                self._refresh_char_list()
                self.detail_label.text = "选择一个角色查看详情"

    def _add_enemy(self, instance):
        def on_select(template):
            enemy = Enemy.from_template(template)
            self.add_enemy(enemy)
        popup = EnemyTemplateSelectorPopup(on_select=on_select)
        popup.open()

    def _delete_enemy(self, instance):
        if hasattr(self, 'selected_entity') and self.selected_entity:
            if getattr(self, 'selected_is_enemy', False):
                for enemy_id, e in list(self.enemies.items()):
                    if e is self.selected_entity:
                        del self.enemies[enemy_id]
                        break
                self._refresh_enemy_list()
                self.detail_label.text = "选择一个角色查看详情"

    def _new_scene(self, instance):
        all_entities = list(self.characters.values()) + list(self.enemies.values())
        self.app.engine.new_scene(all_entities)
        self.app.add_log("【场景切换】所有角色的场景级效果已重置\n- 情感连接次数已重置\n- 镇定剂效果已消退")
        self._show_info("场景切换", "场景已切换!\n- 情感连接(限一次/场景)已重置\n- 镇定剂效果已消退")

    def _show_info(self, title, message):
        popup = InfoPopup(title, message)
        popup.open()


# ---------------------------------------------------------------------------
# 中间面板 - 判定控制 (Center Panel with Tabs)
# ---------------------------------------------------------------------------
class CenterPanel(BoxLayout):
    """中栏 - 判定面板(Tabbed)"""

    def __init__(self, app, **kwargs):
        import traceback
        print("[SIGNALIS] CenterPanel.__init__ start")
        try:
            super().__init__(**kwargs)
            self.app = app
            self.orientation = "vertical"
            self.padding = dp(5)
            self.spacing = dp(5)
            self._build_ui()
            print("[SIGNALIS] CenterPanel.__init__ done")
        except Exception as e:
            print(f"[SIGNALIS] CRASH in CenterPanel.__init__: {e}")
            print(f"[SIGNALIS] TRACEBACK: {traceback.format_exc()}")
            raise

    def _build_ui(self):
        import traceback
        print("[SIGNALIS] CenterPanel._build_ui start")
        try:
            # 标题
            self.add_widget(make_label("判定控制 v2", font_size=20, color=ACCENT_COLOR, bold=True,
                                       size_hint_y=None, height=dp(35)))
            print("[SIGNALIS] CenterPanel title added")

            # TabbedPanel
            print("[SIGNALIS] Building TabbedPanel...")
            from kivy.utils import platform
            is_android = platform == 'android' if hasattr(platform, '__call__') else False
            tab_w = dp(90) if is_android else dp(70)
            self.tab_panel = TabbedPanel(
                do_default_tab=False,
                tab_width=tab_w,
                tab_height=dp(32),
                background_color=PANEL_COLOR,
                border=(0, 0, 0, 0)
            )
            print("[SIGNALIS] TabbedPanel created")

            # 基础检定Tab
            print("[SIGNALIS] Building basic tab...")
            self.tab_panel.add_widget(self._build_basic_tab())
            print("[SIGNALIS] Basic tab added")
            # 对抗检定Tab
            print("[SIGNALIS] Building opposed tab...")
            self.tab_panel.add_widget(self._build_opposed_tab())
            print("[SIGNALIS] Opposed tab added")
            # 战斗Tab
            print("[SIGNALIS] Building combat tab...")
            self.tab_panel.add_widget(self._build_combat_tab())
            print("[SIGNALIS] Combat tab added")
            # 恐怖Tab
            print("[SIGNALIS] Building horror tab...")
            self.tab_panel.add_widget(self._build_horror_tab())
            print("[SIGNALIS] Horror tab added")
            # 共振Tab
            print("[SIGNALIS] Building resonance tab...")
            self.tab_panel.add_widget(self._build_resonance_tab())
            print("[SIGNALIS] Resonance tab added")
            # PCD Tab
            print("[SIGNALIS] Building PCD tab...")
            self.tab_panel.add_widget(self._build_pcd_tab())
            print("[SIGNALIS] PCD tab added")
            # 贴贴Tab
            print("[SIGNALIS] Building intimacy tab...")
            self.tab_panel.add_widget(self._build_intimacy_tab())
            print("[SIGNALIS] Intimacy tab added")
            # 恢复Tab
            print("[SIGNALIS] Building heal tab...")
            self.tab_panel.add_widget(self._build_heal_tab())
            print("[SIGNALIS] Heal tab added")

            self.add_widget(self.tab_panel)
            print("[SIGNALIS] TabbedPanel added to layout")
        except Exception as e:
            print(f"[SIGNALIS] CRASH in CenterPanel._build_ui: {e}")
            print(f"[SIGNALIS] TRACEBACK: {traceback.format_exc()}")
            raise

        # 结果显示区域
        self.add_widget(make_label("判定结果", font_size=14, color=ACCENT_COLOR, bold=True,
                                   size_hint_y=None, height=dp(25)))

        result_scroll = ScrollView(size_hint=(1, 0.35), do_scroll_x=False, scroll_type=['content'])
        self.result_label = Label(
            text="执行检定后结果将显示在这里", font_size=sp(12),
            color=TEXT_COLOR, size_hint_y=None, markup=True,
            font_name=_font()
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.result_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        result_scroll.add_widget(self.result_label)
        self.add_widget(result_scroll)

    def _build_basic_tab(self):
        """基础检定Tab"""
        tab = TabbedPanelHeader(text="基础检定")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, height=dp(320))
        grid.add_widget(make_label("属性:", font_size=13))
        self.basic_attr = make_spinner(ATTR_DISPLAY_MAP["agi"], ATTR_DISPLAY_NAMES,
                                        size_hint_y=None, height=dp(40))
        grid.add_widget(self.basic_attr)

        grid.add_widget(make_label("技能:", font_size=13))
        self.basic_skill = make_spinner(SKILL_DISPLAY_MAP["dodge"], SKILL_DISPLAY_NAMES,
                                         size_hint_y=None, height=dp(40))
        grid.add_widget(self.basic_skill)

        grid.add_widget(make_label("情境调整:", font_size=13))
        self.basic_situational = make_spinner("0", [str(i) for i in range(-3, 4)],
                                               size_hint_y=None, height=dp(40))
        grid.add_widget(self.basic_situational)

        grid.add_widget(make_label("描述:", font_size=13))
        self.basic_desc = TextInput(
            text="", multiline=False,
            background_color=INPUT_BG, foreground_color=TEXT_COLOR,
            font_size=sp(12), size_hint_y=None, height=dp(40),
            font_name=_font()
        )
        grid.add_widget(self.basic_desc)

        content.add_widget(grid)
        content.add_widget(make_button("执行检定", self._do_basic_check,
                                        size_hint_y=None, height=dp(48), font_size=sp(14)))
        content.add_widget(Label())  # spacer

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_opposed_tab(self):
        """对抗检定Tab"""
        tab = TabbedPanelHeader(text="对抗检定")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # 攻击方
        atk_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(150))
        atk_box.add_widget(make_label("--- 攻击方 ---", font_size=12, color=ACCENT_COLOR))
        grid1 = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, height=dp(120))
        grid1.add_widget(make_label("属性:", font_size=12))
        self.opposed_attr1 = make_spinner(ATTR_DISPLAY_MAP["agi"], ATTR_DISPLAY_NAMES,
                                           size_hint_y=None, height=dp(36))
        grid1.add_widget(self.opposed_attr1)
        grid1.add_widget(make_label("技能:", font_size=12))
        self.opposed_skill1 = make_spinner(SKILL_DISPLAY_MAP["firearms"], SKILL_DISPLAY_NAMES,
                                            size_hint_y=None, height=dp(36))
        grid1.add_widget(self.opposed_skill1)
        atk_box.add_widget(grid1)
        content.add_widget(atk_box)

        # 防御方
        def_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(150))
        def_box.add_widget(make_label("--- 防御方 ---", font_size=12, color=ACCENT_COLOR))
        grid2 = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, height=dp(120))
        grid2.add_widget(make_label("属性:", font_size=12))
        self.opposed_attr2 = make_spinner(ATTR_DISPLAY_MAP["agi"], ATTR_DISPLAY_NAMES,
                                           size_hint_y=None, height=dp(36))
        grid2.add_widget(self.opposed_attr2)
        grid2.add_widget(make_label("技能:", font_size=12))
        self.opposed_skill2 = make_spinner(SKILL_DISPLAY_MAP["dodge"], SKILL_DISPLAY_NAMES,
                                            size_hint_y=None, height=dp(36))
        grid2.add_widget(self.opposed_skill2)
        def_box.add_widget(grid2)
        content.add_widget(def_box)

        content.add_widget(make_button("执行对抗", self._do_opposed_check,
                                        size_hint_y=None, height=dp(48), font_size=sp(14)))
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_combat_tab(self):
        """战斗判定Tab"""
        tab = TabbedPanelHeader(text="战斗判定")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, height=dp(240))
        grid.add_widget(make_label("武器:", font_size=13))
        self.combat_weapon = make_spinner(WEAPON_DISPLAY_MAP["rifle"], WEAPON_DISPLAY_NAMES,
                                           size_hint_y=None, height=dp(40))
        grid.add_widget(self.combat_weapon)

        grid.add_widget(make_label("调整值:", font_size=13))
        self.combat_situational = make_spinner("0", [str(i) for i in range(-3, 4)],
                                                size_hint_y=None, height=dp(40))
        grid.add_widget(self.combat_situational)

        grid.add_widget(make_label("瞄准部位:", font_size=13))
        self.combat_called = make_spinner("无", ["无", "head(头部)", "arm(手臂)", "leg(腿部)", "torso(躯干)"],
                                           size_hint_y=None, height=dp(40))
        grid.add_widget(self.combat_called)

        content.add_widget(grid)
        content.add_widget(make_button("攻击!", self._do_combat,
                                        size_hint_y=None, height=dp(48), font_size=sp(16)))
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_horror_tab(self):
        """恐怖检定Tab"""
        tab = TabbedPanelHeader(text="恐怖检定")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, height=dp(140))
        grid.add_widget(make_label("恐怖等级:", font_size=13))
        self.horror_level = make_spinner(HORROR_DISPLAY_MAP["fear"], HORROR_DISPLAY_NAMES,
                                          size_hint_y=None, height=dp(40))
        grid.add_widget(self.horror_level)
        content.add_widget(grid)

        content.add_widget(make_label("v2: 使用 WIL + 感知技能\n成功只+1压力, 失败按等级+压力",
                                       font_size=11, color=DIM_TEXT))
        content.add_widget(make_button("执行恐怖检定", self._do_horror_check,
                                        size_hint_y=None, height=dp(48), font_size=sp(14)))
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_resonance_tab(self):
        """生物共振Tab"""
        tab = TabbedPanelHeader(text="生物共振")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, height=dp(180))
        grid.add_widget(make_label("能力:", font_size=13))
        self.res_ability = make_spinner(RESONANCE_DISPLAY_NAMES[0], RESONANCE_DISPLAY_NAMES,
                                         size_hint_y=None, height=dp(40))
        grid.add_widget(self.res_ability)

        grid.add_widget(make_label("调整:", font_size=13))
        self.res_situational = make_spinner("0", [str(i) for i in range(-3, 4)],
                                             size_hint_y=None, height=dp(40))
        grid.add_widget(self.res_situational)
        content.add_widget(grid)

        btn_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_box.add_widget(make_button("执行共振检定", self._do_resonance_check, font_size=sp(12)))
        btn_box.add_widget(make_button("共振爆发", self._do_resonance_surge, font_size=sp(12)))
        content.add_widget(btn_box)
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_pcd_tab(self):
        """PCD操作Tab"""
        tab = TabbedPanelHeader(text="PCD操作")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(make_label("PCD (人格模型校正数据) - 仅仿形体",
                                       font_size=14, color=ACCENT_COLOR, bold=True))
        content.add_widget(make_label("1点 = 重掷 | 2点 = 加骰 | 3点 = 过载(+2骰,+1压力)\n耗尽触发人格模型加载异常",
                                       font_size=11, color=DIM_TEXT))

        btn_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        btn_box.add_widget(make_button("PCD重掷(1点)", self._do_pcd_reroll, font_size=sp(11)))
        btn_box.add_widget(make_button("PCD加骰(2点)", self._do_pcd_add_die, font_size=sp(11)))
        btn_box.add_widget(make_button("PCD过载(3点)", self._do_pcd_overload, font_size=sp(11)))
        content.add_widget(btn_box)
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_intimacy_tab(self):
        """贴贴机制Tab"""
        tab = TabbedPanelHeader(text="贴贴机制")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(make_label("队友亲密交互 - 压力恢复",
                                       font_size=14, color=ACCENT_COLOR, bold=True))
        content.add_widget(make_label(
            "情感连接(拥抱/安慰): 压力-2 [限一次/场景]\n深度亲密(贴贴/心灵共鸣): 压力-3 [限一次/游戏]",
            font_size=11, color=DIM_TEXT))

        btn_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_box.add_widget(make_button("情感连接(-2压力)", self._do_emotional_bond, font_size=sp(12)))
        btn_box.add_widget(make_button("深度亲密(-3压力)", self._do_deep_intimacy, font_size=sp(12)))
        content.add_widget(btn_box)
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    def _build_heal_tab(self):
        """恢复/治疗Tab"""
        tab = TabbedPanelHeader(text="恢复/治疗")
        tab.font_name = _font()
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(make_label("v2恢复规则:", font_size=14, color=ACCENT_COLOR, bold=True))
        content.add_widget(make_label(
            "仿形体: 维修工具1轮恢复4HP\n人类: 自然恢复2HP/天,每1HP消耗1共振能量\n仿形体濒死: 纳米针剂恢复50%HP并苏醒",
            font_size=11, color=DIM_TEXT))

        btn_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        btn_box.add_widget(make_button("仿形体快速恢复", self._do_replika_heal, font_size=sp(10)))
        btn_box.add_widget(make_button("人类自然恢复", self._do_human_heal, font_size=sp(10)))
        btn_box.add_widget(make_button("纳米针剂恢复", self._do_revive_replika, font_size=sp(10)))
        content.add_widget(btn_box)
        content.add_widget(Label())

        scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        scroll.add_widget(content)
        tab.content = scroll
        return tab

    # --- 判定方法 ---

    def _show_result(self, text):
        self.result_label.text = text.replace("\n", "\n")
        self.app.add_log(text)

    def _do_basic_check(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个攻击方角色")
            return
        attr_display = self.basic_attr.text
        attr = ATTR_KEY_MAP.get(attr_display, attr_display)
        skill_display = self.basic_skill.text
        skill = SKILL_KEY_MAP.get(skill_display, skill_display)
        situational = int(self.basic_situational.text) if self.basic_situational.text else 0
        desc = self.basic_desc.text
        result = self.app.engine.basic_check(char, attr, skill, situational, desc)
        self._show_result(result["details"])

    def _do_opposed_check(self, instance):
        char1 = self.app.current_attacker
        char2 = self.app.current_defender
        if not char1 or not char2:
            self._show_info("提示", "请先设定攻击方和防御方")
            return
        attr1 = ATTR_KEY_MAP.get(self.opposed_attr1.text, self.opposed_attr1.text)
        skill1 = SKILL_KEY_MAP.get(self.opposed_skill1.text, self.opposed_skill1.text)
        attr2 = ATTR_KEY_MAP.get(self.opposed_attr2.text, self.opposed_attr2.text)
        skill2 = SKILL_KEY_MAP.get(self.opposed_skill2.text, self.opposed_skill2.text)
        result = self.app.engine.opposed_check(char1, attr1, skill1, char2, attr2, skill2)
        self._show_result(result["details"])

    def _do_combat(self, instance):
        attacker = self.app.current_attacker
        defender = self.app.current_defender
        if not attacker or not defender:
            self._show_info("提示", "请先设定攻击方和防御方")
            return
        weapon = WEAPON_KEY_MAP.get(self.combat_weapon.text, self.combat_weapon.text)
        situational = int(self.combat_situational.text) if self.combat_situational.text else 0
        called = self.combat_called.text
        if called == "无":
            called = None
        elif "(" in called:
            called = called.split("(")[0]
        result = self.app.engine.combat_attack(attacker, defender, weapon, situational, called)
        self._show_result(result["details"])
        self.app.left_panel._refresh_char_list()
        self.app.left_panel._refresh_enemy_list()

    def _do_horror_check(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个角色")
            return
        level = HORROR_KEY_MAP.get(self.horror_level.text, self.horror_level.text)
        if "(" in level:
            level = level.split("(")[0]
        result = self.app.engine.horror_check(char, level)
        self._show_result(result["details"])

    def _do_resonance_check(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个角色")
            return
        ability = RESONANCE_KEY_MAP.get(self.res_ability.text, self.res_ability.text)
        if "(" in ability:
            ability = ability.split("(")[0]
        situational = int(self.res_situational.text) if self.res_situational.text else 0
        result = self.app.engine.resonance_check(char, ability, situational)
        self._show_result(result["details"])

    def _do_resonance_surge(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个角色")
            return
        result = self.app.engine.resonance_surge(char)
        self._show_result(result["details"])

    def _do_pcd_reroll(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个仿形体角色")
            return
        result = self.app.engine.use_pcd(char, "reroll")
        self._show_result(result["details"])

    def _do_pcd_add_die(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个仿形体角色")
            return
        result = self.app.engine.use_pcd(char, "add_die")
        self._show_result(result["details"])

    def _do_pcd_overload(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个仿形体角色")
            return
        result = self.app.engine.use_pcd(char, "overload")
        self._show_result(result["details"])

    def _do_emotional_bond(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个角色")
            return
        result = self.app.engine.intimacy_action(char, "emotional_bond")
        self._show_result(result["details"])

    def _do_deep_intimacy(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个角色")
            return
        result = self.app.engine.intimacy_action(char, "deep_intimacy")
        self._show_result(result["details"])

    def _do_replika_heal(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个仿形体角色")
            return
        result = self.app.engine.heal_replika(char)
        self._show_result(result["details"])

    def _do_human_heal(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个人类角色")
            return
        def on_confirm(energy):
            result = self.app.engine.heal_human(char, energy)
            self._show_result(result["details"])
        popup = HumanHealPopup(on_confirm=on_confirm)
        popup.open()

    def _do_revive_replika(self, instance):
        char = self.app.current_attacker
        if not char:
            self._show_info("提示", "请先设定一个仿形体角色")
            return
        result = self.app.engine.revive_replika(char)
        self._show_result(result["details"])

    def _show_info(self, title, message):
        popup = InfoPopup(title, message)
        popup.open()


# ---------------------------------------------------------------------------
# 右侧面板 - 日志 (Right Panel)
# ---------------------------------------------------------------------------
class RightPanel(BoxLayout):
    """右栏 - 判定日志"""

    def __init__(self, app, **kwargs):
        import traceback
        print("[SIGNALIS] RightPanel.__init__ start")
        try:
            super().__init__(**kwargs)
            self.app = app
            self.orientation = "vertical"
            self.padding = dp(5)
            self.spacing = dp(5)
            self._build_ui()
            print("[SIGNALIS] RightPanel.__init__ done")
        except Exception as e:
            print(f"[SIGNALIS] CRASH in RightPanel.__init__: {e}")
            print(f"[SIGNALIS] TRACEBACK: {traceback.format_exc()}")
            raise

    def _build_ui(self):
        self.add_widget(make_label("判定日志 v2", font_size=18, color=ACCENT_COLOR, bold=True,
                                   size_hint_y=None, height=dp(35)))

        log_scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
        self.log_label = Label(
            text="暂无判定记录", font_size=sp(11),
            color=TEXT_COLOR, size_hint_y=None, markup=True,
            font_name=_font()
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        log_scroll.add_widget(self.log_label)
        self.add_widget(log_scroll)

        btn_box = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
        btn_box.add_widget(make_button("刷新", self._refresh, font_size=sp(11)))
        btn_box.add_widget(make_button("清除", self._clear, font_size=sp(11)))
        btn_box.add_widget(make_button("导出", self._export, font_size=sp(11)))
        self.add_widget(btn_box)

    def add_entry(self, text):
        current = self.log_label.text
        if current == "暂无判定记录":
            self.log_label.text = text
        else:
            self.log_label.text = current + "\n\n" + text
        Clock.schedule_once(self._scroll_to_bottom, 0.1)

    def _scroll_to_bottom(self, dt):
        pass  # ScrollView auto-scrolls with Label height binding

    def _refresh(self, instance):
        logs = self.app.engine.get_logs()
        if logs:
            self.log_label.text = "\n\n".join(logs)
        else:
            self.log_label.text = "暂无判定记录"

    def _clear(self, instance):
        self.app.engine.clear_logs()
        self.log_label.text = "暂无判定记录"

    def _export(self, instance):
        try:
            path = self.app.data_manager.export_log(self.app.engine.get_logs())
            self.app.add_log(f"日志已导出到: {path}")
            self._show_info("成功", f"日志已导出到:\n{path}")
        except Exception as e:
            self._show_info("错误", f"导出失败: {str(e)}")

    def _show_info(self, title, message):
        popup = InfoPopup(title, message)
        popup.open()


# ---------------------------------------------------------------------------
# 主布局 (Main Layout)
# ---------------------------------------------------------------------------
class MainLayout(BoxLayout):
    """主布局 - 响应式三栏/单栏布局"""

    def __init__(self, app, **kwargs):
        import traceback
        print("[SIGNALIS] MainLayout.__init__ start")
        try:
            super().__init__(**kwargs)
            self.app = app

            # 检测屏幕方向，手机纵向时改为垂直堆叠
            from kivy.core.window import Window
            from kivy.utils import platform
            is_android = platform == 'android' if hasattr(platform, '__call__') else False
            is_portrait = Window.height > Window.width

            if is_android and is_portrait:
                # 手机纵向：垂直堆叠，每栏可滚动
                self.orientation = "vertical"
                self.spacing = dp(4)
                self.padding = dp(4)
                # 左栏 (角色管理) - 可滚动
                print("[SIGNALIS] Portrait mode: vertical stack")
                left_scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
                self.left_panel = LeftPanel(app, size_hint=(1, None))
                self.left_panel.bind(minimum_height=self.left_panel.setter('height'))
                left_scroll.add_widget(self.left_panel)
                self.add_widget(left_scroll)
                # 中栏 (判定面板) - 可滚动
                center_scroll = ScrollView(do_scroll_x=False, scroll_type=['content'])
                self.center_panel = CenterPanel(app, size_hint=(1, None))
                self.center_panel.bind(minimum_height=self.center_panel.setter('height'))
                center_scroll.add_widget(self.center_panel)
                self.add_widget(center_scroll)
                # 右栏 (日志面板) - 固定高度
                self.right_panel = RightPanel(app, size_hint=(1, 0.25))
                self.add_widget(self.right_panel)
            else:
                # 横屏/平板：横向三栏
                self.orientation = "horizontal"
                self.spacing = dp(3)
                try:
                    if is_android:
                        self.padding = dp(4)
                        print("[SIGNALIS] Android padding set")
                    else:
                        self.padding = dp(3)
                except Exception:
                    self.padding = dp(3)
                # 左栏 - 角色管理 (25%)
                print("[SIGNALIS] Building LeftPanel...")
                self.left_panel = LeftPanel(app, size_hint=(0.25, 1))
                self.add_widget(self.left_panel)
                print("[SIGNALIS] LeftPanel added")
                # 中栏 - 判定面板 (50%)
                print("[SIGNALIS] Building CenterPanel...")
                self.center_panel = CenterPanel(app, size_hint=(0.50, 1))
                self.add_widget(self.center_panel)
                print("[SIGNALIS] CenterPanel added")
                # 右栏 - 日志面板 (25%)
                print("[SIGNALIS] Building RightPanel...")
                self.right_panel = RightPanel(app, size_hint=(0.25, 1))
                self.add_widget(self.right_panel)
                print("[SIGNALIS] RightPanel added")
        except Exception as e:
            print(f"[SIGNALIS] CRASH in MainLayout.__init__: {e}")
            print(f"[SIGNALIS] TRACEBACK: {traceback.format_exc()}")
            raise

    def on_size(self, *args):
        """屏幕旋转时重新调整布局"""
        from kivy.core.window import Window
        is_portrait = Window.height > Window.width
        if is_portrait and self.orientation != 'vertical':
            self.orientation = 'vertical'
        elif not is_portrait and self.orientation != 'horizontal':
            self.orientation = 'horizontal'


# ---------------------------------------------------------------------------
# 主应用 (Main App)
# ---------------------------------------------------------------------------
class SignalisApp(App):
    """SIGNALIS TRPG Adjudicator Kivy App"""

    def build(self):
        import traceback
        import os
        print("[SIGNALIS] build() started")

        # ===== 禁用 Android 多指触摸，确保单指滑动正常工作 =====
        try:
            from kivy.config import Config
            Config.set('input', 'mouse', 'mouse,disable_multitouch_on_android')
            print("[SIGNALIS] Multitouch disabled for Android")
        except Exception as e:
            print(f"[SIGNALIS] Config set err: {e}")

        # ===== 加载中文字体 =====
        global _CHINESE_FONT, _FONT_REGISTERED
        try:
            from kivy.core.text import LabelBase
            
            # 1. 优先使用内置字体（打包到 APK 中）
            app_dir = os.path.dirname(os.path.abspath(__file__))
            bundled_fonts = [
                os.path.join(app_dir, 'fonts', 'NotoSansCJK-Regular.ttc'),
                os.path.join(app_dir, 'fonts', 'NotoSansSC-Regular.otf'),
                os.path.join(app_dir, 'fonts', 'NotoSansSC-Regular.ttf'),
            ]
            
            # 2. 系统字体回退列表（优先 .ttc / .otf，最后 Roboto）
            system_fonts = [
                "/system/fonts/NotoSansCJK-Regular.ttc",
                "/system/fonts/NotoSansCJKsc-Regular.ttc",
                "/system/fonts/NotoSansSC-Regular.ttf",
                "/system/fonts/NotoSansSC-Bold.ttf",
                "/system/fonts/NotoSansSC-VF.ttf",
                "/system/fonts/MiSans.ttf",
                "/system/fonts/MiSans-Regular.ttf",
                "/system/fonts/MiSans-Medium.ttf",
                "/system/fonts/DroidSansFallback.ttf",
                "/system/fonts/DroidSansFallbackFull.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/Roboto-Regular.ttf",
            ]
            
            font_path = None
            # 尝试内置字体
            for fpath in bundled_fonts:
                if fpath and os.path.exists(fpath):
                    font_path = fpath
                    print(f"[SIGNALIS] Using bundled font: {font_path}")
                    break
            
            # 尝试系统字体
            if not font_path:
                for fpath in system_fonts:
                    if os.path.exists(fpath):
                        font_path = fpath
                        print(f"[SIGNALIS] Using system font: {font_path}")
                        break
            
            if font_path:
                try:
                    LabelBase.register('chinese', font_path)
                    _CHINESE_FONT = font_path
                    _FONT_REGISTERED = True
                    print(f"[SIGNALIS] Font registered: {font_path}")
                except Exception as e2:
                    print(f"[SIGNALIS] Font register err: {e2}")
                    _FONT_REGISTERED = False
            else:
                print("[SIGNALIS] No CJK font found, fallback to Roboto")
        except Exception as e:
            print(f"[SIGNALIS] Font init err: {e}")

        try:
            Window.clearcolor = BG_COLOR[:3]

            # 横屏
            try:
                from kivy.utils import platform
                if platform == "android":
                    from jnius import autoclass
                    autoclass("org.kivy.android.PythonActivity").setRequestedOrientation(0)
            except:
                pass

            self.engine = AdjudicatorEngine()
            self.data_manager = DataManager()
            self.current_attacker = None
            self.current_defender = None

            self.main_layout = MainLayout(self)
            self.left_panel = self.main_layout.left_panel
            self.center_panel = self.main_layout.center_panel
            self.right_panel = self.main_layout.right_panel

            self._load_defaults()
            print("[SIGNALIS] build() OK")
            return self.main_layout

        except Exception as e:
            print(f"[SIGNALIS] CRASH: {e}")
            print(f"[SIGNALIS] TRACE: {traceback.format_exc()}")
            from kivy.uix.label import Label
            return Label(text=f'错误:\n{e}', font_name=_font())


    def add_log(self, text):
        """添加日志条目"""
        self.right_panel.add_entry(text)

    def _load_defaults(self):
        """加载默认角色和敌人"""
        for template in DEFAULT_CHARACTER_TEMPLATES[:3]:
            char = Character.from_dict(template)
            char.max_hp = char.calculate_hp()
            char.current_hp = char.max_hp
            self.left_panel.add_character(char)

        for template in DEFAULT_ENEMY_TEMPLATES[:3]:
            enemy = Enemy.from_template(template)
            self.left_panel.add_enemy(enemy)

    def on_pause(self):
        return True

    def on_resume(self):
        pass


# =============================================================================
# 5. 入口点 (Entry Point)
# =============================================================================
if __name__ == "__main__":
    SignalisApp().run()
