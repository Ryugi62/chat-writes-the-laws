# Chat Writes the Laws

Twitch chat writes the physics of a tiny world in one fixed sentence:
`when ball hits wall it turns red`. A deterministic compiler turns each sentence into an executable
test; Codex fixes the engine until the test passes; the viewer's name goes into `RULEBOOK.md`.
Chat text outside the grammar is dropped and never reaches the agent. See SPEC.md.

    python3 -m unittest discover -s tests -t .
    python3 -m chatlaws.cli apply --author alice_01 --text "when ball hits wall it turns red"
    python3 -m chatlaws.cli watch xqc --seconds 20   # anonymous read-only IRC
