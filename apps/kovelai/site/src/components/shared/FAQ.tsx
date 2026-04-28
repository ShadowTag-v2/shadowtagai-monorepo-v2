// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

'use client';

export default function FAQ() {
  const faqs = [
    {
      q: 'What is KovelAI / CounselConduit?',
      a: "KovelAI is a privileged research environment you deploy for your clients. Their web searches, AI queries, translations, and transcriptions flow through a secure connection to your firm. CounselConduit is the engine that routes all client research through your privilege umbrella. You monitor every session, give the first legal opinion, and bill the client's credit card automatically. It's another tool in your arsenal to best represent your client.",
    },
    {
      q: 'Who is the buyer? Who is the user?',
      a: 'You — the attorney — are the buyer. Like a police chief buying bulletproof vests for the force, you purchase KovelAI as privileged infrastructure for your clients. Your clients are the users. They log in with their credit card, search freely through your portal, and their research stays privileged. You sit in the oversight seat and monitor the entire cycle.',
    },
    {
      q: 'How do I convince my client to use it?',
      a: "The conversation is straightforward: 'Knowing the Heppner decision, the other side can and will likely obtain all AI and web searching you do outside our firm\\'s KovelAI portal. Either you do it through us, or proceed at your peril.' That\\'s the pitch. The client understands the risk and is happy to pay for protection — it\\'s their case on the line.",
    },
    {
      q: 'What happened in In re Heppner?',
      a: 'In In re Heppner (S.D.N.Y., Feb. 10, 2026), the court ruled that client internet search histories conducted outside of attorney-supervised channels are discoverable in litigation. This includes Google searches, AI chatbot interactions, and any web activity not routed through a privileged infrastructure. KovelAI gives you a turnkey portal to deploy for your clients — routing all that activity through your privilege umbrella.',
    },
    {
      q: 'What does the Kovel Doctrine have to do with it?',
      a: "The Kovel Doctrine (from United States v. Kovel, 296 F.2d 918) extends attorney-client privilege to non-attorney agents working under the attorney's direction — like accountants, interpreters, or technology platforms. When you deploy KovelAI for your clients, their web searches and AI interactions operate under your firm's privilege umbrella. After Heppner, this isn't optional — it's the standard of care.",
    },
    {
      q: 'How does billing work?',
      a: "You set the session rate in compliance with the Rules of Professional Responsibility. Your client logs in with their credit card — which serves as both authentication and payment method. At the end of each billing cycle, the client's card is charged automatically. No invoicing, no collections, no overhead. You monitor usage, you give the first legal opinion, and you get paid.",
    },
    {
      q: 'What does the attorney see?',
      a: 'Everything. The attorney oversight dashboard gives you real-time visibility into every client research session — what they searched, what the AI responded, and when they were active. You give the first legal opinion before the client acts on anything. No more getting blindsided by a client who Googled their way into a bad strategy or texted you incorrect AI-generated conclusions at 3 AM.',
    },
    {
      q: 'How does KovelAI protect my client from themselves?',
      a: 'Your clients will search — with or without you. Without KovelAI, they Google their case, ask ChatGPT for legal opinions, and send you discoverable research at random hours. They irritate you with incorrect AI conclusions and create ammunition for the other side. KovelAI puts you in an oversight position on all case-related research. The client searches freely and relaxes enough to recall all the facts. You see everything first. The privilege holds. It stays between the two of you.',
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
