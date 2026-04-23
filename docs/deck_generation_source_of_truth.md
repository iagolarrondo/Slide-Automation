# Deck generation: editorial & storytelling source of truth

## 1. Purpose

**What this document is for**  
It defines how **deck specs** (structured JSON—or equivalent intermediate representations—intended for the renderer) should be **authored or generated**: storyline, headings, block labels, tone, density, and workflow behavior for humans and automation alike.

**Generation rules vs rendering/template rules**  
| Layer | Owns | Examples |
|--------|------|----------|
| **Generation (this doc)** | *What* the deck says and *how* it reads: narrative arc, slide messages, label semantics, synthesis vs paste, when to ask the user, anti-patterns. | “Headings must read as a story in sequence.” “Block titles are thematic, not ‘Block A’.” |
| **Rendering / template** | *How* text lands in PowerPoint: donor-slide mapping, advisory length **warnings** for titles (no semantic shortening in the renderer), footer behavior. | Sloan: `slide_automation/template_registry/sloan.py` (and `template_map.py` shim). WD: `template_registry/wd.py` + [`wd_donor_inventory.md`](wd_donor_inventory.md). |

**Per-slide-type Sloan rules (density, when to use each type, donor-backed behavior):** see [`slide_layout_specs_sloan_poc.md`](slide_layout_specs_sloan_poc.md). Operational CLI and template mapping are also summarized in the repo root [`README.md`](../README.md).

Rendering cannot fix a weak storyline or placeholder labels. Generation must produce specs that are **message-strong** and **shape-aware** (length and structure that templates can carry) so the renderer’s job is layout fidelity, not salvage editing.

---

## 2. Core principles

- **Think like a consultant** when generating presentations: each slide earns its place in the storyline; every heading should answer “so what?” for the target reader.
- **Prioritize message clarity over literal document phrasing**—especially workplans, transcripts, and internal notes. The spec is the *argument*, not a mirror of the source file.
- **Use project files and prior conversation as the default context source.** Prefer grounded synthesis from what is already in the workspace and thread before inventing or asking.
- **Ask the user only when missing information is materially important**—e.g., audience level, decision being sought, hard constraints (time, red lines), or ambiguity that changes the recommendation arc. Do not interrogate for trivia you can reasonably assume from context.

### Consulting-style defaults

- **Synthesis over transcription**—sources inform claims; they are not pasted back as deck voice.
- **Implications over raw observations** when the evidence supports a “so what” (state the implication, not only the datapoint).
- **Issue-based structure over chronological reporting** unless the timeline itself is the analytical point.
- **Write for manager skim first, deep read second**—headline and block titles should survive a 20-second pass; bullets reward the reader who stays.

---

## 3. Storyline rules

- **Headings must communicate the key message of each slide**—not the topic area alone. Prefer “WD’s gap is orchestration, not tool scarcity” over “Technology assessment.”
- **If all slide headings are read in sequence, they should tell a coherent story**—a reader should reconstruct the thesis without reading body bullets.
- **Avoid vague, generic, or process-heavy headings** such as “Overview,” “Background,” “Next steps” (without a verb or outcome), “Key considerations,” or “Discussion of workstream 1” unless the process *is* the substantive message.

### Slide archetypes by editorial intent

Editorial choice of `type` (see layout specs for mechanical detail):

- **`standard_1_block`** — One headline message with a single stream of supporting points. Use for a unified recommendation, “so what,” closing implication, or any slide where **one column of argument** is clearer than forcing a false split.
- **`standard_2_block`** — **Intentional two-part structure**: contrast, tension, before/after, option A vs B, problem vs response, enabler vs barrier. Do not use simply to divide long text; the two columns must answer different facets of the **same** slide message.
- **`standard_3_block`** — **Three parallel pillars** (e.g., lenses, workstreams, stakeholder groups) of roughly equal weight. Use when readers must carry away **three named buckets**; avoid when two columns or a short sequence of slides would reduce cognitive load.
- **`standard_2_block_big_left` / `standard_2_block_big_right`** — **One dominant narrative** plus a narrower sidebar (context, definitions, caveats, “how to read this,” audience-specific notes). Use when one storyline owns the slide and the rest is supporting, not co-equal.
- **`narrow_image_content` / `wide_image_content`** — The **visual is part of the proof** (process, org, journey, architecture, site context). Use when removing the image would weaken recognition or credibility; prefer text-first layouts when the image is merely decorative.

### Opening slides

- Frame the **business question**, **assessment or engagement goal**, and **scope** in **stakeholder language** (outcomes, decisions, risks, constraints)—what they need to agree on or understand, not how the team organized the work internally.
- **Avoid meta-project labels** in headings and block titles—“project mandate,” “workstream objective,” “deck purpose,” “section overview”—unless **process traceability** (e.g., SOW alignment) is an explicit deliverable. Prefer labels that state substance (e.g., “What we assessed,” “What this covers,” “What decisions this enables”).

### Message hierarchy (slide anatomy)

- **Heading** = the **key message** (the one takeaway if the reader remembers nothing else).
- **Block titles** = the **argument structure**—how that message decomposes into two or three moves; not generic section labels.
- **Bullets** = **support / evidence / nuance**—examples, facts, caveats, next-level detail.
- Bullets **must not carry the full burden of the slide**: if the headline only becomes clear after five dense bullets, rewrite the headline or **split** the content across slides.

---

## 4. Block-title rules

