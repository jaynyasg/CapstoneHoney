# TODOs

## GitHub Actions test workflow

**What:** Add a GitHub Actions workflow that installs the Python package dependencies and runs `python -m pytest` on pushes and pull requests.

**Why:** The DP-HONEY generator will be consumed by teammates as a library and CLI, so automated test feedback would catch format, model artifact, and CLI regressions before they reach the shared branch.

**Pros:** Keeps the registry, generator, artifact validation, CLI, and README consistency checks running automatically on GitHub.

**Cons:** Adds workflow setup and dependency-cache decisions before the team has settled all repo conventions.

**Context:** This was deferred during the DP-HONEY generator CEO/engineering planning pass. The first implementation should document `python -m pytest` locally; once the package scaffold exists, add `.github/workflows/tests.yml` for the supported Python version and include any fixture paths needed by the test suite.

**Depends on / blocked by:** Python scaffold and pytest configuration landing in `pyproject.toml`.
