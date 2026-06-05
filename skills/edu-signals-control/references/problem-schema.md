# edu-signals-control problem schema

The skill normalizes text, image, or random prompts into this compact contract.
The first release intentionally supports single-loop negative feedback only.

```json
{
  "topic": "negative_feedback_loop",
  "language": "zh-CN",
  "forward_gain": "k*A",
  "feedback": "F(s)",
  "query": "closed_loop_and_high_gain_limit",
  "limit": {
    "variable": "k",
    "target": "oo"
  },
  "parameters_for_visual": {
    "A": 1,
    "k": 40,
    "tau": 0.35
  },
  "sample_omegas": [0.1, 0.2, 0.5, 1, 2, 5, 10]
}
```

## Supported topics

| topic | Required fields | Output |
|---|---|---|
| `negative_feedback_loop` | `forward_gain`, `feedback` | `H(s)=G/(1+GB)` and `k -> infinity` limit |
| `first_order_feedback_loop` | `forward_gain`, `feedback=1/(tau*s+1)` | Same formula plus Bode-style visual samples |

## Image problem example

For the screenshot-style block diagram:

- Input: `x`
- Error signal: `u_i = x - F(s)y`
- Forward gain: `kA`
- Output: `y`
- Feedback network: `F(s)`

Normalize it as:

```json
{
  "topic": "negative_feedback_loop",
  "forward_gain": "k*A",
  "feedback": "F(s)",
  "query": "Find H(s)=y/x and lim_{k->oo} H(s)"
}
```

Expected exact result:

```text
H(s) = k*A / (1 + k*A*F(s))
lim_{k->oo} H(s) = 1/F(s)
```

## Data returned to the HTML template

```json
{
  "lesson": {
    "language": "zh-CN",
    "meta": "信号与控制 · 单环负反馈",
    "title": "...",
    "answerLabel": "...",
    "answerValue": "$...$",
    "ui": {}
  },
  "steps": [
    {
      "title": "读出负反馈关系",
      "content": "<p>...</p>$$...$$",
      "highlight": ["summer", "feedback"]
    }
  ],
  "visual": {
    "type": "negative_feedback_loop",
    "forwardGain": "k A",
    "feedback": "F(s)",
    "closedLoop": "...",
    "limit": "...",
    "samples": {
      "bode": [
        {
          "omega": 1,
          "closedLoopMagnitudeDb": 0,
          "closedLoopPhaseDeg": 0,
          "highGainMagnitudeDb": 0,
          "highGainPhaseDeg": 0,
          "feedbackMagnitudeDb": 0,
          "feedbackPhaseDeg": 0
        }
      ]
    }
  }
}
```

The template may render `samples`, but it must not recompute the final closed
loop transfer function or limit.
