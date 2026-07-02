import csv
import keyword
from dataclasses import dataclass, field
from types import SimpleNamespace


def _validate_attribute_name(name, *, label):
    if not name:
        raise ValueError(f'{label} must not be empty')
    if not name.isidentifier() or keyword.iskeyword(name):
        raise ValueError(f'{label} {name!r} is not a valid Python attribute name')


@dataclass
class BidirectionalMapping:
    """Bidirectional mapping between parent keys and child values.

    Parameters
    ----------
    parent_to_children : dict, optional
        Mapping where each key is a parent and each value is a list of children.
        The reverse child-to-parent mapping is built automatically.
    """

    parent_to_children: dict = field(default_factory=dict)
    child_to_parent: dict = field(init=False)

    def __post_init__(self):
        self.child_to_parent = {}
        for parent, children in self.parent_to_children.items():
            for child in children:
                if child in self.child_to_parent:
                    raise ValueError(f'Child {child!r} is assigned to multiple parents')
                self.child_to_parent[child] = parent

    def get_parent(self, child):
        """Return the parent for a child."""
        return self.child_to_parent[child]

    def get_children(self, parent):
        """Return children assigned to a parent."""
        return self.parent_to_children[parent]


@dataclass
class MetadataTable:
    """Metadata table with direct access to rows by index value.

    Rows are indexed by ``index_col``. Each row is stored as a
    :class:`types.SimpleNamespace` with attributes matching the CSV column names.
    ``map_cols`` are exposed as bidirectional mappings from column values
    (parents) to index values (children).
    """

    _rows_by_index: dict
    _index_col: str
    _columns: list
    _index: list
    _mappings: dict

    @classmethod
    def read_csv(cls, csv_fn, sep=',', index_col='sample_id', map_cols=None):
        """Read metadata from a delimited text file.

        Parameters
        ----------
        csv_fn : str or pathlib.Path
            Metadata filename.
        sep : str, optional
            Field delimiter passed to :class:`csv.DictReader`.
        index_col : str, optional
            Column used to index rows and define direct row attributes.
        map_cols : list of str, optional
            Columns used to build bidirectional mappings.
        """
        map_cols = [] if map_cols is None else list(map_cols)

        with open(csv_fn, newline='') as handle:
            reader = csv.DictReader(handle, delimiter=sep)
            columns = reader.fieldnames
            if not columns:
                raise ValueError(f'Metadata file {csv_fn!r} has no header row')

            for column in columns:
                _validate_attribute_name(column, label='Column name')

            if index_col not in columns:
                raise ValueError(f'Index column {index_col!r} is not present in {csv_fn!r}')

            for column in map_cols:
                if column not in columns:
                    raise ValueError(f'Mapping column {column!r} is not present in {csv_fn!r}')

            rows_by_index = {}
            index = []
            mapping_values = {column: {} for column in map_cols}

            for line_number, row in enumerate(reader, start=2):
                index_value = row[index_col]
                _validate_attribute_name(
                    index_value,
                    label=f'Value in index column {index_col!r} on line {line_number}',
                )
                if index_value in rows_by_index:
                    raise ValueError(
                        f'Duplicate value {index_value!r} in index column {index_col!r} '
                        f'on line {line_number}'
                    )

                rows_by_index[index_value] = SimpleNamespace(**row)
                index.append(index_value)

                for column in map_cols:
                    parent = row[column]
                    mapping_values[column].setdefault(parent, []).append(index_value)

        mappings = {
            column: BidirectionalMapping(parent_to_children=parent_to_children)
            for column, parent_to_children in mapping_values.items()
        }

        return cls(
            _rows_by_index=rows_by_index,
            _index_col=index_col,
            _columns=columns,
            _index=index,
            _mappings=mappings,
        )

    def __getitem__(self, index_value):
        """Return the row namespace for an index value."""
        return self._rows_by_index[index_value]

    def __getattr__(self, name):
        try:
            return self._rows_by_index[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def get(self, index_value):
        """Return the row namespace for an index value."""
        return self[index_value]

    def get_columns(self):
        """Return metadata column names."""
        return list(self._columns)

    def get_index(self):
        """Return index values in file order."""
        return list(self._index)

    def get_index_col(self):
        """Return the index column name."""
        return self._index_col

    def get_mapping(self, column):
        """Return the bidirectional mapping for a mapping column."""
        return self._mappings[column]

    def get_mapping_cols(self):
        """Return column names with bidirectional mappings."""
        return list(self._mappings)
