# UI Guidelines

## Visual language and tokens

Use a restrained blue accent, rounded surfaces, clear Segoe UI typography, consistent spacing, and accessible contrast. Light and dark themes share hierarchy and focus behavior. Avoid excessive gradients, glass effects, decoration, and animation.

`ui.styles.theme` is the single design-system source. `DesignTokens` names colors by purpose: background, surfaces, primary/secondary/muted text, borders, accent states, focus, status, disabled, sidebar, and selected navigation. Shared layout constants use the 4, 8, 12, 16, 20, 24, and 32 device-independent spacing scale. Cards use a 12-pixel radius, controls use a 7-pixel radius, and control height is derived from the active application font metrics with a 36-pixel floor. New UI must reuse these tokens rather than introduce page-local colors or heights.

## Navigation and responsive layout

Top-level navigation remains in the left sidebar in this order: Extract, PDF, History, Settings, About. Preserve stable keyboard shortcuts and a visible selected state. The sidebar is bounded between 184 and 210 logical pixels so content can grow without making navigation unreadable. Pages use a clear title, concise description, and card-based task regions.

The Extract page uses a horizontal `QSplitter`, with non-collapsible source and result panels and a usable 350-pixel minimum for each panel. The main window supports 1024×700 and opens at 1280×800. The preview and editor own the flexible vertical space; action rows and forms do not compress them below their useful minimums. Advanced processing is collapsed by default and uses its own vertically scrollable region when expanded.

Do not add absolute positioning or fixed control heights. Bounded panel widths and scroll areas are allowed where they preserve meaning. Compound controls must receive at least their font-derived size hint. At 1024×720, keep source and result side by side; if future localized strings exceed this width, introduce a deliberate breakpoint rather than letting Qt silently compress controls.

## Interaction states

Every workflow must define empty, loading, progress, cancellation, success, disabled, and actionable error states. Do not expose controls as functional before their milestone; use clear disabled states and honest messaging. Long operations never freeze navigation or editing. Cancel actions are visible only while their operation is active. Before OCR, Extract text is the primary result action; after OCR, Copy text, Export, and the compact More menu replace it.

The source empty state is drawn inside the preview surface and names the drop action, alternative import actions, and supported formats. Processed remains disabled with an explanatory tooltip until a processed image exists. Preview controls use short labels or symbols only when an accessible name and tooltip provide the full meaning.

## Accessibility

Provide visible keyboard focus, logical tab order, accessible control names, useful tooltips, sufficient contrast, and native selection/editing behavior. Do not communicate status using color alone. Arabic and mixed text surfaces set their own direction without forcing the whole application into RTL.

The results editor exposes native undo and redo, find and literal replace, select all, clear, line-wrap control, and deterministic cleanup actions. Important shortcuts are `Ctrl+O` (open image), `Ctrl+Return` (extract), `Ctrl+F` (find/replace), `Ctrl+S` (save to enabled history), and `Ctrl+Shift+S` (export). Progress controls and result messages have accessible names and textual state; color is supplementary.

Combo boxes, popup lists, key-sequence fields, and numeric inputs use active theme colors in every state. Minimum OCR confidence is a bounded 0–100% spin box. Every processing checkbox owns visible descriptive text; native Qt indicators are retained so checked state includes a checkmark instead of relying on color. Editor commands use compact tool buttons with accessible names and tooltips, while less frequent result commands live in the More menu. The explicit Copy text action copies the currently edited result. Settings accepts a single capture key chord such as `Ctrl+X`, `Alt+C`, or `Ctrl+Shift+X`.

## DPI and theme QA

Qt coordinates and spacing are logical pixels. Do not multiply sizes by the screen device-pixel ratio. High-DPI capture conversion remains isolated in the capture service. Verify both themes at 100%, 125%, 150%, and 175% display scaling, and at 1024×720, 1280×800, 1440×900, and 1920×1080. Prefer geometry/state assertions over pixel-perfect screenshots because platform font rendering varies.

For both themes, verify normal, hover, pressed, focus, disabled, checked, popup, progress, menu, tooltip, and scrollbar states. Styling must not reference an image resource for a standard control indicator.

## Writing

Use short, direct labels and explain recovery steps. Prefer “Could not open this image. The file is damaged or unsupported.” over technical exception text. Keep technical details in logs without including document content.
