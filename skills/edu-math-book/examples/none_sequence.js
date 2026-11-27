// 数列：构造等比数列求通项 + 分组求和（none 渲染器范例：右页是公式板，没有图）
// sympy 已核：a_n = 2^n − 1，S_n = 2^{n+1} − n − 2
const LESSON = {
  no: 17, score: '12 分', topic: '数列', topicEn: 'Sequences',
  chapter: '第四章 · 数列', chapterEn: 'Sequences',
  title: '加一之后的等比数列',
  subtitle: 'Add one, and a messy recursion turns geometric.',
  stem: String.raw`已知数列 \(\{a_n\}\) 满足 \(a_1=1\)，\(a_{n+1}=2a_n+1\)。`,
  key: {scribble: '递推式<br>两边同加 1<br>→ 等比！', formula: String.raw`\(a_{n+1}+1=2(a_n+1)\)`, caption: '待定系数构造等比数列'},
  keywords: [['构造法', String.raw`把 \(a_{n+1}=pa_n+q\) 改写成 \(a_{n+1}+t=p(a_n+t)\)。`], ['分组求和', '通项拆成几部分，分别用已知公式求和。']],
  predict: {
    q: String.raw`\(a_5\) 等于多少？`,
    options: ['15', '31', '32', '63'], answer: 1,
    explain: String.raw`关键：\(a_n+1=2^n\)，所以 \(a_5=2^5-1\)。`,
    part: 0, challenge: String.raw`若 \(a_{n+1}=3a_n+2\)，<br>该加几？`,
    dockMsg: '你的回合：先在左页猜一下 a₅',
  },
  given: String.raw`\(a_1=1\)<br>\(a_{n+1}=2a_n+1\)`,
  methods: ['构造法', '分组求和'],

  figure: {
    type: 'none',
    board: [
      {t: String.raw`\(a_{n+1}=2a_n+1\)`},
      {t: String.raw`\(\Downarrow\ \ \text{两边}+1\)`, note: 1},
      {t: String.raw`\(a_{n+1}+1=2\,(a_n+1)\)`, k: 1},
      {t: String.raw`\(a_n=2^n-1\)`},
      {t: String.raw`\(S_n=2^{n+1}-n-2\)`},
    ],
  },

  parts: [
    {q: String.raw`求 \(\{a_n\}\) 的通项公式`, steps: [
      {h: '先算几项，找规律',
       chain: [[String.raw`\(a_1=1,\ a_2=3,\ a_3=7,\ a_4=15\)`, '代入递推'], [String.raw`\(a_n+1:\ 2,4,8,16\)`, '每项加 1 是 2 的幂']]},
      {h: '两边同加 1，构造等比数列',
       chain: [[String.raw`\(a_{n+1}+1=2a_n+2\)`, '两边加 1'], [String.raw`\(=2\,(a_n+1)\)`, '提公因式'], [String.raw`\(\{a_n+1\}\) 是公比为 2 的等比数列`, String.raw`首项 \(a_1+1=2\)`]]},
      {h: '写出通项',
       chain: [[String.raw`\(a_n+1=2\cdot 2^{n-1}=2^n\)`, '等比通项'], [String.raw`\(a_n=2^n-1\)`, '']],
       result: {k: String.raw`\(a_n\)`, v: String.raw`\(2^n-1\)`},
       full: String.raw`由 \(a_{n+1}=2a_n+1\) 得 \(a_{n+1}+1=2(a_n+1)\)，又 \(a_1+1=2\neq0\)，<br>∴ \(\{a_n+1\}\) 是首项为 2、公比为 2 的等比数列，\(a_n+1=2^n\)，即 \(a_n=2^n-1\)。`},
    ]},
    {q: String.raw`求 \(\{a_n\}\) 的前 \(n\) 项和 \(S_n\)`, steps: [
      {h: '通项拆成两组',
       chain: [[String.raw`\(S_n=(2+2^2+\cdots+2^n)-n\)`, '分组'], [String.raw`\(2+2^2+\cdots+2^n=\dfrac{2(2^n-1)}{2-1}\)`, '等比求和']]},
      {h: '合并结果',
       chain: [[String.raw`\(S_n=2^{n+1}-2-n\)`, '化简']],
       result: {k: String.raw`\(S_n\)`, v: String.raw`\(2^{n+1}-n-2\)`},
       full: String.raw`\(S_n=\sum_{k=1}^{n}(2^k-1)=\dfrac{2(2^n-1)}{2-1}-n=2^{n+1}-n-2\)。`},
    ]},
  ],
};
