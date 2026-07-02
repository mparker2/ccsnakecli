import os
from types import SimpleNamespace
from snakemake.io import ancient as as_ancient, temp as as_tempfile, protected as as_protected


def config_namespace(obj, keep_dict_keys=frozenset()):
    """Convert nested config dictionaries to attribute-access namespaces.

    Parameters
    ----------
    obj : object
        Configuration object to convert. Dictionaries are converted
        recursively, lists are converted element-wise, and scalar values are
        returned unchanged.
    keep_dict_keys : frozenset of str, optional
        Dictionary keys that should remain dictionaries instead of being
        converted to :class:`types.SimpleNamespace`. This is useful for config
        sections such as ``datasets`` where arbitrary user-defined keys are
        expected.

    Returns
    -------
    object
        Converted configuration object. Nested dictionaries are accessible by
        attribute unless their key is listed in ``keep_dict_keys``.
    """
    def convert(value, key=None):
        if isinstance(value, dict):
            converted = {k: convert(v, k) for k, v in value.items()}
            if key in keep_dict_keys:
                return converted
            return SimpleNamespace(**converted)
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value
    return convert(obj)


def get_attr_or_key(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def get_keypath(obj, path, default=None):
    current = obj
    for part in path.split('/'):
        current = get_attr_or_key(current, part)
        if current is None:
            return default
    return current


def resolve_path(basedir, path):
    """Resolve one or more paths relative to a base directory.

    Parameters
    ----------
    basedir : str
        Base directory.
    path : str or list of str
        Relative path or paths to resolve.

    Returns
    -------
    str or list of str
        Path or paths joined to ``basedir``. The return type matches the input
        ``path`` type.
    """
    if isinstance(path, list):
        return [os.path.join(basedir, p) for p in path]
    return os.path.join(basedir, path)


def make_path_getter(config_key, ancient=False, protected=False):
    """Create a config-backed path resolver factory.

    Parameters
    ----------
    config_key : str
        Slash-delimited path to the config value containing the base directory,
        for example ``"annotation_dir"`` or ``"some/nested/key"``.

    Returns
    -------
    callable
        Factory accepting a raw config dictionary and returning a resolver that
        joins paths to the configured base directory.
    """
    def factory(config):
        base = get_keypath(config, config_key)
        def _wrapped(path, temp=False):
            path = resolve_path(base, path)
            if ancient:
                path = as_ancient(path)
            if protected:
                path = as_protected(path)
            elif temp:
                path = as_tempfile(path)
            return path
        return _wrapped
    return factory