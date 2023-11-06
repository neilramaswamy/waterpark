import argparse

from distribution import get_distribution
from simulator import run_simulation


def main():
    parser = argparse.ArgumentParser(description="Data Generation Script")
    parser.add_argument(
        "--distribution",
        choices=["exponential", "gamma", "uniform", "constant"],
        help="Type of distribution (exponential, uniform, or constant)",
    )
    parser.add_argument(
        "--parameters",
        type=float,
        nargs="+",
        help="Parameters for the selected distribution",
    )
    parser.add_argument(
        "--watermark_delay",
        type=float,
        required=True,
        help="Watermark delay in seconds (a positive scalar integer)",
    )
    parser.add_argument(
        "--watermark_speed",
        type=int,
        required=True,
        help="The watermark will update every watermark_speed number of records",
    )
    parser.add_argument(
        "--input_rate",
        type=int,
        required=True,
        help="Input rate in records per second (a positive scalar integer)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=False,
        default=10,
        help="The number of seconds to run the waterpark simulation for",
    )

    args = parser.parse_args()

    print("Distribution:", args.distribution)
    print("Parameters:", args.parameters)
    print("Watermark Delay:", args.watermark_delay)
    print("Input Rate:", args.input_rate)

    distribution = get_distribution(args.distribution, args.parameters)

    result = run_simulation(
        distribution,
        args.watermark_delay,
        args.watermark_speed,
        args.input_rate,
        args.duration,
    )
    print(result)


if __name__ == "__main__":
    main()
