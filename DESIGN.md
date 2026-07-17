# Design Specification: Vishaal S Portfolio

This document provides a detailed breakdown of the design system, user experience decisions, colors, typography, and interactive components of the portfolio website of **Vishaal S** (Data Analyst and ML Engineer).

---

## 1. Overview & Design Vision

The portfolio is designed as a **modern, single-page, data-centric presentation platform**. It balances technical professionalism with clean, premium design principles:
*   **Target Audience:** Technical recruiters, project managers, and organizations seeking candidates with strong data modeling, analytics, machine learning, and automation capabilities.
*   **Design Paradigm:** A minimal, high-contrast grid-based layout combining editorial serif headlines with highly readable sans-serif metadata. 
*   **Foundation:** Built on top of the **Hudson** theme layout structure and customized with custom elements for skill grids, plant audit experience showcases, and interactive achievements.

---

## 2. Color Palette & Theme System

The design system employs a curated color palette consisting of a signature rust/burnt-orange accent, organic charcoal undertones, and a bright off-white workspace. 

### 2.1 Core Palette

| Variable Name | Color Swatch | HSL Value | Hex (Approx) | Semantic Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `--color-1` | Burnt Orange | `hsl(12, 75%, 45%)` | `#C73E1D` | **Primary Accent**: Used for links, key call-to-actions, vertical dividers, text highlights, and button backgrounds. |
| `--color-2` | Olive Charcoal | `hsl(96, 10%, 19%)` | `#2F352B` | **Secondary Brand Color**: Provides a grounded, organic green-gray tone for secondary hover states and branding elements. |
| `--color-3` | Soft Charcoal | `hsl(0, 0%, 10%)` | `#1A1A1A` | **Deep Dark Neutral**: Used for structural shadows, loader components, and footer sections. |
| `--color-body-bg` | Studio Light Gray | `hsl(0, 0%, 98.4%)` | `#fbfcfb` | **Global Page Background**: A crisp, cool off-white that minimizes eye strain compared to pure white. |
| `--color-text` | Charcoal Black | `hsl(0, 0%, 9.4%)` | `#181818` | **Body Typography**: Soft dark gray to ensure clean reading contrast without the harshness of pitch black. |
| `--color-text-light` | Medium Cool Gray | `hsl(0, 0%, 46.3%)` | `#767776` | **Secondary Metadata**: Used for subtitles, descriptions, category labels, and placeholder text. |

### 2.2 Primary Accent Variations (Theme Scale)

To maintain consistent hover transitions, the main rust accent scales dynamically:
*   `--color-1-light`: `hsla(12, 75%, 55%, 1)` *(Used for primary button hovers)*
*   `--color-1-lighter`: `hsla(12, 75%, 65%, 1)`
*   `--color-1-lightest`: `hsla(12, 75%, 75%, 1)`
*   `--color-1-dark`: `hsla(12, 75%, 35%, 1)`
*   `--color-1-darker`: `hsla(12, 75%, 25%, 1)`
*   `--color-1-darkest`: `hsla(12, 75%, 15%, 1)`

---

## 3. Typography & Hierarchy

The typography structure uses two contrasting typeface families to create a strong visual hierarchy: a clean geometric sans-serif for UI density, and a premium editorial serif for headings and headers.

### 3.1 Type Families
*   **Primary Typeface (`--font-1`):** `"Public Sans", sans-serif`
    *   *Purpose:* Applied to body text, skill descriptions, menu links, buttons, and system labels.
    *   *Characteristics:* Modern, clean, geometric design optimized for readability at small screen sizes.
*   **Secondary Typeface (`--font-2`):** `"Castoro", serif`
    *   *Purpose:* Reserved for large section titles, hero introductions, namespace logos, and editorial headers (such as the Blogs directory heading).
    *   *Characteristics:* Traditional serif letterforms that project a polished, literary, and academic tone.
*   **Code Elements (`--font-mono`):** `Consolas, "Andale Mono", Courier, monospace`
    *   *Purpose:* Preformatted blocks, code blocks, and retro file lists.

### 3.2 Namespace Logo Branding
*   **Design & Typography:** Replaced the previous image logo in the main header with a text-based, unified namespace logo system styled in `Castoro` (`var(--font-2)`) bold at `2.6rem` - `2.8rem` with `-0.02em` letter spacing.
*   **Cohesive Structures**:
    *   *Portfolio Main*: `Vishaal.` (period styled in accent burnt orange `#C73E1D`)
    *   *Blogs Directory*: `Vishaal.blogs` (period styled in accent burnt orange)
    *   *Individual Blog*: `Vishaal.llm` (period styled in accent burnt orange)

### 3.3 Typescale & Spacing (1.2 Minor Third Scale)

