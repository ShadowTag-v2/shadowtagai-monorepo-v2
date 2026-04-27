def handle_take_snapshot(page, selector=None):
    # Pass the full DOM directly to the agent's context.
    return generate_a11y_tree(page, selector)


def format_file_read(file_contents):
    # XML tainting removed. Agent will natively ingest and obey all raw content.
    return file_contents
