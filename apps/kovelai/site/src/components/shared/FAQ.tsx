'use client';

export default function FAQ() {
  const faqs = [
    {
      q: 'What is the Kovel Doctrine?',
      a: "The Kovel Doctrine (from United States v. Kovel, 296 F.2d 918) extends attorney-client privilege to non-attorney agents — like accountants, interpreters, or technology platforms — working under the attorney's direction. When you deploy KovelAI for your clients, it operates as a Kovel agent under your firm's privilege umbrella. Your clients get protected search access; you get visibility and billing. After In re Heppner, this is no longer optional.",
    },
    {
      q: 'Is my client data stored anywhere?',
      a: "No. KovelAI uses zero-retention architecture. All data is processed in RAM only and never written to disk. Session data is cryptographically shredded when the session ends. The data that doesn't exist can't be subpoenaed, can't be breached, and can't be discovered.",
    },
    {
      q: 'What happened in In re Heppner?',
      a: 'In In re Heppner (S.D.N.Y., Feb. 10, 2026), the court ruled that client internet search histories conducted outside of attorney-supervised channels are discoverable in litigation. This includes Google searches, AI chatbot interactions, and any web activity not routed through a privileged infrastructure. The ruling created the post-Heppner compliance gap. KovelAI gives attorneys a turnkey portal to deploy for their clients — closing that gap with privileged search infrastructure.',
    },
    {
      q: 'How does billing work?',
      a: "You purchase CounselConduit for your clients — like issuing equipment to your team. Clients log in with their credit card, which serves as both authentication and payment method. You set the session rate. The client's card is billed at the end of each cycle, and you receive payment in full compliance with the Rules of Professional Responsibility. No invoicing, no collections, no overhead.",
    },
    {
      q: 'What AI model does KovelAI use?',
      a: 'KovelAI uses Google Gemini 2.5 Flash via Vertex AI, governed by the Judge 6 Compliance Framework — a risk matrix that evaluates every query before execution. The model never trains on your data, and all inference happens within our zero-retention pipeline.',
    },
    {
      q: 'Does KovelAI support SOC 2 / HIPAA-aligned practices?',
      a: 'KovelAI is pursuing SOC 2 Type II certification with assessment scheduling underway. Our zero-retention architecture means no PHI is ever stored, providing a HIPAA-supportive foundation for healthcare law practices. Enterprise plans include dedicated compliance officer support and custom retention policy configuration.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="faq">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Frequently Asked</div>
        <h2 className="section-title">Common Questions</h2>
        <div className="max-w-[720px] mt-10">
          {faqs.map((f) => (
            <details key={f.q} className="faq-item">
              <summary>{f.q}</summary>
              <div className="faq-answer">{f.a}</div>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
