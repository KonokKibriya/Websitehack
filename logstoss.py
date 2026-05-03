#!/usr/bin/env python3
# NASA LEAK CHECKER v5.0 - FULLY FIXED
# Developer: @KonokKibriya
# Telegram: https://t.me/bdlogsbd
# GitHub: https://github.com/KonokKibriya

import sys
import os
import time
import socket
import json
import re
import base64
from datetime import datetime

# ANSI Colors
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
B = '\033[1m'
N = '\033[0m'

# Hidden API Configuration (Base64 Encoded)
_ENCODED_APIS = [
    "aHR0cDovLzQ1LjE1MS4xNTIuMTk5OjgwMDAvc2VhcmNo",
    "aHR0cDovLzEwNC4xMjguNjQuMTMwOjgwMDAvc2VhcmNo",
]

class SecureAPI:
    @staticmethod
    def get_api_url(index=0):
        if index < len(_ENCODED_APIS):
            return base64.b64decode(_ENCODED_APIS[index]).decode()
        return base64.b64decode(_ENCODED_APIS[0]).decode()

def clear():
    os.system('clear')

def http_request(host, port, path):
    """HTTP request using socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))
        
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nAccept: application/json\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        
        response = b""
        while True:
            try:
                data = sock.recv(8192)
                if not data:
                    break
                response += data
            except:
                break
        sock.close()
        
        response_str = response.decode('utf-8', errors='ignore')
        if '\r\n\r\n' in response_str:
            return response_str.split('\r\n\r\n', 1)[1]
        return response_str
    except:
        return None

def search_api(domain):
    """Search using hidden API"""
    api_url = SecureAPI.get_api_url(0)
    
    if api_url.startswith('http://'):
        api_url = api_url[7:]
    
    parts = api_url.split(':')
    if len(parts) >= 2:
        host = parts[0]
        port = int(parts[1].split('/')[0])
        base_path = '/' + '/'.join(parts[1].split('/')[1:]) if '/' in parts[1] else '/search'
    else:
        host = parts[0]
        port = 8000
        base_path = '/search'
    
    search_path = f"{base_path}?q={domain}"
    
    try:
        result = http_request(host, port, search_path)
        if result:
            return json.loads(result)
    except:
        pass
    
    return None

def extract_credentials(data, domain):
    """Extract credentials from response"""
    credentials = []
    seen = set()  # For tracking duplicates
    
    if isinstance(data, dict):
        # Try different response formats
        for key in ['matches', 'results', 'data', 'credentials', 'leaks', 'items']:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    cred = parse_credential(item, domain)
                    if cred:
                        # Create unique key for duplicate checking
                        unique_key = f"{cred['domain']}:{cred['username']}:{cred['password']}"
                        if unique_key not in seen:
                            seen.add(unique_key)
                            credentials.append(cred)
                if credentials:
                    break
    
    elif isinstance(data, list):
        for item in data:
            cred = parse_credential(item, domain)
            if cred:
                unique_key = f"{cred['domain']}:{cred['username']}:{cred['password']}"
                if unique_key not in seen:
                    seen.add(unique_key)
                    credentials.append(cred)
    
    return credentials

def parse_credential(item, default_domain):
    """Parse credential from various formats"""
    try:
        if isinstance(item, str):
            if ':' in item:
                parts = item.split(':', 2)
                if len(parts) >= 2:
                    domain = parts[0] if '.' in parts[0] else default_domain
                    username = parts[1]
                    password = parts[2] if len(parts) > 2 else ''
                    return {'domain': domain, 'username': username, 'password': password}
        
        elif isinstance(item, dict):
            domain = item.get('domain', item.get('site', item.get('source', default_domain)))
            username = item.get('username', item.get('email', item.get('user', item.get('login', ''))))
            password = item.get('password', item.get('pass', item.get('pwd', item.get('key', ''))))
            
            # Handle nested data
            if not username and 'data' in item:
                data_item = item['data']
                if isinstance(data_item, dict):
                    username = data_item.get('username', data_item.get('email', ''))
                    password = data_item.get('password', data_item.get('pass', ''))
            
            if username and password:
                return {'domain': domain, 'username': str(username), 'password': str(password)}
        
        # Handle tuple or list format
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            domain = default_domain
            username = str(item[0])
            password = str(item[1]) if len(item) > 1 else ''
            return {'domain': domain, 'username': username, 'password': password}
    
    except Exception as e:
        pass
    
    return None

def check_password_strength(password):
    """Check password strength"""
    if not password or password == 'N/A':
        return 'UNKNOWN'
    if len(password) < 6:
        return 'WEAK'
    elif len(password) < 10:
        return 'MEDIUM'
    elif re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'\d', password):
        return 'STRONG'
    elif re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'STRONG'
    return 'MEDIUM'

def show_banner():
    """Display banner"""
    clear()
    
    banner = f"""
{R}     ███╗   ██╗ █████╗ ███████╗ █████╗ {N}
{R}     ████╗  ██║██╔══██╗██╔════╝██╔══██╗{N}
{R}     ██╔██╗ ██║███████║███████╗███████║{N}
{R}     ██║╚██╗██║██╔══██║╚════██║██╔══██║{N}
{R}     ██║ ╚████║██║  ██║███████║██║  ██║{N}
{R}     ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{N}
{W}     ██╗     ███████╗ █████╗ ██╗  ██╗{N}
{W}     ██║     ██╔════╝██╔══██╗██║ ██╔╝{N}
{W}     ██║     █████╗  ███████║█████╔╝ {N}
{W}     ██║     ██╔══╝  ██╔══██║██╔═██╗ {N}
{W}     ███████╗███████╗██║  ██║██║  ██╗{N}
{W}     ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝{N}
"""
    print(banner)
    print(f"{C}{'=' * 70}{N}")
    print(f"{B}{C}         ADVANCED DATA LEAK CHECKER v5.0{N}".center(70))
    print(f"{C}{'=' * 70}{N}")
    print(f"{Y}👨‍💻 Developer: {C}@KonokKibriya{N}")
    print(f"{Y}📢 Telegram:  {C}https://t.me/bdlogsbd{N}")
    print(f"{Y}🐙 GitHub:    {C}https://github.com/KonokKibriya{N}")
    print(f"{C}{'=' * 70}{N}\n")

def save_to_json(credentials, domain, limit):
    """Save credentials to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create reports directory
    reports_dir = os.path.expanduser("~/nasa_reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Prepare data for JSON
    json_data = {
        "scan_info": {
            "target_domain": domain,
            "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_found": len(credentials),
            "limit_requested": limit,
            "tool_version": "NASA Leak Checker v5.0",
            "developer": "@KonokKibriya",
            "telegram": "https://t.me/bdlogsbd"
        },
        "statistics": {},
        "credentials": []
    }
    
    # Calculate statistics
    strengths = {'STRONG': 0, 'MEDIUM': 0, 'WEAK': 0, 'UNKNOWN': 0}
    domains_count = {}
    
    for cred in credentials:
        strength = check_password_strength(cred['password'])
        strengths[strength] = strengths.get(strength, 0) + 1
        domains_count[cred['domain']] = domains_count.get(cred['domain'], 0) + 1
    
    json_data["statistics"] = {
        "password_strength": strengths,
        "domains_found": domains_count,
        "unique_domains": len(domains_count)
    }
    
    # Add credentials
    for cred in credentials:
        json_data["credentials"].append({
            "domain": cred['domain'],
            "username": cred['username'],
            "password": cred['password'],
            "strength": check_password_strength(cred['password'])
        })
    
    # Save JSON file
    json_filename = f"{reports_dir}/NASA_Leak_{domain}_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return json_filename

def display_results(credentials, domain, limit):
    """Display results with pagination support"""
    total = len(credentials)
    
    if total == 0:
        print(f"{R}┌──────────────────────────────────────────────────────────────────{N}")
        print(f"{R}│❌ NO LEAKS FOUND for: {domain}{N}")
        print(f"{R}└──────────────────────────────────────────────────────────────────{N}")
        return False
    
    # Calculate statistics
    strengths = {'STRONG': 0, 'MEDIUM': 0, 'WEAK': 0, 'UNKNOWN': 0}
    domains_count = {}
    
    for cred in credentials:
        strength = check_password_strength(cred['password'])
        strengths[strength] = strengths.get(strength, 0) + 1
        domains_count[cred['domain']] = domains_count.get(cred['domain'], 0) + 1
    
    # Header
    print(f"{G}┌──────────────────────────────────────────────────────────────────{N}")
    print(f"{G}│✅ FOUND {total} CREDENTIALS for {domain} (Limit: {limit}){N}")
    print(f"{G}└──────────────────────────────────────────────────────────────────{N}")
    print(f"{C}{'=' * 70}{N}")
    
    # Password Strength Statistics
    print(f"{B}{C}📊 PASSWORD STRENGTH STATISTICS:{N}")
    for strength, count in strengths.items():
        if count > 0:
            color = G if strength == 'STRONG' else Y if strength == 'MEDIUM' else R
            percentage = (count / total) * 100
            bar_length = int(percentage / 2)
            bar = '█' * bar_length + '░' * (50 - bar_length)
            print(f"   {color}{strength}: {count:3d} ({percentage:5.1f}%) {bar}{N}")
    
    # Domains found
    print(f"\n{B}{C}🌐 DOMAINS FOUND ({len(domains_count)} unique):{N}")
    for dom, count in sorted(domains_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   • {dom}: {count} credentials")
    
    # Display credentials with pagination
    print(f"\n{B}{C}🔐 LEAKED CREDENTIALS:{N}")
    print(f"{C}{'─' * 70}{N}")
    
    items_per_page = 20
    total_pages = (total + items_per_page - 1) // items_per_page
    current_page = 1
    
    while current_page <= total_pages:
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total)
        
        print(f"\n{Y}📄 Page {current_page}/{total_pages} (Showing {start_idx + 1}-{end_idx} of {total}){N}\n")
        
        for idx in range(start_idx, end_idx):
            cred = credentials[idx]
            strength = check_password_strength(cred['password'])
            icon = '🟢' if strength == 'STRONG' else '🟡' if strength == 'MEDIUM' else '🔴'
            
            print(f"{Y}[{idx + 1}]{N}")
            print(f"   {C}┌─ Domain:{N} {W}{cred['domain']}{N}")
            print(f"   {C}├─ User:{N}  {G}{cred['username'][:60]}{N}")
            print(f"   {C}├─ Pass:{N}  {R}{cred['password'][:60]}{N}")
            print(f"   {C}└─ Strength:{N} {icon} {strength}")
            print()
        
        # Pagination controls
        if current_page < total_pages:
            print(f"{C}{'─' * 70}{N}")
            print(f"{Y}➡️  Press Enter for next page, or 'q' to quit viewing{N}")
            choice = input(f"{C}└─> {W}").strip().lower()
            if choice == 'q':
                break
            current_page += 1
            clear()
            # Re-display header
            print(f"{G}✅ FOUND {total} CREDENTIALS for {domain}{N}")
            print(f"{C}{'=' * 70}{N}")
        else:
            break
    
    print(f"{C}{'─' * 70}{N}")
    
    # Save to JSON
    json_file = save_to_json(credentials, domain, limit)
    print(f"{G}💾 Results saved to: {json_file}{N}")
    
    return True

def loading_animation(text="Processing", duration=1):
    """Loading animation"""
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f'\r{C}[{chars[i % len(chars)]}] {text}...{N}')
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    print()

