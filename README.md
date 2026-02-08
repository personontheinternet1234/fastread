# fastread

Utilizing ChatGPT response streaming and Rapid Serial Visual Presentation (RSVP), fastread helps you to read about 4x as fast (regular reading in wpm: 250. Reading using this and RSVP: ~1000).

Inspired by this video by "Buffed" on youtube: https://youtu.be/NdKcDPBQ-Lw?si=Lkx1QNXcHn0NjjCt

(Optional) Create a virtual environment:
```bash
python -m venv venv
. venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
export OPENAI_API_KEY=yourapikey
```

```bash
python src/main.py
```

Set wpm to however fast you want to read (750 wpm?).

Choose whether or not to minimize the full response record (I'd minimize it if I were you, using the top right button, as it's kinda distracting)

Write a prompt (probably something higher-level like about a definition or how something works, not math or code, as I don't render latex or anything), and press enter.

Look on the red, centered letter, and focus hard. You should be able to read and understand the response from ChatGPT faster than you would by just scanning a response on the website.

Once done, you can view the full response via the full response record.

You can also type up new prompts once the old one is finished.
