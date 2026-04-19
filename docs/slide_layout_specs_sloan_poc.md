# Slide Type Guidance

**Renderer contract:** Each slide’s JSON `"type"` must match [`slide_automation/template_map.py`](../src/slide_automation/template_map.py) and a slide in **`templates/Sloan_Donor_Deck.pptx`** (donor-slide cloning).

**Supported `"type"` values:** `cover`, `agenda`, `divider`, `standard_1_block`, `standard_2_block`, `standard_3_block`, `standard_2_block_big_left`, `standard_2_block_big_right`, `narrow_image_content`, `wide_image_content`.

Below: one reference pattern for two-column content, then per-type notes for the donor deck. Editorial rules for specs: [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md).

---

# Worked Example (`standard_2_block`)

## Layout Overview

**Layout name:** Content slide, 2 blocks

**JSON `type`:** `standard_2_block`

**Short purpose:** Compare two streams of information side by side under one headline.

**Typical use cases:** Compare options, workstreams, before/after, product vs go-to-market, current state vs future state.

**Do not use when:** One side is much denser than the other, the content needs a table, or one side depends heavily on charts.

---

## Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| title | title text | Yes | Main message of the slide |
| subtitle | short text | No | Context, source, or framing |
| left_block_title | short text | Yes | Label for left column |
| left_block_body | bullets | Yes | Left-side argument or content |
| right_block_title | short text | Yes | Label for right column |
| right_block_body | bullets | Yes | Right-side argument or content |

---

## Content Rules by Placeholder

### title
- Role: State the main message, not just the topic.
- Ideal length: 6 to 14 words.
- Hard limit: About 90 characters.
- Style constraints: Prefer one line, two lines max.
- Fallback if too long: Rewrite into a clearer action title.

### subtitle
- Role: Add limited context only if needed.
- Ideal length: 3 to 10 words.
- Hard limit: One short line.
- Style constraints: Optional. Do not force it.
- Fallback if empty: Leave blank, do not invent filler.

### left_block_title
- Role: Name the left category clearly.
- Ideal length: 1 to 4 words.
- Hard limit: 6 words.
- Style constraints: Keep parallel with right title.
- Fallback if too long: Compress to label form.

### left_block_body
- Role: Present the left-side points cleanly.
- Ideal structure: Bullets.
- Ideal capacity: 2 to 4 bullets, mostly one line each.
- Hard limit: 5 bullets, avoid more than 2 lines per bullet.
- Style constraints: Default body size, may reduce slightly if needed.
- Fallback if too dense: Split slide or move to a denser layout.

### right_block_title
- Role: Name the right category clearly.
- Ideal length: 1 to 4 words.
- Hard limit: 6 words.
- Style constraints: Parallel structure with left title.
- Fallback if too long: Compress to label form.

### right_block_body
- Role: Present the right-side points cleanly.
- Ideal structure: Bullets.
- Ideal capacity: 2 to 4 bullets, mostly one line each.
- Hard limit: 5 bullets, avoid more than 2 lines per bullet.
- Style constraints: Match left side density as much as possible.
- Fallback if too dense: Split slide or move to a denser layout.

---

## Slide-Level Rules

**Narrative pattern:** One message, two parallel supporting buckets.

**Best for:** Clean side-by-side comparison where both sides have comparable weight.

**Avoid:** Uneven content, paragraphs, raw data dumps, highly visual exhibits.

**Escalation / fallback logic:**
- If title is too long, rewrite.
- If one side is much denser, consider a 1-block slide or split into two slides.
- If content needs more explanation, use a more narrative layout.
- If there are too many bullets, reduce to 3 key points or split.

---

## Visual / Styling Notes

- Default body font size: 18
- Minimum body font size: 16
- Default title size: Follow template default
- Maximum bullets per block: 4 preferred, 5 absolute max
- Maximum lines per bullet: 2
- Notes on spacing: If only 2 bullets, allow slightly looser spacing
- Notes on alignment: Keep left and right blocks visually balanced
- Notes on safe zones / no-go areas: Avoid spilling into footer / logo area

---

## Example References

**Example 1:**
- Why it is a good example: Uses symmetric categories and short bullets.
- What this example teaches: Good balance between both columns.

**Example 2:**
- Why it is a good example: Strong action title and clean hierarchy.
- What this example teaches: The title does real narrative work instead of just naming the topic.

---

# Donor slide layout specs (Sloan donor deck)

