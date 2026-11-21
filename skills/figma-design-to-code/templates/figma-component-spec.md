# Figma Component & Handoff Specification

> Use this specification before authoring or connecting any reusable Figma component to production code. Replace `<...>` angle-bracket values with verified Figma and codebase facts; mark unverified rows `NOT ASSESSED` (never `PASS`).

## Metadata

| Field | Value |
|---|---|
| **Component Name** | `<ComponentName>` |
| **Figma File Key & URL** | `<fileKey>` — `<https://www.figma.com/design/...>` |
| **Node ID (Colon Format)** | `<1234:5678>` (converted from URL `node-id=1234-5678`) |
| **Library Publish Status** | `<Published | Unpublished Draft>` |
| **Code Connect Tier** | `<Tier 0 (Skip) | Tier 1 (send_code_connect_mappings) | Tier 2 (.figma.ts) | Tier 3 (Legacy .figma.tsx)>` |
| **Target Code Path** | `<src/components/ui/ComponentName.tsx>` |
| **Owner / Last Verified** | `<Author / YYYY-MM-DD>` |

---

## 1. Variant Matrix (`<= 30` Combination Cap)

Model structural/visual geometry permutations as `VARIANT` axes, and offload text labels, icons, toggles, and arbitrary children to Component Properties (Section 2).

| Axis Name | Values | Count | Maps to Code Prop or Pseudo-State |
|---|---|---:|---|
| `<Variant>` | `<Primary, Secondary, Ghost>` | `<3>` | `<variant: "primary" \| "secondary" \| "ghost">` |
| `<Size>` | `<Sm, Md, Lg>` | `<3>` | `<size: "sm" \| "md" \| "lg">` |
| `<State>` | `<Default, Hover, Focus, Disabled>` | `<4>` | `<CSS :hover/:focus-visible + disabled>` |

- **Total Variant Product**: `<3 x 3 x 4 = 36 -> SPLIT>` (Hard Cap: `<= 30` variants per `ComponentSetNode`; if `> 30`, split by `Style` or extract `.Building Blocks/` subcomponents and document rationale below).
- **Grid Arrangement & Split Rationale**: `<Columns = State; Rows = Size x Variant; or split rationale>`

---

## 2. Component Properties (`TEXT`, `BOOLEAN`, `INSTANCE_SWAP`, `SLOT`)

| Property Name (Exact Case) | Property Type | Default Value | Wired Descendant (`componentPropertyReferences`) | Mapped Code Prop & Type |
|---|---|---|---|---|
| `<Label>` | `TEXT` | `<"Continue">` | `<TextLayer:Label -> characters>` | `<children: ReactNode \| string>` |
| `<ShowLeadingIcon>` | `BOOLEAN` | `<false>` | `<IconSlot -> visible>` | `<Omitted if inferred from leadingIcon != null>` |
| `<LeadingIcon>` | `INSTANCE_SWAP` | `<Icon/Placeholder>` | `<IconSlot -> mainComponent>` | `<leadingIcon?: ReactNode>` |
| `<BodyContent>` | `SLOT` | `<Empty slot frame>` | `<BodySlot -> slotContentId>` | `<children: ReactNode>` |

- **Omitted Non-Code Properties**: `<List Figma-only helper properties intentionally omitted from code Props interface>`

---

## 3. Auto Layout & Responsive Translation Spec

| Layer / Node | `layoutMode` | Primary / Counter Sizing | Child `layoutSizing` (H / V) | Padding & Gap Tokens | Min / Max Bounds | Target Code Layout (`Flex` / `Grid` / `@container` / Native) |
|---|---|---|---|---|---|---|
| `<Root>` | `<HORIZONTAL>` | `<AUTO / FIXED>` | `<HUG / FIXED>` | `<padding: 8px 16px; gap: 8px>` | `<minH: 44px; maxW: none>` | `<inline-flex items-center gap-2 min-h-11 px-4 py-2>` |
| `<Content>` | `<VERTICAL>` | `<FIXED / AUTO>` | `<FILL / HUG>` | `<padding: 0; gap: 4px>` | `<minW: 0>` | `<flex-1 min-w-0 flex flex-col gap-1>` |

- **Wrapping & Overflow Rule**: `<Describe textAutoResize='HEIGHT', line-clamp, or truncate behavior>`
- **Responsive Reflow (`320px / 390px / 768px / 1440px`)**: `<Describe how fixed desktop frames adapt via clamp(), minmax(), or container queries>`

---

## 4. Variable Bindings & Code Syntax

| Visual Property | Figma Variable Path | Variable Scope (Non-`ALL_SCOPES`) | `WEB` Code Syntax (`var(--...)`) | `iOS` / `ANDROID` Syntax | Light & Dark Verified |
|---|---|---|---|---|---|
| `<Background Fill>` | `<color/bg/accent>` | `<FRAME_FILL, SHAPE_FILL>` | `<var(--color-bg-accent)>` | `<Color.bgAccent / colorBgAccent>` | `<Yes | No>` |
| `<Label Fill>` | `<color/text/on-accent>` | `<TEXT_FILL>` | `<var(--color-text-on-accent)>` | `<Color.textOnAccent>` | `<Yes | No>` |
| `<Border Radius>` | `<radius/md>` | `<CORNER_RADIUS>` | `<var(--radius-md)>` | `<Radius.md / radiusMd>` | `<N/A>` |
| `<Item Spacing>` | `<spacing/2>` | `<GAP>` | `<var(--space-2)>` | `<Spacing.s2 / space2>` | `<N/A>` |

- **Unbound Raw Overrides Audit**: `<Confirm 0 raw hexes/pixels on published library layers, or list tracked exceptions>`

---

## 5. States, Accessibility Annotations & Asset Manifest

- **Interactive & Edge States Covered**: `<Default, Hover, Focus-Visible, Active, Disabled, Loading, Error, Empty, Long-Text Wrapping>`
- **Accessibility Annotations**:
  - **Semantic Element & ARIA**: `<Native <button type="button">, aria-disabled, aria-busy, aria-describedby>`
  - **Keyboard Contract**: `<Tab focusable, Enter/Space activates, Escape closes if overlay>`
  - **Contrast & Touch Target**: `<Text >= 4.5:1 APCA/WCAG AA; hit area >= 44x44px (or >= 24x24px minimum)>`
- **Exported Asset Manifest**:

| Asset Name | Format & Scale | Local Repo Path (Committed) | Dimensions & Sizing Rule |
|---|---|---|---|
| `<brand-mark>` | `<SVG (SVGO clean)>` | `<src/assets/icons/brand-mark.svg>` | `<24x24px explicit box; img width:100% height:100%>` |
| `<hero-card-art>` | `<WebP @1x/@2x + fallback PNG>` | `<public/images/hero-card@2x.webp>` | `<Explicit width/height attributes; 0 CLS>` |

---

## 6. Simplicity & Readiness Gate Sign-Off

- **Simplicity Q1/Q2 Check**: `<State why existing primitives/props could not be simplified further and confirm zero redundant Auto Layout wrapper groups>`
- **Code Connect Status**: `<Tier 0 skipped (rationale) | Tier 1 mapped via send_code_connect_mappings | Tier 2 .figma.ts verified>`
- **Handoff Gate Verdict**: `<PASS | CONCERNS | NOT ASSESSED | FAIL>`
