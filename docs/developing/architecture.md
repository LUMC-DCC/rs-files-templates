# Architecture

```{mermaid}
flowchart TD
    I[Caller] --> C1[CitationModel]
    I --> C2[CodeMetaModel]
    I --> C3[SecurityModel]
    I --> CN[Future file models]

    C1 --> B[FileTemplateModel]
    C2 --> B
    C3 --> B
    CN --> B

    C1 --> T1[CITATION.cff.j2]
    C2 --> T2[codemeta.json.j2]
    C3 --> T3[SECURITY.md.j2]

    T1 --> O1[CITATION.cff]
    T2 --> O2[codemeta.json]
    T3 --> O3[SECURITY.md]

    O1 --> S1[CFF schema]
    O2 --> S2[CodeMeta schema]
```

## Design rules

1. A generated file owns a dedicated Pydantic model.
2. Models contain only fields needed by that file.
3. Common nested concepts come from the published `rsm-schema` package.
4. Jinja handles presentation; Python handles validation and non-trivial normalization.
5. Structured output is validated against its format schema when one exists.
6. Compatibility with the published RSM JSON Schema is checked in CI.
