import { promises as fs } from 'node:fs'
import { glob } from 'node:fs/promises'

const out = []
for await (const p of glob('ops/.telemetry/report_*.md')) {
  const text = await fs.readFile(p, 'utf8')
  const stamp = (p.match(/report_(.+)\.md$/) || [,''])[1]
  const vis = /GitHub visibility: \*\*(.+?)\*\*/.exec(text)?.[1] ?? 'UNKNOWN'
  const rows = [...text.matchAll(/\*\*(.+?)\*\*: CPU ([\d.]+)% .* RAM ([\d.]+) MB/g)]
  for (const m of rows) {
    const name = m[1]
    const cpu = Number(m[2])
    const mem = Number(m[3])
    out.push({ stamp, name, cpu, mem, vis })
  }
}

const header = 'stamp,name,cpu,mem,github_visibility\n'
const csv = header + out.map(r=>`${r.stamp},${r.name},${r.cpu},${r.mem},${r.vis}`).join('\n')
await fs.writeFile('ops/.telemetry/telemetry.csv', csv)
console.log('Wrote ops/.telemetry/telemetry.csv with', out.length, 'rows')

