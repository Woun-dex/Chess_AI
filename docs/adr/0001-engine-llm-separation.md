# ADR 0001: Separation of Engine Calculation from LLM Instruction

## Status
Accepted

## Context
In building an intelligent Chess AI Tutor, two distinct capabilities are required:
1. **Absolute Truth & Accuracy in Chess Calculation**: Evaluation of moves, detecting legal moves, determining best continuations, identifying blunders/mistakes, and positional depth scoring.
2. **Pedagogical Explanation & Natural Language Coaching**: Explaining *why* a move was a mistake, translating engine evaluations into human concepts (e.g., "weak d5 pawn", "premature queen outing", "hanging minor piece"), asking the student Socratic questions, and generating interactive exercises.

LLMs are probabilistic language models prone to hallucinations, non-determinism, and calculation failures on complex board states. They cannot reliably calculate tactical lines or verify chess legality. Conversely, chess engines (Stockfish 16/17 via UCI protocol) provide deterministic, superhuman evaluation but output raw centipawns or mate-in-N with algebraic move sequences that mean little to a human student.

## Decision
We enforce a strict boundary:
- **Stockfish is the single source of truth for all chess calculations, evaluations, legality validation (supported by `python-chess`), and engine play.**
- **The LLM (via an adapter pattern) is strictly a pedagogical tutor.**
- **The LLM will NEVER independently determine move legality, calculate evaluations, or propose candidate moves from scratch without engine validation.**
- All prompts sent to the LLM tutor must inject pre-calculated, structured engine data:
  - Position FEN
  - Engine evaluation (centipawns / mate)
  - Engine best move and alternative candidate lines
  - Move classification (Brilliant, Great, Best, Excellent, Good, Inaccuracy, Mistake, Blunder)
  - Tactical motifs identified by heuristic analysis (pin, fork, skewer, undefended piece)

## Consequences
### Positive
- Zero engine hallucinations presented to the user as chess truth.
- Explanations remain grounded in objective calculations.
- Cost and latency optimization: engine evaluations run in dedicated async workers and are cached by FEN hash; LLM calls only happen when tutoring/explanation is explicitly requested.

### Negative
- Requires a structured data transformation layer between Stockfish UCI output and LLM prompt context.
- System requires high-performance async workers to run UCI engine analysis without blocking tutor chats.

