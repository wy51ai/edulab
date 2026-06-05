# edu-signals-control conventions

## Symbols

| Symbol | Meaning |
|---|---|
| `x` | input signal |
| `y` | output signal |
| `u_i` | error / amplifier input signal |
| `G(s)` | forward-path transfer function |
| `B(s)` or `F(s)` | feedback-path transfer function |
| `k` | scalar loop-gain parameter |
| `A` | amplifier gain factor |
| `H(s)` | closed-loop transfer function `y/x` |

## Negative-feedback sign convention

For a single-loop negative-feedback system:

```text
u_i = x - B(s)y
y = G(s)u_i
```

Therefore:

```text
y = G(s)(x - B(s)y)
y(1 + G(s)B(s)) = G(s)x
H(s) = y/x = G(s)/(1 + G(s)B(s))
```

The plus sign in the denominator is a consequence of the subtracting summing
node. If the diagram uses positive feedback, the denominator changes to
`1 - G(s)B(s)`, but that is outside this skill's first-release promise.

## High loop-gain limit

For the screenshot-style problem:

```text
G(s) = kA
B(s) = F(s)
H(s) = kA / (1 + kA F(s))
```

Divide numerator and denominator by `kA`:

```text
H(s) = 1 / (F(s) + 1/(kA))
```

As `k -> infinity`, `1/(kA) -> 0`, so:

```text
lim H(s) = 1/F(s)
```

Teaching intuition: high loop gain forces the error signal near zero, so the
closed-loop behavior is determined mainly by the inverse of the feedback
network.

## Frequency samples

The HTML visual uses precomputed samples at `s = j*omega`.

- Samples are only for display.
- Exact answers come from `control_kernel.py`.
- If `F(s)` is symbolic and cannot be numerically sampled, use a separate
  concrete visual example such as `F(s)=1/(tau*s+1)` while keeping the symbolic
  answer unchanged.

## Self-checks

Before delivering a generated page:

1. Kernel formula equals `G/(1+GB)`.
2. Kernel limit equals the answer card.
3. Final step contains the same kernel answer.
4. The rendered HTML contains `lesson-data` and no `__LESSON_DATA__`.
5. For concrete examples, all Bode samples are finite.
