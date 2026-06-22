# reaction spec 与 data 数据格式

`build_*` 写一个 **reaction spec**，`reaction_kernel.assemble_data(spec)` 校验并装配成注入模板的
**data**。两种作者级别都汇流到同一份 data。

---

## 一、meta（必填）
```jsonc
"meta": {
  "title": "甲烷的燃烧",              // 标题
  "subtitle": "CH₄ + O₂ 的氧化放热…",  // 副标题（accent 色）
  "language": "zh-CN",               // "zh-CN" | "en"，决定 UI 文案与图例语言
  "category": "junior",              // junior(初中) | inorganic(高中无机) | organic(有机机理)
  "accent": "amber",                 // 强调色：amber/indigo/emerald/sky/violet/cyan/red/green/orange...
  "engine": "morph",                 // auto | morph | mechanism（auto：organic 或带 fragments → mechanism）
  "equation": "..."                  // 可选；不填则由配平自动生成 LaTeX（机理路径建议显式给）
}
```

## 二、conditions（反应条件 + 叠加层开关）
```jsonc
"conditions": {
  "text": "点燃",            // 箭头上方条件文字（点燃/通电/催化…）
  "under": "电解",           // 可选，箭头下方文字
  "reversible": true,        // 可逆反应 ⇌
  "exothermic": true,        // 放热（语义标注）
  "flame": true,             // 显示火焰叠加层（燃烧/强放热）
  "transitionGlow": true,    // 过渡态能量光（黄）
  "catalyst": { "label": "浓硫酸 (H⁺)", "formula": "H^+" }  // 显示催化剂开关；机理里催化剂为 fragment
}
```

## 三、A. 高层路径（species + atom_map）—— 推荐用于“原子打散重组”反应
```jsonc
"reactants": [ {"species":"CH4","count":1,"pos":[-4,0.2,0]}, {"species":"O2","count":2} ],
"products":  [ {"species":"CO2","count":1,"pos":[-2.7,1.1,0]}, {"species":"H2O","count":2} ],
// pos 可省略 → 自动居中布局；rot 可选（弧度，[rx,ry,rz]）
"atom_map": [
  ["CH4#1.C",  "CO2#1.Y"],          // 反应物原子引用 ↔ 产物原子引用（同一个原子的去向）
  ["O2#1.Oa",  "CO2#1.Xa"], ...
]
```
- **实例引用**：`SPECIES#k.slot`。同物种多份按出现顺序编号 `#1 #2`（如两个 O2 → `O2#1 O2#2`）。
- **atom_map 必须是反应物原子↔产物原子的双射**：每个反应物原子、每个产物原子各出现且仅出现一次，
  且配对两端元素相同。kernel 会严格校验并报错。
- **全局原子 id** 由 atom_map 顺序生成：元素 + 计数（`C1 H1 H2 … O1 …`）。
  叠加层（如 `electrons`）若要引用原子，用这些 id（顺序确定，可预知）。

### 各物种的 slot 名（atom_map 里用）
| 物种 | slot |
|---|---|
| 双原子 `H2 O2 N2 Cl2` | `Ha,Hb` / `Oa,Ob` / `Na,Nb` / `Cla,Clb` |
| `CO` | `C,O` |
| 线形 `CO2` | `Y`(中心C), `Xa,Xb`(两端O) |
| 弯曲 `H2O` | `A`(O), `Ha,Hb` |
| 四面体 `CH4` | `C, H1,H2,H3,H4` |
| 三角锥 `NH3` | `A`(N), `H1,H2,H3` |
| 单原子 `Na C Fe Mg` | `X` |
| 离子对 `NaCl` | `Na, Cl` |

（新物种在 `lib/molecules.py` 定义其 slot；`python3 lib/molecules.py` 可打印各物种原子。）

## 三、B. 低层路径（显式 atoms + bonds）—— 推荐用于有机机理
直接给全局原子与键，kernel 只校验守恒/键差，不做实例展开：
```jsonc
"atoms": [
  {"id":"C1","el":"C","frag":"acetyl","flocal":[0,0.2,0],
   "start":[...world...],"end":[...world...],"rmol":"乙酸#1","pmol":"乙酸乙酯#1"}, ...
],
"bonds_before": [ {"a":"C1","b":"O1","order":2}, {"a":"C1","b":"O2","order":1}, ... ],
"bonds_after":  [ {"a":"C1","b":"O3","order":1}, {"a":"O2","b":"H10","order":1}, ... ],
"fragments": [
  {"id":"acetyl",   "K0":{"pos":[-4.5,0.5,0],"rot":[0,0,0]}, "K1":{...}, "K2":{...}},
  {"id":"catalyst", "catalyst":true, "K0":{...},"K1":{...},"K2":{...}}
],
"labels": [ {"id":"r-acid","text":"乙酸 (CH₃COOH)","color":"red","phase":"reactant","atoms":["C1","O1",...]}, ... ]
```
- **frag/flocal**：mechanism 引擎用——原子归属片段 `frag`，`flocal` 是片段内局部坐标；
  运行时由片段关键帧 `K0/K1/K2`（pos+rot 弧度）整体变换。
- **start/end**：morph 回退与标签用（=K0/K2 作用于 flocal，可用 `reaction_kernel._apply` 算）。
- **键序 order**：`1/2/3`；`"ionic"` 离子键（细虚弱化显示）。
- **catalyst 片段**：`catalyst:true` → 青色质子辉光 + 开关；其原子**不计入原子守恒计数**（催化剂再生）。

## 四、steps（分步讲解，建议 3 步对应三阶段）
```jsonc
"steps": [
  {"title":"反应物混合","html":"<span class='text-red-400 font-semibold'>…</span> 富文本说明"},
  {"title":"点燃燃烧","html":"…断键…"},
  {"title":"生成产物","html":"…原子守恒…"}
]
```
阶段边界固定：进度 `[0,0.4)` 接近 → `[0.4,0.7]` 过渡（断/成键高亮、抖动、火焰/能量峰）→ `(0.7,1]` 分离。
步进器按 3 步映射（>3 步会均分高亮，但分子动画仍按上述三阶段）。

## 五、可选叠加层
```jsonc
"electrons": [ {"from":"Na1","to":"Cl1","count":1,"label":"e⁻"} ],   // 氧化还原电子转移（全局 id）
"energy":    { "activation":0.5, "deltaH":-0.75,                     // 能量-反应进程曲线（0~1 相对量）
               "reactantLabel":"CH₄+O₂", "productLabel":"CO₂+H₂O" }  // deltaH<0 放热、>0 吸热
```

## 六、assemble_data 产出的 data（注入模板）
`{ meta, conditions, atoms[{id,el,color,radius,start,end,frag?,flocal?,rmol,pmol}],
   bonds{before,after,broken,formed,kept}, labels[], elementCounts{}, legend[],
   steps[], fragments[], energy, electrons[], ui{} }`
模板读 `__REACTION_DATA__` 数据岛即渲染；`render_html(data, out)` 负责把 data 注入模板。
