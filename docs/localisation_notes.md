# Question 3 — Localization Evaluation Notes

## Overview

This document evaluates the localization capability of the AI voice assistant across two different markets:

- Philippines (Filipino / Tagalog)
- Indonesia (Bahasa Indonesia)

The evaluation focuses on:

- Speech recognition configuration (ASR)
- Voice generation configuration (TTS)
- Cultural localization versus direct translation
- Customer conversation patterns
- Code-switching behavior
- Objection handling
- Knowledge-grounded responses
- Human-agent escalation
- Known testing limitations

The goal of localization is not only to translate words but also to ensure that conversations feel natural, culturally appropriate, and aligned with how customers communicate in real-world scenarios.

---

# 1. ASR / TTS Configuration

| Market | ASR Provider / Model | Language Code | TTS Voice |
|---|---|---|---|
| Philippines | Deepgram Nova-3 | `tl` | Elliot |
| Indonesia | Deepgram Nova-3 | `id` | Elliot |

## Configuration Details

### Philippines

The assistant was configured to support Filipino (Tagalog) conversations using:

- ASR Language: `tl`
- Speech Recognition Model: Deepgram Nova-3
- Voice Output: Elliot TTS voice

The evaluation focused on:

- Filipino conversational style
- Respectful speech patterns
- Handling of insurance terminology
- Customer objection management

---

### Indonesia

The assistant was configured to support Bahasa Indonesia conversations using:

- ASR Language: `id`
- Speech Recognition Model: Deepgram Nova-3
- Voice Output: Elliot TTS voice

The evaluation focused on:

- Financial terminology recognition
- Customer repayment discussions
- Formal and informal Bahasa usage
- Loan assistance conversations

---

# 2. Localization Approach

Localization differs from translation.

A translation system attempts to convert words from one language to another.

A localized conversational AI adapts:

- Tone
- Cultural expectations
- Customer communication patterns
- Common vocabulary
- Level of formality
- Customer relationship style

The evaluation checked whether the assistant responses sounded like a natural local customer interaction rather than a translated script.

---

# 3. Philippines Localization Evaluation

## Scenario

The AI assistant handled a health insurance lead qualification conversation.

The customer:

- Did not have existing health insurance
- Requested information about available options
- Raised concerns about premium affordability
- Requested to speak with a human representative

---

# Localization Examples — Philippines

| Literal Translation | Localized Implementation | Why It Is Better |
|---|---|---|
| "Do you have a couple of minutes to chat?" translated directly into Tagalog | "May ilang minuto po ba kayo?" | Uses the Filipino respectful marker `po` and follows the natural way Filipinos ask permission during conversations. |
| Direct disagreement when handling pricing objections | "Naiintindihan ko po" before providing alternatives | Filipino conversations generally value acknowledgment and empathy before presenting solutions. This avoids sounding argumentative. |
| Directly transferring a customer to an agent after a request | "Oo po. Maaari ko po kayong i-connect sa isang insurance specialist..." | Provides reassurance before escalation and maintains a polite customer experience. |

---

# Transcript Evidence — Philippines

## Respectful Conversation Style

Assistant:

> "Hi po, si Alex ito galing sa HDFC. Tumatawag po ako tungkol sa isang insurance option na maaaring bagay sa inyo. May ilang minuto po ba kayo?"

Observation:

- The assistant uses respectful Filipino communication patterns.
- The use of "po" creates a more natural customer-service interaction.

---

## Objection Handling

Customer:

> "Mahal masyado yung premium."

Assistant:

> "Naiintindihan ko po."

Observation:

The assistant acknowledges the concern before providing additional information.

This follows a common Filipino customer-service expectation:

1. Recognize customer concern.
2. Show empathy.
3. Provide possible next steps.

The response avoids directly challenging the customer or defending the product price.

---

## Human Escalation

Customer:

> "Pwede bang makausap yung taong mismo, hindi bot?"

Assistant:

> "Oo po. Maaari ko po kayong i-connect sa isang insurance specialist na makakatulong sa inyo."

Observation:

The assistant:

- Recognized the escalation request.
- Did not attempt to force continued automation.
- Maintained polite communication.
- Offered a smooth handoff process.

---

# 4. Indonesia Localization Evaluation

## Scenario

The AI assistant handled a loan repayment assistance conversation.

The customer:

- Asked about an upcoming installment payment.
- Requested reduction of installments.
- Explained temporary financial difficulty.
- Requested assistance from a human representative.

---

# Localization Examples — Indonesia

| Literal Translation | Localized Implementation | Why It Is Better |
|---|---|---|
| Using formal/legal translation for "Penalty" | Using common customer-facing terms such as "denda", "cicilan", and "jatuh tempo" | These terms are commonly understood by Indonesian customers and sound natural in financial conversations. |
| Using only formal Bahasa Indonesia | Mixing formal and conversational expressions based on customer tone | Real Indonesian conversations commonly shift between formal and casual language depending on customer comfort. |
| Rejecting installment reduction directly | Explaining available options such as restructuring and tenure extension | Provides assistance-oriented communication instead of a simple refusal. |

---

# Transcript Evidence — Indonesia

## Financial Terminology Handling

Customer:

