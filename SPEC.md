# SPEC - Chat Writes the Laws

## Purpose (목적)
Twitch chat co-authors the rules of a small physics world. A viewer types one sentence in a fixed
grammar. The sentence is compiled into an executable test. Codex then fixes the engine until the
test passes, and the viewer's name is written into the rulebook. Untrusted chat text never reaches
the agent: only the compiled test does.

## Ubiquitous language
- **Sentence**: raw chat text. **Law**: a parsed sentence (`subject`, `object`, `color`, `author`).
- **Grammar**: `when <thing> hits <thing> it turns <color>` over a closed vocabulary.
- **Compiler**: sentence -> Law -> test source. The only door from chat to the agent.
- **Engine**: `chatlaws/engine.py`, the world simulation Codex edits.
- **Rulebook**: `RULEBOOK.md`, one line per accepted law with its author.

## Success conditions (성공 조건, numbers)
1. Grammar: 100% of 8 valid fixtures accepted, 100% of 12 invalid fixtures (injection, emoji, unknown word, too long, non-ASCII) rejected.
2. Conflict: a second law with the same (subject, object) and a different color is rejected 100%; exact duplicates rejected.
3. Compile: one accepted sentence yields exactly 1 runnable test file; it fails (red) against the baseline engine.
4. Agent boundary: the Codex prompt contains 0 bytes of raw chat text (asserted by test).
5. Core loop once, locally: sentence -> compile -> red -> `codex exec` fix -> green -> rulebook line with author, end to end under 300 s.
6. Anonymous Twitch IRC line parsing: 100% of 5 fixture lines parsed, PING/JOIN lines ignored.
7. Unit tests: >= 15, all green; zero third-party dependencies (stdlib only).

## Given / When / Then
- Given an empty rulebook, When viewer `alice_01` sends `when ball hits wall it turns red`, Then a Law is accepted and a test file `tests/laws/test_law_001_ball_wall.py` is written.
- Given that law exists, When `bob_02` sends `when ball hits wall it turns blue`, Then it is rejected with reason `conflict` and nothing is written.
- Given any text outside the grammar, When it is submitted, Then it is rejected with reason `grammar` and is never shown, stored or sent to Codex.
- Given an accepted law whose test is red, When Codex edits the engine and the test turns green, Then `RULEBOOK.md` gets a line naming the author and the Codex session id is recorded.

## Non-goals (비목표)
- Chat raw text never reaches the agent: it is not passed to a prompt, file, or log outside the grammar compiler.
- No writing to Twitch chat, no Twitch login, no developer app, no viewer accounts impersonated.
- No LLM calls at stream time; the compiler is deterministic.
- No payments, no API keys.
