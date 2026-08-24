# Adding a template

For a text-oriented generated file:

1. Add a Jinja template under `src/rs_files_templates/templates/`.
2. Add a model in its own `models/<template>.py` module, derived with
   `rsm_template_base()` from the smallest useful set of `RSMMetadata` fields.
3. Set `template_name`, `output_name`, and, when applicable, `schema_url` and `media_type`.
4. Reuse nested models from `rsm_schema.generated`. Put cross-template normalization helpers in
   `models/utils.py`.
5. Add rendering tests and a schema-backed test when the output format publishes a schema.
6. Add the model to the public package exports.

Keep complex transformations in the per-template model. Jinja should make the output structure
obvious and primarily decide layout and optional sections.

## Bundling several files into one archive

Some targets (such as GitHub issue forms) require several files at fixed relative paths, so the
platform reads them as a group. Render this as one archive model instead of one model per file:

1. Add a Jinja template per archive member under `templates/`, as usual.
2. Set `media_type = "zip"` and `output_name` to the `.zip` path.
3. Override `archive_entries()` to return `{member filename: rendered content}`, rendering each
   member with `renderer.render_template(template_name, data)`.
4. Leave `template_name` pointing at the primary (or first) member template for documentation;
   `render_text()` is not used for archive models.

`render_file()` detects `media_type == "zip"` and writes `archive_entries()` as a zip instead of
writing `render_text()` as a single file.
