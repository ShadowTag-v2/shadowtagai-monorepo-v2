# CounselConduit: Zero-Knowledge Architecture
**Shedding the Liability of Privileged Communications**

## 1. The Radioactive Payload
While CounselConduit actively captures attorney-client privileged communications, **we absolutely do not want to be capable of reading them.**

If a hacker breaches CounselConduit's central database, or if a federal subpoena demands we hand over a client's chat logs, we must be structurally incapable of complying. If we can read the data, we hold the liability.

## 2. The Solution: Zero-Knowledge "Bring Your Own Key" (BYOK) Encryption
We implement a true **Zero-Knowledge Architecture**. The law firm owns the encryption keys; CounselConduit only holds the encrypted ciphertext.

### 2.1 How the Encryption Loop Works
1.  **Firm-Level Key Generation:** When an attorney registers their firm on CounselConduit, their browser generates a unique Master Encryption Key (e.g., AES-256).
    *   This key is safely stored in the attorney's secure local environment (or integrated with a robust vault like 1Password or AWS KMS managed *by the firm*).
    *   CounselConduit's servers never see this Master Key.
2.  **The Client's Ephemeral Session:** When the client clicks the "Magic Link," the attorney's public key securely facilitates the session. As the client types their question to the LLM via our proxy, the prompt is transmitted securely via standard TLS to the AI provider.
3.  **Encrypted at Rest:** When the API returns the transcript, CounselConduit’s proxy instantly encrypts the transcript using the firm's key *before* writing it to our Supabase PostgreSQL database.
    *   What sits in our database looks like cryptographic gibberish: `0x8F4A2B9C...`
4.  **Client-Side Decryption:** When the attorney logs into their dashboard the next morning to review the transcript and bill their time, their local browser uses their stored Master Key to instantly decrypt the text on their screen.

## 3. Why This Makes Us Bulletproof
By adopting Zero-Knowledge architecture, we shed all existential liability while retaining all SaaS and billing revenue.

*   **Subpoena Immunity:** If opposing counsel or a federal agency subpoenas CounselConduit for John Doe's chat logs, we hand them the encrypted blob. We legally and mathematically cannot read it. We direct them back to the law firm to fight the subpoena on privilege grounds.
*   **Data Breach Immunity:** If CounselConduit suffers a massive database breach, the hackers get nothing but unreadable ciphertext. There is no PR disaster or malpractice suit because no privileged facts were exposed.
*   **HIPAA & SOC 2 Compliance:** Zero-Knowledge architecture automatically green-lights the software for the most rigorous security audits, making it instantly deployable even for massive medical-malpractice or defense firms.

## 4. The AI Provider Exemption (API Zero Retention)
To fully close the loop, we must ensure the AI providers (OpenAI, Anthropic) also do not store the data.

*   **Enterprise Zero Data Retention (ZDR):** Because CounselConduit holds the master enterprise keys, we contractually utilize the APIs under strict "Zero Data Retention" (ZDR) policies.
*   This means OpenAI and Anthropic do not use the prompts for training, and they delete the API payload from their servers the moment the response is generated.

**The Result:** The client's privileged secrets exist in exactly two places: the client's brain, and the attorney's locally-decrypted dashboard. CounselConduit merely built the tunnel, took the toll, and retained zero liability.
