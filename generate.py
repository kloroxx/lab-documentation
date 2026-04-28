#!/usr/bin/env python3
"""
Nexus 9K VPC Pair Config Generator
====================================
Generates Cisco NX-OS configuration for a pair of Nexus 93240YC-FX2
switches replacing a Nexus 5K VPC pair.

Usage:
    python3 generate.py                    # Interactive mode
    python3 generate.py --vars my_vars.yml # Use specific variables file
    python3 generate.py --both             # Generate both switch configs

Author:  Michael Nesteriak
GitHub:  github.com/kloroxx
Version: 1.0
"""

import argparse
import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# ----------------------------------------
# CONFIG
# ----------------------------------------
TEMPLATE_FILE = "nexus9k_vpc_template.j2"
VARIABLES_FILE = "variables.yml"
OUTPUT_DIR = "generated_configs"


def load_variables(vars_file: str) -> dict:
    """Load variables from YAML file."""
    if not os.path.exists(vars_file):
        print(f"[ERROR] Variables file not found: {vars_file}")
        print(f"        Copy variables_template.yml to {vars_file} and fill in your values.")
        sys.exit(1)
    with open(vars_file, "r") as f:
        return yaml.safe_load(f)


def load_template(template_file: str) -> object:
    """Load Jinja2 template."""
    template_dir = os.path.dirname(os.path.abspath(template_file))
    template_name = os.path.basename(template_file)
    if not os.path.exists(template_file):
        print(f"[ERROR] Template file not found: {template_file}")
        sys.exit(1)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env.get_template(template_name)


def generate_config(template, variables: dict, switch_num: int) -> str:
    """Render configuration for specified switch number."""
    variables["switch_num"] = switch_num
    return template.render(**variables)


def save_config(config: str, hostname: str, switch_num: int):
    """Save generated config to output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_DIR}/{hostname}_SW{switch_num}_{timestamp}.cfg"
    with open(filename, "w") as f:
        f.write(config)
    print(f"[OK] Config saved: {filename}")
    return filename


def print_summary(variables: dict):
    """Print a summary of what will be generated."""
    print("\n" + "="*60)
    print("  NEXUS 9K VPC PAIR CONFIG GENERATOR")
    print("="*60)
    print(f"  Switch 1:    {variables['switch1']['hostname']} ({variables['switch1']['mgmt_ip']})")
    print(f"  Switch 2:    {variables['switch2']['hostname']} ({variables['switch2']['mgmt_ip']})")
    print(f"  VPC Domain:  {variables['vpc_domain']}")
    print(f"  VLANs:       {len(variables['vlans'])} configured")
    print(f"  SVIs:        {len(variables['svis'])} with HSRP")
    print(f"  FEX Units:   {len(variables['fex_units'])} configured")
    print(f"  NTP Servers: {len(variables['ntp_servers'])} configured")
    print(f"  TACACS+:     {len(variables['tacacs']['servers'])} servers")
    print(f"  Syslog:      {len(variables['logging']['servers'])} servers")
    print("="*60 + "\n")


def interactive_mode(variables: dict) -> int:
    """Ask user which switch to generate config for."""
    print_summary(variables)
    print("Which switch config would you like to generate?")
    print("  [1] Switch 1 only  —  " + variables['switch1']['hostname'])
    print("  [2] Switch 2 only  —  " + variables['switch2']['hostname'])
    print("  [3] Both switches")
    print()
    choice = input("Enter choice [1/2/3]: ").strip()
    if choice not in ["1", "2", "3"]:
        print("[ERROR] Invalid choice. Enter 1, 2, or 3.")
        sys.exit(1)
    return int(choice)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Nexus 9K VPC pair configurations from YAML variables."
    )
    parser.add_argument(
        "--vars",
        default=VARIABLES_FILE,
        help=f"Path to variables YAML file (default: {VARIABLES_FILE})"
    )
    parser.add_argument(
        "--template",
        default=TEMPLATE_FILE,
        help=f"Path to Jinja2 template file (default: {TEMPLATE_FILE})"
    )
    parser.add_argument(
        "--switch",
        type=int,
        choices=[1, 2],
        help="Generate config for switch 1 or 2 (skips interactive prompt)"
    )
    parser.add_argument(
        "--both",
        action="store_true",
        help="Generate configs for both switches"
    )
    args = parser.parse_args()

    # Load files
    variables = load_variables(args.vars)
    template = load_template(args.template)

    # Determine which switches to generate
    if args.both:
        switches = [1, 2]
    elif args.switch:
        switches = [args.switch]
    else:
        choice = interactive_mode(variables)
        if choice == 3:
            switches = [1, 2]
        else:
            switches = [choice]

    # Generate configs
    for sw_num in switches:
        hostname = variables[f"switch{sw_num}"]["hostname"]
        print(f"[..] Generating config for Switch {sw_num}: {hostname}")
        config = generate_config(template, variables.copy(), sw_num)
        save_config(config, hostname, sw_num)

    print(f"\n[DONE] Configs saved to ./{OUTPUT_DIR}/")
    print("       Review before applying to production equipment.\n")


if __name__ == "__main__":
    main()
