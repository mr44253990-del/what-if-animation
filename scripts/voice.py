"""Step 2: Voice Generation — Google Gemini TTS

Completely remove ElevenLabs and migrate the entire voice generation pipeline to Google's Gemini Text-to-Speech API.

TTS Model:
"gemini-3.8-flash-tts"

Requirements:

1. Use Google Gemini TTS exclusively. Remove all ElevenLabs dependencies, API calls, voice IDs, authentication, and configuration.
2. Use "GEMINI_API_KEY" from environment variables.
3. Support Google's built-in voice selection, voice style, accent, emotion, narration speed, and expressive delivery.
4. Read "src/episodes/<slug>/episode.json".
5. Generate natural, cinematic narration with consistent voice identity.
6. Preserve the existing genre-specific pause and pacing system.
7. Generate word-level timestamps using a separate forced-alignment process on the generated audio. Do not assume Gemini returns word timestamps.
8. Adjust timestamps after audio tightening so every word remains synchronized with the final audio.
9. Cache generated audio using a hash of the script, model, voice, and voice settings. Changing only pause settings must not trigger another Gemini API call.
10. Print Gemini API usage and estimated credits/cost when available.

Command:

"python <skill>/scripts/voice.py <slug> [--force]"

Output files:

- "public/<slug>/voice_raw.wav" — Original Gemini-generated audio.
- "public/<slug>/voice.wav" — Final tightened audio.
- "src/episodes/<slug>/words.json" — Final synchronized word timestamps.
- "out/<slug>/words_raw.json" — Original alignment data.

episode.json voice configuration:

{
  "voice": {
    "provider": "google",
    "model": "gemini-3.8-flash-tts",
    "id": "Kore",
    "style": "Cinematic storyteller, deep expressive narration",
    "language": "en-US"
  },
  "gaps": {
    "word": 0.12,
    "comma": 0.2,
    "sentence": 0.3,
    "question": 0.45,
    "pairs": {
      "anything|One": 0.6
    }
  }
}

Important:
Google api key... AQ.Ab8RN6IIdaygdOx-GxuxF4lSDfvl7kqQivvPLUDsA44GGUSp6g.....
- Use Google's official Gemini TTS API.
- Support both WAV generation and audio processing.
- Keep compatibility with the existing "plan.py" pipeline.
- Preserve all existing output schemas and timing formats.
- Automatically handle API errors, retries, and caching.
- Never fall back to ElevenLabs.
- Do not regenerate audio when only gap values change.
- Ensure final word timestamps match the tightened audio precisely.

Deliver a fully working migration, not just a modified configuration file. Update dependencies, API integration, alignment, caching, and all related scripts.nger than its limit is cut to the limit, from its middle.
"""
import base64, hashlib, json, re, sys, time

import numpy as np

from wi import SR, api, spent_since, decode, ep_dir, load_episode, load_json, log_cost, out_dir, pub_dir, save_json, write_wav

slug = sys.argv[1]
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash-tts",
    input=[{
        "type": "user_input",
        "content": [{
            "type": "text",
            "text": "Have a wonderful day!",
            "annotations": [{
                "type": "speech_metadata",
                "style": "cheerful and friendly",
            }],
        }],
    }],
    response_format={"type": "audio"},
    generation_config={
        "speech_config": [
            {"voice": "Kore"},
        ]
    },
)

with open("out.wav", "wb") as f:
    f.write(base64.b64decode(interaction.output_audio.data))
