import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sympy as sp


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "edu-signals-control"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SignalsControlKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel = load_module("control_kernel", SKILL / "lib" / "control_kernel.py")

    def assert_sympy_equal(self, got, expected):
        self.assertEqual(sp.simplify(got - expected), 0)

    def test_negative_feedback_closed_loop_and_high_gain_limit(self):
        sol = self.kernel.solve_negative_feedback_loop(
            forward_gain="k*A",
            feedback="F(s)",
        )

        s = sp.Symbol("s")
        k, A = sp.symbols("k A")
        F = sp.Function("F")

        self.assertEqual(sol["kind"], "negative_feedback_loop")
        self.assert_sympy_equal(sol["closed_loop"], A * k / (A * k * F(s) + 1))
        self.assert_sympy_equal(sol["high_gain_limit"], 1 / F(s))
        self.assertIn(sol["high_gain_limit_latex"], sol["answer_latex"])

    def test_concrete_first_order_feedback_has_exact_limit_and_bode_samples(self):
        sol = self.kernel.solve_negative_feedback_loop(
            forward_gain="k*A",
            feedback="1/(tau*s + 1)",
            parameter_values={"A": 2, "tau": 0.25, "k": 40},
            sample_omegas=(0.1, 1, 10),
        )

        s, tau = sp.symbols("s tau")
        self.assert_sympy_equal(sol["high_gain_limit"], tau * s + 1)
        self.assertGreaterEqual(len(sol["samples"]["bode"]), 3)
        for sample in sol["samples"]["bode"]:
            self.assertGreater(sample["omega"], 0)
            self.assertTrue(math.isfinite(sample["closedLoopMagnitudeDb"]))
            self.assertTrue(math.isfinite(sample["closedLoopPhaseDeg"]))
            self.assertTrue(math.isfinite(sample["feedbackMagnitudeDb"]))


class SignalsControlGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generate = load_module("signals_control_generate", SKILL / "scripts" / "generate.py")

    def test_builders_return_visual_contracts(self):
        cases = {
            "negative_feedback_loop": self.generate.build_feedback_limit_data(),
            "first_order_feedback_loop": self.generate.build_first_order_feedback_data(),
        }

        for visual_type, data in cases.items():
            with self.subTest(visual_type=visual_type):
                self.assertEqual(data["visual"]["type"], visual_type)
                self.assertIn(data["_answer"], data["lesson"]["answerValue"])
                self.assertIn(data["_answer"], data["steps"][-1]["content"])
                self.assertGreaterEqual(len(data["steps"]), 4)
                self.assertGreaterEqual(len(data["visual"]["samples"]["bode"]), 3)

    def test_rendered_html_contains_data_and_no_placeholder(self):
        data = self.generate.build_feedback_limit_data()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feedback-limit.html"
            self.generate.render_html(data, out)
            html = out.read_text(encoding="utf-8")

        self.assertNotIn("__LESSON_DATA__", html)
        self.assertIn('"type": "negative_feedback_loop"', html)
        self.assertIn("lesson-data", html)
        self.assertIn(data["_answer"], html)
        self.assertIn("MathJax", html)

    def test_cli_generates_all_registered_examples(self):
        modes = ["feedback-limit", "first-order-feedback", "random"]
        with tempfile.TemporaryDirectory() as tmp:
            for mode in modes:
                with self.subTest(mode=mode):
                    out = Path(tmp) / f"{mode}.html"
                    result = subprocess.run(
                        [sys.executable, str(SKILL / "scripts" / "generate.py"), mode, str(out)],
                        cwd=REPO,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    html = out.read_text(encoding="utf-8")
                    self.assertIn("lesson-data", html)
                    self.assertNotIn("__LESSON_DATA__", html)


class SignalsControlPackagingTests(unittest.TestCase):
    def test_package_metadata_mentions_signals_control(self):
        package = json.loads((REPO / "package.json").read_text(encoding="utf-8"))

        self.assertIn("signals-control", package["keywords"])
        self.assertIn("control-systems", package["keywords"])
        self.assertIn("feedback", package["keywords"])
        self.assertIn("transfer-function", package["keywords"])
        self.assertIn("edu-signals-control", package["description"])

    def test_readme_and_manifests_mention_skill(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        readme_zh = (REPO / "README.zh-CN.md").read_text(encoding="utf-8")
        plugin = (REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        marketplace = (REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")

        for content in (readme, readme_zh, plugin, marketplace):
            self.assertIn("edu-signals-control", content)

    def test_ignores_generated_outputs(self):
        npmignore = (REPO / ".npmignore").read_text(encoding="utf-8")

        self.assertIn("skills/edu-signals-control/output/", npmignore)


if __name__ == "__main__":
    unittest.main()
