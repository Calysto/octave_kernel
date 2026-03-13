"""ASV benchmarks for OctaveEngine."""

from __future__ import annotations

from typing import ClassVar

from octave_kernel.kernel import OctaveEngine


class TimeEngineStartup:
    """Time the full engine startup (spawning the Octave process)."""

    def time_startup(self):
        engine = OctaveEngine()
        engine._cleanup()


class TimeEvalRoundTrip:
    """Time eval round-trip latency for simple expressions."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def time_arithmetic(self):
        self.engine.eval("1 + 1;", silent=True)

    def time_variable_assign(self):
        self.engine.eval("x = 42;", silent=True)

    def time_string_assign(self):
        self.engine.eval("s = 'hello world';", silent=True)

    def time_for_loop(self):
        self.engine.eval("for i = 1:100; x = i; end", silent=True)

    def time_function_call(self):
        self.engine.eval("x = zeros(10, 10);", silent=True)


class TimeEvalWithOutput:
    """Time evals that produce output (exercises stream/line handlers)."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def time_scalar_output(self):
        self.engine.eval("disp(42)")

    def time_row_vector_output(self):
        self.engine.eval("disp(1:10)")

    def time_matrix_output(self):
        self.engine.eval("disp(reshape(1:25, 5, 5))")

    def time_string_output(self):
        self.engine.eval("disp('benchmark output string')")


class TimeMatrixOps:
    """Time matrix computation evals."""

    def setup(self):
        self.engine = OctaveEngine()
        self.engine.eval("A = rand(50, 50);", silent=True)
        self.engine.eval("B = rand(50, 50);", silent=True)

    def teardown(self):
        self.engine._cleanup()

    def time_multiply(self):
        self.engine.eval("C = A * B;", silent=True)

    def time_transpose(self):
        self.engine.eval("C = A';", silent=True)

    def time_element_sum(self):
        self.engine.eval("s = sum(A(:));", silent=True)

    def time_eigenvalues(self):
        self.engine.eval("e = eig(A);", silent=True)

    def time_solve(self):
        self.engine.eval("x = A \\ B(:, 1);", silent=True)


class TimeEvalInputSizes:
    """Time eval with inputs of varying sizes passed as Octave literals."""

    params: ClassVar = [10, 50, 100]
    param_names: ClassVar = ["n"]

    def setup(self, n):
        self.engine = OctaveEngine()

    def teardown(self, n):
        self.engine._cleanup()

    def time_create_zeros(self, n):
        self.engine.eval(f"A = zeros({n}, {n});", silent=True)

    def time_create_rand(self, n):
        self.engine.eval(f"A = rand({n}, {n});", silent=True)

    def time_linspace(self, n):
        self.engine.eval(f"x = linspace(0, 1, {n});", silent=True)


class PeakMemEngineStartup:
    """Peak memory for spawning an Octave process."""

    def peakmem_startup(self):
        engine = OctaveEngine()
        engine._cleanup()


class PeakMemEvalExpressions:
    """Peak memory for eval calls with various expression types."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def peakmem_arithmetic(self):
        self.engine.eval("1 + 1;", silent=True)

    def peakmem_for_loop(self):
        self.engine.eval("for i = 1:100; x = i; end", silent=True)

    def peakmem_string_output(self):
        self.engine.eval("disp('benchmark output string')")


class PeakMemMatrixAllocation:
    """Peak memory when allocating matrices of varying sizes in Octave."""

    params: ClassVar = [10, 100, 500]
    param_names: ClassVar = ["n"]

    def setup(self, n):
        self.engine = OctaveEngine()

    def teardown(self, n):
        self.engine._cleanup()

    def peakmem_zeros(self, n):
        self.engine.eval(f"A = zeros({n}, {n});", silent=True)

    def peakmem_rand(self, n):
        self.engine.eval(f"A = rand({n}, {n});", silent=True)

    def peakmem_multiply(self, n):
        self.engine.eval(
            f"A = rand({n}, {n}); B = rand({n}, {n}); C = A * B;", silent=True
        )


class TimeCompletions:
    """Time completion_matches eval (exercises Octave's completion engine)."""

    def setup(self):
        self.engine = OctaveEngine()

    def teardown(self):
        self.engine._cleanup()

    def time_completions_two_chars(self):
        self.engine.eval('completion_matches("di")', silent=True)

    def time_completions_three_chars(self):
        self.engine.eval('completion_matches("mat")', silent=True)

    def time_completions_empty(self):
        self.engine.eval('completion_matches("")', silent=True)
