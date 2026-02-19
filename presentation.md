---
marp: true
theme: default
paginate: true
style: |
  :root {
    --color-bg: #fdfdfd;
    --color-fg: #2d2d2d;
    --color-accent: #3b82f6;
    --color-accent-light: #eff6ff;
    --color-muted: #6b7280;
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  }
  section {
    background: var(--color-bg);
    color: var(--color-fg);
    padding: 60px 80px;
  }
  h1 {
    color: var(--color-accent);
    font-weight: 700;
  }
  h2 {
    color: var(--color-fg);
    border-bottom: 2px solid var(--color-accent);
    padding-bottom: 8px;
    font-weight: 600;
  }
  h3 {
    color: var(--color-muted);
    font-weight: 400;
  }
  a {
    color: var(--color-accent);
  }
  code {
    background: var(--color-accent-light);
    color: var(--color-accent);
    padding: 2px 6px;
    border-radius: 4px;
  }
  pre code {
    background: #1e293b;
    color: #e2e8f0;
  }
  pre {
    background: #1e293b;
    border-radius: 8px;
    padding: 24px;
  }
  blockquote {
    border-left: 4px solid var(--color-accent);
    padding-left: 20px;
    color: var(--color-muted);
    font-style: italic;
  }
  ul, ol {
    line-height: 1.8;
  }
  section.lead {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  section.lead h1 {
    font-size: 2.8em;
    margin-bottom: 0;
  }
  section.lead h3 {
    font-size: 1.3em;
  }
  section.lead p {
    font-size: 1.2em;
    max-width: 70%;
  }
  em {
    color: var(--color-accent);
    font-style: normal;
    font-weight: 600;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# marp2video

### Narrated presentations from Markdown

<!-- My name is PJ. Occasionally I have to make demo or training videos. Over the past year I've gotten increasingly frustrated with the process of doing this. So I built something to fix it. -->

---

## The Problem

- Recording demo or training videos is painful
- You need a quiet room, a microphone, no background noise
- You stumble over words, re-record, stumble again
- Eventually you get something usable

<!-- If you want the audio to sound decent, you need to find a quiet room, set up a microphone, make sure there's no background noise. Then you record your script, and inevitably you stumble over a word or realize you said something wrong. So you do another take. And another. Eventually you get something usable. -->

---

## The Worse Problem

- A week later, you need to update that video
- Maybe the API changed, or there's a better way to explain something
- You can re-record the whole thing, or splice in a patch that never matches

> Updating a training video used to take hours.
> iMovie seems unnecessarily complicated for simple decks with narration or a screencast.

<!-- But here's where it gets worse. A week later, you need to update that video. Maybe the API changed, or there's a new feature, or you just found a better way to explain something. Now you have two choices. Re-record the entire thing to keep the audio consistent, or record just the changed section and try to splice it in. And it never quite matches. The tone is different, the room sounds different, the energy level is off. So most of us just live with outdated training materials because updating them is such a hassle. Updating a single training video used to cost me 45 minutes of re-recording. Now I edit the Markdown and regenerate. Thirty seconds. -->

---

<!-- _class: lead -->

# marp2video

Write slides in Markdown. Add speaker notes.
Run one command. Get a narrated video.

<!-- I built something to solve this. It's called marp2video. You write your presentation as a Markdown file. You put your narration in the speaker notes, inside HTML comments. Then you run one command and get a full narrated MP4 video. Need to make a change? Edit the text, regenerate. That's it. No microphone. No quiet room. Just Markdown to video. -->

---

## Why Not a Cloud TTS Service?

### Cost
- Services like ElevenLabs charge per character
- Fine for occasional use, but it adds up fast for training content
- With marp2video, generation is free after setup

### Privacy
- Cloud services send your scripts and voice to third-party servers
- With marp2video, everything runs locally -- your content never leaves your machine

<!-- You might be thinking, don't tools like this already exist? What about ElevenLabs or other voice cloning services? They do exist, and they're good. But there are two problems. First, cost. These services charge per character or per minute. If you're frequently updating training materials, that adds up. With marp2video, once you've set it up, every generation is free. Second, privacy. When you use a cloud service, your scripts go to their servers. If your training materials cover proprietary systems or sensitive information, you're handing that to a third party. With marp2video, the TTS engine runs on your machine. Your voice model stays local. Nothing leaves your computer. -->

---

## Markdown as Single Source of Truth

- One `.md` file contains your slides, your script, and your content
- The same file renders as a slide deck, a narrated video, or a web page
- Plain text is trivially ingestible for RAG and semantic search
- Your knowledge base and your presentations become the same artifact

<!-- Here's something I didn't expect when I started using this. When your entire presentation lives in a single Markdown file, that file becomes useful for a lot more than making videos. The slide content and the speaker notes together form a complete written document. You can feed it directly into a RAG pipeline. An LLM can index it, search it, answer questions about it. Try doing that with a video file or a PowerPoint. You'd need to transcribe the audio, extract text from images, piece it all together. With Markdown, the content is already structured plain text. It's ready to be ingested as-is. -->

---

## Content Lives in Git

- Markdown diffs are clean and easy to review
- Speaker note changes show up in pull requests like any other text
- Branch, review, and merge presentation updates the way you manage code
- The video is a build artifact -- not the source of truth

<!-- Because it's all Markdown, it fits naturally into Git. You can diff your presentations. You can see exactly what changed between versions. Someone fixes a factual error in a speaker note? That's a one-line change in a pull request. You review it, approve it, merge it. Now try reviewing a change to a video file in a PR. You can't. The video is opaque. With this approach, the Markdown is what you version and collaborate on. The MP4 is just an output you generate from source, the same way you compile code. You could even regenerate videos in CI. Push a change and your pipeline rebuilds the video automatically. -->

---

## Accessibility for Free

- Speaker notes are the transcript -- they exist *before* the video does
- Slide content provides structure and visual information
- Together they satisfy WCAG multimedia text-alternative requirements
- No separate captioning or transcription step needed

<!-- There's an accessibility angle here that I think is underappreciated. WCAG guidelines require text alternatives for multimedia. Usually that means someone has to go back and caption the video or write a transcript after the fact. It's tedious, so it often doesn't happen, or it gets done badly. With marp2video, you wrote the transcript first. The speaker notes are the script. You satisfy the text-alternative requirement before the video even exists. The accessible version isn't an afterthought, it's the input. -->

---

## How It Works

```
 .md file  ──▶  Parse  ──▶  Render  ──▶  TTS  ──▶  Assemble  ──▶  .mp4
                  │           │           │            │
              split slides  Marp CLI  Chatterbox    ffmpeg
              extract notes  → PNG    → WAV per     → segment
                                       slide         → concat
```

<!-- Under the hood, marp2video runs a four-stage pipeline. Parse the Markdown, render slides as PNGs with Marp CLI, synthesize audio with Chatterbox TTS, and stitch it all together with ffmpeg. If you give it a short sample of your voice, the TTS clones you. It picks up your timbre, your pacing, enough that people do a double take. Let me walk through each stage. -->

---

## Stage 1: Parsing

- Splits the Markdown on `---` delimiters, the same separators Marp uses
- First block is YAML front matter (theme, styles) -- skipped
- HTML comments are extracted as speaker notes
- Marp directive comments like `<!-- _class: lead -->` are filtered out
- Each slide becomes a `Slide` dataclass: index, body text, and notes

```python
@dataclass
class Slide:
    index: int
    body: str
    notes: str | None
```

<!-- Parsing is the boring part, which is good. Split on triple-dash delimiters. The first block is YAML front matter, skip it. Then for each slide block, pull out the HTML comments. One wrinkle: Marp uses HTML comments for its own directives too, things like underscore-class or underscore-paginate. Those get filtered out with a regex so they don't end up in the narration. I learned that one the hard way when my first test video started reading out "class colon lead" in the middle of a sentence. What you're left with is a list of Slide dataclasses. Index, body, notes. That's it. -->

---

## Stage 2: Rendering

- Calls Marp CLI via `npx @marp-team/marp-cli` or a global `marp` install
- Renders the entire deck as PNG images at 2x scale for 1920x1080 output
- Output files are numbered: `slides.001`, `slides.002`, etc.
- A sanity check confirms the image count matches the parsed slide count

```bash
npx @marp-team/marp-cli presentation.md \
    --images png --image-scale 2 --output slides
```

<!-- Rendering is just a subprocess call to Marp CLI. It checks for a global marp install first, falls back to npx if you don't have one. We ask for PNG output at 2x scale, which gets us 1920 by 1080 images. Marp numbers the output files as slides dot 001, slides dot 002, and so on. There's a sanity check after this step. If the parser found 12 slides but Marp only produced 11 images, we bail out immediately. Better to stop here than produce a video where slide 7's audio plays over slide 8's image and you don't notice until someone else watches it. -->

---

## Stage 3: TTS with Chatterbox

- Chatterbox TTS runs locally -- no API calls, no data leaving your machine
- Sentences are grouped into chunks of four before synthesis
- Each chunk becomes a tensor, concatenated with `torch.cat` into one WAV
- Voice cloning takes a short WAV sample of your voice
- Slides without notes get a silence WAV written in pure Python

```python
# Chunking: 12 sentences → 3 TTS calls instead of 12
sentence_groups = [" ".join(sentences[i:i+4])
                   for i in range(0, len(sentences), 4)]
```

<!-- This is the slow part. Chatterbox is a neural TTS model, runs on your local GPU or CPU. You give it a WAV sample of your voice and it clones you. The first version of this generated one sentence at a time, and it sounded choppy. The model would reset its prosody at every sentence boundary. So now it groups four sentences together before each generation call. The difference is obvious. You get natural pacing across sentences because the model sees a full paragraph instead of fragments. Each chunk comes back as a tensor. We concatenate them all with torch dot cat and write one WAV per slide. For slides with no speaker notes, it just writes a silent WAV. That's pure Python, a RIFF header and zeroed sample data, no audio libraries needed for that part. -->

---

## Stage 4: Assembly with ffmpeg

- Each slide becomes an MPEG-TS segment: image looped for the audio duration
- Video uses `libx264` with the `stillimage` tune -- almost no bitrate wasted
- Images are scaled and padded to exactly 1920x1080
- Audio is encoded as 192 kbps AAC
- Segments are concatenated with ffmpeg's concat demuxer into the final MP4

```
slide.png + audio.wav  ──▶  segment_001.ts
slide.png + audio.wav  ──▶  segment_002.ts
                            ...
all .ts files  ──▶  concat demuxer  ──▶  output.mp4
```

<!-- Last stage. For each slide we build an MPEG transport stream segment. The PNG gets looped as video frames for exactly the duration of that slide's audio. We use x264 with the stillimage tuning flag, which tells the encoder that frames aren't changing. It figures out pretty quickly that every frame is identical and the video bitrate drops to almost nothing. Images get scaled and padded to 1920 by 1080 regardless of their original aspect ratio, so the output is always consistent. Audio goes through AAC at 192 kilobits. Then once all the segments exist, ffmpeg's concat demuxer joins them. That last step is just a stream copy. No re-encoding. It writes the final MP4 in a couple of seconds. -->

---

## When things go wrong

- All intermediate files land in a single temp directory
- If a stage fails, the temp directory is preserved -- go look at what happened
- On success, it's cleaned up (or kept with `--keep-temp`)
- Subprocess stderr is captured and only printed on failure
- Files are zero-padded: `audio_001.wav`, `segment_001.ts`, easy to correlate

<!-- So what happens when something breaks? Everything goes into one temp directory. PNGs, WAVs, transport stream segments, all of it. If a stage fails, that directory sticks around. You can go in and see exactly which slides rendered, which audio files got generated, where things stopped. It makes debugging pretty straightforward. On a successful run, the temp files get cleaned up unless you pass keep-temp. I use keep-temp a lot during testing because I want to listen to individual slide audio files before watching the whole video. The subprocess calls all capture standard error and only print it when something actually fails, so a normal run is just progress lines. -->

---

## Getting Started

```bash
source setup.sh
python -m marp2video deck.md --voice my-voice.wav
```

In about two minutes, you get a 1080p MP4 with narration in your voice.

- Provide a short voice sample for cloning, or skip `--voice` for the default
- GPU recommended -- CPU fallback works but is slower
- Tune the output with `--exaggeration`, `--cfg-weight`, and `--temperature`

<!-- Getting started is simpler than it sounds. You record about five to ten minutes of yourself reading varied content. Different emotions, different pacing, questions and statements. That recording becomes your voice sample. Then it's one command. Point it at your slide deck, pass in your voice file, and a couple minutes later you have a narrated video. You can tune how expressive the voice sounds, how closely it follows the cloning, all from the command line. I built this as a personal project, but I'm planning to use it for our internal docs and demos. -->

---

<!-- _class: lead -->

This entire presentation was generated using *marp2video*.

The voice you're hearing was synthesized from a Markdown file
and cloned to my voice using the exact system I just described.

No microphone. No recording session.

<!-- Now here's the thing. Everything you've been listening to? This whole presentation? It was generated with marp2video. The voice you're hearing is synthesized from text, cloned to my voice using the system I just described. Every word was written in a Markdown file and run through the pipeline. No microphone. No recording session. If I need to change something, I edit the script and regenerate in about thirty seconds. -->

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Thanks

I built this in an afternoon with Claude Code.

The repo is on GitHub -- happy to walk through the setup.

*Questions?*

<!-- One more thing. I built this in an afternoon with Claude Code. The whole pipeline, start to finish. That's marp2video. The repo is on GitHub if you want to try it. I'm happy to walk through the setup or answer questions. Thanks. -->