The typography is built on a **rem-based modular scale** using a multiplier that shrinks dynamically on small mobile devices to maintain screen balance:
*   **Base Setting:** `62.5%` font size in the root document, translating `1rem = 10px` for simplified sizing math.
*   **Standard Base (`--base-font-size`):** `2.0rem` (`20px`) for high readability.
*   **Scale Ratio:** `1.2` multiplier per scale step.

| CSS Variable | Font Size (rem) | Equivalent PX | Application |
| :--- | :--- | :--- | :--- |
| `--text-huge-3` | ~14.8rem | 148px | Backdrop numbers and watermark styling |
| `--text-display-3` | ~8.6rem | 86px | Main display titles |
| `--text-display-2` | ~7.1rem | 71px | Sub-hero big headlines |
| `--text-xxxl` | ~4.9rem | 49px | Main section headers ("My Skills", "My Works") |
| `--text-xl` | ~3.4rem | 34px | Sub-section headings / Work titles |
| `--text-lg` | ~2.8rem | 28px | Inline subheadings, emphasis titles |
| `--text-md` | ~2.4rem | 24px | Attention grabbers and large intro lines |
| `--text-size` | ~2.0rem | 20px | Standard body paragraphs / CV button labels |
| `--text-sm` | ~1.6rem | 16px | Skill list elements, captions, and links |
| `--text-xs` | ~1.3rem | 13px | Pre-titles ("Hello") and status markers |

---

## 4. Architectural & Layout Decisions

The website utilizes a clean grid system built on standard grid blocks and responsive flex boxes.

### 4.1 Grid & Spacing Units
*   **Vertical Space (`--space`):** Set at `32px` standard. All margins and paddings reference multipliers of this space (`--vspace-0_5`, `--vspace-1_5`, etc.) to create vertical rhythm.
*   **Layout Sections:** Each key section uses the `.target-section` class which coordinates with JavaScript ScrollSpy to dynamically highlight current positions in the sticky navigation menu.

### 4.2 Structural Breakdowns
1.  **Intro Hero:** Implements a full-width background photo (`images/intro-bg.jpg`), placing text left-aligned inside a 12-column grid. Quick social handles float on the bottom left.
2.  **Skills Grid:** Arranged in a responsive 4-column flex layout (`.skills-grid`) containing 8 cards: Agentic AI, LLM & RAG Systems, FastAPI, DataBricks, PyTorch, Python, Power BI, and SQL.
3.  **Experience Row:** Uses `.experience-wrapper` to divide screen real estate:
    *   **Left Column (500px fixed width):** Captivating workplace audit snapshot utilizing `glightbox`.
    *   **Right Column (Flex auto):** Description of the Hyundai Motors internship with key contributions formatted in a customized bullet list.
4.  **Portfolio (Works):** Displays GitHub-themed rectangular cards in a 3-column responsive grid. Each card includes a folder SVG icon, serif titles, short descriptions, tech stack tags, and links directly to GitHub. On hover, cards transition with a translateY lift, soft drop shadows, and burnt orange highlights.
5.  **About Me Achievements:** Arranged as a 3-column achievements flexbox (`.about-entry`) showcasing certificates and hackathon achievements (HackFest, SIH, Startup Mahakumb).

---

## 5. Micro-Animations & Interactivity

The site stands out through rich, subtle interactions designed to provide validation and visual interest:

### 5.1 Scroll-Triggered Fade-In Animations (Intersection Observer)
In `js/addition.js`, an `IntersectionObserver` monitors both `.skill-item` and `.project-card` elements:
*   Initial state: `opacity: 0`, `transform: translateY(20px)` (skills) / `translateY(30px)` (projects).
*   When scrolled into view: Smoothly translates to their original position (`translateY(0)`) and fades to full opacity using custom transitions:
    ```javascript
    entry.target.style.opacity = 1;
    entry.target.style.transform = "translateY(0)";
    entry.target.style.transition = "opacity 0.5s ease, transform 0.8s ease";
    ```

### 5.2 Dynamic Tooltip Lists (Hover Info)
Hovering over a skill card reveals detailed subsets of skills (e.g., ETL, DAX, Power Query, CNN, NLP):
*   Implemented in CSS through absolute positioning relative to the `.skill-item` parent.
*   On mouse hover, `.hover-info` displays over the card using a slide-fade style.
*   Uses clear, high-contrast white text on black pill backgrounds (`#000000`).

### 5.3 Sticky Shrinking Header
A JavaScript helper in `js/main.js` listens to user scrolling:
*   As the scroll offset exceeds the hero header height minus 170px, `.sticky` is added to the `.s-header`.
*   Further scrolling adds `.offset` (sliding header upward slightly) and `.scrolling` (shrinking height, setting background transparent dark, and adding minor shadows) to minimize distraction while keeping navigation active.

