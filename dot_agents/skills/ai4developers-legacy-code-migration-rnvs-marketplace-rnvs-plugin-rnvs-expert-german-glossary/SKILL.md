---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-german-glossary
description: Complete German-English glossary for RNVS/VNRM telecommunications terminology with context-aware translation. This skill should be used when encountering German variables, abbreviations, or technical terms in legacy RNVS code or documentation.
allowed-tools: Read
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/german-glossary by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# German Telecommunications Glossary Skill

## Purpose

Provides comprehensive German-English translation for RNVS/VNRM terminology, abbreviations, and technical concepts for analyzing legacy RNVS code that contains German variable names, abbreviations, or business terms.

## When to Use

- Translating German variable names (rfnr, rnb, onkz, etc.)
- Expanding German abbreviations (RNB, TNB, PDA, BNetzA, etc.)
- Understanding compound German words (Rufnummernverwaltungssystem)
- Disambiguating context-specific terms (Besitzer vs Eigentümer)
- Creating German business documentation (Fachkonzept)

## Quick Reference

The glossary contains **200+ telecommunications terms** organized in these categories:

1. **Core Telecommunications Terms** - RNB, TNB, PDA, ONKZ, etc.
2. **System Components** - RNVS, VNRM, DDS, ComServ, etc.
3. **Organizational Abbreviations** - BNetzA, DTAG, DTIT, etc.
4. **Technical Abbreviations** - PK, VE, NZ, BSA, etc.
5. **Network & Technology** - PSTN, IMS, SIP, VoIP, etc.
6. **Cloud & Infrastructure** - OTC, TPC, FCI, DCP, etc.

**See [REFERENCE.md](REFERENCE.md) for the complete glossary tables.**

## Instructions

### 1. Variable Translation

When encountering a German variable name:
1. Check the variable glossary in REFERENCE.md
2. Find the English translation and German full form
3. Note the data type and context

**Example**: `rfnr` → `callNumber` (Rufnummer - Phone number)

### 2. Abbreviation Expansion

When encountering an abbreviation:
1. Check the abbreviation glossary in REFERENCE.md
2. Get the German full form, English translation, and context
3. Note which category it belongs to

**Example**: `RNB` → Rufnummernblock (Number Block) - Core Telecommunications

### 3. Context-Aware Translation

Some terms have different meanings based on context:

- **Besitzer** → "possessor" (in porting context) or "holder" (in legal context)
- **Eigentümer** → "owner" (legal owner, originator)
- **Auftrag** → "order" (booking context) or "task" (work context)

See REFERENCE.md Special Cases section for full details.

### 4. Compound Word Decomposition

For long German compound words:
1. Check the compound words section in REFERENCE.md
2. Break down into component parts
3. Understand the combined meaning

**Example**: `Rufnummernverwaltungssystem` → Rufnummer + Verwaltung + System → Phone Number Management System (RNVS)

## Usage in Commands

Commands dealing with German code should reference this skill:

```markdown
**Refer to the german-glossary skill** for German term translations and abbreviation full forms.
```

## Progressive Disclosure

- **SKILL.md** (this file) - Instructions and overview
- **[REFERENCE.md](REFERENCE.md)** - Complete glossary tables (200+ terms)
- **[examples.md](examples.md)** - Practical usage examples

Load REFERENCE.md when looking up specific terms.
Load examples.md when needing to see translation patterns.

## Best Practices

1. **Always provide both forms**: German (English) for traceability
2. **Use context clues**: Choose the right translation based on usage
3. **Document unknowns**: If a term isn't in the glossary, note "Unknown - needs verification"
4. **Preserve system names**: Keep RNVS, VNRM, DDS, ComServ as-is
5. **Expand on first use**: Spell out abbreviations with full form on first mention

---

**For the complete glossary database, see [REFERENCE.md](REFERENCE.md)**
