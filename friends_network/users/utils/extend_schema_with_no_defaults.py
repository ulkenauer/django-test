from drf_spectacular.utils import extend_schema_view
from drf_spectacular.utils import extend_schema


def extend_schema_view_no_defaults(**kwargs):
    return extend_schema_view(
        list=extend_schema(exclude=True),
        retrieve=extend_schema(exclude=True),
        create=extend_schema(exclude=True),
        update=extend_schema(exclude=True),
        partial_update=extend_schema(exclude=True),
        destroy=extend_schema(exclude=True),
    )