Operating rules for the PoC **donor deck** (`Sloan_Donor_Deck.pptx`). They are practical guidance, not schema.

## Global Rules Across the Template

- Section title keeps the template’s default font, size, and styling.
- Section title must always fit on one line.
- Main header / action title keeps the template’s default font, size, and styling.
- Main header must fit in two lines.
- Body titles keep the template’s default font, size, and styling.
- Body titles must fit on one line.
- Body text is the only flexible text zone.
- Body text must never go below 10 pt.
- AutoFit is not allowed.
- If content does not fit, shorten it, split it, or move to another layout.
- Footer / sources keep template styling and may wrap only when genuinely necessary.
- Placeholders define the available real estate and should be treated as hard boundaries.
- Icons, small callouts, and embellishments are optional manual enrichments and are out of scope for v1 automation.

---

## Layout Overview

**Layout name:** Cover

**Internal ID:** cover

**Short purpose:** Open the presentation with the topic, project identity, and key contextual metadata. Can also be reused as a back cover or Q&A end slide.

**Typical use cases:** Opening slide, final Q&A slide, final thank-you or closing page.

**Do not use when:** The slide needs substantial explanatory content, agenda structure, or body copy.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| title | title text | Yes | Main presentation topic |
| subtitle | short text | Yes | Project / report descriptor |
| date | short text | Yes | Date or version marker |
| background_image | image | Usually | Visual anchor for the cover |
| footer_branding | fixed graphic | Template | Institutional / project branding |

### Content Rules by Placeholder

#### title
- Role: State the presentation topic clearly and prominently.
- Ideal length: Short phrase.
- Hard limit: Must fit within template title area without resizing.
- Style constraints: Uses template style only.
- Fallback if too long: Rewrite more tightly, remove non-essential qualifiers, or move detail to subtitle.

#### subtitle
- Role: Clarify the type of document, class, project, or workstream.
- Ideal length: 2 to 8 words.
- Hard limit: One short line or compact two-line equivalent only if the template naturally allows it.
- Style constraints: Fixed template styling.
- Fallback if too long: Compress to document label form.

#### date
- Role: Provide date or version reference.
- Ideal length: Short date string.
- Hard limit: One line.
- Style constraints: Fixed template styling.
- Fallback if too long: Use shorter date format.

### Slide-Level Rules

**Narrative pattern:** One topic, one descriptor, one date.

**Best for:** Setting the frame and tone of the deck.

**Avoid:** Overloading with team names, long subtitles, or narrative text.

**Escalation / fallback logic:**
- If title is too long, shorten aggressively.
- If more metadata is needed, move it to an agenda or intro slide.
- For Q&A use, replace title with a short closing phrase and keep the rest minimal.

### Visual / Styling Notes

- Cover should remain visually clean and spacious.
- Background image is important to tone-setting but should not impair title legibility.
- Avoid adding extra blocks of text.

---

## Layout Overview

**Layout name:** Agenda

**Internal ID:** agenda

**Short purpose:** Introduce the structure of a longer presentation and preview its section flow.

**Typical use cases:** Early in the deck, after the cover, when the presentation has enough length or complexity to warrant signposting.

**Do not use when:** The deck is very short or sectioning would feel artificial.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| title | title text | Yes | Slide heading / action title |
| agenda_items | repeated short text items | Yes | Main sections of the deck |
| optional_subitems | short text | No | Limited sub-structure under a section, if template supports it |
| background_image | image | Usually | Visual support |

### Content Rules by Placeholder

#### title
- Role: Introduce the deck structure.
- Ideal length: Very short, usually one label or phrase.
- Hard limit: Must fit template title space.
- Style constraints: Fixed template style.
- Fallback if too long: Compress.

#### agenda_items
- Role: Name major sections of the deck.
- Ideal structure: 3 to 5 section titles.
- Ideal capacity: Short labels.
- Hard limit: Must stay readable and visually balanced.
- Style constraints: Keep naming parallel across sections.
- Fallback if too dense: Merge sections or simplify wording.

### Slide-Level Rules

**Narrative pattern:** Section roadmap.

**Best for:** Longer presentations with clear section breaks.

**Avoid:** Tiny decks, hyper-detailed outlines, or cluttered sub-bullets.

**Escalation / fallback logic:**
- If too many sections, merge them into broader buckets.
- If section names are too long, shorten to concise labels.

### Visual / Styling Notes

