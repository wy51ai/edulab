import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sympy as sp


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "edu-higher-math"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HigherMathKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel = load_module("calculus_kernel", SKILL / "lib" / "calculus_kernel.py")

    def assert_sympy_equal(self, got, expected):
        self.assertEqual(sp.simplify(got - expected), 0)

    def test_cartesian_double_integral_exact_answer(self):
        sol = self.kernel.solve_cartesian_double_integral(
            "x + y",
            x_bounds=(0, 1),
            y_bounds=(0, 2),
        )

        self.assert_sympy_equal(sol["exact"], sp.Integer(3))
        self.assertEqual(sol["answer_latex"], "3")
        self.assertGreaterEqual(len(sol["samples"]["cells"]), 9)

    def test_polar_unit_disk_integral_uses_jacobian(self):
        sol = self.kernel.solve_polar_double_integral(
            "1",
            r_bounds=(0, 1),
            theta_bounds=(0, "2*pi"),
        )

        self.assert_sympy_equal(sol["exact"], sp.pi)
        self.assertEqual(sol["answer_latex"], r"\pi")
        self.assertGreaterEqual(len(sol["samples"]["rings"]), 3)

    def test_surface_flux_uses_parametric_normal(self):
        sol = self.kernel.solve_surface_flux(
            vector_field=("x", "y", "z"),
            parametrization=("u", "v", "1"),
            u_bounds=(0, 1),
            v_bounds=(0, 1),
        )

        self.assert_sympy_equal(sol["exact"], sp.Integer(1))
        self.assertEqual(sol["answer_latex"], "1")
        self.assertGreaterEqual(len(sol["samples"]["surface"]), 9)
        self.assertGreaterEqual(len(sol["samples"]["vectors"]), 4)

    def test_first_order_ode_with_initial_condition(self):
        sol = self.kernel.solve_first_order_ode(
            rhs="y",
            x0=0,
            y0=1,
            sample_bounds=(-1, 1),
        )

        x = sp.Symbol("x")
        self.assert_sympy_equal(sol["solution_expr"], sp.exp(x))
        self.assertIn("e^{x}", sol["solution_latex"])
        self.assertGreaterEqual(len(sol["samples"]["slope_field"]), 25)
        self.assertGreaterEqual(len(sol["samples"]["solution_curve"]), 20)


class HigherMathGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generate = load_module("higher_math_generate", SKILL / "scripts" / "generate.py")

    def test_builders_return_visual_contracts(self):
        cases = {
            "double_integral": self.generate.build_double_integral_data(),
            "polar_integral": self.generate.build_polar_integral_data(),
            "surface_flux": self.generate.build_surface_flux_data(),
            "ode_slope_field": self.generate.build_ode_data(),
        }

        for visual_type, data in cases.items():
            with self.subTest(visual_type=visual_type):
                self.assertEqual(data["visual"]["type"], visual_type)
                self.assertIn(data["_answer"], data["lesson"]["answerValue"])
                self.assertIn(data["_answer"], data["steps"][-1]["content"])
                self.assertGreaterEqual(len(data["steps"]), 4)

    def test_rendered_html_contains_data_and_no_placeholder(self):
        data = self.generate.build_ode_data()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ode.html"
            self.generate.render_html(data, out)
            html = out.read_text(encoding="utf-8")

        self.assertNotIn("__LESSON_DATA__", html)
        self.assertIn('"type": "ode_slope_field"', html)
        self.assertIn(data["_answer"], html)
        self.assertIn("MathJax", html)

    def test_cli_generates_all_registered_examples(self):
        modes = ["double-integral", "polar-integral", "surface-flux", "ode", "random"]
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


class HigherMathPackagingTests(unittest.TestCase):
    def test_package_metadata_mentions_higher_math(self):
        package = json.loads((REPO / "package.json").read_text(encoding="utf-8"))

        self.assertIn("higher-math", package["keywords"])
        self.assertIn("calculus", package["keywords"])
        self.assertIn("differential-equations", package["keywords"])
        self.assertIn("edu-higher-math", package["description"])

    def test_ignores_generated_outputs_and_local_sync_artifacts(self):
        gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
        npmignore = (REPO / ".npmignore").read_text(encoding="utf-8")

        self.assertIn("*.baiduyun.uploading.cfg", gitignore)
        self.assertIn("skills/edu-higher-math/output/", npmignore)


if __name__ == "__main__":
    unittest.main()
