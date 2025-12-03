import argparse
import os
from pathlib import Path
import numpy as np
import librosa


def generate_waveform_svg(audio_path, num_bars=50, aspect_ratio=10.0):
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    samples_per_bar = len(y) // num_bars

    bar_heights = []
    for i in range(num_bars):
        start_idx = i * samples_per_bar
        end_idx = start_idx + samples_per_bar
        segment = y[start_idx:end_idx]

        if len(segment) > 0:
            rms = np.sqrt(np.mean(segment ** 2))
            bar_heights.append(rms)
        else:
            bar_heights.append(0)

    max_height = max(bar_heights) if max(bar_heights) > 0 else 1
    bar_heights = [h / max_height for h in bar_heights]

    svg_height = 100
    svg_width = svg_height * aspect_ratio

    bar_width = svg_width / (num_bars * 2 - 1)
    bar_spacing = bar_width

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" '
        f'width="{svg_width}" height="{svg_height}">'
    ]

    center_y = svg_height / 2

    for i, height in enumerate(bar_heights):
        x = i * (bar_width + bar_spacing)

        bar_height = height * svg_height * 0.9
        y_top = center_y - (bar_height / 2)

        svg_parts.append(
            f'<rect x="{x:.2f}" y="{y_top:.2f}" '
            f'width="{bar_width:.2f}" height="{bar_height:.2f}" '
            f'fill="currentColor" shape-rendering="crispEdges"/>'
        )

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


def process_directory(input_dir, num_bars=50, aspect_ratio=10.0):
    input_path = Path(input_dir)
    output_dir = Path('./waveform_svgs')

    output_dir.mkdir(exist_ok=True)

    audio_files = list(input_path.glob('*.m4a'))

    if not audio_files:
        print(f"No .m4a files found in {input_dir}")
        return

    print(f"Found {len(audio_files)} audio files")
    print(f"Generating waveforms with {num_bars} bars, aspect ratio {aspect_ratio}:1")

    for idx, audio_file in enumerate(audio_files, 1):
        try:
            print(f"Processing [{idx}/{len(audio_files)}]: {audio_file.name}")

            svg_content = generate_waveform_svg(
                str(audio_file),
                num_bars=num_bars,
                aspect_ratio=aspect_ratio
            )

            output_file = output_dir / f"{audio_file.stem}.svg"

            output_file.write_text(svg_content)

        except Exception as e:
            print(f"Error processing {audio_file.name}: {e}")

    print(f"\nComplete! SVG files saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate waveform SVG visualizations from audio files'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing audio files (.m4a)'
    )
    parser.add_argument(
        '--bars',
        type=int,
        default=50,
        help='Number of vertical bars in the waveform (default: 50)'
    )
    parser.add_argument(
        '--aspect-ratio',
        type=float,
        default=10.0,
        help='Width to height ratio (default: 10.0 for 10:1)'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: {args.input_dir} is not a valid directory")
        return 1

    process_directory(args.input_dir, args.bars, args.aspect_ratio)

    return 0


if __name__ == '__main__':
    exit(main())