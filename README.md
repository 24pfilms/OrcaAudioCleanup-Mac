# OrcaAudioCleanup for Mac

**Clean up the voice in your videos, on your own Mac.**

[squarecirclelabs.com](https://squarecirclelabs.com) · [Download for Mac](https://github.com/24pfilms/OrcaAudioCleanup-Mac/releases/latest/download/OrcaAudioCleanup.dmg)

OrcaAudioCleanup cleans up the voice in any video or audio file: wind, echo, traffic, a noisy room.
It lives in the menu bar: drop a recording on it and `<name>-enhanced` appears beside the original,
with the voice restored, the background turned down, and the picture left as it was. Everything runs
on your Mac. There is no account, no upload and no length limit. Your original file is never changed.

There is also a Windows version: see [squarecirclelabs.com](https://squarecirclelabs.com).

OrcaAudioCleanup for Mac is [Booth](https://github.com/shrimbly/booth) by shrimbly (MIT licence),
renamed. All the credit for the app and its engine goes to Booth.

## Requirements

- macOS 14 (Sonoma) or later on an Apple silicon Mac (M1 or newer), with 16 GB of memory or more.
  Intel Macs are not supported.
- About 2 GB of disk space for the voice models and the engine, downloaded the first time.
- [ffmpeg](https://ffmpeg.org), to read and write audio and video. OrcaAudioCleanup uses yours if
  you have one, and otherwise downloads its own during setup (57 MB).

## Install

1. Download `OrcaAudioCleanup.dmg` from the
   [latest release](https://github.com/24pfilms/OrcaAudioCleanup-Mac/releases/latest).
2. Open it and drag OrcaAudioCleanup into Applications.
3. **The first time only:** the app is not signed by Apple, so macOS says it "can't be opened" or
   "cannot verify the developer". Click **Done** (not Move to Trash), then open
   **System Settings › Privacy & Security**, scroll down and click **Open Anyway** next to
   OrcaAudioCleanup. After that it opens normally.

   If you're comfortable with Terminal, this does the same thing:

   ```bash
   xattr -dr com.apple.quarantine /Applications/OrcaAudioCleanup.app
   ```

4. OrcaAudioCleanup appears in the menu bar, not in the Dock. The first time, it sets up its engine
   and downloads the voice models: about 1.1 GB, once.

To use the `booth` command in Terminal as well, link the copy inside the app onto your `PATH`:

```bash
ln -s /Applications/OrcaAudioCleanup.app/Contents/Resources/bin/booth /usr/local/bin/booth
```

## Use OrcaAudioCleanup

Give it a recording in whichever way is handy:

- Drop the file on the menu bar icon, or into the open popover.
- Select files in Finder and press **⌃⌥E**.
- Right-click files in Finder and choose **Quick Actions › Clean up with OrcaAudioCleanup**.
- Choose **Open With › OrcaAudioCleanup**.

It works through files one at a time and writes `<name>-enhanced` next to each. When one is done,
play it in the popover and hold **⌥** to hear the original. **Mix** sets how much speech, background
and music to keep. You hear each change as you make it, and saving a new mix takes seconds, because
the voice models don't run again.

It rebuilds your voice rather than filtering it, so always listen before you post.

## Use the command line

```bash
booth talk.mp4                    # writes talk-enhanced.mp4 and talk-enhanced.wav
booth *.mov                       # several files, one after another
booth talk.mp4 -s 80 -b 0 -m 0    # stronger voice, no background, no music
booth podcast.wav -o clean.wav    # choose the output
booth talk.mp4 --engine df3       # fastest: removes noise without restoring the voice
booth talk.mp4 --stems-dir stems  # keep stems, then…
booth remix stems -b 25           # …change the mix in a second or two
```

Progress, messages and errors go to stderr, and each finished file's path goes to stdout, so
`booth *.mov | xargs open` opens the results. Ctrl-C stops cleanly. Results are written only
when a file is completely done, so a stopped or failed run leaves nothing half-written behind.

For a video, the enhanced sound goes into a copy of the same container (`.mp4`, `.mov`, `.mkv`,
`.webm`…). The picture is copied losslessly; `--crf N` re-encodes it instead. Subtitles, other
audio tracks, the recording date and location come along where the container allows. The enhanced
`.wav` is always written as well. `booth` refuses any output, or kept stem, that would
replace the input file.

`booth remix DIR` replaces the outputs the stems were made with, or writes to `-o PATH`
instead. If the original video has moved, `-o new.wav` still renders the audio.

The first run downloads the voice models it needs (about 1.1 GB) before it starts.
`booth setup` does that ahead of time, and `booth setup --check` reports what is
missing.

### Options

| Option | Default | |
|---|---|---|
| `-s`, `--speech 0-100` | 54 | Enhancement strength |
| `-b`, `--background 0-100` | 10 | Room tone and other background sound |
| `-m`, `--music 0-100` | 10 | Music |
| `-o`, `--output PATH` | `<input>-enhanced.<ext>` | Where to write: a file name, or a folder for the default name (one input only) |
| `--audio-only` | off | Write only the `.wav`, not a new video |
| `--crf N` | copy | Re-encode the video at CRF N |
| `--stems-dir DIR` | — | Keep preview stems for `booth remix DIR` (one input only) |
| `--keep-stems DIR` | — | Write the clean, background and music stems for inspection (one input only) |
| `--engine` | `sidon` | `sidon` restores the voice; `mossformer2` and `df3` only remove noise (`df3` is fastest). If it can't run, the next one is used and the result line says so |
| `--no-split` | off | Skip music separation: about twice as fast, the music level does nothing |
| `--device` | `cpu` | `mps` or `auto` for music separation |
| `-v`, `--verbose` | off | Log each processing step and its timing |
| `-q`, `--quiet` | off | No progress; print only the finished files, errors and engine fallbacks |

`booth enhance --help` lists the fine-tuning switches (`--no-breaths`, `--no-declick`, `--no-smooth`,
`--lufs N` from −70 to −5, and others). [How it works](docs/how-it-works.md) explains what each one does.

| Exit status | Meaning |
|---|---|
| 0 | Every file was enhanced |
| 1 | At least one file failed; the others were still written |
| 2 | The command line was wrong |
| 130 | Stopped with Ctrl-C |

Set `BOOTH_DEBUG=1` to see the full error behind a one-line failure message.

### Speed

A 3-minute video takes about 40 seconds on an M5 Pro, and a 10-minute recording just under 2
minutes. Music separation takes over a third of that and voice restoration about half; Sidon loads
its models while the music is being separated. `--no-split` saves about a quarter when the
recording has no music.

## How it works

```
original ──Sidon (generative restoration)──▶ studio speech ─▶ tone + gate ─┐
original ──demucs──▶ vocals ──DeepFilterNet3──▶ speech key + background    ├─▶ mix
                     music ────────────────────────────────────────────────┘
```

The voice comes from **Sidon** ([sarulab-speech/sidon-v0.1](https://huggingface.co/sarulab-speech/sidon-v0.1)),
a generative speech-restoration model. Rather than subtracting noise, it predicts clean speech
features and resynthesizes 48 kHz studio speech from them, so it rebuilds bandwidth and harmonics
that a denoiser can only muffle. Demucs separates the music, and DeepFilterNet3 marks where speech
is, so the pauses between words can be brought down without clipping word onsets.

Measured against Adobe Podcast Enhance v2 on four real recordings:

| | DNSMOS OVR | UTMOS | Spectral distance to Adobe |
|---|---|---|---|
| Original | 2.46 | 2.05 | 9.6 dB |
| **OrcaAudioCleanup (Sidon)** | **3.37** | **3.56** | **6.2 dB** |
| Adobe Podcast | 3.35 | 3.60 | — |

[docs/how-it-works.md](docs/how-it-works.md) has the full pipeline, the post-processing and why
each step is there, the calibration of the other engines, and the benchmark.
[docs/app-protocol.md](docs/app-protocol.md) describes how the app drives the engine.

## Build

```bash
git clone https://github.com/24pfilms/OrcaAudioCleanup-Mac && cd OrcaAudioCleanup-Mac
uv sync --python 3.11                       # the engine, in .venv
app/scripts/build-app.sh --open             # OrcaAudioCleanup.app, using this checkout's engine
swift test --package-path app               # the app's tests
```

Building needs the Command Line Tools for Xcode (`xcode-select --install`), not Xcode itself.
[app/README.md](app/README.md) has the details (it still uses Booth's names for the code).

Releases are built by GitHub: push a tag `v<version>` matching `pyproject.toml` and
[.github/workflows/release.yml](.github/workflows/release.yml) runs the tests, builds the app and
the disk image, and uploads `OrcaAudioCleanup-<version>.dmg`, `OrcaAudioCleanup.dmg` and
`SHA256SUMS` to the release. Running the workflow by hand builds and tests without publishing.
Releases are not signed or notarized by Apple (see Install, step 3).

The app icon is `app/Resources/OrcaAudioCleanup.icns`; `python packaging/icon/make_icns.py` redraws it.

## Credits and licence

OrcaAudioCleanup for Mac is [Booth](https://github.com/shrimbly/booth) by shrimbly, renamed, used
under the MIT licence. Booth's licence is kept unchanged in [LICENSE](LICENSE).

The app also carries uv (MIT or Apache 2.0), the Geist Serif typeface (SIL Open Font License),
Silero VAD's speech detector (MIT) and DeepFilterNet3 (MIT or Apache 2.0). The engine downloads these
models under their own licences: Sidon and w2v-BERT 2.0 (MIT), Demucs (MIT) and ClearVoice
MossFormer2 (Apache 2.0), and on a Mac without ffmpeg, a build of FFmpeg (GPL 3.0).
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) has the details, and the app has a copy of it and
of `LICENSE` in `Contents/Resources`.
