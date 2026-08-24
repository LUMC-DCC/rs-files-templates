# rs-files-templates

Reusable, typed generators for standardized research-software project files.

```{mermaid}
flowchart LR
    A[Application data] --> M[Per-file Pydantic model]
    M --> R[Renderer]
    R --> J[Jinja template]
    J --> F[Generated file]
    F --> V{Schema available?}
    V -->|yes| S[Schema validation]
    V -->|no| D[Done]
    S --> D
```

## Start here

- **[Using](using/index.md)** — install the package and generate individual project files.
- **[Developing](developing/index.md)** — add models and templates or work on the rendering API.

```{toctree}
:maxdepth: 2
:caption: Using
:hidden:

using/index
using/quickstart
using/models
using/validation
```

```{toctree}
:maxdepth: 2
:caption: Developing
:hidden:

developing/index
developing/architecture
developing/adding-templates
developing/contracts
developing/testing
developing/api
```
