# Architecture

Each public model is a projection of `rsm_schema.RSMMetadata` and owns one
packaged template and one output file. Python performs validation and derived
normalization; Jinja renders the final representation.

The README and six documentation-page models use the same RSM-only input contract
as the community-file models. They do not accept repository state, badges, template
variants, builder commands, or presentation settings.

Repository generators can post-process rendered files with repository state.
`rs-repo-templates`, for example, inserts badges for generated workflows and adds
MkDocs, Zensical, Sphinx, or pkgdown configuration.

## Design rules

1. A generated file owns a dedicated Pydantic model.
2. Every model field is selected from published `RSMMetadata`.
3. Models contain only fields needed by their output.
4. Jinja handles presentation; Python handles validation and normalization.
5. Structured output is validated against its format schema when one exists.
6. Compatibility with the published RSM JSON Schema is checked in CI.
7. Archive models represent formats that require a fixed multi-file unit, such as
   GitHub issue forms.
