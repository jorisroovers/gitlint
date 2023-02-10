# hatch_build.py is executed by hatch at build-time and can contain custom build logic hooks
import os
from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    """Custom metadata hook for hatch that ensures that gitlint and gitlint-core[trusted-deps] versions always match"""

    def update(self, metadata: dict) -> None:
        # Only enforce versioning matching outside of the 'dev' environment, this allows for re-use of the 'dev'
        # environment between different git branches.
        if os.environ.get("HATCH_ENV_ACTIVE", "not-dev") != "dev":
            metadata["dependencies"] = [f"gitlint-core[trusted-deps]=={metadata['version']}"]
