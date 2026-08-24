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
