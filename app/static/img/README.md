# Brand images

Drop the official University of Portsmouth logo here named **`uop-logo.svg`**
(preferred) or `uop-logo.png` / `.jpg`.

The app detects it automatically (see the `inject_brand` context processor in
`app/__init__.py`) and shows it in the sidebar, auth pages, header and error
pages. Until a file is present, a "SM" fallback tile is shown, so nothing breaks.

A logo that reads well on a **white** background works best — it is placed on a
white "chip" so it stays legible on the purple sidebar.
