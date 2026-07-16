# UI Guidelines

## Visual language

Use a restrained blue accent, rounded surfaces, clear Segoe UI typography, consistent spacing, and accessible contrast. Light and dark themes must share hierarchy and focus behavior. Avoid excessive gradients, glass effects, decoration, and animation.

## Navigation and layout

Top-level navigation remains in the left sidebar in this order: Extract, PDF, History, Settings, About. Preserve stable keyboard shortcuts and visible selected state. Pages use a clear title, concise description, and card-based task regions. The Extract page grows into a source workspace on the left and result workspace on the right.

## Interaction states

Every workflow must define empty, loading, progress, cancellation, success, disabled, and actionable error states. Do not expose controls as functional before their milestone; use clear disabled states and honest messaging. Long operations never freeze navigation or editing.

## Accessibility

Provide visible keyboard focus, logical tab order, accessible control names, useful tooltips, sufficient contrast, and native selection/editing behavior. Do not communicate status using color alone. Arabic and mixed text surfaces must set appropriate direction without forcing the whole application into RTL.

## Writing

Use short, direct labels and explain recovery steps. Prefer “Could not open this image. The file is damaged or unsupported.” over technical exception text. Keep technical details in logs without including document content.