- Agenda should read quickly.
- Section names shown here should match section labels used later on standard content slides.

---

## Layout Overview

**Layout name:** Divider

**Internal ID:** divider

**Short purpose:** Mark the transition into a new section of the deck.

**Typical use cases:** Only when the deck includes an agenda and sections are substantial enough to benefit from explicit transitions.

**Do not use when:** The presentation is short, sections are minimal, or dividers would feel ceremonial rather than useful.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Name of the new section |
| background_image | image | Usually | Visual anchor / pacing device |
| optional_subtitle | short text | No | Occasional supporting phrase if template allows |

### Content Rules by Placeholder

#### section_title
- Role: Announce the next section clearly.
- Ideal length: 2 to 6 words.
- Hard limit: Must fit template without resizing.
- Style constraints: Fixed template style.
- Fallback if too long: Compress to cleaner label.

### Slide-Level Rules

**Narrative pattern:** Pause, then transition.

**Best for:** Resetting attention before a new substantive section.

**Avoid:** Using as filler or between every minor topic.

**Escalation / fallback logic:**
- If the deck is not long enough to justify dividers, skip them.
- If section names are too verbose, simplify them to agenda-style labels.

### Visual / Styling Notes

- Divider should feel spacious and intentional.
- Do not turn it into a content slide.

---

## Layout Overview

**Layout name:** Standard, 1 Block

**Internal ID:** standard_1_block

**Short purpose:** Present one coherent content block under a section label and a main action title.

**Typical use cases:** Key messages, highlights, synthesis, next steps, clustered evidence around one theme, one main narrative thread.

**Do not use when:** The slide naturally splits into distinct side-by-side comparisons, multiple unrelated buckets, or image-led storytelling.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Section tracking label |
| title | title text | Yes | Main action title |
| block_title | short text | Usually | Label for the main content block |
| block_body | bullets / short structured text | Yes | Main content area |
| footer | short text | No | Sources or notes |

### Content Rules by Placeholder

#### section_title
- Role: Track where the audience is in the deck.
- Ideal length: Very short section label.
- Hard limit: One line only.
- Style constraints: Fixed template style.
- Fallback if too long: Match agenda phrasing but shorten.

#### title
- Role: State the key message of the slide.
- Ideal length: Strong action title that fits two lines.
- Hard limit: Two lines only.
- Style constraints: Fixed template styling.
- Fallback if too long: Rewrite more tightly.

#### block_title
- Role: Frame the content block.
- Ideal length: 2 to 6 words.
- Hard limit: One line only.
- Style constraints: Fixed template styling.
- Fallback if too long: Compress to label form.

#### block_body
- Role: Carry the main substance of the slide.
- Ideal structure: Bullets, grouped highlights, short narrative text, or compact internal sub-structure.
- Ideal capacity: Enough to make one point clearly without crowding.
- Hard limit: Must fit within placeholder without resizing below 10 pt.
- Style constraints: This is the main flex zone.
- Fallback if too dense: Cut, split into two slides, or move to a 2- or 3-block layout.

#### footer
- Role: Sources, footnotes, or essential caveats.
- Ideal length: Minimal.
- Hard limit: May wrap only when truly necessary.
- Style constraints: Fixed template styling.
- Fallback if too long: Tighten citation style or move non-essential notes elsewhere.

### Slide-Level Rules

**Narrative pattern:** One section, one message, one main content bucket.

**Best for:** Synthesis, highlights, next steps, one-theme explanatory slides.

**Avoid:** Forcing unrelated content into one block.

**Escalation / fallback logic:**
- If body content starts fragmenting into distinct categories, move to 2 or 3 blocks.
- If the slide requires a large image, use an image-content layout instead.
- If a side callout is useful, treat it as optional manual enhancement.

### Visual / Styling Notes

- This is the default workhorse content slide.
- Manual icons or side accents are optional and out of scope for v1.

---

## Layout Overview

**Layout name:** Standard, 2 Blocks

**Internal ID:** standard_2_block

**Short purpose:** Present two related content buckets under one main message.

**Typical use cases:** Comparison, before/after, option A vs option B, current vs future, two supporting workstreams, two evidence buckets.

**Do not use when:** One side is much heavier than the other, three distinct buckets are needed, or the slide is strongly image-led.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Section tracking label |
| title | title text | Yes | Main action title |
| left_block_title | short text | Yes | Label for left block |
| left_block_body | bullets / grouped content | Yes | Left-side content |
| right_block_title | short text | Yes | Label for right block |
| right_block_body | bullets / grouped content | Yes | Right-side content |
| footer | short text | No | Sources or notes |

