# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 0.32.0

- Snap plot fix [#175](https://github.com/Calysto/octave_kernel/pull/175) ([@PhilFreeman](https://github.com/PhilFreeman))
- Add libglu1 to apt.txt, switch to JupyterLab for Binder [#173](https://github.com/Calysto/octave_kernel/pull/173) ([@jtpio](https://github.com/jtpio))
- Add Binder files [#172](https://github.com/Calysto/octave_kernel/pull/172) ([@jtpio](https://github.com/jtpio))
- Fix tests with Octave 5. [#160](https://github.com/Calysto/octave_kernel/pull/160) ([@QuLogic](https://github.com/QuLogic))

<!-- <END NEW CHANGELOG ENTRY> -->

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
