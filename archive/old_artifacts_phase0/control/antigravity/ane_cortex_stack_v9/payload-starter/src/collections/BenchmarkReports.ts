export default {
  slug: 'benchmark-reports',
  fields: [
    { name: 'repoId', type: 'text', required: true },
    { name: 'title', type: 'text', required: true },
    { name: 'summary', type: 'textarea' },
    { name: 'findings', type: 'json' },
  ],
};
