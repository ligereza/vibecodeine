#!/usr/bin/env python3
"""Process-local compatibility bridge for MLflow/AzureML artifact plugins."""
from __future__ import annotations

import inspect


def patch_azureml_artifact_builder() -> str:
    """Make azureml-mlflow 1.60 work with MLflow 3 constructor kwargs."""
    from mlflow.store.artifact.artifact_repository_registry import (
        _artifact_repository_registry,
    )

    builder = _artifact_repository_registry._registry.get("azureml")
    if builder is None:
        raise RuntimeError("azureml_artifact_builder_missing")
    try:
        parameters = inspect.signature(builder).parameters
    except (TypeError, ValueError):
        parameters = {}
    if "tracking_uri" in parameters:
        return "native"

    # Avoid wrapping our own wrapper when a process imports the compat module
    # more than once.
    if getattr(builder, "_mak_mlflow_compat", False):
        return "signature_bridge"

    def compatible_builder(artifact_uri=None, tracking_uri=None,
                           registry_uri=None):
        del tracking_uri, registry_uri
        return builder(artifact_uri)

    compatible_builder._mak_mlflow_compat = True
    _artifact_repository_registry.register("azureml", compatible_builder)
    return "signature_bridge"
