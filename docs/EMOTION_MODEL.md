# Emotion Model

States are multidimensional: valence, arousal, intensity, persistence, confidence,
relevance, uncertainty, temporal duration, origin, context association.

Multiple simultaneous states are allowed; no forced single label.

Intensity update (conceptual):

I(t+dt) = decay(I(t), dt) + reinforcement(E, C, M)

Where E=experience significance, C=context relevance, M=relevant memory.
Bounded to [0,1]. Decay functions configurable. Reinforcement constrained.

Transitions are context-dependent suggestions, not inevitable sequences.