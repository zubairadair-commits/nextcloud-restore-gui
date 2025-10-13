#!/usr/bin/env python3
"""
Demo script to test domain validation logic independently.
This demonstrates the validation features without requiring a running Nextcloud instance.
"""

import re
import sys

def validate_domain_format(domain):
    """
    Validate domain format with comprehensive checks.
    Returns: (is_valid, error_message)
    """
    if not domain or not domain.strip():
        return (False, "Domain cannot be empty")
    
    domain = domain.strip()
    
    # Check for wildcard domains
    is_wildcard = domain.startswith('*.')
    if is_wildcard:
        domain_to_check = domain[2:]  # Remove *. prefix
    else:
        domain_to_check = domain
    
    # Basic format validation
    # Allow localhost, IP addresses, and domain names
    if domain_to_check == 'localhost':
        return (True, None)
    
    # Check if it's an IP address (IPv4 or IPv6)
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ipv4_pattern, domain_to_check):
        if is_wildcard:
            return (False, "Wildcard domains are not valid for IP addresses")
        return (True, None)
    
    # Check for IPv6 (simple check)
    if ':' in domain_to_check and '[' not in domain_to_check:
        if is_wildcard:
            return (False, "Wildcard domains are not valid for IPv6 addresses")
        return (True, None)
    
    # Domain name validation
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    if not re.match(domain_pattern, domain_to_check):
        return (False, "Invalid domain format. Use format like: example.com or subdomain.example.com")
    
    # Check for port specification
    if ':' in domain_to_check and not domain_to_check.count(':') > 1:  # Not IPv6
        parts = domain_to_check.rsplit(':', 1)
        try:
            port = int(parts[1])
            if port < 1 or port > 65535:
                return (False, "Invalid port number")
        except ValueError:
            return (False, "Invalid port specification")
    
    return (True, "Wildcard domain" if is_wildcard else None)

def print_validation_result(domain, result):
    """Print validation result with formatting"""
    is_valid, message = result
    
    status_icon = "✓" if is_valid else "✗"
    color = "\033[92m" if is_valid else "\033[91m"  # Green or Red
    if is_valid and message:  # Warning
        color = "\033[93m"  # Orange/Yellow
        status_icon = "⚠️"
    reset = "\033[0m"
    
    print(f"{color}{status_icon} {domain:40s}{reset}", end="")
    if message:
        print(f" - {message}")
    else:
        print()

def run_validation_demo():
    """Run comprehensive validation demo"""
    print("=" * 80)
    print("Domain Validation Demo")
    print("=" * 80)
    print()
    
    # Test cases
    test_cases = [
        # Valid domains
        ("localhost", "Valid - localhost"),
        ("example.com", "Valid - simple domain"),
        ("subdomain.example.com", "Valid - subdomain"),
        ("my-cloud.example.com", "Valid - domain with hyphen"),
        ("deep.nested.subdomain.example.com", "Valid - deep nesting"),
        
        # Valid IPs
        ("192.168.1.100", "Valid - IPv4"),
        ("100.64.1.100", "Valid - Tailscale IP"),
        ("127.0.0.1", "Valid - IPv4 localhost"),
        ("::1", "Valid - IPv6 localhost"),
        ("2001:db8::1", "Valid - IPv6"),
        
        # Valid with ports
        ("example.com:8080", "Valid - domain with port"),
        ("192.168.1.100:8443", "Valid - IP with port"),
        
        # Wildcard domains
        ("*.example.com", "Valid wildcard"),
        ("*.dev.example.com", "Valid wildcard subdomain"),
        
        # Invalid formats
        ("", "Empty domain"),
        ("   ", "Whitespace only"),
        ("my domain.com", "Spaces in domain"),
        ("example..com", "Double dot"),
        ("-example.com", "Starting with hyphen"),
        ("example-.com", "Ending with hyphen"),
        ("example.com:", "Port missing number"),
        ("example.com:99999", "Port out of range"),
        ("*.192.168.1.100", "Wildcard with IP"),
        ("example,com", "Invalid character"),
        ("ex@mple.com", "Invalid character"),
    ]
    
    print("Testing Valid Domains:")
    print("-" * 80)
    for domain, description in test_cases[:17]:
        result = validate_domain_format(domain)
        print(f"{description:45s}: ", end="")
        print_validation_result(domain, result)
    
    print("\nTesting Invalid Domains:")
    print("-" * 80)
    for domain, description in test_cases[17:]:
        result = validate_domain_format(domain)
        print(f"{description:45s}: ", end="")
        print_validation_result(domain, result)
    
    # Interactive mode
    print("\n" + "=" * 80)
    print("Interactive Mode - Enter domains to validate (Ctrl+C to exit)")
    print("=" * 80)
    print()
    
    try:
        while True:
            domain = input("Enter domain: ").strip()
            if domain:
                result = validate_domain_format(domain)
                print_validation_result(domain, result)
                print()
    except KeyboardInterrupt:
        print("\n\nDemo completed!")

if __name__ == "__main__":
    run_validation_demo()
