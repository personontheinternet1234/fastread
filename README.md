# fastread

Utilizing Rapid Serial Visual Presentation (RSVP), fastread helps you to read about 4x as fast (regular reading in wpm: 250. Reading using this and RSVP: ~1000).

You can use fastread to prompt ChatGPT and read responses really quickly, OR to read through a pdf really quickly (I use it for my CI-H readings lol)

Inspired by this video by "Buffed" on youtube: https://youtu.be/NdKcDPBQ-Lw?si=Lkx1QNXcHn0NjjCt

(Optional) Create a virtual environment:
```bash
python -m venv venv
. venv/bin/activate
```

Install required python packages
```bash
pip install -r requirements.txt
```

Run fastread
```bash
python src/main.py
```

How to use fastread with ChatGPT:

1) Set your OpenAI API Key
```bash
export OPENAI_API_KEY=yourapikey
```

2) Set wpm to however fast you want to read (750 wpm?).

3) Choose whether or not to minimize the full response record (I'd minimize it if I were you, using the top right button, as it's kinda distracting)

4) Write a prompt (probably something higher-level like about a definition or how something works, not math or code, as I don't render latex or anything), and press enter.

5) Look on the red, centered letter, and focus hard. You should be able to read and understand the response from ChatGPT much faster than you would by just scanning a response on the website.

How to use fastread with PDFs:

1) Upload your PDF by dragging it into the window.

2) Set wpm to however fast you want to read (750 wpm?).

3) Choose whether or not to minimize the full response record (I'd minimize it if I were you, using the top right button, as it's kinda distracting)

4) Press the button in the top right.

5) Look on the red, centered letter, and focus hard. You should be able to read and understand the response much faster than you would by just scanning the pdf.

Once done, you can view the full response via the full response record.

You can also type up new prompts once the old one is finished.

You can turn off the UI if distracting using TAB

You can pause / play your current content or skip it using the buttons on the top right
