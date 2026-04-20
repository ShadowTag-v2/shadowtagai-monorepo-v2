import { Linkedin, ShieldCheck } from 'lucide-react';

export default function TeamSection() {
  const founders = [
    {
      name: 'Erik Hancock',
      role: 'Principal Architect',
      linkedin: 'https://linkedin.com/in/[LINKEDIN-ID]',
      img: 'https://via.placeholder.com/150', // ACTION: Replace with real photo
      bio: 'Ex-Google Cloud Principal. Built ShadowTag architecture.',
    },
    {
      name: '[CO-FOUNDER NAME REQUIRED]',
      role: 'Head of Governance',
      linkedin: 'https://linkedin.com/in/[LINKEDIN-ID]',
      img: 'https://via.placeholder.com/150', // ACTION: Replace with real photo
      bio: 'Specialist in AI Safety and Sovereign Infrastructure.',
    },
  ];

  return (
    <section className="py-24 border-t border-tension bg-void" id="team">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center gap-4 mb-12">
          <ShieldCheck className="w-6 h-6 text-accent" />
          <h2 className="text-2xl font-mono text-starlight tracking-tight">COMMAND_STRUCTURE</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {founders.map((f, i) => (
            <div
              key={i}
              className="group relative p-6 bg-surface border border-tension rounded-xl hover:border-accent transition-colors duration-300"
            >
              <div className="flex items-start gap-6">
                <div className="w-20 h-20 rounded bg-tension overflow-hidden grayscale group-hover:grayscale-0 transition-all">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={f.img} alt={f.name} className="w-full h-full object-cover" />
                </div>
                <div>
                  <h3 className="text-xl font-sans text-starlight font-medium">{f.name}</h3>
                  <div className="text-accent font-mono text-xs uppercase tracking-wider mb-2">
                    {f.role}
                  </div>
                  <p className="text-ghost text-sm mb-4 leading-relaxed">{f.bio}</p>
                  <a
                    href={f.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-ghost hover:text-white text-xs font-mono uppercase transition-colors"
                  >
                    <Linkedin className="w-3 h-3" />
                    Verification_Link
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 p-4 border border-burn/20 bg-burn/5 rounded text-center">
          <p className="text-burn font-mono text-xs">
            ⚠️ COMPLIANCE NOTICE: This section must be updated with real Founder identities to meet
            Google Start Tier requirements.
          </p>
        </div>
      </div>
    </section>
  );
}
