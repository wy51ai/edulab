#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — 把反应 spec 经 reaction_kernel 计算后注入 template/reaction.html，产出单页交互网页。

数据由 lib/reaction_kernel.py 驱动（单一数据源）：配平、原子守恒、键的断/成、坐标与方程一致。
每个 build_* 返回一个“作者 spec”，assemble_data 负责校验与装配。

依赖 sympy。用能 import sympy 的解释器运行（本机：/opt/homebrew/bin/python3.11）：
    python3 scripts/generate.py <反应key> [输出.html]
    python3 scripts/generate.py list
    python3 scripts/generate.py all <输出目录>
"""

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "template" / "reaction.html"
PLACEHOLDER = "__REACTION_DATA__"

sys.path.insert(0, str(SKILL_DIR / "lib"))
import reaction_kernel as K          # noqa: E402


def render_html(data: dict, out_path: Path) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"模板中未找到占位符 {PLACEHOLDER}")
    out_path.write_text(template.replace(PLACEHOLDER, json.dumps(data, ensure_ascii=False)),
                        encoding="utf-8")
    return out_path


def _p(html):
    return f"<p>{html}</p>"


# =====================================================================
# 1) 甲烷燃烧（初中·morph·火焰·放热）—— 旗舰范例
# =====================================================================
def build_combustion_ch4():
    return {
        "meta": {"title": "甲烷的燃烧", "subtitle": "CH₄ + O₂ 的氧化放热燃烧反应机理",
                 "language": "zh-CN", "category": "junior", "accent": "amber", "engine": "morph"},
        "conditions": {"text": "点燃", "exothermic": True, "flame": True},
        "reactants": [{"species": "CH4", "count": 1, "pos": [-4.0, 0.2, 0]},
                      {"species": "O2", "count": 2}],   # 两个 O2 实例（O2#1 给 CO2，O2#2 给水）
        "products": [{"species": "CO2", "count": 1, "pos": [-2.7, 1.1, 0]},
                     {"species": "H2O", "count": 2}],
        "atom_map": [
            ["CH4#1.C", "CO2#1.Y"],
            ["O2#1.Oa", "CO2#1.Xa"], ["O2#1.Ob", "CO2#1.Xb"],
            ["O2#2.Oa", "H2O#1.A"], ["O2#2.Ob", "H2O#2.A"],
            ["CH4#1.H1", "H2O#1.Ha"], ["CH4#1.H2", "H2O#1.Hb"],
            ["CH4#1.H3", "H2O#2.Ha"], ["CH4#1.H4", "H2O#2.Hb"],
        ],
        "energy": {"activation": 0.5, "deltaH": -0.75, "reactantLabel": "CH₄+O₂", "productLabel": "CO₂+H₂O"},
        "steps": [
            {"title": "反应物混合",
             "html": "<span class='text-slate-200 font-semibold'>甲烷 (CH₄)</span> 与 "
                     "<span class='text-red-400 font-semibold'>氧气 (O₂)</span> 分子混合靠近。"
                     "此时 C–H 键与 O=O 键都很稳定，常温下不自发反应，需<span class='text-amber-400 font-semibold'>点燃提供活化能</span>。"},
            {"title": "点燃燃烧",
             "html": "达到着火点后，<span class='border-b border-dashed border-amber-500'>C–H 键与 O=O 键剧烈断裂</span>，"
                     "原子被打散并重新组合。这是剧烈的<span class='text-amber-400 font-semibold'>氧化放热反应</span>，"
                     "瞬间释放大量热与光，即火焰。"},
            {"title": "生成产物",
             "html": "原子重组生成 <span class='text-slate-200 font-semibold'>二氧化碳 (CO₂)</span> 与 "
                     "<span class='text-blue-300 font-semibold'>水 (H₂O)</span>。"
                     "注意反应前后原子种类与数目守恒（1C、4H、4O），质量守恒。"},
        ],
    }


# =====================================================================
# 2) 氢气燃烧（初中·morph·火焰）
# =====================================================================
def build_combustion_h2():
    return {
        "meta": {"title": "氢气的燃烧", "subtitle": "2H₂ + O₂ 点燃生成水",
                 "language": "zh-CN", "category": "junior", "accent": "sky", "engine": "morph"},
        "conditions": {"text": "点燃", "exothermic": True, "flame": True},
        "reactants": [{"species": "H2", "count": 2}, {"species": "O2", "count": 1}],
        "products": [{"species": "H2O", "count": 2}],
        "atom_map": [
            ["O2#1.Oa", "H2O#1.A"], ["O2#1.Ob", "H2O#2.A"],
            ["H2#1.Ha", "H2O#1.Ha"], ["H2#1.Hb", "H2O#1.Hb"],
            ["H2#2.Ha", "H2O#2.Ha"], ["H2#2.Hb", "H2O#2.Hb"],
        ],
        "energy": {"activation": 0.45, "deltaH": -0.7, "reactantLabel": "H₂+O₂", "productLabel": "H₂O"},
        "steps": [
            {"title": "反应物混合",
             "html": "两个 <span class='text-sky-300 font-semibold'>氢分子 (H₂)</span> 与一个 "
                     "<span class='text-red-400 font-semibold'>氧分子 (O₂)</span> 靠近。"},
            {"title": "点燃反应",
             "html": "点燃后 <span class='border-b border-dashed border-sky-400'>H–H 键与 O=O 键断裂</span>，"
                     "原子重新组合，放出大量热（氢气是清洁燃料）。"},
            {"title": "生成水",
             "html": "每个氧原子结合两个氢原子，生成两分子 <span class='text-blue-300 font-semibold'>水 (H₂O)</span>。"
                     "原子守恒：4H、2O。"},
        ],
    }


# =====================================================================
# 3) 电解水（初中·morph·分解·吸热/通电）
# =====================================================================
def build_electrolysis_water():
    return {
        "meta": {"title": "电解水", "subtitle": "通电使水分解为氢气和氧气",
                 "language": "zh-CN", "category": "junior", "accent": "cyan", "engine": "morph"},
        "conditions": {"text": "通电", "under": "电解"},
        "reactants": [{"species": "H2O", "count": 2}],
        "products": [{"species": "H2", "count": 2}, {"species": "O2", "count": 1}],
        "atom_map": [
            ["H2O#1.A", "O2#1.Oa"], ["H2O#2.A", "O2#1.Ob"],
            ["H2O#1.Ha", "H2#1.Ha"], ["H2O#1.Hb", "H2#1.Hb"],
            ["H2O#2.Ha", "H2#2.Ha"], ["H2O#2.Hb", "H2#2.Hb"],
        ],
        "energy": {"activation": 0.35, "deltaH": 0.55, "reactantLabel": "H₂O", "productLabel": "H₂+O₂"},
        "steps": [
            {"title": "通电前",
             "html": "两个 <span class='text-cyan-300 font-semibold'>水分子 (H₂O)</span> 静置，"
                     "O–H 键稳定，需要<span class='text-cyan-400 font-semibold'>持续通入电能</span>才能分解。"},
            {"title": "通电分解",
             "html": "接通直流电，<span class='border-b border-dashed border-cyan-400'>O–H 键断裂</span>，"
                     "氢、氧原子分别向两极迁移并重新组合。这是<span class='text-cyan-400 font-semibold'>吸热</span>的分解反应。"},
            {"title": "生成气体",
             "html": "氢原子两两结合成 <span class='text-sky-300 font-semibold'>氢气 (H₂)</span>（负极），"
                     "氧原子结合成 <span class='text-red-400 font-semibold'>氧气 (O₂)</span>（正极），体积比约 2:1。原子守恒：4H、2O。"},
        ],
    }


# =====================================================================
# 4) 钠在氯气中燃烧（高中无机·morph·氧化还原·电子转移）
# =====================================================================
def build_redox_na_cl2():
    return {
        "meta": {"title": "钠与氯气", "subtitle": "2Na + Cl₂ —— 电子转移的氧化还原反应",
                 "language": "zh-CN", "category": "inorganic", "accent": "violet", "engine": "morph"},
        "conditions": {"text": "点燃", "exothermic": True, "transitionGlow": True},
        "reactants": [{"species": "Na", "count": 2}, {"species": "Cl2", "count": 1}],
        "products": [{"species": "NaCl", "count": 2}],
        "atom_map": [
            ["Na#1.X", "NaCl#1.Na"], ["Na#2.X", "NaCl#2.Na"],
            ["Cl2#1.Cla", "NaCl#1.Cl"], ["Cl2#1.Clb", "NaCl#2.Cl"],
        ],
        # 电子转移：每个 Na 失去 1 个电子给对应的 Cl（全局 id 由 atom_map 顺序决定）
        "electrons": [
            {"from": "Na1", "to": "Cl1", "count": 1, "label": "e⁻"},
            {"from": "Na2", "to": "Cl2", "count": 1, "label": "e⁻"},
        ],
        "energy": {"activation": 0.4, "deltaH": -0.8, "reactantLabel": "Na+Cl₂", "productLabel": "NaCl"},
        "steps": [
            {"title": "反应物",
             "html": "<span class='text-violet-300 font-semibold'>钠原子 (Na)</span> 最外层有 1 个电子，"
                     "<span class='text-green-400 font-semibold'>氯分子 (Cl₂)</span> 每个氯原子最外层有 7 个电子，都趋向 8 电子稳定结构。"},
            {"title": "电子转移",
             "html": "点燃后 <span class='border-b border-dashed border-green-400'>Cl–Cl 键断裂</span>，"
                     "每个钠原子把 1 个 <span class='text-cyan-300 font-semibold'>电子 (e⁻)</span> 转移给氯原子："
                     "钠被<span class='text-amber-400 font-semibold'>氧化</span>为 Na⁺，氯被<span class='text-sky-400 font-semibold'>还原</span>为 Cl⁻。"},
            {"title": "生成离子化合物",
             "html": "Na⁺ 与 Cl⁻ 靠静电作用（离子键）形成 <span class='text-violet-300 font-semibold'>氯化钠 (NaCl)</span>。"
                     "化合价：Na 0→+1、Cl 0→−1，得失电子守恒，原子守恒：2Na、2Cl。"},
        ],
    }


# =====================================================================
# 5) 酯化反应（高中有机·mechanism·催化剂·过渡态）—— 复刻 3d.html，但数据驱动
# =====================================================================
_EST_FRAGS = {
    "acetyl":    {"K0": {"pos": [-4.5, 0.5, 0], "rot": [0, 0, 0]},
                  "K1": {"pos": [-0.7, 0.1, 0], "rot": [0, 0, 0]},
                  "K2": {"pos": [-2.5, 1.2, 0], "rot": [0, 0, -0.1]}},
    "leavingOH": {"K0": {"pos": [-3.5, -0.1, 0.2], "rot": [0, 0, 0]},
                  "K1": {"pos": [0.5, -0.5, -0.3], "rot": [0, 0, -0.2]},
                  "K2": {"pos": [3.2, -1.5, -0.5], "rot": [0.2, 0.3, 0.5]}},
    "ethoxy":    {"K0": {"pos": [4.5, -0.5, 0], "rot": [0, 0, 0]},
                  "K1": {"pos": [0.6, 0.2, 0.15], "rot": [0, 0, 0]},
                  "K2": {"pos": [-1.38, 1.05, 0], "rot": [0, 0, 0]}},
    "leavingH":  {"K0": {"pos": [3.9, -1.1, 0], "rot": [0, 0, 0]},
                  "K1": {"pos": [1.1, -1.3, -0.3], "rot": [0, 0, 0]},
                  "K2": {"pos": [3.9, -2.0, -0.5], "rot": [0, 0, 0]}},
    "catalyst":  {"catalyst": True,
                  "K0": {"pos": [-4.5, 2.5, 0.5], "rot": [0, 0, 0]},
                  "K1": {"pos": [-0.5, -1.0, -0.3], "rot": [0, 0, 0]},
                  "K2": {"pos": [5.0, 1.0, 1.0], "rot": [0, 0, 0]}},
}
# id, el, frag, 片段内局部坐标（取自 3d.html）
_EST_ATOMS = [
    ("C1", "C", "acetyl", [0, 0.2, 0]), ("O1", "O", "acetyl", [0, 1.25, 0]),
    ("C2", "C", "acetyl", [-1.2, -0.5, 0]), ("H1", "H", "acetyl", [-1.2, -1.2, 0.8]),
    ("H2", "H", "acetyl", [-1.2, -1.2, -0.8]), ("H3", "H", "acetyl", [-2.0, -0.1, 0]),
    ("O2", "O", "leavingOH", [0, 0, 0]), ("H4", "H", "leavingOH", [0.7, -0.5, 0.1]),
    ("O3", "O", "ethoxy", [0, 0, 0]), ("C3", "C", "ethoxy", [1.1, 0.4, 0]),
    ("H5", "H", "ethoxy", [1.1, 1.0, 0.8]), ("H6", "H", "ethoxy", [1.1, 1.0, -0.8]),
    ("C4", "C", "ethoxy", [2.3, -0.3, 0]), ("H7", "H", "ethoxy", [2.3, -0.9, 0.8]),
    ("H8", "H", "ethoxy", [2.3, -0.9, -0.8]), ("H9", "H", "ethoxy", [3.0, 0.3, 0]),
    ("H10", "H", "leavingH", [0, 0, 0]),
    ("Hp", "H", "catalyst", [0, 0, 0]),
]
# 反应物态成键（乙酸 + 乙醇）
_EST_BEFORE = [
    ("C1", "O1", 2), ("C1", "C2", 1), ("C2", "H1", 1), ("C2", "H2", 1), ("C2", "H3", 1),
    ("C1", "O2", 1), ("O2", "H4", 1),
    ("O3", "C3", 1), ("C3", "H5", 1), ("C3", "H6", 1), ("C3", "C4", 1),
    ("C4", "H7", 1), ("C4", "H8", 1), ("C4", "H9", 1), ("O3", "H10", 1),
]
# 产物态成键（乙酸乙酯 + 水）
_EST_AFTER = [
    ("C1", "O1", 2), ("C1", "C2", 1), ("C2", "H1", 1), ("C2", "H2", 1), ("C2", "H3", 1),
    ("C1", "O3", 1), ("O3", "C3", 1), ("C3", "H5", 1), ("C3", "H6", 1), ("C3", "C4", 1),
    ("C4", "H7", 1), ("C4", "H8", 1), ("C4", "H9", 1),
    ("O2", "H4", 1), ("O2", "H10", 1),
]
_EST_RMOL = {"acetyl": "乙酸#1", "leavingOH": "乙酸#1", "ethoxy": "乙醇#1", "leavingH": "乙醇#1", "catalyst": "H+"}
_EST_PMOL = {"acetyl": "乙酸乙酯#1", "ethoxy": "乙酸乙酯#1", "leavingOH": "水#1", "leavingH": "水#1", "catalyst": "H+"}


def build_esterification():
    atoms = []
    for aid, el, frag, flocal in _EST_ATOMS:
        f = _EST_FRAGS[frag]
        atoms.append({
            "id": aid, "el": el, "frag": frag, "flocal": flocal,
            "start": K._apply(flocal, f["K0"]["pos"], f["K0"]["rot"]),
            "end": K._apply(flocal, f["K2"]["pos"], f["K2"]["rot"]),
            "rmol": _EST_RMOL[frag], "pmol": _EST_PMOL[frag],
        })
    fragments = [dict(v, id=k) for k, v in _EST_FRAGS.items()]
    # 浮动标签（显式提供）
    acetyl_eth = ["C1", "O1", "C2", "H1", "H2", "H3", "O3", "C3", "H5", "H6", "C4", "H7", "H8", "H9"]
    labels = [
        {"id": "r-acid", "text": "乙酸 (CH₃COOH)", "color": "red", "phase": "reactant",
         "atoms": ["C1", "O1", "C2", "H1", "H2", "H3", "O2", "H4"]},
        {"id": "r-ethanol", "text": "乙醇 (C₂H₅OH)", "color": "blue", "phase": "reactant",
         "atoms": ["O3", "C3", "H5", "H6", "C4", "H7", "H8", "H9", "H10"]},
        {"id": "p-ester", "text": "乙酸乙酯 (CH₃COOC₂H₅)", "color": "emerald", "phase": "product",
         "atoms": acetyl_eth},
        {"id": "p-water", "text": "水 (H₂O)", "color": "cyan", "phase": "product",
         "atoms": ["O2", "H4", "H10"]},
    ]
    return {
        "meta": {"title": "酯化反应", "subtitle": "乙酸 + 乙醇 的费歇尔酯化反应机理",
                 "language": "zh-CN", "category": "organic", "accent": "indigo", "engine": "mechanism",
                 "equation": r"\text{CH}_3\text{COOH} + \text{C}_2\text{H}_5\text{OH} "
                             r"\underset{\Delta}{\overset{\text{浓硫酸}}{\rightleftharpoons}} "
                             r"\text{CH}_3\text{COOC}_2\text{H}_5 + \text{H}_2\text{O}"},
        "conditions": {"text": "催化、加热", "reversible": True, "transitionGlow": True,
                       "catalyst": {"label": "浓硫酸催化剂 (H⁺)", "formula": "H^+"}},
        "reactants": [{"species": "乙酸"}, {"species": "乙醇"}],
        "products": [{"species": "乙酸乙酯"}, {"species": "水"}],
        "atoms": atoms,
        "bonds_before": [{"a": a, "b": b, "order": o} for a, b, o in _EST_BEFORE],
        "bonds_after": [{"a": a, "b": b, "order": o} for a, b, o in _EST_AFTER],
        "fragments": fragments,
        "labels": labels,
        "energy": {"activation": 0.62, "deltaH": -0.12, "reactantLabel": "酸+醇", "productLabel": "酯+水"},
        "steps": [
            {"title": "反应物准备",
             "html": "<span class='text-red-400 font-semibold'>乙酸 (CH₃COOH)</span> 与 "
                     "<span class='text-blue-400 font-semibold'>乙醇 (C₂H₅OH)</span> 在浓硫酸催化下靠近。"
                     "游离 <span class='text-cyan-400 font-semibold'>质子 (H⁺)</span> 先质子化羰基氧，使羰基碳更易被进攻。"},
            {"title": "碰撞与过渡态",
             "html": "乙醇羟基氧进攻羰基碳，临界瞬间虚线键同时断生："
                     "<span class='border-b border-dashed border-amber-500'>酸 C–OH 键、醇 O–H 键断裂</span>，"
                     "<span class='border-b border-dashed border-emerald-500'>新 C–O 酯键与 H₂O 形成</span>。能量最高的过渡态。"},
            {"title": "产物生成与分离",
             "html": "脱去一分子 <span class='text-cyan-400 font-semibold'>水 (H₂O)</span>，"
                     "生成有香味的 <span class='text-emerald-400 font-semibold'>乙酸乙酯 (CH₃COOC₂H₅)</span>。"
                     "<span class='text-indigo-300 font-semibold'>催化剂 H⁺</span> 再生，实现“酸脱羟基醇脱氢”。"},
        ],
    }


# =====================================================================
# 6) 葡萄糖有氧氧化（细胞呼吸·morph·36原子·暗色·火焰·放热）—— 最复杂示例
# =====================================================================
def build_glucose_combustion():
    return {
        "meta": {
            "title": "葡萄糖的有氧氧化",
            "subtitle": "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O（细胞呼吸核心反应）",
            "language": "zh-CN",
            "category": "inorganic",
            "accent": "amber",
            "engine": "morph",
        },
        "conditions": {"text": "酶催化", "exothermic": True, "flame": True},
        "reactants": [
            {"species": "Glucose", "count": 1},
            {"species": "O2", "count": 6},
        ],
        "products": [
            {"species": "CO2", "count": 6},
            {"species": "H2O", "count": 6},
        ],
        "atom_map": [
            # 6 个碳原子 → 6 个 CO₂ 的中心碳
            ["Glucose#1.C1", "CO2#1.Y"], ["Glucose#1.C2", "CO2#2.Y"],
            ["Glucose#1.C3", "CO2#3.Y"], ["Glucose#1.C4", "CO2#4.Y"],
            ["Glucose#1.C5", "CO2#5.Y"], ["Glucose#1.C6", "CO2#6.Y"],
            # 葡萄糖 6 个 O → 6 个 H₂O 的氧
            ["Glucose#1.O1", "H2O#1.A"], ["Glucose#1.O2", "H2O#2.A"],
            ["Glucose#1.O3", "H2O#3.A"], ["Glucose#1.O4", "H2O#4.A"],
            ["Glucose#1.O5", "H2O#5.A"], ["Glucose#1.O6", "H2O#6.A"],
            # 葡萄糖 12 个 H → 6 个 H₂O 各 2 个 H
            ["Glucose#1.H1",  "H2O#1.Ha"], ["Glucose#1.HO2", "H2O#1.Hb"],
            ["Glucose#1.H2",  "H2O#2.Ha"], ["Glucose#1.HO3", "H2O#2.Hb"],
            ["Glucose#1.H3",  "H2O#3.Ha"], ["Glucose#1.HO4", "H2O#3.Hb"],
            ["Glucose#1.H4",  "H2O#4.Ha"], ["Glucose#1.HO5", "H2O#4.Hb"],
            ["Glucose#1.H5",  "H2O#5.Ha"], ["Glucose#1.HO6", "H2O#5.Hb"],
            ["Glucose#1.H6a", "H2O#6.Ha"], ["Glucose#1.H6b", "H2O#6.Hb"],
            # 6 个 O₂（12 个 O）→ 6 个 CO₂ 的两端氧
            ["O2#1.Oa", "CO2#1.Xa"], ["O2#1.Ob", "CO2#1.Xb"],
            ["O2#2.Oa", "CO2#2.Xa"], ["O2#2.Ob", "CO2#2.Xb"],
            ["O2#3.Oa", "CO2#3.Xa"], ["O2#3.Ob", "CO2#3.Xb"],
            ["O2#4.Oa", "CO2#4.Xa"], ["O2#4.Ob", "CO2#4.Xb"],
            ["O2#5.Oa", "CO2#5.Xa"], ["O2#5.Ob", "CO2#5.Xb"],
            ["O2#6.Oa", "CO2#6.Xa"], ["O2#6.Ob", "CO2#6.Xb"],
        ],
        "energy": {
            "activation": 0.25,
            "deltaH": -0.95,
            "reactantLabel": "C₆H₁₂O₆+O₂",
            "productLabel": "CO₂+H₂O",
        },
        "steps": [
            {
                "title": "反应物：葡萄糖与 6 个氧分子",
                "html": (
                    "<span class='text-amber-300 font-semibold'>葡萄糖 (C₆H₁₂O₆)</span> 是 6 碳醛糖，"
                    "含 1 个醛基（C₁=O）、5 个羟基（C–OH）和 5 根 C–C 骨架键，共 24 个原子。"
                    "<span class='text-red-400 font-semibold'>6 个 O₂</span> 提供 12 个氧原子。"
                    "这是生命<span class='text-amber-400'>细胞呼吸</span>的核心放热反应，释放 △G ≈ −2803 kJ/mol。"
                ),
            },
            {
                "title": "碳骨架逐步断裂·键全面重组",
                "html": (
                    "在细胞酶系（糖酵解→丙酮酸脱氢→三羧酸循环）的催化下，"
                    "C–C 链与 C–H 键<span class='border-b border-dashed border-red-400'>逐步断裂</span>，"
                    "O=O 键同步裂开；碳原子逐一氧化。共断裂 <span class='text-red-400 font-semibold'>17+ 根旧键</span>，"
                    "同时形成 <span class='text-green-400 font-semibold'>18 根新键</span>（12 根 C=O 和 12 根 O–H）。"
                ),
            },
            {
                "title": "生成 6CO₂ + 6H₂O · 原子守恒",
                "html": (
                    "6 个碳原子各与 2 个来自 O₂ 的氧原子结合，生成"
                    "<span class='text-slate-200 font-semibold'> 6 分子 CO₂</span>（线形，两个 C=O）；"
                    "12 个氢原子与葡萄糖内的 6 个氧原子结合，生成"
                    "<span class='text-cyan-300 font-semibold'> 6 分子 H₂O</span>（弯曲形）。"
                    "原子守恒：反应前后各 6C · 12H · 18O，质量守恒。"
                ),
            },
        ],
    }


REGISTRY = {
    "combustion_ch4": build_combustion_ch4,
    "combustion_h2": build_combustion_h2,
    "electrolysis_water": build_electrolysis_water,
    "redox_na_cl2": build_redox_na_cl2,
    "esterification": build_esterification,
    "glucose_combustion": build_glucose_combustion,
}


def main(argv):
    if not argv or argv[0] == "list":
        print("已注册反应:")
        for k in REGISTRY:
            print("  -", k)
        return
    if argv[0] == "random":
        import random
        seed = int(argv[1]) if len(argv) > 1 else 0
        out = Path(argv[2]) if len(argv) > 2 else (SKILL_DIR / "output" / "random.html")
        key = random.Random(seed).choice(list(REGISTRY))
        render_html(K.assemble_data(REGISTRY[key]()), out)
        print(f"written: {out}  (seed={seed} -> {key})")
        return
    if argv[0] == "all":
        out_dir = Path(argv[1]) if len(argv) > 1 else (SKILL_DIR / "output")
        out_dir.mkdir(parents=True, exist_ok=True)
        for k in REGISTRY:
            render_html(K.assemble_data(REGISTRY[k]()), out_dir / f"{k}.html")
            print("written:", out_dir / f"{k}.html")
        return
    key = argv[0]
    if key not in REGISTRY:
        print(f"未知反应 {key}；可用: {', '.join(REGISTRY)}")
        sys.exit(1)
    out = Path(argv[1]) if len(argv) > 1 else (SKILL_DIR / "output" / f"{key}.html")
    render_html(K.assemble_data(REGISTRY[key]()), out)
    print("written:", out)


if __name__ == "__main__":
    main(sys.argv[1:])
