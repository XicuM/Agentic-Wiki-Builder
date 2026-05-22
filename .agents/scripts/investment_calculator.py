import argparse
import math

def calculate_cagr(start_val, end_val, years):
    """Compound Annual Growth Rate"""
    return (end_val / start_val) ** (1 / years) - 1

def calculate_fv(rate, periods, pmt, pv=0):
    """
    Future Value
    rate: interest rate per period
    periods: number of periods
    pmt: payment per period
    pv: present value
    """
    if rate == 0:
        return pv + (pmt * periods)
    
    fv = pv * (1 + rate)**periods + pmt * (((1 + rate)**periods - 1) / rate)
    return fv

def main():
    parser = argparse.ArgumentParser(description="Investment Calculator for Agentic Framework")
    subparsers = parser.add_subparsers(dest="command", help="Available calculations")

    # CAGR
    parser_cagr = subparsers.add_parser("cagr", help="Calculate CAGR")
    parser_cagr.add_argument("--start", type=float, required=True, help="Starting value")
    parser_cagr.add_argument("--end", type=float, required=True, help="Ending value")
    parser_cagr.add_argument("--years", type=float, required=True, help="Number of years")

    # Future Value
    parser_fv = subparsers.add_parser("fv", help="Calculate Future Value")
    parser_fv.add_argument("--rate", type=float, required=True, help="Annual interest rate (e.g. 0.07 for 7%)")
    parser_fv.add_argument("--years", type=float, required=True, help="Number of years")
    parser_fv.add_argument("--pmt", type=float, required=True, help="Annual payment/contribution")
    parser_fv.add_argument("--pv", type=float, default=0, help="Present value (initial investment)")

    args = parser.parse_args()

    if args.command == "cagr":
        cagr = calculate_cagr(args.start, args.end, args.years)
        print(f"CAGR: {cagr:.2%}")
    elif args.command == "fv":
        fv = calculate_fv(args.rate, args.years, args.pmt, args.pv)
        print(f"Future Value: €{fv:,.2f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
