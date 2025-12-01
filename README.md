# Waveform SVG generator

A tool for generating waveform SVGs from M4A audio files.

## Requirements

Use Python `3.12`.
Avoid Python `3.13` as it is unstable at the time of coding (removed `audioop` which `pydub` depends on).

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Batch, all files inside audio_files, with high resolution and 5:1 aspect ratio:
```bash
python main.py -b audio_files -s 2000 -a 5.0
```

Single file, lower detail, 3:1 aspect ratio:
```bash
python main.py file.m4a -s 500 -a 3.0
```
