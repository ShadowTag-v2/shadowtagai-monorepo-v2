export default function BlogTeaser() {
  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="blog">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Insights</div>
        <h2 className="section-title">From the KovelAI Blog</h2>
        <div className="glass-card mt-10 max-w-[720px]">
          <div className="blog-teaser-tag">Legal AI · Heppner · Compliance</div>
          <h3 className="text-lg font-semibold text-primary-text mb-3">
            The AI Slop Problem: Why <em>Heppner</em> Changes Everything for Client Web Activity
          </h3>
          <p className="text-sm leading-relaxed text-secondary-text mb-4">
            AI-generated content — &ldquo;AI slop&rdquo; — has flooded the internet. Clients
            googling legal questions now receive hallucinated answers from ChatGPT, Gemini, and
            Perplexity. After <em>Heppner</em>, every one of those AI-mediated searches is
            discoverable. Here&apos;s what that means for your practice and why privilege-first
            infrastructure is no longer optional.
          </p>
          <a
            href="/blog/heppner-ai-slop"
            className="text-sm text-blue hover:text-primary-text transition-colors"
          >
            Read the full analysis →
          </a>
        </div>
      </div>
    </section>
  );
}
