set allow-duplicate-variables := true

import '.devbox/virtenv/pokerops.ansible-utils.molecule/justfile'

MOLECULE_REVISION := `command git rev-parse --abbrev-ref HEAD`
MOLECULE_SCENARIO := 'install'

format: sync
  uv run black . --fast --quiet

python-lint: sync
  #!/usr/bin/env bash
  uv run black . --fast --quiet --check
  uv run ruff check
  uv run basedpyright plugins/
  uv run ty check plugins/

python-test: sync
  #!/usr/bin/env bash
  uv run pytest tests/pytest