- **Block titles must be meaningful and interpretable on their own**—they are skim anchors; someone scanning only left/right column headers should still understand the contrast or structure.
- **Do not shorten titles into broken fragments** (dangling prepositions, half-phrases, opaque labels). The renderer **does not** repair long titles—keep them **complete and meaningful** in the spec so layout overflow is avoided at the source.
- **Do not use placeholders like “Implication 1 / 2 / 3”** when each block carries a distinct idea. Replace with **thematic labels** that encode the implication (e.g., “Assume uneven maturity,” “Center governance and trust,” “Anchor use cases in real friction”).
- **Prefer thematic labels that communicate the actual content**—parallel structure across blocks on the same slide is good when it clarifies comparison (e.g., “Where humans stay central” / “Where machines add value”).

---

## 5. Content-generation rules

- **Documents should inform the story, not be quoted or mirrored mechanically.** No long paste of source paragraphs into bullets unless the deliverable explicitly requires citation-style fidelity.
- **Avoid language like “according to the workplan”** unless the client explicitly needs audit traceability; otherwise it reads like draft scaffolding, not a finished deck.
- **Translate source material into consultant-style synthesis**—insight, implication, and recommendation-forward phrasing; bullets support the heading, they do not replace it.
- **Preserve nuance, but keep structure executive and digestible**—trade-offs and caveats belong in tight bullets, not wall-of-text dumps.

### Source-usage hierarchy

When multiple project files exist, **prioritize and synthesize** in roughly this order (always subordinate to explicit user instructions in-thread):

1. **User direction in the request and conversation**—audience, objective, red lines, must-include points.
2. **Authoritative or client-facing artifacts** when present (signed scope, approved plans, formal assessments)—for commitments, framing, and defensible claims.
3. **Workplans, syllabi, steering decks**—for **structure, scope, milestones, and governance**; mine for what was promised, not for slide-ready prose or internal jargon as headlines.
4. **Minutes of meetings and transcripts**—for **decisions, quotes, facts, and tensions**; synthesize into implications; avoid chronological play-by-play unless the timeline is the point.
5. **Drafts, scratch notes, and informal captures**—treat as **hints**; do not promote unvetted lines to headline claims without corroboration from higher-trust sources.

If sources **conflict**, prefer **explicit synthesis of the tension** in body bullets (or a clarifying question to the user) over silently picking the newest or longest file.

---

## 6. Density and fitting rules

- **Titles and block titles should be generated with fit in mind**—know the template family (e.g., narrow vs wide title, two-column labels) and bias toward **shorter, stronger** phrasing up front; the renderer will **not** shorten them for you.
- **If something is too long, rewrite it meaningfully** in the spec—restate the idea in fewer words with the same substance; do not rely on the renderer to truncate.
- **Never use broken endings or ellipsis-based mutilation for titles** in generated specs.

---

## 7. Audience and tone

- **Default to a consultant-style presentation tone**: confident, precise, outcome-oriented; avoid tutorial voice and generic “AI assistant” enthusiasm.
- **Balance analytical rigor with executive clarity**—each slide should be defensible in a partner review and readable in a 30-second board skim.
- **Adapt density based on audience and deliverable needs**—workshop working sessions allow more bullets; exec readouts demand fewer, harder-hitting lines; same storyline, different grain.

---

## 8. Workflow rules

- **Default when the user requests a presentation inside a project with existing context**  
  - Ingest relevant project files and conversation.  
  - Propose a **skeleton storyline** (slide sequence + intended message per slide) mentally or explicitly before filling bodies.  
  - Generate the spec **directly** when the arc is clear from context.

- **When to generate directly vs when to ask clarifying questions**  
  - **Generate directly** when: audience tier is inferable, objective matches prior thread, deck type matches examples in repo, and no single ambiguity would flip the structure.  
  - **Ask first** when: conflicting goals in sources, missing decision or success criterion, unknown audience (e.g., plant floor vs C-suite), or legal/compliance sensitivity that changes framing.

- **What questions are worth asking** (short list)  
  - Who is the primary audience and what decision (if any) should this deck support?  
  - Length / slide count budget?  
  - Must-include facts, numbers, or red lines?  
  - Tone: internal-only vs client-facing?  

  Questions **not** worth defaulting to: exhaustive style preferences, font debates, or “confirm you want a title slide” when context already implies a full deck.

---

## 9. Anti-patterns / what not to do

- **Generic AI-sounding headings** (“Leveraging synergies,” “Harnessing innovation,” “In today’s fast-paced environment”).  
- **Broken compressed labels** that only make sense with the body text (“Mgmt view,” “Risks area,” “Tech piece”).  
- **Process-justification slides** (“Why we did this assessment”) unless the stakeholder genuinely needs the meta-narrative; prefer implication-forward slides.  
- **Literal repetition of source documents** as bullets without synthesis.  
- **Content that sounds like notes** (“Talk about X,” “Insert chart here,” “FYI from call”)—replace with presentation-ready statements or omit.

---

## 10. Open issues / future enhancements

- **Rich text emphasis** (bold/italic within bullets or titles) if/when the renderer and template contract support it consistently.  
- **Smarter density management**—tie generation to per-layout character guidance and optional “density mode” in the spec.  
- **More robust layout selection**—explicit or inferred mapping from message type (e.g., compare/contrast → two-block) beyond today’s manual `type` choice.  
- **Agent / tool packaging**—CLI + library boundaries, validation hooks, and “generate from project” flows that **enforce** this document as system/developer instructions alongside JSON schema.

---

*This file is the editorial contract for spec quality. Template mapping and PPT mechanics live elsewhere.*
