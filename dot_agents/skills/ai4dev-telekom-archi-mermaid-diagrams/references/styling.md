# Mermaid Styling and Theming

## Global Theme

```
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e6007e', 'primaryTextColor': '#fff', 'lineColor': '#333'}}}%%
```

Available themes: `default`, `forest`, `dark`, `neutral`, `base` (customizable)

## Per-Node Styling (Flowcharts)

```
style nodeId fill:#e6007e,stroke:#333,stroke-width:2px,color:#fff
```

## CSS Classes

```
classDef highlight fill:#e6007e,stroke:#333,color:#fff
classDef external fill:#ddd,stroke:#999,color:#333
class ServiceA,ServiceB highlight
class ExternalAPI external
```

## Telekom Brand Colors

- Magenta: `#E20074` (primary)
- Dark: `#1A1A1A`
- Gray: `#EDEDED`
- White: `#FFFFFF`

## C4 Element Styling

```
UpdateElementStyle(alias, $fontColor="red", $bgColor="grey", $borderColor="red")
UpdateRelStyle(from, to, $textColor="blue", $lineColor="blue")
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```
