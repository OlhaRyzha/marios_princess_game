# Tests

Run the suite from the project root:

```bash
make test
```

The test code has three clear roles:

- `conftest.py` owns shared lifecycle setup. It starts and stops Pygame with dummy video and audio drivers, so tests do not open a window or require speakers.
- `factories/` builds small test objects with the exact state a scenario needs. Factories contain no assertions and do not manage global resources.
- `unit/` contains behavior-focused tests written as Arrange → Act → Assert.
- `integration/` verifies runtime transitions and collaboration between components.

Add a fixture when setup must be safely created and cleaned up. Add a factory when tests need several variations of the same object. Keep one-off values directly in the test so the scenario remains visible.

Run the coverage baseline before review:

```bash
make coverage
```

Time, held input, random generation, and audio have explicit fake implementations
under `tests/factories/`. Prefer them over sleeping or patching global Pygame
functions.
