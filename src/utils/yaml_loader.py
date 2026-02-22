"""A simple yaml loader

Load the content of a yaml file into a python dict. Environment variable can be specified with ${VAR_NAME}. A
default string value can be specified with ${VAR_NAME:DEFAULT}. Able to process multiple occurrences.

requirement: PyYAML
Based on https://gist.github.com/zobayer1/26e25bf98c8e647e095b48283309fe72
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from yaml.parser import ParserError

_var_matcher = re.compile(r"\${([^}^{]+)}")
_tag_matcher = re.compile(r"[^$]*\${([^}^{]+)}.*")


def _path_constructor(_loader: Any, node: Any):
    def replace_fn(match):
        envparts = f"{match.group(1)}:".split(":")
        return os.environ.get(envparts[0], envparts[1])

    return _var_matcher.sub(replace_fn, node.value)


def load_yaml(config_path: Path) -> dict:
    yaml.add_implicit_resolver("!envvar", _tag_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("!envvar", _path_constructor, yaml.SafeLoader)
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f.read())
    except (FileNotFoundError, PermissionError, ParserError):
        return {}
