# Chat Writes the Laws

Twitch chat writes the physics of a tiny world in one fixed sentence:
`when ball hits wall it turns red`. A deterministic compiler turns each sentence into an executable
test; Codex patches one file (`chatlaws/lawtable.py`) until the test passes; the viewer's name goes into
`RULEBOOK.md` and onto the screen. Chat text outside the grammar is dropped and never reaches the agent,
the screen or any log (only a counter). See SPEC.md.

    python3 -m unittest discover -s tests -t .
    python3 -m chatlaws.cli apply --author local_dev --text "when ball hits wall it turns red"
    python3 -m chatlaws.cli live <channel> --seconds 600     # anonymous read-only IRC + screen
    # screen: http://127.0.0.1:8765/  -> OBS "Browser" source, 1280x720, no external requests

Live loop: IRC line -> grammar (drop = counter only) -> queue -> precompiled test (112 grammar combinations)
-> red -> `codex exec` patches the law table -> green -> `state.json` -> canvas + rulebook overlay.
Screenshots and the red test output are in `docs/`.
