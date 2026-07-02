from .config import config_namespace, make_path_getter
from .rules import (
    bool_flag, auto_bool_flag, optional_flag,
    format_params, format_command
)
from .runtime import setup_tmpdir_getter, rule_resources_getter, conda_env_getter


annotations_getter = make_path_getter('annotation_dir', ancient=True, protected=True)
raw_data_getter = make_path_getter('raw_data_dir', ancient=True, protected=True)
results_getter = make_path_getter('results_dir')