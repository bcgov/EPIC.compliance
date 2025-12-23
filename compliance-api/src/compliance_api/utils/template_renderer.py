"""Render the given template with data."""

import os
from typing import Dict

from jinja2 import DictLoader, Environment, FileSystemBytecodeCache, Template


# Set up cache directory path
CACHE_DIR = "/tmp/jinja_cache"

# Ensure the cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Set up Jinja2 with Bytecode Cache
bytecode_cache = FileSystemBytecodeCache(
    directory=CACHE_DIR, pattern="jinja_cache_%s.cache"
)

env = Environment(bytecode_cache=bytecode_cache, trim_blocks=True, lstrip_blocks=True)

# Persistent loader
env.loader = DictLoader({})

# Cache for already loaded templates
_template_cache: Dict[str, Template] = {}


def render_template_with_data(
    template_name: str, template_content: str, data: dict
) -> str:
    """
    Render a Jinja2 template with given data, using bytecode caching for efficiency.

    :param template_name: Unique name for the template (used in caching).
    :param template_content: Raw HTML template string.
    :param data: Dictionary containing data to be injected into the template.
    :return: Rendered HTML string.
    """
    # Check in-memory cache first
    cache_key = template_name

    if cache_key not in _template_cache:
        # Clean the template content
        template_content_clean = template_content.replace("\n", "")

        # Add to the loader's mapping (doesn't replace the entire loader)
        env.loader.mapping[template_name] = template_content_clean

        # Get and cache the compiled template
        _template_cache[cache_key] = env.get_template(template_name)

    # Render using cached template
    template = _template_cache[cache_key]
    return template.render(**data)


def clear_template_cache():
    """Clear the in-memory template cache."""
    _template_cache.clear()
    env.loader.mapping.clear()
