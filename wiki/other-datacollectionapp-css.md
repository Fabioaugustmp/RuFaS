# Other — DataCollectionApp-css

# DataCollectionApp — font-awesome.css

## Overview

`font-awesome.css` is a vendored copy of **Font Awesome 4.0.3**, a classic icon font stylesheet. It provides the DataCollectionApp's UI with a scalable icon system driven by a custom web font. The file defines the `@font-face` declaration that loads the icon font, the base `.fa` class that activates icon rendering, and roughly 400 icon glyph mappings that map CSS class names (e.g., `fa-save`, `fa-trash-o`) to Unicode private-use-area code points in the font.

This is a static asset — it has no JavaScript, no runtime logic, and no dependencies on other modules. It is consumed by the application's HTML templates and other stylesheets.

## File Structure

The stylesheet is organized into five logical sections:

| Section | Purpose |
|---|---|
| `@font-face` declaration | Registers the `FontAwesome` font family and points to the font files in `../fonts/` |
| Base `.fa` class | Sets the font family, inline-block display, and text rendering hints |
| Sizing & layout utilities | `.fa-lg`, `.fa-2x` … `.fa-5x`, `.fa-fw`, `.fa-ul`, `.fa-li`, `.fa-border`, `.pull-left`/`.pull-right` |
| Animation & transforms | `.fa-spin`, `.fa-rotate-*`, `.fa-flip-*`, `.fa-stack*` |
| Icon glyph definitions | ~400 `.fa-*:before` rules mapping class names to font code points |

## Key Components

### Font Loading

The `@font-face` rule registers the `FontAwesome` family and provides four font formats for cross-browser compatibility:

```css
@font-face {
  font-family: 'FontAwesome';
  src: url('../fonts/fontawesome-webfont.eot?v=4.0.3');
  src: url('../fonts/fontawesome-webfont.eot?#iefix&v=4.0.3') format('embedded-opentype'),
       url('../fonts/fontawesome-webfont.woff?v=4.0.3') format('woff'),
       url('../fonts/fontawesome-webfont.ttf?v=4.0.3') format('truetype'),
       url('../fonts/fontawesome-webfont.svg?v=4.0.3#fontawesomeregular') format('svg');
  font-weight: normal;
  font-style: normal;
}
```

The `?v=4.0.3` query string is a cache-busting mechanism — bumping the version forces browsers to re-download the font after an upgrade. The font files themselves live in `DataCollectionApp/fonts/`, one directory up from this stylesheet.

### Base Icon Class

Every icon is rendered by applying the `.fa` class to an element (typically an `<i>` or `<span>`), followed by a specific icon class:

```html
<i class="fa fa-save"></i>
```

The `.fa` class sets:

- `display: inline-block` — allows the icon to be sized and transformed like a block element while remaining inline
- `font-family: FontAwesome` — activates the icon font
- `font-style: normal` and `font-weight: normal` — prevents inherited italics/bold from distorting glyphs
- `-webkit-font-smoothing: antialiased` and `-moz-osx-font-smoothing: grayscale` — improves glyph rendering on macOS

### Sizing Utilities

Icons scale relative to the surrounding font size:

| Class | Effect |
|---|---|
| `.fa-lg` | 1.33× with adjusted line-height and vertical alignment |
| `.fa-1_25x` | 1.25× |
| `.fa-1_5x` | 1.5× |
| `.fa-2x` … `.fa-5x` | 2× through 5× |

Note the underscore in `.fa-1_25x` and `.fa-1_5x` — CSS class names cannot contain a literal dot, so the decimal point is replaced with an underscore.

Additional layout helpers:

- `.fa-fw` — fixed width (1.2857em) for aligning icons in vertical lists
- `.fa-ul` / `.fa-li` — replaces standard list bullets with icons
- `.fa-border` — adds a subtle border and padding for a "badge" look
- `.pull-left` / `.pull-right` — floats the icon with appropriate margin

### Animation and Transforms

- `.fa-spin` — infinite 2-second linear rotation, with `@keyframes spin` defined for all major browsers (including `-webkit-`, `-moz-`, `-o-`, and `-ms-` prefixes)
- `.fa-rotate-90` / `-180` / `-270` — fixed rotation, with an IE `filter` fallback
- `.fa-flip-horizontal` / `.fa-flip-vertical` — mirror transforms, also with IE filter fallbacks
- `.fa-stack` / `.fa-stack-1x` / `.fa-stack-2x` — overlays two icons (e.g., a small icon on a larger circle/square background); `.fa-inverse` turns the foreground icon white

### Icon Glyph Definitions

The bulk of the file consists of rules like:

```css
.fa-save:before,
.fa-floppy-o:before {
  content: "\f0c7";
}
```

Each rule uses the `:before` pseudo-element to inject a character from the font's **Private Use Area** (Unicode range `\f000`–`\f196`). Screen readers ignore these code points, so the icons are purely decorative and do not pollute accessibility trees.

Many icons have aliases — for example, `fa-gear` and `fa-cog` map to the same glyph, as do `fa-save`/`fa-floppy-o` and `fa-rotate-left`/`fa-undo`. This preserves backward compatibility with older class names.

## Usage in the Application

Icons are used throughout the DataCollectionApp's HTML templates. Typical patterns:

```html
<!-- Action button -->
<button class="btn btn-primary">
  <i class="fa fa-save"></i> Save Record
</button>

<!-- Navigation -->
<a href="/dashboard"><i class="fa fa-home"></i> Dashboard</a>

<!-- Status indicator -->
<span class="fa-stack">
  <i class="fa fa-circle fa-stack-2x"></i>
  <i class="fa fa-check fa-stack-1x fa-inverse"></i>
</span>
```

Because the file is a static stylesheet, it has no call graph, execution flow, or runtime entry points. It is loaded once via a `<link>` tag (or bundled by the app's build pipeline) and applies globally.

## Integration Notes

- **Font files required**: The stylesheet will not render icons unless the four font files (`fontawesome-webfont.eot`, `.woff`, `.ttf`, `.svg`) are present in `DataCollectionApp/fonts/`. If icons appear as empty boxes or "tofu" characters, the font files are missing or the relative path is broken.
- **Version pinning**: This is Font Awesome 4.0.3, an older major version. The class naming scheme (`fa-*`) differs from Font Awesome 5+ (which uses `fas`/`far`/`fab` prefixes). Do not mix class names from different major versions.
- **No JavaScript dependency**: Unlike Font Awesome 5's SVG/JS mode, this CSS-only approach requires no script tags and works in any environment that loads the stylesheet.
- **IE compatibility**: The file includes `filter` fallbacks for IE's `BasicImage` transform, and the `@-ms-keyframes` block for the spin animation, indicating the app still targets legacy browsers.