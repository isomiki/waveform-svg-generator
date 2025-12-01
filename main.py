import argparse
import os
import sys

import numpy as np
from pydub import AudioSegment
from tqdm import tqdm


def generate_waveform_svg(audio_path, output_svg_path, samples=1000, aspect=10.0):
    audio = AudioSegment.from_file(audio_path).set_channels(1)
    data = np.array(audio.get_array_of_samples(), dtype=np.float32)
    data = data / 32768.0

    chunk_size = max(1, len(data) // samples)
    peaks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        peaks.append((np.max(chunk), np.min(chunk)))

    view_width = 100
    view_height = view_width / aspect
    center_y = view_height / 2
    bar_width = view_width / len(peaks)

    path = [f"M 0 {center_y}"]

    for i, (pos, _) in enumerate(peaks):
        x = (i + 1) * bar_width
        y = center_y - pos * center_y * 0.95
        path.append(f"L {x:.6g} {y:.6g}")

    for i in reversed(range(len(peaks))):
        x = i * bar_width
        _, neg = peaks[i]
        y = center_y - neg * center_y * 0.95
        path.append(f"L {x:.6g} {y:.6g}")

    path.append("Z")
    path_data = " ".join(path)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}" preserveAspectRatio="xMidYMid slice"><path d="{path_data}" fill="white"/></svg>"""

    with open(output_svg_path, "w") as f:
        f.write(svg)


def batch_generate_waveforms(directory, samples=1000, aspect=10.0):
    output_dir = "waveform_svgs"
    os.makedirs(output_dir, exist_ok=True)

    m4a_files = [f for f in os.listdir(directory) if f.endswith(".m4a")]

    if not m4a_files:
        print(f"No .m4a files found in {directory}")
        return

    print(f"Found {len(m4a_files)} m4a files.")

    for filename in tqdm(m4a_files, total=len(m4a_files), desc="Generating SVGs"):
        input_path = os.path.join(directory, filename)
        output_filename = filename.replace(".m4a", ".svg")
        output_path = os.path.join(output_dir, output_filename)

        try:
            generate_waveform_svg(
                input_path, output_path, samples=samples, aspect=aspect
            )
        except Exception as e:
            print(f"Failed to generate waveform for {filename}: {e}")

    print(f"Done! Waveforms saved to {output_dir}/")


def single_file_waveform(filename, samples=500, aspect=10.0):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return

    if not filename.endswith(".m4a"):
        print(f"Error: File must be .m4a format")
        return

    output_dir = "waveform_svgs"
    os.makedirs(output_dir, exist_ok=True)

    output_filename = os.path.basename(filename).replace(".m4a", ".svg")
    output_path = os.path.join(output_dir, output_filename)

    try:
        generate_waveform_svg(filename, output_path, samples=samples, aspect=aspect)
        print(f"Generated: {output_path}")
    except Exception as e:
        print(f"Failed to generate waveform: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG waveforms from m4a audio files"
    )
    parser.add_argument(
        "-b", "--batch", metavar="DIR", help="Batch process directory of m4a files"
    )
    parser.add_argument(
        "-s",
        "--samples",
        type=int,
        default=1000,
        help="Number of sample points (detail level, default: 1000)",
    )
    parser.add_argument(
        "-a",
        "--aspect",
        type=float,
        default=5.0,
        help="Aspect ratio width:height (default: 5.0 = 5:1)",
    )

    args = parser.parse_args()

    if (args.samples is None) != (args.aspect is None):
        print("Error: Both -s and -a must be provided together, or neither")
        sys.exit(1)

    samples = args.samples if args.samples is not None else 1000
    aspect = args.aspect if args.aspect is not None else 10.0

    if args.batch:
        batch_generate_waveforms(args.batch, samples=samples, aspect=aspect)
    elif args.filename:
        single_file_waveform(args.filename, samples=samples, aspect=aspect)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
