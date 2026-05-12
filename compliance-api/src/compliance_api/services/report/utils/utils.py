"""Shared utility functions for report generation."""
from openpyxl.utils import get_column_letter

from compliance_api.services.epic_track_service.track_service import TrackService


def sort_dataframe_for_pivot_order(data_frame, column_orders):
    """Sort DataFrame rows to control pivot table column field order.

    Excel builds pivot cache item order from first-occurrence in source data.
    By sorting the dataframe so desired values appear first, we ensure the
    pivot cache (and thus column display) follows the desired order.

    Args:
        data_frame: pandas DataFrame to sort
        column_orders: dict mapping column names to desired value order lists
            e.g. {"compliance_finding": ["In", "Out", "Not Determined"]}

    Returns:
        Sorted DataFrame (original is not modified)
    """
    if data_frame.empty:
        return data_frame

    df = data_frame.copy()

    # Build a combined sort key
    # For each column in column_orders, assign a sort priority based on position
    for col, desired_order in column_orders.items():
        if col not in df.columns:
            continue

        # Create mapping: value -> sort priority (lower = first)
        order_map = {val: idx for idx, val in enumerate(desired_order)}
        # Values not in desired_order get a high priority (appear after)
        max_priority = len(desired_order)

        # Add temporary sort column
        sort_col = f"_sort_{col}"
        df[sort_col] = df[col].map(lambda v: order_map.get(v, max_priority))

    # Sort by all the temporary columns
    sort_cols = [c for c in df.columns if c.startswith("_sort_")]
    if sort_cols:
        df = df.sort_values(by=sort_cols, kind="stable")
        # Remove temporary columns
        df = df.drop(columns=sort_cols)

    return df.reset_index(drop=True)


def get_project_details(project_map, row):
    """Resolve project name/type from approved and unapproved project sources."""
    # Project Logic:
    # If case_file.project_id is null it is unapproved
    # and you should be able to find it in the unapproved_projects table
    # If case_file.project_id has a valid number it should be from EPIC.Track
    if not row.project_id:
        project_name = row.unapproved_project_name
        project_type = row.unapproved_project_type
    else:
        if row.project_id in project_map:
            project = project_map[row.project_id]
        else:
            date = row.case_file_date_created.date() if row.case_file_date_created else None
            project = TrackService.get_project_by_id(row.project_id, as_of_date=date)
            project_map[row.project_id] = project
        project_name = project.get("name") if project else None
        project_type = project.get("type", None).get("name", None) if project else None

    return project_name, project_type


@staticmethod
def populate_template_table_sheet(workbook, sheet_name, data_frame, columns, headers):
    """Populate a template worksheet table while preserving workbook pivot structure."""
    worksheet = workbook[sheet_name]
    table = next(iter(worksheet.tables.values()), None)

    if table is None:
        raise ValueError(f"Template sheet '{sheet_name}' does not contain an Excel table.")

    min_col = 1
    min_row = 1
    table_column_count = len(getattr(table, "tableColumns", []) or [])
    if table_column_count < 1:
        raise ValueError(f"Template sheet '{sheet_name}' table has no columns.")
    max_col = table_column_count

    table_headers = [
        worksheet.cell(row=min_row, column=column_number).value
        for column_number in range(min_col, max_col + 1)
    ]

    header_to_column_key = dict(zip(headers, columns))

    special_headers = {"Index", "Unique Key"}
    unknown_headers = [
        header for header in table_headers
        if header not in special_headers and header not in header_to_column_key
    ]
    if unknown_headers:
        raise ValueError(
            f"Template sheet '{sheet_name}' has unmapped headers: {unknown_headers}"
        )

    records = data_frame.reindex(columns=columns).to_dict("records")

    last_used_row = max(worksheet.max_row, min_row + 1)
    for row_number in range(min_row + 1, last_used_row + 1):
        for column_number in range(min_col, max_col + 1):
            worksheet.cell(row=row_number, column=column_number).value = None

    for row_index, record in enumerate(records, start=1):
        excel_row = min_row + row_index
        for col_offset, header in enumerate(table_headers):
            column_number = min_col + col_offset
            if header == "Index":
                value = row_index
            elif header == "Unique Key":
                value = record.get("enforcement_document_number")
            else:
                column_key = header_to_column_key[header]
                value = record.get(column_key)
            worksheet.cell(row=excel_row, column=column_number).value = value

    new_last_row = min_row + max(len(records), 1)
    table.ref = (
        f"{get_column_letter(min_col)}{min_row}:"
        f"{get_column_letter(max_col)}{new_last_row}"
    )


def reorder_pivot_column_items(workbook, field_name, desired_order):
    """Reorder pivot field items to enforce a specific column display order.

    Sets sortType='manual' and reorders items in pivotField.items to control
    the display order. Does NOT set refreshOnLoad to avoid Excel rebuilding
    the item order from cache.
    """
    # Collect all unique pivot caches from worksheets
    pivot_cache_pairs = []  # List of (cache, pivot) tuples

    for worksheet in workbook.worksheets:
        if not hasattr(worksheet, '_pivots'):
            continue
        for pivot in worksheet._pivots:
            cache = pivot.cache
            if cache is not None:
                pivot_cache_pairs.append((cache, pivot))

    # Group pivots by cache
    cache_to_pivots = {}
    for cache, pivot in pivot_cache_pairs:
        cache_id = id(cache)
        if cache_id not in cache_to_pivots:
            cache_to_pivots[cache_id] = {'cache': cache, 'pivots': []}
        cache_to_pivots[cache_id]['pivots'].append(pivot)

    for cache_data in cache_to_pivots.values():
        cache = cache_data['cache']
        pivots = cache_data['pivots']

        # Find the cache field matching field_name and record its index
        field_idx = None
        cache_field = None
        for idx, cf in enumerate(cache.cacheFields):
            if cf.name == field_name:
                field_idx = idx
                cache_field = cf
                break

        if field_idx is None or cache_field is None:
            continue
        if not hasattr(cache_field, 'sharedItems') or cache_field.sharedItems is None:
            continue
        if not hasattr(cache_field.sharedItems, '_fields'):
            continue

        shared_items = cache_field.sharedItems._fields
        if not shared_items:
            continue

        # Build cache_index -> value mapping (don't modify sharedItems order)
        cache_idx_to_value = {}
        for i, item in enumerate(shared_items):
            if hasattr(item, 'v'):
                cache_idx_to_value[i] = item.v

        # Update all pivot tables using this cache
        for pivot in pivots:
            if field_idx >= len(pivot.pivotFields):
                continue

            pivot_field = pivot.pivotFields[field_idx]
            if pivot_field.items is None:
                continue

            # Separate data items (have a cache index) from subtotal/blank items
            data_items = [item for item in pivot_field.items if item.x is not None]
            other_items = [item for item in pivot_field.items if item.x is None]

            # Sort data items by position in desired_order (unknowns go last)
            def sort_key(item):
                val = cache_idx_to_value.get(item.x, "")
                try:
                    return (0, desired_order.index(val))
                except ValueError:
                    return (1, item.x)  # Unknowns go last, in cache order

            data_items.sort(key=sort_key)
            pivot_field.items = data_items + other_items
            pivot_field.sortType = "manual"
            pivot_field.autoSort = False  # Disable auto-sorting

        # Do NOT set refreshOnLoad - that causes Excel to rebuild item order from cache
        # cache.refreshOnLoad = True