### Content Rules by Placeholder

#### title
- Role: Capture the relationship between the two blocks.
- Ideal length: Fit in two lines.
- Hard limit: Two lines only.
- Style constraints: Fixed template style.
- Fallback if too long: Tighten into a clearer message.

#### left_block_title / right_block_title
- Role: Name each bucket clearly.
- Ideal length: Short labels.
- Hard limit: One line only.
- Style constraints: Fixed template style.
- Fallback if too long: Compress.

#### left_block_body / right_block_body
- Role: Carry the substance of each side.
- Ideal structure: Bullets, short grouped items, compact cards, or concise supporting text.
- Ideal capacity: Balanced density across both sides.
- Hard limit: Must fit without resizing below 10 pt.
- Style constraints: Flexible body zone only.
- Fallback if too dense: Shorten, split, or move to a dominant-side variant.

### Slide-Level Rules

**Narrative pattern:** One message supported by two parallel buckets.

**Best for:** Side-by-side logic, paired ideas, clean comparisons.

**Avoid:** Highly uneven content loads or pretending unrelated topics are linked.

**Escalation / fallback logic:**
- If one side is much denser, use big-left or big-right variant.
- If content becomes card-heavy or too detailed, simplify or split.
- If more than two buckets are truly needed, use 3-block.

### Visual / Styling Notes

- Blocks should feel balanced, even if not identical.
- Internal card groupings are acceptable as long as they remain visually coherent.

---

## Layout Overview

**Layout name:** Standard, 3 Blocks

**Internal ID:** standard_3_block

**Short purpose:** Present three related buckets under one main message.

**Typical use cases:** Three pillars, three workstreams, three takeaways, three dimensions of a framework.

**Do not use when:** One bucket dominates heavily, one bucket is empty, or the slide needs detailed body copy.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Section tracking label |
| title | title text | Yes | Main action title |
| block_1_title | short text | Yes | Label for first block |
| block_1_body | bullets / short text | Yes | First content block |
| block_2_title | short text | Yes | Label for second block |
| block_2_body | bullets / short text | Yes | Second content block |
| block_3_title | short text | Yes | Label for third block |
| block_3_body | bullets / short text | Yes | Third content block |
| footer | short text | No | Sources or notes |

### Content Rules by Placeholder

#### title
- Role: Frame the three buckets under one umbrella message.
- Ideal length: Fit in two lines.
- Hard limit: Two lines.
- Style constraints: Fixed template style.
- Fallback if too long: Rewrite more tightly.

#### block titles
- Role: Name each bucket clearly and in parallel form.
- Ideal length: Very short.
- Hard limit: One line.
- Style constraints: Fixed template style.
- Fallback if too long: Compress to label form.

#### block bodies
- Role: Deliver concise supporting content for each bucket.
- Ideal structure: Short bullets or compact short text.
- Ideal capacity: Keep each block light.
- Hard limit: Must fit without shrinking below 10 pt.
- Style constraints: Flexible body zone.
- Fallback if too dense: Reduce detail or split into multiple slides.

### Slide-Level Rules

**Narrative pattern:** One message, three coordinated buckets.

**Best for:** Frameworks, pillars, phased logic, grouped takeaways.

**Avoid:** Dense explanatory prose or imbalanced content.

**Escalation / fallback logic:**
- If one block dominates, move to 2-block dominant-side layout or a sequence of slides.
- If each block needs real detail, split across multiple slides.

### Visual / Styling Notes

- This layout has the lowest tolerance for verbosity.
- Parallel wording across all three blocks matters more here than in other layouts.

---

## Layout Overview

**Layout name:** Standard, 2 Blocks with Dominant Side

**Internal IDs:** standard_2_block_big_left, standard_2_block_big_right

**Short purpose:** Present two related buckets where one side needs materially more space than the other.

**Typical use cases:** Main analysis plus side takeaway, large evidence panel plus smaller interpretation, dominant framework block plus secondary note block.

**Do not use when:** Both sides are truly balanced or when the secondary side becomes decorative rather than meaningful.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Section tracking label |
| title | title text | Yes | Main action title |
| dominant_block_title | short text | Yes | Label for larger block |
| dominant_block_body | bullets / grouped content | Yes | Main content area |
| secondary_block_title | short text | Yes | Label for smaller block |
| secondary_block_body | bullets / short text | Yes | Supporting content |
| footer | short text | No | Sources or notes |