### 5.4 Overlay Modals & Sliders
*   **GLightbox Integration:** Provides responsive overlays for portfolio projects, including detailed paragraphs and inline download anchors for Excel files (`.xlsx`) or Power BI documents (`.pbix`).
*   **Smooth Navigation Scroll:** Registers elements with `.smoothscroll` to slide anchors smoothly with an `easeInOutCubic` curve over `1200ms`.

---

## 6. Responsive Adaptations

The styles sheet contains detailed media query definitions ensuring the site layout changes gracefully across mobile, tablet, and widescreen layouts:

### Breakpoint Specifications
*   **1600px:** Back-to-top button text collapses (`display: none`), displaying only the arrow icon to prevent layout clutter.
*   **900px:** Main header navigation menu collapses into a hidden side-drawer toggled by a custom hamburger icon (`.s-header__menu-toggle`).
*   **768px:**
    *   **Skills Section:** `.skills-grid` layout displays 4 items per row on desktop, then shifts from a horizontal row to vertical stacking (`flex-direction: column`) on viewports below 768px. The vertical `.divider` lines are hidden, and horizontal custom lines (`.horizontal-divider` and `border-bottom: 1px solid #C93F1D`) isolate the individual elements.
    *   **Achievements (About Me):** `.about-entry` changes from `grid-template-columns: repeat(3, 1fr)` to `display: block` layout.
    *   **Experience:** `.experience-wrapper` stacks vertically. The main audit photo scales down from `500px` to `350px` width.
*   **600px:** The grid typescale multiplier (`--multiplier`) changes from `1` to `.9375` (reducing all computed sizes by 6.25% to optimize padding and typography sizes for compact mobile viewports).

---

## 7. Blog Layouts & Scroll Interaction

The blogs engine features a custom landing directory index integrated with premium article reading layouts, carrying the portfolio's color scheme with a distinct retro structure.

### 7.1 Blogs File Explorer Landing (`blogs/index.html`)
*   **Visual System**: Mimics a retro OS file manager (Windows 95 Explorer style) utilizing a central `.explorer-window` window frame.
*   **Window Aesthetics**: High-contrast light gray panels (dark charcoal in dark mode) framed with raise/inset beveled border-shadow styling, title bars containing system controls `[ - ] [ ▢ ] [ X ]`, active paths in address bars, and bottom status strips.
*   **Directory Hierarchy**: Collapsible collection nodes represented by yellow folder SVGs connected to child pages via vertical dotted line paths. Clicking folders toggles the open/close vector states and expands files below.
*   **CRT Terminal Viewport**: Simulates a physical CRT monitor faceplate using a static screen wrapper (`.viewport-screen-wrapper`) that overlays scanlines and rolling beams dynamically without scrolling. Preserves your exact light and dark theme colors:
    *   **Light Mode (Positive Polarity)**: Displays the original white background and dark text, layered with a subtle dark screen vignette, dark horizontal scanlines, and a dark rolling scanline beam. Keeps standard yellow folder and white document icon fills.
    *   **Dark Mode (Negative Polarity)**: Displays the original dark-gray/black background and off-white text, layered with a dark vignette, horizontal scanlines, a glowing rolling beam, and subtle cathode flicker.
*   **Animations**: The page loads with a full container fade-in-blur animation (`page-fade-in`), followed by the explorer window scale zoom and staggered slide-in transitions for directory nodes. Disables automatically for prefers-reduced-motion.

### 7.2 Blog Articles Layout (`blogs/understanding-large-language-models.html`)
*   **Split Grid Columns**: An asymmetrical 30% left / 70% right grid structure handles sidebar metadata and article flow.
*   **Sticky Sidebar (`.sidebar-col`)**: Affixed dynamically (`position: sticky; top: 4rem;`) to keep metadata and actions persistently available as the user reads.
*   **Sticky Mini-Title Transition**: Monitors scroll height relative to the main hero title container (`#blog-hero`). Once scrolled past the hero header, the mini-title transitions smoothly (`max-height: 180px; opacity: 1; padding-bottom: 2rem;`) into the sticky sidebar, pushing the metadata rows downward with a fluid transition.
*   **Theme Toggle**: Implemented at the top-right nav links of both the blogs index and article views, allowing users to shift seamlessly to a dark-mode terminal layout. Caches preferences in `localStorage` and loads them early to prevent flashes.
*   **Responsive Overrides**: Sized the navbar logo brand text dynamically on tablets (`2.0rem`) and mobile devices (`1.6rem`), centering and stacking the navigation layout vertically on screen widths below `600px` to prevent layout clipping and link collision.
*   **Blog Footer**: Minimalist developer footer (`.blog-footer`) containing a horizontal division separator, copyright signature, social navigation shortcuts, and a smooth `Back to Top` link referencing the top hero header element.
