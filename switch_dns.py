r"""
SWITCH DNS

The standard use of this script is to alternate between previous and current configurations. This
can be done manually from the command line with elevated permissions.

This script will generally only affect the first two entries (primary and reserve) in the IPv4 and
IPv6 DNS registries, although the /curr command will list all DNS entries contained in both.

Run the script from the command line to do the following:

- switch_dns.py set -G <dns_group> [options]
  (Requires Admin) Set DNS entries to a pre-defined group. The groups are stored in dns_groups.json,
  where they can be added to manually if desired. If <dns_group> is "/prev", the script will roll
  back the DNS configuration to the previous configuration remembered.

- switch_dns.py set -S <ip_ver> <tier> <new_dns> [options]
  (Requires Admin) Set a single DNS entry. <ip_ver> must be either "ipv4" or "ipv6". <tier> can be
  "primary" or "reserve", but can also be a number denoting registry index. <new_dns> is the address
  of the desired DNS server. All arguments are case insensitive.
  
- switch_dns.py get (/groups | <dns_group>)
  Obtain certain information. If "/groups" is used, all groups in dns_groups.json are listed out. If
  <dns_group> is used, the addresses of that group are listed out. Setting <dns_group> to "/prev" 
  shows the previous configuration remembered, while "/curr" shows the current configuration.

CAUTION:
    * Script requires docopt to work (installation: pip install docopt==0.6.2)
    * Script needs internet connection for ipconfig output to include DNS info
    * To `set` new DNS servers, script MUST be run with elevated permissions
    * If modifying the code, always check DNS registry manually after testing (`ipconfig /all`)
"""
# Standard library full imports
import subprocess
import json
import sys
import os
import re
# Related third-party full imports
import docopt

"=================================================================================================="
"Setup"

# Make sure cwd is always relative to script
os.chdir(os.path.dirname(__file__))

"=================================================================================================="
"Constants"

# Connection name to use by default (see: "Control Panel\Network and Internet\Network Connections")
CONNECTION = "Wi-Fi" #this can be any valid network interface

# Check if script is currently running as Admin (source: https://stackoverflow.com/a/16285248)
IS_ADMIN = os.system("net session > nul 2>&1") == 0 #runtime constant, not "true" constant

# Command line interface for docopt
USAGE_MSG = """
Switch DNS

Usage:
  switch_dns.py set -G <dns_group> [options]
  switch_dns.py set -S <ip_ver> <tier> <new_dns> [options]
  switch_dns.py get (/groups | <dns_group>)
  switch_dns.py -h | --help

Options:
  -G --group   Set group of DNS addresses.
  -S --single  Set a single DNS address.
  -q --quiet   Print less config details.
  -h --help    Show this screen.
"""

"=================================================================================================="
"Variables"

# Standard groups of DNS server addresses
dns_groups = json.load(open("./dns_groups.json"))

"=================================================================================================="
"Helper Functions"

def index_to_tier(index):
    """Convert numerical index to named tier"""
    tier = ("Primary" if index == 1 else
            "Reserve" if index == 2 else
            "Index %s" % index)
    return tier


def get_curr_dns_servers():
    """Return dict of current IPv4 and IPv6 DNS servers"""
    # Pattern to match DNS section of ipconfig output
    dns_pattern = re.compile(r"""
    DNS[ ]Servers.*?:[ ]        # Locate section listing DNS servers
    (?P<ipv6>([0-9a-f:]+\s+)+)  # Extract all IPv6 DNS addresses
    (?P<ipv4>([0-9.]+   \s+)+)  # Extract all IPv4 DNS addresses
    """, re.VERBOSE)
    # Get data from ipconfig where current DNS servers are listed
    ipconfig = subprocess.check_output("ipconfig /all").decode()
    # Split matched section into separate addresses
    curr_dns_servers = re.search(dns_pattern, ipconfig).groupdict()
    curr_dns_servers["ipv6"] = re.split(r"\s+", curr_dns_servers["ipv6"])[:-1]
    curr_dns_servers["ipv4"] = re.split(r"\s+", curr_dns_servers["ipv4"])[:-1]
    # Return current DNS servers
    return curr_dns_servers


