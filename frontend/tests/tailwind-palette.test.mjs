// Regression tests for the Tailwind config.
// Bug: custom colors defined directly under `theme` replaced Tailwind's default
// palette, so classes like bg-blue-600 were never generated and the UI looked
// unstyled (the Upload button was white text on a white background).

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname, extname } from 'node:path'
import { fileURLToPath } from 'node:url'
import postcss from 'postcss'
import tailwindcss from 'tailwindcss'
import config from '../tailwind.config.js'

const FRONTEND = join(dirname(fileURLToPath(import.meta.url)), '..')
const SRC = join(FRONTEND, 'src')

// Color families the UI uses, both from Tailwind's default palette and from the
// custom palette in tailwind.config.js.
const PALETTES = 'blue|gray|green|indigo|red|amber|emerald|slate|white|black'
const COLOR_CLASS = new RegExp(
  `(?<![\\w-])((?:[a-z-]+:)*(?:bg|text|border|ring|from|to|via|fill|stroke)-(?:${PALETTES})(?:-\\d{2,3})?)(?![\\w-])`,
  'g',
)

function sourceFiles(dir) {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) return sourceFiles(path)
    return ['.js', '.jsx'].includes(extname(name)) ? [path] : []
  })
}

function colorClassesUsedInSource() {
  const found = new Set()
  for (const file of sourceFiles(SRC)) {
    for (const match of readFileSync(file, 'utf8').matchAll(COLOR_CLASS)) {
      found.add(match[1])
    }
  }
  return [...found].sort()
}

async function buildStylesheet({ content, input } = {}) {
  // Point content at absolute paths so the build does not depend on the cwd.
  const tailwindConfig = {
    ...config,
    content: content ?? [join(FRONTEND, 'index.html'), join(SRC, '**/*.{js,jsx}')],
  }
  const css = input ?? readFileSync(join(SRC, 'index.css'), 'utf8')
  const result = await postcss([tailwindcss(tailwindConfig)]).process(css, {
    from: join(SRC, 'index.css'),
  })
  return result.css
}

// In CSS a class such as hover:bg-blue-700 is written hover\:bg-blue-700.
function isGenerated(css, className) {
  const selector = '.' + className.replace(/:/g, '\\:')
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp(`${escaped}(?![\\w-])`).test(css)
}

test('the app uses at least one color class (sanity check on the scanner)', () => {
  const classes = colorClassesUsedInSource()
  assert.ok(classes.length > 0, 'no color classes found in src/')
  assert.ok(classes.includes('bg-blue-600'), 'expected bg-blue-600 (Upload button) in src/')
})

test('every color class used in src/ is generated in the stylesheet', async () => {
  const css = await buildStylesheet()
  const missing = colorClassesUsedInSource().filter((cls) => !isGenerated(css, cls))
  assert.deepEqual(
    missing,
    [],
    `These classes are used in src/ but missing from the generated CSS: ${missing.join(', ')}`,
  )
})

test('custom palette values still apply (emerald-600 is #16a34a, not the default)', async () => {
  // Use a raw class string so this checks the config itself, not what src/ happens to use.
  const css = await buildStylesheet({
    input: '@tailwind utilities;',
    content: [{ raw: '<div class="bg-emerald-600"></div>' }],
  })
  const rule = css.match(/\.bg-emerald-600\s*\{[^}]*\}/)
  assert.ok(rule, '.bg-emerald-600 rule not generated')
  // #16a34a = rgb(22 163 74). Tailwind's default emerald-600 is #059669 (5 150 105).
  assert.match(rule[0], /22 163 74/)
})
