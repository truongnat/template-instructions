# Contributing to Agentic SDLC

Thank you for your interest in contributing to the Agentic SDLC Kit! We welcome contributions from the community.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/agentic-sdlc.git
    cd agentic-sdlc
    ```
3.  **Set up the environment**:
    We recommend using Docker for a consistent environment:
    ```bash
    docker-compose up -d --build
    docker-compose exec agentic-core bash
    ```
    Or locally with Python 3.10+:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```

## Development Workflow

1.  Create a new branch for your feature or bugfix:
    ```bash
    git checkout -b feature/my-awesome-feature
    ```
2.  Make your changes.
3.  Run tests to ensure no regressions:
    ```bash
    pytest
    ```
4.  Commit your changes using conventional commits (e.g., `feat: add new skill`, `fix: resolve issue #123`).

## Project Structure

-   `agentic_sdlc/`: Core package source code.
    -   `defaults/`: Golden master for skills, rules, and workflows.
    -   `intelligence/`: AI sub-agents logic.
    -   `infrastructure/`: CLI, Git bridging, Docker tools.
-   `docs/`: Documentation.
-   `tests/`: Unit and integration tests.

## Adding a New Skill

1.  Add the skill definition markdown to `agentic_sdlc/defaults/skills/`.
2.  Register the skill in `GEMINI.md`.
3.  Add tests ensuring the skill prompts work as expected.

## Pull Request Process

1.  Push your branch to GitHub.
2.  Open a Pull Request against the `main` branch.
3.  Ensure CI checks pass (Linting, Tests).
4.  A maintainer will review your PR.

## Code of Conduct

Please be respectful and kind to others. Harassment or abusive behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
