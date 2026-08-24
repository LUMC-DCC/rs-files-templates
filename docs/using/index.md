# Using

Use one Pydantic model per output file. Models validate inputs before Jinja sees them, and each
model knows its packaged template, output filename, media type, and optional output schema.
