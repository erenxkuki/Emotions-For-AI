"""Generate a synthetic emotion dataset (JSONL) for Emotions for AI."""

import json
import random

random.seed(42)

templates = {
    "happy": [
        "I am so happy about {t}", "I finally {t} and feel great", "This is wonderful news about {t}",
        "I feel joyful and excited", "I am thrilled with the result", "Great success today with {t}",
        "I am delighted and grateful", "What a fantastic outcome for {t}", "I feel amazing right now",
        "I am really pleased with {t}", "I am in a great mood", "This made my day better",
        "I am smiling and content", "I feel upbeat and positive", "I am so glad about {t}",
        "Everything is going well", "I am cheerful and energized", "I feel blessed and happy",
        "This is the best news", "I am overjoyed with {t}",
    ],
    "sad": [
        "I feel sad and lost", "I am struggling lately", "Everything feels difficult and heavy",
        "I am disappointed and tired", "I feel lonely and down", "I am heartbroken about {t}",
        "I feel hopeless and empty", "I am grieving and sorrowful", "I feel blue and weary",
        "I am melancholic and sad", "I feel dejected and low", "I am unhappy about {t}",
        "I feel miserable and alone", "I am downcast and gloomy", "I feel sorrowful and tired",
        "I am depressed and sad", "I feel wretched and unhappy", "I am despondent about {t}",
        "I feel forlorn and lost", "I am sad and disappointed",
    ],
    "curious": [
        "I am curious about how this works", "Tell me more about it", "I wonder what happened",
        "I want to explore this idea", "How does this mechanism function", "I am intrigued by {t}",
        "I am eager to learn more", "I have a question about {t}", "I am inquisitive and interested",
        "I want to understand {t}", "I am curious and engaged", "Tell me how {t} works",
        "I wonder if {t} is true", "I am fascinated by {t}", "I want to know more about {t}",
        "I am questioning and exploring", "I am curious about the details", "I wonder why {t}",
        "I am interested in {t}", "I want to investigate {t}",
    ],
    "concern": [
        "I am worried and anxious", "I feel concerned about the situation", "I am nervous and uneasy",
        "This makes me a bit fearful", "I am afraid of failing", "I am worried about {t}",
        "I feel uneasy and tense", "I am anxious about {t}", "I am concerned and watchful",
        "I feel apprehensive about {t}", "I am worried and tense", "I am concerned for {t}",
        "I feel uneasy about {t}", "I am anxious and nervous", "I am worried about the outcome",
        "I feel concerned and afraid", "I am uneasy and worried", "I am anxious about {t}",
        "I feel concerned and tense", "I am worried and watchful",
    ],
    "frustrated": [
        "I am frustrated that it broke again", "This is so annoying and irritating", "I am angry at the delay",
        "Why does this keep failing", "I am upset about the mistake", "I am frustrated with {t}",
        "This is infuriating and annoying", "I am irritated by {t}", "I am angry and frustrated",
        "I am annoyed and upset", "I am frustrated and angry", "I am upset about {t}",
        "This is so frustrating", "I am irritated and annoyed", "I am angry and upset",
        "I am frustrated with the result", "I am annoyed and angry", "I am upset and frustrated",
        "This makes me angry", "I am frustrated and irritated",
    ],
    "relieved": [
        "I am relieved it is finally over", "Thank goodness that ended well", "I feel better now",
        "That was a close call but okay", "I am glad it worked out", "I am relieved about {t}",
        "I feel relieved and calm", "I am glad and relieved", "I feel at ease now",
        "I am relieved and happy", "I feel relieved and better", "I am glad {t} is over",
        "I feel relieved and relaxed", "I am relieved and grateful", "I feel calm and relieved",
        "I am relieved and content", "I feel relieved and safe", "I am glad and relieved",
        "I feel relieved and okay", "I am relieved and at peace",
    ],
}
topics = ["the project","the result","the exam","the situation","the delay","the mistake","the outcome","the plan","my work","the news"]

samples = []
for label, tmpls in templates.items():
    for t in tmpls:
        for _ in range(5):  # 5 variations per template
            s = t.format(t=random.choice(topics)) if "{t}" in t else t
            samples.append({"text": s, "label": label})

random.shuffle(samples)
with open("data/emotions_db.jsonl", "w", encoding="utf-8") as f:
    for s in samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")
print(f"Generated {len(samples)} samples -> data/emotions_db.jsonl")