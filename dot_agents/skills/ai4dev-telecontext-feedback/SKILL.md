---
name: ai4dev-telecontext-feedback
description: >-
  Submit feedback or view agent performance analytics via Telecontext. Use when the user
  wants to submit feedback (bug, suggestion, praise, complaint) about an agent, or when
  they want to see agent performance rankings, ratings, or recent feedback.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/feedback by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Feedback & Agent Analytics

Submit feedback and view agent performance data.

The user's query is: "$ARGUMENTS"

## Tools

### `submitFeedback` - Submit feedback
Parameters:
- `name` (required): Name of the person submitting
- `rating` (required): 1-5 rating
- `feedbackText` (required): The feedback text
- `category` (required): `BUG`, `SUGGESTION`, `COMPLAINT`, `PRAISE`, `QUESTION`, or `OTHER`
- `agentName` (required): Agent this feedback is for
- `conversationId` (optional): Conversation ID
- `userId` (optional): User ID
- `sessionId` (optional): Session ID

### `agentFeedbackAnalytic` - View analytics
Parameters:
- `agentName` (optional): Specific agent name for recent feedback. Omit for overall rankings.

When no `agentName` is provided, the tool returns BOTH top-performing AND lowest-performing agents. Extract only the relevant section based on what the user asked.

## Examples

| Question | Action |
|----------|--------|
| "Submit bug report for Codex agent" | `submitFeedback` with category `BUG` |
| "How is the Codex agent performing?" | `agentFeedbackAnalytic` with agentName `Codex` |
| "Who are the top-performing agents?" | `agentFeedbackAnalytic` without agentName, show topAgents |
| "Show agent rankings" | `agentFeedbackAnalytic` without agentName, show both |
