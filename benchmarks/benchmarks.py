"""ASV benchmarks for OctaveEngine."""

from __future__ import annotations

from octave_kernel.kernel import OctaveEngine


class TimeEngineStartup:
    """Time the full engine startup (spawning the Octave process)."""

    def time_startup(self):
        engine = OctaveEngine()
        engine._cleanup()


class TimeEvalRoundTrip:
    """Time eval round-trip latency for representative expressions."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def time_arithmetic(self):
        self.engine.eval("1 + 1;", silent=True)

    def time_for_loop(self):
        self.engine.eval("for i = 1:100; x = i; end", silent=True)

    def time_matrix_output(self):
        self.engine.eval("disp(reshape(1:25, 5, 5))")


class TimeMatrixOps:
    """Time matrix computation evals."""

    def setup(self):
        self.engine = OctaveEngine()
        self.engine.eval("A = rand(50, 50); B = rand(50, 50);", silent=True)

    def teardown(self):
        self.engine._cleanup()

    def time_multiply(self):
        self.engine.eval("C = A * B;", silent=True)

    def time_eigenvalues(self):
        self.engine.eval("e = eig(A);", silent=True)


class TimeCompletions:
    """Time completion_matches eval (exercises Octave's completion engine)."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def time_completions(self):
        self.engine.eval('completion_matches("mat")', silent=True)


class PeakMemEngineStartup:
    """Peak memory for spawning an Octave process."""

    def peakmem_startup(self):
        engine = OctaveEngine()
        engine._cleanup()


class PeakMemEval:
    """Peak memory for representative eval calls."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def peakmem_arithmetic(self):
        self.engine.eval("1 + 1;", silent=True)

    def peakmem_matrix_alloc(self):
        self.engine.eval("A = rand(100, 100);", silent=True)
