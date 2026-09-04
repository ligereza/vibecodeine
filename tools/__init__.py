"""MAK's tools package.

This file exists to make ``tools`` a regular package rather than a namespace
package, and that is the whole of its job.

The FLUJO motor ships a ``tools/`` directory too. While both were namespace
packages, ``tools`` resolved to the union of every ``tools/`` directory on
``sys.path``, in ``sys.path`` order. ``flujo.cli._expose_repo_namespace``
inserts the motor checkout at ``sys.path[0]`` when imported, so any MAK module
that imported ``tools.<name>`` after ``tests/test_autonomia_cli.py`` had run
got the motor's copy instead of this repository's.

That is how ``tests/test_repo_audit.py`` came to audit the motor: run alone it
reported MAK's 106 tools and passed, run in the full suite it reported the
motor's 131 and failed, with nothing in the diff to explain the difference.

A regular package pins ``tools.__path__`` to this directory, so the binding no
longer depends on import order or on what another checkout does to
``sys.path``. Subdirectories without their own ``__init__.py``
(``tools/portfolio``, ``tools/recovered``) keep working: a regular package can
still contain namespace subpackages.
"""
