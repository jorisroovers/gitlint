# hatch_build.py is executed by hatch at build-time and can contain custom build logic hooks
from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    """Custom metadata hook for hatch that ensures that gitlint and gitlint-core[trusted-deps] versions always match"""

    def update(self, metadata: dict) -> None:
        metadata["dependencies"] = [f"gitlint-core[trusted-deps]=={metadata['version']}"]
