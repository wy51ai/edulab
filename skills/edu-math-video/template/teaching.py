"""Optional teaching metadata: structural checks, never a mathematical proof verifier."""
import math


def check_teaching(script):
    errors, report = [], []
    for scene in script:
        for index, line in enumerate(scene.get("lines", [])):
            where = f"[{scene.get('scene')} {index}]"
            pause = line.get("pause_after", 0)
            if (isinstance(pause, bool) or not isinstance(pause, (int, float))
                    or not math.isfinite(pause) or not 0 <= pause <= 30):
                errors.append(f"{where} pause_after must be a finite number from 0 to 30 seconds")
            elif pause:
                report.append(f"{where} think for {pause:g}s after: {line.get('zh', '')}")
            if "theorem" not in line:
                continue
            theorem = line["theorem"]
            if not isinstance(theorem, dict):
                errors.append(f"{where} theorem must be an object")
                continue
            for field in ("name", "conclusion"):
                if not isinstance(theorem.get(field), str) or not theorem[field].strip():
                    errors.append(f"{where} theorem.{field} must be a nonempty string")
            conditions = theorem.get("conditions")
            if not isinstance(conditions, list) or not conditions:
                errors.append(f"{where} theorem.conditions needs at least one claim with its reason")
                continue
            report.append(f"{where} theorem: {theorem.get('name', '')}")
            for condition in conditions:
                if (not isinstance(condition, dict)
                        or any(not isinstance(condition.get(key), str) or not condition[key].strip()
                               for key in ("claim", "reason"))):
                    errors.append(f"{where} each theorem.conditions entry needs nonempty claim and reason")
                else:
                    report.append(f"  {condition['claim']} <- {condition['reason']}")
            report.append(f"  => {theorem.get('conclusion', '')}")
    return errors, "\n".join(report) + "\n\nStructural checks only; verify the mathematics and show these conditions in anim.js.\n"
