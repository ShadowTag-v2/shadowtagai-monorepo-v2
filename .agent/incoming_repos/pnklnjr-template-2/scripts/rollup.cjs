#!/usr/bin/env node
const fs = require('fs')
const glob = require('glob')

const files = glob.sync('docs/**/*.{md,mdx,txt}', { nodir: true })
const buckets = { KEEP: [], REFERENCE: [], DISCARD: [] }

for (const f of files){
  const content = fs.readFileSync(f,'utf8')
  const tag = (content.match(/#\s*(KEEP|REFERENCE ONLY|DISCARD)/i)?.[1] || '').toUpperCase()
  if (tag === 'KEEP') buckets.KEEP.push(f)
  else if (tag.startsWith('REFERENCE')) buckets.REFERENCE.push(f)
  else buckets.DISCARD.push(f)
}

const out = `# Exec Roll-Up
- KEEP: ${buckets.KEEP.length}
- REFERENCE ONLY: ${buckets.REFERENCE.length}
- DISCARD: ${buckets.DISCARD.length}

## KEEP
${buckets.KEEP.map(x=>`- ${x}`).join('\n')}

## REFERENCE ONLY
${buckets.REFERENCE.map(x=>`- ${x}`).join('\n')}

## DISCARD
${buckets.DISCARD.map(x=>`- ${x}`).join('\n')}
`
fs.writeFileSync('ROLLUP.md', out)
console.log('✅ ROLLUP.md generated.')

