"""Development task runner (delegates to uv and existing scripts)."""

from __future__ import annotations

import nox

nox.options.default_venv_backend = 'none'


@nox.session
def setup(session):
    """Full native + Python bootstrap (OrbbecSDK, pyorbbecsdk, libferret, venv)."""
    session.run('bash', 'scripts/dev-setup', external=True)


@nox.session
def sync(session):
    """Refresh Python dependencies only (requires existing .venv)."""
    session.run('uv', 'sync', '--group', 'dev', external=True)


@nox.session
def test(session):
    # Avoid "uv run" re-syncing the broken PyPI wxPython wheel on Fedora.
    session.run('.venv/bin/python', '-m', 'pytest', external=True)


@nox.session
def lint(session):
    session.run('uv', 'run', 'ruff', 'check', external=True)


@nox.session
def format(session):
    session.run('uv', 'run', 'ruff', 'format', external=True)


@nox.session
def run(session):
    session.run('bash', './ferret', external=True)


@nox.session
def check(session):
    """License checks and optional hardware validation."""
    args = session.posargs or []
    session.run('bash', 'scripts/dev-check', *args, external=True)
