# SpotBot Data Formalization Plan

This document outlines how we will process the raw exercise data in `SpotBotData` to create a high-quality, spec-driven database for SpotBot.

## Current State
- `finalCombinedExercises.json`: ~2.3MB, likely contains the bulk of the data.
- `scrapedExercises.json` & `freeExercises.json`: Supporting sources.
- `duplicates.json`: Already identified issues.

## Objectives
1. **Deduplication**: Merge overlapping records while preserving the best descriptions and metadata.
2. **Standardization**: Ensure all muscle groups, equipment types, and difficulty levels use a consistent enum-like schema.
3. **Anatomy Mapping**: Add precise primary and secondary muscle targets to match the "Fitbod" style heatmap.
4. **Instruction Cleanup**: Use LLM agents to rewrite instructions for clarity and "SpotBot" tone.
5. **Appwrite Preparation**: Format data for bulk import into Appwrite collections.

## Action Steps

### Phase 1: Analysis
- An agent will script a scan of `finalCombinedExercises.json` to count unique muscle groups and equipment.
- Identify "sparse" records (missing images, instructions, or targets).

### Phase 2: Extension
- Cross-reference with competitor research (Strong/Fitbod) to find missing exercises (e.g., specific yoga poses, mobility drills).
- Fetch or generate placeholder SVG/Images for exercises that lack them.

### Phase 3: Formalization
- Create a `exercises_v1.json` which follows the exact Appwrite schema.
- Create a "Local Seed" version (SQLite compatible) for the app's initial offline database.

## Automation Workflow
The **Data Engineer Agent** will run scripts in the `SpotBotData/Scripts` directory to perform these transformations automatically.
