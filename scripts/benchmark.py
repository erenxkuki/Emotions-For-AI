"""Performance benchmark for EFA core."""

import time

from emotions_ai import EmotionAI


def main():
    ai = EmotionAI(persistence=False)
    n = 100
    t0 = time.perf_counter()
    for i in range(n):
        ai.chat_sync(user_id="bench", message=f"message {i}")
    dt = time.perf_counter() - t0
    print(f"chat_sync x{n}: {dt:.3f}s ({n/dt:.1f} ops/s)")

    # simulation
    import asyncio

    t0 = time.perf_counter()
    asyncio.run(ai.simulate_time("bench", duration_seconds=86400, step_seconds=60))
    print(f"simulate 24h/60s: {time.perf_counter()-t0:.3f}s")


if __name__ == "__main__":
    main()