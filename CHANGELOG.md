# Changelog

All notable changes to `edulab` (higher mathematics & education skills) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-06-06

### Added
- **edu-signals-control skill**:
  - Introductory signals and control-system feedback problem solver.
  - Generates interactive lesson pages for single-loop negative feedback, closed-loop transfer functions, and high loop-gain limits (`H(s)=kA/(1+kAF(s)) -> 1/F(s)`).
- **edu-higher-math skill**:
  - Extended exact-computation solver to higher mathematics: double integrals, polar integrals, surface flux, and first-order differential equations.
  - Interactive SVG visualizations of integration domains, 3D parametric surfaces, and differential equation slope fields.

## [1.1.0] - 2026-06-04

### Changed
- Converted plugin marketplace source to standard GitHub format for backwards compatibility with earlier Claude Code releases.
- Added visual walkthrough preview (`demo1.png`) in README.
- Enhanced dependency installation checks: proactively prompts before installing missing system libraries.

### Fixed
- Fixed 3D coordinate system rotation centering in Three.js renderer.
- Fixed MathJax equation rendering delimiters and mobile viewport overflow.

## [1.0.0] - 2026-06-04

### Added
- Initial release of `edulab` educational skills suite.
- **edu-solid-geometry skill**: Solves 3D solid geometry problems using coordinate + vector method with exact `sympy` symbolic math.
- Generates self-contained interactive HTML lesson pages (MathJax explanation on the left, interactive Three.js 3D model on the right).
- Full compatibility with `skills` CLI (`npx skills add wy51ai/edulab`) and Claude Code marketplace.
