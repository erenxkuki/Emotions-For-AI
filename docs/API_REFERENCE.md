# API Reference

High-level: `EmotionAI(model=..., persistence=True)`, `.chat()`, `.chat_sync()`,
`.chat_stream()`, `.get_state()`, `.state_history()`, `.clear_state()`,
`.delete_user_memory()`, `.export_state()`, `.simulate_time()`.

REST: `/health`, `/chat`, `/state/{user_id}`, `/state/{user_id}/history`,
`/memory/{user_id}`.