> "Saya mau tanya soal cicilan yang jatuh tempo."

Observation:

The assistant correctly maintained common Indonesian financial terminology:

- Cicilan
- Jatuh tempo
- Restrukturisasi
- Tenor

These terms match how customers normally discuss loan repayment topics.

---

## Handling Financial Difficulty

Customer:

> "Bulan ini agak susah bayarannya nih. Ada solusi nggak?"

Assistant:

> "Tentu. Bapak/Ibu dapat mengajukan penjadwalan ulang atau perpanjangan tenor agar cicilan bulanan menjadi lebih ringan."

Observation:

The assistant:

- Recognized the customer's financial difficulty.
- Avoided unsupported promises.
- Provided available assistance options.
- Guided the customer toward appropriate resolution paths.

---

## Human Escalation

Customer:

> "Bisa saya bicara sama orang aslinya, bukan robot?"

Assistant:

> "Baik. Saya akan menyambungkan Anda dengan tim kami yang dapat membantu secara langsung."

Observation:

The assistant:

- Identified explicit escalation intent.
- Completed the handoff process.
- Avoided unnecessary questioning.

---

# 5. Code-Switching Behavior Observed

## Philippines

### Observed Behavior

The conversation remained primarily Filipino, while commonly used English business terms were naturally included.

Examples:

- Health insurance
- Premium
- Licensed insurance agent
- Insurance specialist

Observation:

The assistant handled Filipino-English terminology naturally without forcing full translation of commonly used industry terms.

Filipino conversations frequently contain English loanwords, especially in professional and financial contexts.

---

## Indonesia

### Observed Behavior

The conversation remained primarily Bahasa Indonesia.

Common financial terms were preserved:

- Cicilan
- Jatuh tempo
- Restrukturisasi
- Tenor

Observation:

The assistant maintained domain-specific Indonesian terminology instead of replacing commonly used words with unnecessary English equivalents.

---

# 6. Observed ASR Performance

## Philippines

### Results

The Filipino conversation was successfully recognized and processed.

Observed capabilities:

- Tagalog speech recognition worked correctly.
- Respectful conversational phrases were understood.
- Insurance-related terminology was handled successfully.

No major ASR failures were observed in the evaluated transcript.

### Future Validation Areas

Additional testing should include:

- Different Filipino accents.
- Faster conversational speech.
- Background noise conditions.
- More Taglish conversations.

---

## Indonesia

### Results

The Bahasa Indonesia conversation was successfully recognized and processed.

Observed capabilities:

- Financial terminology was correctly understood.
- Loan-related customer queries were handled successfully.
- Common Indonesian expressions were recognized.

No major ASR failures were observed in the evaluated transcript.

### Future Validation Areas

Additional testing should include:

- Regional accents.
- Informal customer conversations.
- Higher variation in pronunciation.

---

# 7. Indonesian Regional Accent Performance

## Current Testing Status

Testing was limited to standard Bahasa Indonesia pronunciation.

No dedicated evaluation was performed with speakers from different Indonesian regions.

Potential regional variations include:

- Java
- Sumatra
- Bali
- Sulawesi
- Other local dialect influences

## Known Gap

Regional accent performance requires additional validation using native speakers from multiple regions.

Production deployment should include:

- Native speaker testing.
- Regional accent evaluation.
- ASR error monitoring after deployment.

---

# 8. Known Native Speaker / Compliance Gaps

The current evaluation has several limitations:

## Native Speaker Coverage

Testing was performed using available voice resources and pronunciation references rather than a large sample of native speakers.

Additional validation with native Filipino and Indonesian speakers is recommended.

---

## Regional Language Coverage

The evaluation focused on standard language usage.

Additional testing is required for:

- Regional accents.
- Informal speech patterns.
- Customer-specific vocabulary variations.

---

## Domain Vocabulary Monitoring

Financial and insurance conversations contain specialized terminology.

Continuous monitoring is recommended for:

- New product names.
- Plan names.
- Financial terminology.
- Customer-specific phrases.

---

# 9. Overall Localization Assessment

| Evaluation Area | Philippines | Indonesia |
|---|---|---|
| Language Understanding | ✅ Successful | ✅ Successful |
| Cultural Adaptation | ✅ Respectful Filipino communication style | ✅ Appropriate Indonesian financial communication style |
| Objection Handling | ✅ Empathy-first approach | ✅ Solution-oriented repayment guidance |
| Knowledge Retrieval | ✅ Responses grounded in available information | ✅ Responses grounded in repayment knowledge base |
| Human Escalation | ✅ Smooth escalation flow | ✅ Smooth escalation flow |
| Hallucination Prevention | ✅ No unsupported insurance claims | ✅ No unsupported financial claims |
| Further Improvement | Accent testing and broader Taglish validation | Regional accent testing |

---

# Conclusion

The voice assistant demonstrated successful multilingual conversational capability for Filipino and Bahasa Indonesia markets.

The evaluation showed:

- Effective localization beyond direct translation.
- Appropriate cultural communication patterns.
- Successful objection handling.
- Correct knowledge-grounded responses.
- Smooth human-agent escalation.

Future improvements should focus on broader native speaker testing, regional accent validation, and continuous ASR monitoring in production environments.


