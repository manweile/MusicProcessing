---
applyTo: "components/server/web/**/*.css"
---

# CSS Instructions

## Purpose
- Keep CSS focused on the ESP32-hosted dashboard assets served by the server component.
- Prefer simple, readable, low-risk styling that is easy to maintain alongside the embedded firmware codebase.
- Treat CSS as a lightweight presentation layer, not as a place for application logic or workflow state.

## General Rules
- Keep changes minimal and buildable.
- Prefer plain CSS; do not introduce preprocessors, bundlers, frameworks, or generated styles.
- Do not add external CSS dependencies, icon packs, font CDNs, or browser-side build tooling.
- Keep file structure simple and compatible with SPIFFS-hosted static assets.
- Prefer deterministic, explicit rules over clever abstractions.

## Scope And Architecture
- Restrict dashboard CSS to presentation concerns only.
- Do not encode business logic, protocol assumptions, or state-machine behavior into CSS structure.
- Keep styling compatible with separate HTML, CSS, and JavaScript assets.
- Prefer one shared stylesheet unless a second file is clearly justified by asset separation requirements.

## Naming And Organization
- Use clear, descriptive class names based on purpose or section.
- Prefer simple class-based selectors over deep descendant selectors.
- Avoid overly specific selectors that make later dashboard iteration harder.
- Group rules by page section in this order when practical:
  1. page or app shell
  2. system information
  3. controls
  4. workflow output
  5. propane data
  6. utility or state classes

## Layout Guidance
- Mobile-first by default.
- Prefer straightforward layout techniques such as:
  - flexbox for one-dimensional alignment
  - CSS grid for the control layout when row/column structure matters
- Keep layouts robust for both:
  - desktop development use
  - tablet and phone production use
- Avoid fragile pixel-perfect positioning.
- Avoid absolute positioning unless it is clearly necessary.

## Visual Style
- Prefer a clean, utilitarian interface over decorative styling.
- Use conservative spacing, borders, and contrast.
- Keep typography simple and system-font based.
- Do not rely on hover-only behavior for important interactions.
- Ensure controls remain usable on touch devices.

## State Styling
- Use CSS classes for visual states such as:
  - success
  - warning
  - error
  - disabled
  - active
- Keep state names semantic and reusable.
- Do not hide critical status information using color alone; support clarity through labels, layout, or emphasis.

## Responsiveness
- Design for narrow screens first, then widen progressively.
- Use breakpoints only when needed to improve readability or control layout.
- For Milestone 5B, ensure the control grid can collapse cleanly on smaller screens without losing workflow clarity.

## Maintainability
- Reuse shared spacing, sizing, and color patterns consistently.
- Prefer small, obvious rule sets over large theme systems.
- Remove dead rules when markup changes.
- Avoid unused selectors and speculative styling for features that do not yet exist.

## Forbidden Additions
- No CSS frameworks.
- No Sass, Less, Tailwind, or generated utility layers.
- No animation libraries.
- No hidden dependency on JavaScript-generated class names that are undocumented.
- No styling that assumes production dashboard features before those features exist.

## Milestone-Specific Guidance
- Milestone 5A Hello World:
  - keep styling intentionally minimal
  - style only the page shell, button, and output field needed for the proof of interaction
  - avoid prematurely adding dashboard grids, cards, or complex responsive systems
- Milestone 5B Dashboard:
  - expand styling only as needed to support the required section order and control layout
  - keep the workflow output prominent and readable
  - prioritize clarity of status, controls, and propane data over visual polish

## Validation
- Verify the stylesheet works when served directly from SPIFFS as a static asset.
- Verify the page remains usable on both desktop and mobile-sized screens.
- Verify changes do not depend on unavailable external assets.
- Keep the CSS easy to inspect and debug in a normal browser during local dashboard development.