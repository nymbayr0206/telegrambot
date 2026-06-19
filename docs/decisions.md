# Hermes Decisions

## 2026-06-02

Decision: Add visual agent system as a first-class web dashboard route.

Reason: The user asked to build the Hermes visual agent system, and the existing `web` app already provides routing, sidebar navigation, icons, cards, and dashboard styling.

Impact: The new workflow is visible in the app at `/visual-agents` and can be expanded later with backend-backed project state.

## 2026-06-02

Decision: Keep UI text on the new page in Mongolian.

Reason: The user explicitly required the UI to be in Mongolian.

Impact: Component identifiers and docs file names remain English, while visible workflow copy is Mongolian.

## 2026-06-02

Decision: Store social content brand files under `skills/social-media/brands/<brand>/`.

Reason: Brand assets are part of the social-media skill workflow, and the user needs logo, font, settings, and poster template files visible by brand.

Impact: The dashboard can list, create, upload, preview, and delete files in brand asset folders without inventing a separate storage location.
