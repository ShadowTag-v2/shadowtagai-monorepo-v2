export default {
  slug: 'semantic-memories',
  fields: [
    { name: 'repoId', type: 'text', required: true },
    { name: 'subject', type: 'text', required: true },
    { name: 'summary', type: 'textarea', required: true },
    { name: 'kind', type: 'text' },
    { name: 'evidence', type: 'json' },
  ],
}
