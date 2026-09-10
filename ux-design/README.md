# 🎨 UX Design & Workflow Engineering Skill

> Human-centered workflow design, interaction architecture, and cognitive usability engineering for any system (simple, medium, complex, digital, physical, conversational, or operational service). Automatically handles both greenfield workflow creation and brownfield UX audit/redesign.

---

## ⚡ Quick Install

Install this skill directly into your current project or workspace using `npx skills`:

```bash
npx skills add HaoNgo232/my-skills --skill ux-design
```

---

## 🎯 What this Skill Does

- **Adaptive Context Engine (Tri-Axial Matrix)**: Automatically tunes the interaction model across 3 orthogonal dimensions:
  1. *User Expertise*: Novice / Casual (progressive disclosure, self-evident wizard) vs. Trained Specialist (hotkeys, bulk actions, high data density).
  2. *Failure Risk Level*: Low-stakes (frictionless, free exploration, undo-first) vs. Mission-critical (safety bounds, dual confirmation, strict state transparency).
  3. *Interaction Medium*: Digital GUI (Web/Mobile/Desktop), Conversational UI (Voice/AI Agent), Physical Hardware/IoT, or Human Service Journey.
- **The 7 Ontological Elements**: Structures every single interaction step by: *Actor & Context*, *Trigger & Pre-conditions*, *Input/Intent Transmission*, *Decision Gateways*, *System Feedback*, *Error Boundaries*, and *Exit/Next Best Action*.
- **Anti-Non-Human Bias Guardrails**: Eliminates robotic and developer-centric UX antipatterns grounded in cognitive neuroscience:
  - *4-Chunk Working Memory Bottleneck* (Nelson Cowan 2001)
  - *Cognitive Miser Principle* (Fiske & Taylor 1984)
  - *Alan Cooper's 3-Layer Model* (Mental Model vs. Implementation Model vs. Represented Model)
  - *Curse of Knowledge & Database/Leaky Abstraction Leakage*
  - *Norman's Gulf of Execution & Gulf of Evaluation*
  - *System 1 Intuitive Protection* (Daniel Kahneman)
  - *Alert Fatigue Prevention* (Undo-first instead of confirmation modals)
- **Unified Dual-Mode (Greenfield & Brownfield)**:
  - *Greenfield Design*: Creates optimal, frictionless workflows from scratch.
  - *Brownfield Audit & Redesign*: Automatically invokes `references/ux-audit.md` when analyzing existing screens, code, or flows, classifying issues by Severity (🔴 Critical, 🟡 Major, 🟢 Minor) and producing actionable fixes with measurable **Impact Scorecards**.

---

## 📋 File Reference

- Skill specification: [`SKILL.md`](./SKILL.md)
- Playbook for auditing & redesigning existing systems: [`references/ux-audit.md`](./references/ux-audit.md)
- In-depth research monograph on cognitive biases (60KB, 34 academic citations): [`references/cognitive-biases.md`](./references/cognitive-biases.md)
- Catalog of reusable workflow patterns: [`references/workflow-patterns.md`](./references/workflow-patterns.md)
- Annotated bibliography of foundational books & international standards: [`references/literature.md`](./references/literature.md)

---

## 📄 License

[MIT](../LICENSE)
