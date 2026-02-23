# Format detection

When you don't specify `--format`, deck2video auto-detects whether a file is Marp or Slidev by inspecting frontmatter and body content.

## Detection priority chain

The detection algorithm checks six signals in order. The first match wins:

| Priority | Signal | Result |
|----------|--------|--------|
| 1 | `marp: true` in frontmatter | Marp |
| 2 | Slidev-only key in frontmatter | Slidev |
| 3 | Marp directive comment in body | Marp |
| 4 | Vue/Slidev component in body | Slidev |
| 5 | No signals found | Marp (fallback) |

### Step 1: Parse YAML frontmatter

The detector reads the first `---` block (everything between the opening `---\n` and the next `\n---`).

### Step 2: check for `marp: true`

If the frontmatter contains `marp: true` on its own line, detection returns **Marp** immediately. This is the strongest and most explicit signal.

```yaml
---
marp: true
theme: gaia
---
```

### Step 3: check for Slidev-only frontmatter keys

If any frontmatter line starts with a key that's unique to Slidev, detection returns **Slidev**. The recognized Slidev-only keys are:

- `transition`
- `clicks`
- `drawings`
- `routerMode`
- `aspectRatio`
- `canvasWidth`
- `themeConfig`
- `fonts`
- `favicon`
- `titleTemplate`

Example:

```yaml
---
transition: slide-left
fonts:
  sans: Inter
---
```

Keys that are common to both formats (like `theme` or `title`) are not used as signals.

### Step 4: check for Marp directive comments

After frontmatter, the detector scans the body for Marp-style directive comments:

```markdown
<!-- _class: lead -->
<!-- paginate: false -->
<!-- backgroundColor: #2d2d2d -->
```

The full list of directive keywords recognized:

`class`, `paginate`, `header`, `footer`, `backgroundColor`, `backgroundImage`, `backgroundPosition`, `backgroundRepeat`, `backgroundSize`, `color`, `theme`, `math`, `size`, `style`, `headingDivider`

Matching is case-insensitive. Both `<!-- class: ... -->` and `<!-- _class: ... -->` are recognized.

### Step 5: check for Vue/Slidev components

The detector looks for Vue component tags that are specific to Slidev:

- `<v-click>`
- `<v-clicks>`
- `<v-after>`
- `<v-click-hide>`
- `<Arrow>`
- `<RenderWhen>`
- `<SlidevVideo>`

If any of these appear in the body, detection returns **Slidev**.

### Step 6: Fallback

If none of the above signals are found, the format defaults to **Marp**. Plain markdown with `---` delimiters and HTML comments has always been treated as Marp, so this preserves backward compatibility.

## Overriding detection

Use `--format` to bypass auto-detection entirely:

```bash
# Force Marp
python -m deck2video deck.md --format marp

# Force Slidev
python -m deck2video deck.md --format slidev
```

When `--format` is set to `marp` or `slidev`, the detection step is skipped completely.

## When auto-detection gets it wrong

**Ambiguous decks.** A markdown file with no `marp: true`, no Slidev-specific frontmatter keys, no directive comments, and no Vue components defaults to Marp. If it's actually a Slidev deck, use `--format slidev`.

**Shared frontmatter keys.** Keys like `theme` are used by both formats. A deck with `theme: seriph` (a Slidev theme) and no other signals will be detected as Marp. Add a Slidev-specific key like `transition` to the frontmatter, or use `--format slidev`.

**Comments that look like directives.** If your speaker notes happen to start with a directive keyword (e.g., `<!-- class dismissed, let's move on -->`), the Marp directive filter will consume that comment. Unlikely in practice, but worth knowing about.

## Logging

Detection decisions are logged at the INFO level. When debugging, check the log file in the temp directory (`deck2video.log`) for lines like:

```
Detected Marp format (marp: true in frontmatter)
Detected Slidev format (frontmatter key: transition)
Detected Marp format (directive comments in body)
No format signals found, defaulting to Marp
```