### Content Rules by Placeholder

#### dominant_block_body
- Role: Carry the heavier share of the slide’s substance.
- Ideal structure: Bullets, grouped items, or compact structured content.
- Hard limit: Must still fit cleanly without abusing density.
- Fallback if too dense: Split slide or move to 1-block.

#### secondary_block_body
- Role: Support, contrast, summarize, or complement the dominant block.
- Ideal structure: Short bullets or compact text.
- Hard limit: Keep visibly lighter than dominant block.
- Fallback if too dense: Reassess whether this should be a balanced 2-block or a separate slide.

### Slide-Level Rules

**Narrative pattern:** One main content bucket plus one supporting bucket.

**Best for:** Asymmetric comparisons, main panel plus takeaway, large block plus side synthesis.

**Avoid:** Forcing symmetry or using the smaller side for filler.

**Escalation / fallback logic:**
- Choose big-left or big-right based on reading flow and which content should dominate.
- If both sides become dense, use regular 2-block or split.

### Visual / Styling Notes

- Treat the side imbalance as a conscious rhetorical choice.
- Direction [left or right] is a layout variant, not a different logical family.

---

## Layout Overview

**Layout name:** Image and Content

**Internal IDs:** narrow_image_content, wide_image_content

**Short purpose:** Combine light content with an image when the slide would otherwise feel too text-light.

**Typical use cases:** Context-setting, visual support, one or two points plus illustrative image, lighter transitional content.

**Do not use when:** The content is dense enough to warrant a standard layout or the image is merely decorative without helping the slide.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| section_title | short text | Yes | Section tracking label |
| title | title text | Yes | Main action title |
| image | image | Yes | Visual support |
| content_block_title | short text | Usually | Label for text block |
| content_block_body | bullets / short text | Yes | Supporting content |
| footer | short text | No | Sources or notes |

### Content Rules by Placeholder

#### image
- Role: Occupy meaningful real estate while reinforcing the point of the slide.
- Ideal structure: One clean image.
- Hard limit: Must not interfere with text safe zones.
- Style constraints: Crop allowed if needed.
- Fallback if weak image: Use a standard text layout instead.

#### content_block_body
- Role: Provide concise supporting information.
- Ideal capacity: Light to moderate content only.
- Hard limit: If body starts becoming dense, this is the wrong layout.
- Style constraints: Body text only may flex, never below 10 pt.
- Fallback if too dense: Move to a standard content slide.

### Slide-Level Rules

**Narrative pattern:** One message, one image, one compact supporting content area.

**Best for:** Slides where image and content genuinely work together.

**Avoid:** Using the image as wallpaper for a text-heavy slide.

**Escalation / fallback logic:**
- Use narrow or wide version based on how much image real estate helps the message.
- If the image adds little, prefer a standard content layout.

### Visual / Styling Notes

- These layouts are secondary and should be used selectively.
- Image choice matters more here than in any other non-cover layout.

---

## Layout Overview

**Layout name:** Quote

**Internal ID:** quote

**Short purpose:** Spotlight one central statement, quote, or key message that the speaker will unpack verbally.

**Typical use cases:** Rare. High-emphasis statements, external quotes, or a key synthesis line.

**Do not use when:** The slide needs detailed explanation, multiple supporting points, or normal content density.

### Placeholder Map

| Placeholder name | Content type | Required? | Purpose |
|---|---|---:|---|
| quote_text | quote / short statement | Yes | Central message |
| attribution | short text | No | Source or speaker |
| section_title | short text | No | Optional if the layout includes it |
| footer | short text | No | Source notes |

### Content Rules by Placeholder

#### quote_text
- Role: Carry one memorable line only.
- Ideal length: Short enough to remain visually striking.
- Hard limit: If it reads like a paragraph, this is the wrong layout.
- Style constraints: Fixed template styling.
- Fallback if too long: Cut to core phrase or move to standard layout.

### Slide-Level Rules

**Narrative pattern:** One statement, one emphasis point.

**Best for:** Rare high-emphasis moments.

**Avoid:** Using it as a normal content slide.

**Escalation / fallback logic:**
- If additional support is needed on-slide, use a standard layout instead.

### Visual / Styling Notes

- Low priority for PoC.
- Optional for v1 automation.
