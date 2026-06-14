# Advanced Mermaid Features

Advanced configuration, styling, theming, and other powerful features for creating professional diagrams.

## Contents

- [YAML Configuration](#yaml-configuration)
- [Themes](#themes)
- [Custom Theme Variables](#custom-theme-variables)
- [Layout Options](#layout-options)
- [Look Options](#look-options)
- [Complete Configuration Example](#complete-configuration-example)
- [Flowchart Styling](#flowchart-styling)
- [Subgraph Styling](#subgraph-styling)
- [Click Events and Links](#click-events-and-links)
- [Comments and Documentation](#comments-and-documentation)
- [Complex Styling Example](#complex-styling-example)
- [Accessibility Tips](#accessibility-tips)
- [Performance Tips](#performance-tips)
- [Integration](#integration)
- [Best Practices](#best-practices)

## YAML Configuration

Add YAML configuration at the top of diagrams:

```mermaid
---
config:
  theme: dark
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#fff"
    primaryBorderColor: "#333"
    lineColor: "#666"
---
flowchart TD
    A --> B
```

## Themes

### Built-in Themes

| Theme | Description |
|-------|-------------|
| `default` | Standard blue theme |
| `forest` | Green earth tones |
| `dark` | Dark mode friendly |
| `neutral` | Grayscale professional |
| `base` | Minimal, customization-ready |

### Theme Examples

```mermaid
---
config:
  theme: dark
---
flowchart LR
    A[Start] --> B[Process]
    B --> C{Decision}
```

```mermaid
---
config:
  theme: forest
---
flowchart LR
    A[Start] --> B[Process]
```

## Custom Theme Variables

Override specific colors:

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#fff"
    primaryBorderColor: "#d63031"
    lineColor: "#74b9ff"
    secondaryColor: "#00b894"
    tertiaryColor: "#fdcb6e"
    background: "#f0f0f0"
    mainBkg: "#ffffff"
    textColor: "#333333"
    nodeBorder: "#333333"
    clusterBkg: "#f9f9f9"
    clusterBorder: "#666666"
---
flowchart TD
    A --> B --> C
```

## Layout Options

### Dagre Layout (Default)

```mermaid
---
config:
  layout: dagre
---
flowchart TD
    A --> B
```

### ELK Layout (Advanced)

For complex diagrams with better automatic layout:

```mermaid
---
config:
  layout: elk
  elk:
    mergeEdges: true
    nodePlacementStrategy: BRANDES_KOEPF
---
flowchart TD
    A --> B
```

**ELK node placement strategies:**

- `SIMPLE` - Basic placement
- `NETWORK_SIMPLEX` - Network optimization
- `LINEAR_SEGMENTS` - Linear arrangement
- `BRANDES_KOEPF` - Balanced (default)

## Look Options

### Classic Look

```mermaid
---
config:
  look: classic
---
flowchart LR
    A --> B --> C
```

### Hand-Drawn Look

```mermaid
---
config:
  look: handDrawn
---
flowchart LR
    A --> B --> C
```

## Complete Configuration Example

```mermaid
---
config:
  theme: base
  look: handDrawn
  layout: dagre
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#fff"
    primaryBorderColor: "#d63031"
    lineColor: "#74b9ff"
---
flowchart TD
    Start([Begin]) --> Input[Gather Data]
    Input --> Process{Valid?}
    Process -->|Yes| Store[(Save)]
    Process -->|No| Error[Show Error]
    Store --> End([Complete])
```

## Flowchart Styling

### Class-based Styling

```mermaid
flowchart TD
    A[Success]:::success
    B[Warning]:::warning
    C[Error]:::error

    classDef success fill:#00b894,stroke:#00a383,color:#fff
    classDef warning fill:#fdcb6e,stroke:#e8b923,color:#333
    classDef error fill:#ff6b6b,stroke:#ee5253,color:#fff

    A --> B --> C
```

### Node-specific Styling

```mermaid
flowchart LR
    A[Node A]
    B[Node B]

    style A fill:#ff6b6b,stroke:#333,stroke-width:4px
    style B fill:#4ecdc4,stroke:#333,stroke-width:2px

    A --> B
```

### Link Styling

```mermaid
flowchart LR
    A --> B --> C

    linkStyle 0 stroke:#ff6b6b,stroke-width:4px
    linkStyle 1 stroke:#4ecdc4,stroke-width:2px
```

## Subgraph Styling

```mermaid
flowchart TB
    subgraph Frontend
        A[Web App]
        B[Mobile App]
    end

    subgraph Backend
        C[API]
        D[Database]
    end

    A & B --> C --> D

    style Frontend fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style Backend fill:#fff3e0,stroke:#ff9800,stroke-width:2px
```

## Click Events and Links

Add interactive elements:

```mermaid
flowchart LR
    A[GitHub]
    B[Documentation]

    click A "https://github.com" "Go to GitHub"
    click B "https://mermaid.js.org" "View Docs"

    A --> B
```

## Comments and Documentation

```mermaid
flowchart TD
    %% This is a single-line comment

    %% Multi-line comments use
    %% multiple comment lines

    A[Start]
    B[Process]

    %% Define relationships
    A --> B

    %% Add styling
    style A fill:#90EE90
```

## Complex Styling Example

```mermaid
flowchart TB
    subgraph production[Production]
        direction LR
        lb[Load Balancer]

        subgraph servers[App Servers]
            app1[Server 1]
            app2[Server 2]
        end

        cache[(Redis)]
        db[(PostgreSQL)]
    end

    subgraph monitoring[Monitoring]
        logs[Logs]
        metrics[Metrics]
    end

    users[Users] --> lb
    lb --> app1 & app2
    app1 & app2 --> cache & db
    app1 & app2 --> logs --> metrics

    style production fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style servers fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style monitoring fill:#e3f2fd,stroke:#2196f3,stroke-width:2px

    classDef serverClass fill:#81c784,stroke:#4caf50,stroke-width:2px
    class app1,app2 serverClass

    linkStyle 0,1,2 stroke:#4caf50,stroke-width:2px
```

## Accessibility Tips

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#0066cc"
    primaryTextColor: "#ffffff"
    primaryBorderColor: "#003d7a"
    lineColor: "#333333"
---
flowchart TD
    A[High Contrast] --> B[Clear Labels]
```

- Use high contrast color combinations
- Don't rely solely on color to convey meaning
- Include descriptive text labels
- Test with color blindness simulators

## Performance Tips

For large diagrams:

```mermaid
---
config:
  layout: elk
  elk:
    mergeEdges: true
---
flowchart TD
    %% ELK handles complex layouts better
    %% Merge edges reduces visual clutter
```

- Use ELK layout for diagrams with >20 nodes
- Enable edge merging for simplified connections
- Split very large diagrams into multiple views
- Use subgraphs to organize complexity
- Limit styling to essential elements

## Integration

### Markdown Files

````markdown
# Architecture

```mermaid
flowchart LR
    A --> B
```
````

### HTML

```html
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
        startOnLoad: true,
        theme: 'dark'
    });
</script>

<pre class="mermaid">
    flowchart LR
        A --> B
</pre>
```

### React

```jsx
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: true,
    theme: 'forest'
});

function Diagram() {
    useEffect(() => {
        mermaid.contentLoaded();
    }, []);

    return (
        <div className="mermaid">
            flowchart LR
                A --> B
        </div>
    );
}
```

## Curve Types for Flowcharts

Control edge routing via frontmatter:

```mermaid
---
config:
  flowchart:
    curve: stepBefore
---
flowchart LR
    A --> B --> C
```

Options: `basis`, `bumpX`, `bumpY`, `cardinal`, `catmullRom`, `linear`, `monotoneX`, `monotoneY`, `natural`, `step`, `stepAfter`, `stepBefore`

## Diagram-Specific Theme Variables

### Sequence Diagrams

`actorBkg`, `actorBorder`, `actorTextColor`, `actorLineColor`, `signalColor`, `signalTextColor`, `labelBoxBkgColor`, `labelBoxBorderColor`, `activationBorderColor`, `activationBkgColor`, `sequenceNumberColor`

### Pie Charts

`pie1`–`pie12`, `pieTitleTextSize`, `pieTitleTextColor`, `pieSectionTextSize`, `pieStrokeColor`

### Timeline

`cScale0`–`cScale11` (section colors), `disableMulticolor` (config flag)

## Theme Gotchas

- Theme engine only accepts hex colors (e.g., `#ff0000`) — not CSS color names
- Only the `base` theme supports full `themeVariables` customization
- Derived variables are computed automatically from primary colors

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Use themes consistently** — Same theme for related diagrams
3. **Don't over-style** — Too many colors reduces clarity
4. **Test hand-drawn look** — Some diagrams work better with classic
5. **Use ELK for complex layouts** — When dagre creates crossed lines
6. **Comment configurations** — Explain non-obvious styling
7. **Keep accessible** — Sufficient color contrast
8. **Test exports** — Verify rendering in target format
9. **Version control configs** — Track theme changes
