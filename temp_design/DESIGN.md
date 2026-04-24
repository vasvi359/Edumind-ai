# Design System Strategy: The Luminal Scholar

## 1. Overview & Creative North Star
The North Star for this design system is **"The Digital Sanctuary."** This interface acts as a calm, meditative space for high-level cognition, moving away from high-contrast stimulation toward a muted, focused atmosphere.

We achieve this through a **balanced, professional density** and a palette of desaturated, dusty violets. This system uses its muted tones not just as accents, but as a "tonal wash" that defines functional zones. By layering sophisticated surfaces and utilizing clear typography scales, we create an environment that feels like a modern research archive—stable, quiet, and intellectually rigorous.

---

## 2. Color & Tonal Architecture
The palette is rooted in a desaturated amethyst and grey-violet spectrum. We prioritize low-chroma colors to minimize visual fatigue, using the neutral base (#797677) to anchor the experience.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or containment. 
Boundaries must be defined through:
*   **Background Color Shifts:** Placing a subtle tonal sidebar against the main stage to create distinction.
*   **Tonal Transitions:** Using the shift from the neutral base (#797677) to secondary surfaces (#7a767a) to define content areas.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of tactile materials. 
*   **Level 0 (Base):** `neutral` (#797677) - The foundational canvas.
*   **Level 1 (Sub-sections):** Secondary tones (#7a767a) - Used for background sections or utility bars.
*   **Level 2 (Active Elements):** Primary-tinted surfaces - Reserved for the primary "work surface" (e.g., the code editor or active document).
*   **Level 3 (Pop-overs):** Tertiary accents (#797390) - For floating menus or contextual help.

### The "Muted Gradient" Rule
To add depth to the desaturated aesthetic:
*   **The Amethyst Wash:** Use a subtle linear gradient for primary CTAs: `primary` (#7b757f) to a slightly deeper variant at a 135-degree angle.
*   **Glassmorphism:** For navigation headers, use the neutral base with 80% opacity and a `24px` backdrop-blur, allowing the underlying muted tones to bleed through softly.

---

## 3. Typography: Editorial Authority
We pair **Manrope** (Display/Headlines) with **Inter** (Body/UI) to create a "Technical-Editorial" hybrid.

*   **Display (Manrope):** Balanced sizing. Use `display-lg` with standard letter-spacing to maintain a professional, academic tone.
*   **Headlines (Manrope):** Use `headline-sm` for module titles. Manrope’s geometric nature feels modern and "designed."
*   **Body (Inter):** All long-form educational content uses `body-lg` with a controlled line-height (1.5) to ensure focus and efficient scanning.
*   **Code & Labels (Inter):** Use `label-md` for metadata. Code blocks utilize a desaturated secondary background to make technical snippets feel like integrated parts of the lesson.

---

## 4. Elevation & Depth
In "The Digital Sanctuary," depth is achieved through **Tonal Layering** rather than traditional shadows.

*   **The Layering Principle:** To lift a card, place a slightly lighter surface on a darker neutral background. The subtle shift in hex values provides enough contrast for the human eye to perceive elevation naturally.
*   **Ambient Shadows:** If a floating state is required (e.g., a modal), use an ultra-diffused, low-opacity shadow tinted with the `primary` hex (#7b757f) to keep the shadow "atmospheric" rather than heavy.
*   **The Ghost Border:** If a boundary is strictly required for accessibility, use a variant of the primary color at 20% opacity.

---

## 5. Signature Components

### Buttons & Actions
*   **Primary Action:** A solid `primary` (#7b757f) fill with high-contrast text. Corner radius is set to `1` (Subtle) for a sharp, precise, "software-grade" feel.
*   **Secondary Action:** A secondary muted fill (#7a767a). This reinforces the "Stone Sanctuary" aesthetic.
*   **Tertiary:** No background. Text color is derived from the primary palette.

### The Educational Console (Code Blocks/Terminal)
*   **Background:** A darkened variant of the secondary or tertiary color.
*   **Styling:** Forbid 1px borders. Use a left-hand "accent bar" of 4px solid `primary` (#7b757f) to denote the active line or block.
*   **Corner Radius:** Subtle rounding (`1`) to maintain consistency with the rest of the interface.

### Input Fields
*   **Resting State:** A slightly shifted neutral background with no border.
*   **Focus State:** A subtle glow using the `tertiary` color (#797390) at low opacity.

### Cards & Lists
*   **Prohibition:** Never use divider lines.
*   **Separation:** Utilize the "Normal" spacing scale (level 2) to provide clear rhythmic separation between items.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use the desaturated primary color (#7b757f) for focus indicators and progress bars to maintain brand identity.
*   **Do** prioritize "Functional Calm." Use the Normal spacing setting to ensure the UI feels organized and efficient.
*   **Do** use subtle background shifts to indicate different interactive zones.

### Don’t
*   **Don’t** use high-vibrancy purples; stick to the muted, desaturated palette defined by the primary and tertiary tokens.
*   **Don’t** increase spacing to "Spacious" levels; maintain the "Normal" (level 2) density for a professional, compact tool feel.
*   **Don’t** use fully opaque borders to separate content; rely on the subtle contrast between the neutral (#797677) and secondary (#7a767a) colors.