def set_dns(ip_ver, index, new_dns, quiet=False):
    """Set one of the connections' DNS servers"""
    
    # (Temporary) Raise error if the index is out of currently-handled range
    if index > 2: #if the index isn't for a primary or reserve DNS (e.g. Index 3)
        raise NotImplementedError("Cannot yet handle DNS indices above Reserve (Index 2)")
    
    # Formatted variables for config printout
    IPvX = "IPv" + ip_ver[-1]   #slightly formatted ip_ver
    tier = index_to_tier(index) #DNS tier to use for printout
    
    # Get current DNS address from lookup table
    old_dns = dns_groups["/curr"][ip_ver][index - 1]
    
    # Check if DNS entry already has this configuration
    if old_dns == new_dns:
        if not quiet: print(f"{IPvX} {tier} DNS already set to {new_dns}")
        return None
    
    # Delete current DNS address before insertion
    os.system(f'netsh interface {ip_ver} del dns "{CONNECTION}" {old_dns} > nul')
    
    # Insert new DNS address in place of the old one
    os.system(f'netsh interface {ip_ver} add dns "{CONNECTION}" {new_dns} {index} > nul')
    
    # Refresh lookup table for ground truth
    dns_groups["/curr"] = get_curr_dns_servers()
    true_dns = dns_groups["/curr"][ip_ver][index - 1]
    
    # Update /prev to old_dns if config was successful
    if true_dns == new_dns:
        dns_groups["/prev"][ip_ver][index - 1] = old_dns
    
    # Optionally notify user of result
    if not quiet:
        # Compare ground truth with expected value
        if true_dns == new_dns:
            print(f"Configured {IPvX} {tier} DNS to {new_dns}")
        else: #if ground truth and new_dns don't match for some reason
            print(f"{IPvX} {tier} DNS not set correctly (Unknown Error)")
    
    # Finish setting DNS
    return None

"=================================================================================================="
"Main"

def main():
    """View or configure DNS server entries"""

    # Set up docopt command line interface
    args = docopt.docopt(USAGE_MSG)
    
    # Get /curr lookup table for dns_groups
    dns_groups["/curr"] = get_curr_dns_servers()
    
    # Configure single or multiple DNS servers
    if args["set"]:
    
        # Check if script is running in Admin mode
        if not IS_ADMIN:
            if not quiet: print("Setting DNS servers requires Admin access")
            return None
        
        # Configure individual DNS manually
        if args["--single"]:
            # Shorten variables for easier use
            new_dns = args["<new_dns>"].lower()
            ip_ver  = args["<ip_ver>" ].lower()
            tier    = args["<tier>"   ].lower()
            # Convert tier to DNS index
            if re.match(r"(primary|reserve|\d+)", tier):
                index = (
                    1 if tier == "primary" else
                    2 if tier == "reserve" else int(tier))
            else: #if regex validation failed
                raise ValueError("Tier not recognized")
            # Configure desired DNS address
            set_dns(ip_ver, index, new_dns, args["--quiet"])
            # Update changes to dns_groups.json
            dns_groups.pop("/curr") #may change externally over time
            json.dump(dns_groups, open("./dns_groups.json", "w"), indent=4)
        
        # Configure full set of DNS servers
        if args["--group"]:
            # Configure DNS servers one at a time
            dns_group = dns_groups[args["<dns_group>"].lower()]
            set_dns("ipv6", 1, dns_group["ipv6"][0], args["--quiet"])
            set_dns("ipv6", 2, dns_group["ipv6"][1], args["--quiet"])
            set_dns("ipv4", 1, dns_group["ipv4"][0], args["--quiet"])
            set_dns("ipv4", 2, dns_group["ipv4"][1], args["--quiet"])
            # Update changes to dns_groups.json
            dns_groups.pop("/curr") #may change externally over time
            json.dump(dns_groups, open("./dns_groups.json", "w"), indent=4)
    
    # View available DNS groups
    if args["get"]:
        
        # List names of available DNS groups
        if args["/groups"]:
            for key in dns_groups.keys():
                print(key.title())
        
        # View addresses in a particular group
        if args["<dns_group>"] is not None:
            # Get DNS group as variable for easier use
            dns_group = dns_groups[args["<dns_group>"].lower()]
            # View both IPv6 and IPv4 addresses
            for ip_ver in ["IPv6", "IPv4"]:
                # List all available DNS addresses
                ip_ver_servers = dns_group[ip_ver.lower()]
                for index in range(1, len(ip_ver_servers) + 1):
                    # Identify tier to use in printout
                    tier = index_to_tier(index)
                    # Get current dns under this ip_ver and index
                    curr_dns = ip_ver_servers[index - 1]
                    # Print final result to console
                    print(f"{ip_ver} {tier} DNS: {curr_dns}")
    
    # Exit main
    return None


if __name__ == "__main__":
    # Note: add more error-handling later
    main()

