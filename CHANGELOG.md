# Changelog

## 0.39.0

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.38.0...42ddad5cafa20b0ec91251fd58591ccdd3d2a884))

### Enhancements made

- Validate Octave executable on engine init and clean up diagnostics [#273](https://github.com/Calysto/octave_kernel/pull/273) ([@blink1073](https://github.com/blink1073))
- Add Binder support with Qt/Xvfb and document JupyterHub setup [#271](https://github.com/Calysto/octave_kernel/pull/271) ([@blink1073](https://github.com/blink1073))
- Change default executable to octave and always pass --no-gui [#270](https://github.com/Calysto/octave_kernel/pull/270) ([@blink1073](https://github.com/blink1073))
- Start Xvfb globally in action instead of per-command [#269](https://github.com/Calysto/octave_kernel/pull/269) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Test Python 3.10 on ubuntu-22.04 in test-linux matrix [#272](https://github.com/Calysto/octave_kernel/pull/272) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2026-03-07&to=2026-03-09&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2026-03-07..2026-03-09&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Aclaude+updated%3A2026-03-07..2026-03-09&type=Issues))

## 0.38.0

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.37.1...9feccd1dc747d1287c3fa920b95078abc45a0a9a))

### Enhancements made

- Improve snap support and update supported platforms [#267](https://github.com/Calysto/octave_kernel/pull/267) ([@blink1073](https://github.com/blink1073))
- Document qt backend and expose executable as configurable trait [#266](https://github.com/Calysto/octave_kernel/pull/266) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2026-03-06&to=2026-03-07&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2026-03-06..2026-03-07&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Aclaude+updated%3A2026-03-06..2026-03-07&type=Issues))

## 0.37.1

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.37.0...03f3ecbf733f7850bc6b9d03a37721ad965abb09))

### Enhancements made

- Add snap support and consolidate CI test jobs [#265](https://github.com/Calysto/octave_kernel/pull/265) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2026-03-05&to=2026-03-06&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2026-03-05..2026-03-06&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Aclaude+updated%3A2026-03-05..2026-03-06&type=Issues))

## 0.37.0

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.36.0...1f6f5b774b1afdf43f6a7080887dbf512f589b41))

### Enhancements made

- Add composite GitHub Action for Octave installation [#259](https://github.com/Calysto/octave_kernel/pull/259) ([@blink1073](https://github.com/blink1073))
- Add typing support with mypy strict mode [#256](https://github.com/Calysto/octave_kernel/pull/256) ([@blink1073](https://github.com/blink1073))
- Add flatpak support for Octave auto-detection [#254](https://github.com/Calysto/octave_kernel/pull/254) ([@blink1073](https://github.com/blink1073))
- Add macOS runner to CI test matrix [#253](https://github.com/Calysto/octave_kernel/pull/253) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Clean up Windows Octave install [#264](https://github.com/Calysto/octave_kernel/pull/264) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))
- Adopt zizmor for GitHub Actions static analysis [#263](https://github.com/Calysto/octave_kernel/pull/263) ([@blink1073](https://github.com/blink1073))
- Extend ruff linting and fix all violations [#262](https://github.com/Calysto/octave_kernel/pull/262) ([@blink1073](https://github.com/blink1073))
- Add a step to the GitHub Action to verify octave install [#261](https://github.com/Calysto/octave_kernel/pull/261) ([@blink1073](https://github.com/blink1073))
- Add unit tests for OctaveEngine, OctaveKernel, and check module [#260](https://github.com/Calysto/octave_kernel/pull/260) ([@blink1073](https://github.com/blink1073))
- Add Windows CI test job [#258](https://github.com/Calysto/octave_kernel/pull/258) ([@blink1073](https://github.com/blink1073))
- Move test dependencies to dependency-groups [#257](https://github.com/Calysto/octave_kernel/pull/257) ([@blink1073](https://github.com/blink1073))
- Add tests_check job for branch protection [#255](https://github.com/Calysto/octave_kernel/pull/255) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))
- Bump the actions group with 3 updates [#252](https://github.com/Calysto/octave_kernel/pull/252) ([@blink1073](https://github.com/blink1073))
- Add dependabot config [#251](https://github.com/Calysto/octave_kernel/pull/251) ([@blink1073](https://github.com/blink1073))
- Add pre-commit hooks and apply code quality fixes [#250](https://github.com/Calysto/octave_kernel/pull/250) ([@blink1073](https://github.com/blink1073))
- Replace Makefile with justfile and migrate to uv [#249](https://github.com/Calysto/octave_kernel/pull/249) ([@blink1073](https://github.com/blink1073))
- Add CodeQL analysis workflow configuration [#248](https://github.com/Calysto/octave_kernel/pull/248) ([@blink1073](https://github.com/blink1073))
- Fix CI install of octave [#247](https://github.com/Calysto/octave_kernel/pull/247) ([@blink1073](https://github.com/blink1073))
- Update ci again [#246](https://github.com/Calysto/octave_kernel/pull/246) ([@blink1073](https://github.com/blink1073))
- Fix octave install in CI and update supported Python versions [#245](https://github.com/Calysto/octave_kernel/pull/245) ([@blink1073](https://github.com/blink1073))
- Update supported pythons [#243](https://github.com/Calysto/octave_kernel/pull/243) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2024-04-15&to=2026-03-05&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2024-04-15..2026-03-05&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Aclaude+updated%3A2024-04-15..2026-03-05&type=Issues))

## 0.36.0

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.35.1...79d09bfd8f9e6ef05516a2263453f257e15e90be))

### Enhancements made

- Prefer octave-cli if available [#236](https://github.com/Calysto/octave_kernel/pull/236) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Switch to hatch custom build [#238](https://github.com/Calysto/octave_kernel/pull/238) ([@blink1073](https://github.com/blink1073))
- Update Release Scripts [#237](https://github.com/Calysto/octave_kernel/pull/237) ([@blink1073](https://github.com/blink1073))

### Other merged PRs

- Clarify use environment variable wording [#229](https://github.com/Calysto/octave_kernel/pull/229) ([@goyalyashpal](https://github.com/goyalyashpal))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2022-11-29&to=2024-04-15&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2022-11-29..2024-04-15&type=Issues) | [@goyalyashpal](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Agoyalyashpal+updated%3A2022-11-29..2024-04-15&type=Issues)

## 0.35.1

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.35.0...59c1841ae47ec594516d0aca355e0ef14f7eb61f))

### Bugs fixed

- Include test and example notebook in sdist [#228](https://github.com/Calysto/octave_kernel/pull/228) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2022-11-28&to=2022-11-29&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2022-11-28..2022-11-29&type=Issues)

## 0.35.0

No merged PRs

## 0.34.2

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.34.1...0c2501cc4d452cad5ee17f6a5369d57c6da30a90))

### Bugs fixed

- Fix error: '\_make_figures' undefined near line 1, column 1 [#212](https://github.com/Calysto/octave_kernel/pull/212) ([@mokeyish](https://github.com/mokeyish))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2022-02-07&to=2022-03-31&type=c))

[@mokeyish](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Amokeyish+updated%3A2022-02-07..2022-03-31&type=Issues)

## 0.34.1

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.34.0...d6b0a4a0beae56e5b85e6640cf29fb2a504fc1d5))

### Bugs fixed

- Improve handling of default inline toolkit [#209](https://github.com/Calysto/octave_kernel/pull/209) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2022-01-04&to=2022-02-07&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2022-01-04..2022-02-07&type=Issues)

## 0.34.0

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/v0.33.1...0ae34050c2e6a2cbf45b9cdb1a69762fece9e081))

### Enhancements made

- Use octave executable and qt backend by default [#204](https://github.com/Calysto/octave_kernel/pull/204) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Fail if kernel test fails [#203](https://github.com/Calysto/octave_kernel/pull/203) ([@blink1073](https://github.com/blink1073))
- Use published jupyter_kernel_test [#202](https://github.com/Calysto/octave_kernel/pull/202) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2021-11-27&to=2022-01-04&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2021-11-27..2022-01-04&type=Issues)

## 0.33.1

([Full Changelog](https://github.com/Calysto/octave_kernel/compare/0.32.0...94f977d10ee6e1e278a2b2d79239f953a3274b7b))

### Maintenance and upkeep improvements

- Prep for jupyter releaser usage [#200](https://github.com/Calysto/octave_kernel/pull/200) ([@blink1073](https://github.com/blink1073))
- Upgrade to jupyter packaging and github actions [#199](https://github.com/Calysto/octave_kernel/pull/199) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/octave_kernel/graphs/contributors?from=2020-05-23&to=2021-11-27&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Foctave_kernel+involves%3Ablink1073+updated%3A2020-05-23..2021-11-27&type=Issues)

## 0.32.0

- Snap plot fix [#175](https://github.com/Calysto/octave_kernel/pull/175) ([@PhilFreeman](https://github.com/PhilFreeman))
- Add libglu1 to apt.txt, switch to JupyterLab for Binder [#173](https://github.com/Calysto/octave_kernel/pull/173) ([@jtpio](https://github.com/jtpio))
- Add Binder files [#172](https://github.com/Calysto/octave_kernel/pull/172) ([@jtpio](https://github.com/jtpio))
- Fix tests with Octave 5. [#160](https://github.com/Calysto/octave_kernel/pull/160) ([@QuLogic](https://github.com/QuLogic))

## v0.31.0

- Use new line_handler from metakernel (optionally) [#158](https://github.com/Calysto/octave_kernel/pull/158) ([@blink1073](https://github.com/blink1073))
- Add the full license [#157](https://github.com/Calysto/octave_kernel/pull/157) ([@toddrme2178](https://github.com/toddrme2178))

## v0.30.2

- Allow inline backend to be specified using plot magic [#154](https://github.com/Calysto/octave_kernel/pull/154) ([@blink1073](https://github.com/blink1073))

## v0.30.1

- Clean up plot handling and add config [#153](https://github.com/Calysto/octave_kernel/pull/153) ([@blink1073](https://github.com/blink1073))

## v0.29.2

- Add a Dockerfile [#151](https://github.com/Calysto/octave_kernel/pull/151) ([@blink1073](https://github.com/blink1073))

## v0.28.6

- Adds texinfo to README [#140](https://github.com/Calysto/octave_kernel/pull/140) ([@sigurdurb](https://github.com/sigurdurb))

## v0.28.5

- Use `jupyter` rather than `ipython` in README [#137](https://github.com/Calysto/octave_kernel/pull/137) ([@robertoostenveld](https://github.com/robertoostenveld))

## v0.28.4

- Include `LICENSE.txt` file in wheels [#131](https://github.com/Calysto/octave_kernel/pull/131) ([@toddrme2178](https://github.com/toddrme2178))

## v0.28.3

- Kernel JSON path as env variable [#114](https://github.com/Calysto/octave_kernel/pull/114) ([@diocas](https://github.com/diocas))

## v0.28.2

- Ensure `octaverc` does not override PS1 [#108](https://github.com/Calysto/octave_kernel/pull/108) ([@blink1073](https://github.com/blink1073))

## v0.28.0

- Switch to a `data_files` based install [#104](https://github.com/Calysto/octave_kernel/pull/104) ([@blink1073](https://github.com/blink1073))

## v0.27.1

- Fix unmatched backtick [#101](https://github.com/Calysto/octave_kernel/pull/101) ([@Carreau](https://github.com/Carreau))
- Use conda forge octave for testing [#100](https://github.com/Calysto/octave_kernel/pull/100) ([@blink1073](https://github.com/blink1073))

## v0.27.0

- Add images and switch to metakernel standard install method [#99](https://github.com/Calysto/octave_kernel/pull/99) ([@blink1073](https://github.com/blink1073))
- Fix Travis and add Python 3.6 test [#92](https://github.com/Calysto/octave_kernel/pull/92) ([@blink1073](https://github.com/blink1073))

## v0.24.7

- Fix project URL in setup.py [#73](https://github.com/Calysto/octave_kernel/pull/73) ([@shoyer](https://github.com/shoyer))

## v0.23.1

- Fix readline behavior on Windows [#68](https://github.com/Calysto/octave_kernel/pull/68) ([@blink1073](https://github.com/blink1073))

## v0.23.0

- Fix indefinite pause on Windows [#67](https://github.com/Calysto/octave_kernel/pull/67) ([@blink1073](https://github.com/blink1073))
- Override input again [#66](https://github.com/Calysto/octave_kernel/pull/66) ([@blink1073](https://github.com/blink1073))

## v0.22.0

- Disambiguate license [#64](https://github.com/Calysto/octave_kernel/pull/64) ([@blink1073](https://github.com/blink1073))
- Fix interrupt and shutdown behavior [#63](https://github.com/Calysto/octave_kernel/pull/63) ([@blink1073](https://github.com/blink1073))

## v0.21.0

- Fix `imwrite` handling [#61](https://github.com/Calysto/octave_kernel/pull/61) ([@blink1073](https://github.com/blink1073))

## v0.20.0

- Add handling of input functions [#60](https://github.com/Calysto/octave_kernel/pull/60) ([@blink1073](https://github.com/blink1073))

## v0.18.0

- Handle `surf` vs `imshow` [#51](https://github.com/Calysto/octave_kernel/pull/51) ([@thomasjm](https://github.com/thomasjm))

## v0.16.1

- Add makefile [#43](https://github.com/Calysto/octave_kernel/pull/43) ([@blink1073](https://github.com/blink1073))
- Plot images at their native resolution, without any resizing [#40](https://github.com/Calysto/octave_kernel/pull/40) ([@alexdu](https://github.com/alexdu))

## v0.13

- Also use `OCTAVE_EXECUTABLE` in banner property if available [#21](https://github.com/Calysto/octave_kernel/pull/21) ([@zertrin](https://github.com/zertrin))
- Fixed deprecation warning in Jupyter 4 caused by importing from IPython.kernel [#16](https://github.com/Calysto/octave_kernel/pull/16) ([@akubera](https://github.com/akubera))
