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

8. Live loop (new): anonymous IRC line -> grammar -> queue -> compile -> red -> patch -> green -> screen, wired end to end. Only in-grammar sentences enter the queue; everything else only increments a counter.
9. Latency: chat line accepted by the grammar to law visible in `state.json` (the file the screen polls) <= 20 s, measured 3 times in `projects` notes. The patch scope is one file, `chatlaws/lawtable.py` (the law table); test templates are precompiled per grammar combination (4 x 4 x 7 = 112).
10. Screen: one local HTML page, no external URL, usable as an OBS browser source. A canvas physics scene plus a rulebook overlay (law text + author name) plus a conflict-rejection toast. >= 3 distinct laws are visibly applied in a headless screenshot.

## Given / When / Then
- Given an empty rulebook, When viewer `alice_01` sends `when ball hits wall it turns red`, Then a Law is accepted and a test file `tests/laws/test_law_001_ball_wall.py` is written.
- Given that law exists, When `bob_02` sends `when ball hits wall it turns blue`, Then it is rejected with reason `conflict` and nothing is written.
- Given any text outside the grammar, When it is submitted, Then it is rejected with reason `grammar` and is never shown, stored or sent to Codex.
- Given an accepted law whose test is red, When Codex edits the engine and the test turns green, Then `RULEBOOK.md` gets a line naming the author and the Codex session id is recorded.
- Given a running watcher on a channel, When a chat line inside the grammar arrives, Then it is queued, compiled, patched into the law table, and `state.json` lists the law with its author within 20 s of the line being accepted.
- Given a running watcher, When a chat line outside the grammar arrives, Then only the counter `dropped` in `state.json` goes up; the text and the author are not on the screen, not in `state.json`, not in the log, not in the Codex prompt.
- Given the screen is open, When `state.json` gains a law, Then the overlay shows `Law NNN`, the sentence and `@author`, and the next time the subject hits the object in the physics scene the subject changes color.
- Given a second law with the same (subject, object) and a different color, When it arrives, Then the screen shows a `conflict` toast naming the sentence (it is inside the grammar) and the world does not change.
- Given a developer typed a sentence on the command line, Then its author label stays `local_dev`; no viewer is imitated.

## UI acceptance (UI 수용기준)
The screen is a fixed 1280x720 stream overlay (OBS browser source), scaled to fit; it is read from a distance, not touched.
1. Mobile first: N/A as a primary target (stream surface); it still scales to any window with no scrollbars (checked at 1280x720).
2. One screen, one question: the only prompt is the example sentence at the top of the rulebook; there are no inputs or buttons.
3. Type hierarchy: law sentence 17 px, toast 19 px, labels 12 to 15 px, weight >= 400, one system font.
4. Spacing: values on a 4 px grid (ui_audit spacing_grid >= 80%, measured 100%); panel padding 24 px.
5. Bottom CTA: N/A (no buttons).
6. Numbers first: the rulebook shows the law number first; the dropped-line counter is the footer.
7. Evidence folded: N/A (no tables).
8. Microcopy: short active English, a conflict states `Conflict - rejected` and the sentence.
9. Color and contrast: dark surface, one brand accent (Twitch purple), one status color (red for conflict); text on the panel >= 4.5:1.
10. Performance and dependencies: 0 external URLs (asserted by test), state polled every 400 ms from the local server.

## Non-goals (비목표)
- Chat raw text never reaches the agent: it is not passed to a prompt, file, or log outside the grammar compiler.
- No writing to Twitch chat, no Twitch login, no developer app, no viewer accounts impersonated.
- No LLM calls at stream time; the compiler is deterministic.
- No payments, no API keys.
