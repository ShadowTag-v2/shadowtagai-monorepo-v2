import React from 'react';

/**
 * A2UI JSON Schema Definition:
 * 
 * Base Widget:
 * {
 *   "type": "markdown" | "kv" | "list" | "form" | "actions",
 *   "title": "Optional Title",
 *   "data": ... (varies by type)
 * }
 */

const MarkdownWidget = ({ content }) => (
  <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>{content}</div>
);

const KVWidget = ({ data }) => (
  <div className="a2ui-kv-grid" style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem', fontSize: '0.9rem' }}>
    {Object.entries(data).map(([key, value]) => (
      <React.Fragment key={key}>
        <div style={{ color: '#8b949e', fontWeight: 'bold' }}>{key}:</div>
        <div style={{ color: '#c9d1d9' }}>{value}</div>
      </React.Fragment>
    ))}
  </div>
);

const ListWidget = ({ items }) => (
  <ul style={{ margin: '0', paddingLeft: '1.2rem' }}>
    {items.map((item, idx) => (
      <li key={idx} style={{ marginBottom: '0.25rem' }}>{item}</li>
    ))}
  </ul>
);

const FormWidget = ({ fields, onSubmit }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    onSubmit(Object.fromEntries(formData));
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {fields.map((field) => (
        <label key={field.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <span style={{ fontSize: '0.8rem', color: '#8b949e' }}>{field.label}</span>
          <input 
            type={field.type || 'text'} 
            name={field.name} 
            placeholder={field.placeholder}
            style={{ padding: '0.5rem', background: '#0d1117', border: '1px solid #30363d', color: 'white', borderRadius: '4px' }}
          />
        </label>
      ))}
      <button type="submit" style={{ marginTop: '0.5rem' }}>Submit</button>
    </form>
  );
};

export const A2UIRenderer = ({ payload, onAction }) => {
  if (!payload) return null;

  // If payload is just a string, treat as markdown/text
  if (typeof payload === 'string') {
    return <MarkdownWidget content={payload} />;
  }

  const { type, title, data } = payload;

  return (
    <div className="a2ui-widget" style={{ border: '1px solid #30363d', borderRadius: '6px', padding: '1rem', marginTop: '0.5rem', background: '#161b22' }}>
      {title && <h3 style={{ marginTop: 0, fontSize: '1rem', borderBottom: '1px solid #30363d', paddingBottom: '0.5rem', marginBottom: '1rem' }}>{title}</h3>}
      
      {type === 'markdown' && <MarkdownWidget content={data} />}
      {type === 'kv' && <KVWidget data={data} />}
      {type === 'list' && <ListWidget items={data} />}
      {type === 'form' && <FormWidget fields={data.fields} onSubmit={(vals) => onAction('form_submit', vals)} />}
      
      {/* Error Fallback */}
      {!['markdown', 'kv', 'list', 'form'].includes(type) && (
        <div style={{ color: 'red' }}>Unknown widget type: {type}</div>
      )}
    </div>
  );
};
