'use client';

export default function FAQ() {
  const faqs = [
    {
      q: 'What is the Kovel Doctrine?',
      a: "The Kovel Doctrine (from United States v. Kovel, 296 F.2d 918) extends attorney-client privilege to non-attorney agents — like accountants, interpreters, or technology platforms — working under the attorney's direction. When you deploy KovelAI for your clients, their web searches and AI interactions operate under your firm's privilege umbrella. The attorney stays in the loop, provides the first legal opinion, and the client gets protected access to research without risk of discovery. After In re Heppner, this isn't optional — it's the standard of care.",
    },
    {
      q: 'How does KovelAI protect my client?',
      a: "Your clients are already searching the internet about their case — Google, ChatGPT, Reddit. Every one of those searches is discoverable. KovelAI gives you a turnkey portal to deploy for your clients so their research happens inside your privilege umbrella. Instead of getting ambushed by random, discoverable AI searches, you see everything they search, provide the first legal opinion, and keep a complete, privileged archive. The client relaxes enough to recall all the facts of their case — and opposing counsel can't touch any of it.",
    },
    {
      q: 'Is my client data stored anywhere?',
      a: "No. KovelAI uses zero-retention architecture. All data is processed in RAM only and never written to disk. Session data is cryptographically shredded when the session ends. The data that doesn't exist can't be subpoenaed, can't be breached, and can't be discovered.",
    },
    {
      q: 'What happened in In re Heppner?',
      a: 'In In re Heppner (S.D.N.Y., Feb. 10, 2026), the court ruled that client internet search histories conducted outside of attorney-supervised channels are discoverable in litigation. This includes Google searches, AI chatbot interactions, and any web activity not routed through a privileged infrastructure. KovelAI gives attorneys a turnkey portal to deploy for their clients — routing all that activity through your privilege umbrella so the client can research freely and you maintain oversight.',
    },
    {
      q: 'How does billing work?',
      a: "You purchase CounselConduit as infrastructure for your clients — like a police chief buying bulletproof vests for the force. The client logs in with their credit card, which serves as both authentication and payment method. You set the session rate in compliance with the Rules of Professional Responsibility. The client's card is billed at the end of each billing cycle, and you receive payment automatically. No invoicing, no collections, no overhead. You monitor usage, you provide the first legal opinion, and you get paid.",
    },
    {
      q: 'What AI model does KovelAI use?',
      a: 'KovelAI uses Google Gemini 2.5 Flash via Vertex AI, governed by the Judge 6 Compliance Framework — a risk matrix that evaluates every query before execution. The model never trains on your data, and all inference happens within our zero-retention pipeline. Your client gets AI-powered research; you get a clean, privileged archive of everything they explored.',
    },
    {
      q: 'What does the attorney see?',
      a: "Everything. The attorney monitoring dashboard gives you real-time visibility into your client's research sessions — what they searched, what the AI responded, and how long they spent. You provide the first legal opinion before the client acts on anything. No more getting blindsided by a client who Googled their way into a bad strategy. You sit in the loop, maintain privilege, and bill automatically.",
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
