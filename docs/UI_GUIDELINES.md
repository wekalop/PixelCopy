# UI Guidelines

## Visual language

Use a restrained blue accent, rounded surfaces, clear Segoe UI typography, consistent spacing, and accessible contrast. Light and dark themes must share hierarchy and focus behavior. Avoid excessive gradients, glass effects, decoration, and animation.

## Navigation and layout

Top-level navigation remains in the left sidebar in this order: Extract, PDF, History, Settings, About. Preserve stable keyboard shortcuts and visible selected state. Pages use a clear title, concise description, and card-based task regions. The Extract page grows into a source workspace on the left and result workspace on the right.

## Interaction states

Every workflow must define empty, loading, progress, cancellation, success, disabled, and actionable error states. Do not expose controls as functional before their milestone; use clear disabled states and honest messaging. Long operations never freeze navigation or editing.

## Accessibility

Provide visible keyboard focus, logical tab order, accessible control names, useful tooltips, sufficient contrast, and native selection/editing behavior. Do not communicate status using color alone. Arabic and mixed text surfaces must set appropriate direction without forcing the whole application into RTL.

The results editor exposes native undo and redo, find and literal replace, select all, clear, line-wrap control, and explicit deterministic cleanup actions. Important shortcuts are `Ctrl+O` (open image), `Ctrl+Return` (extract), `Ctrl+F` (find/replace), `Ctrl+S` (save to enabled history), and `Ctrl+Shift+S` (export). Progress controls and result messages have accessible names and textual state; color is supplementary.

Combo boxes, their popup lists, key-sequence fields, and numeric inputs use the active theme colors in every state. Extract-page options and actions use bounded grids so labels remain readable at the supported 1100×680 minimum window size. The explicit **Copy text** button copies the currently edited result. Settings provides a capture-shortcut recorder that accepts a single key chord such as `Ctrl+X`, `Alt+C`, or `Ctrl+Shift+X`; successful registration updates the Capture tooltip and persists for the next launch.

## Writing

Use short, direct labels and explain recovery steps. Prefer “Could not open this image. The file is damaged or unsupported.” over technical exception text. Keep technical details in logs without including document content.