def main():
    show_banner()
    
    while True:
        try:
            # Get target domain
            print(f"{C}┌─{Y}[{C}🎯 ENTER TARGET DOMAIN/URL{Y}]{N}")
            target = input(f"{C}└─> {W}").strip()
            
            if not target:
                print(f"{R}❌ Please enter a valid domain!{N}")
                continue
            
            # Extract domain
            domain = target.lower()
            if '://' in domain:
                domain = domain.split('://')[1]
            domain = domain.split('/')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            
            print(f"{G}✓ Target: {Y}{domain}{N}")
            
            # Select limit
            print(f"\n{C}┌─{Y}[{C}📊 SELECT LIMIT{Y}]{N}")
            print(f"  {G}1{N}. Quick (50)")
            print(f"  {G}2{N}. Standard (100) {C}[Default]{N}")
            print(f"  {G}3{N}. Deep (500)")
            print(f"  {G}4{N}. Extreme (1000)")
            print(f"  {G}5{N}. Custom")
            
            choice = input(f"{C}└─> {W}").strip()
            
            limits = {'1': 50, '2': 100, '3': 500, '4': 1000}
            if choice in limits:
                limit = limits[choice]
            elif choice == '5':
                while True:
                    try:
                        limit = int(input(f"{C}Enter custom limit (10-5000): {W}"))
                        if 10 <= limit <= 5000:
                            break
                        else:
                            print(f"{R}Limit must be between 10 and 5000!{N}")
                    except ValueError:
                        print(f"{R}Please enter a valid number!{N}")
            else:
                limit = 100
            
            print(f"{C}[*] Limit: {Y}{limit}{N}")
            
            # Search
            loading_animation("Connecting to secure API", 1)
            loading_animation("Searching database", 1.5)
            
            # API search
            api_data = search_api(domain)
            
            if api_data:
                credentials = extract_credentials(api_data, domain)
                if credentials:
                    # Apply limit
                    credentials = credentials[:limit]
                    display_results(credentials, domain, limit)
                else:
                    print(f"{Y}⚠️ No credentials found in API response{N}")
            else:
                print(f"{R}❌ Unable to connect to secure API{N}")
                print(f"{Y}💡 Please check your internet connection and try again{N}")
            
            # Continue?
            print(f"\n{C}┌─{Y}[{C}🔄 SEARCH AGAIN?{Y}]{N}")
            again = input(f"{C}└─> {W}").lower()
            if again != 'y':
                print(f"\n{G}┌──────────────────────────────────────────────────────────────────{N}")
                print(f"{G}│👋 THANKS FOR USING NASA LEAK CHECKER!{N}")
                print(f"{G}│🔗 Join Telegram: https://t.me/bdlogsbd{N}")
                print(f"{G}│💬 Contact: @KonokKibriya{N}")
                print(f"{G}└──────────────────────────────────────────────────────────────────{N}")
                break
            
            show_banner()
            
        except KeyboardInterrupt:
            print(f"\n{R}⚠️ Operation cancelled by user{N}")
            print(f"{G}👋 Goodbye!{N}")
            sys.exit(0)
        except Exception as e:
            print(f"{R}❌ Error: {str(e)}{N}")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}⚠️ Interrupted{N}")
        sys.exit(0)