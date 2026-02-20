# =============================================================================
# username_generator — Package Initialization
# =============================================================================
# Exports the public API so consumers can do:
#   from username_generator import generate_username, generate_batch
# =============================================================================

__version__ = "0.1.0"

from username_generator.core import generate_batch, generate_username

__all__ = ["generate_username", "generate_batch", "__version__"]
