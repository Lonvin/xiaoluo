#!/usr/bin/env python3
import sys, re
from pathlib import Path

INJECTION_PATTERNS = [
    (r"忽略.{0,20}(之前|前面|以上|所有).{0,20}(指令|规则|提示|设定)", "cmd_override"),
    (r"(你|现在|此刻).{0,10}(是|变成|成为).{0,20}(新|不同)", "identity_redef"),
    (r"(忘记|删除|清除).{0,20}(记忆|规则|设定|SOUL)", "memory_wipe"),
    (r"DAN|do anything now|越狱|jailbreak", "jailbreak"),
]

DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/", "rm_root"),
    (r"curl.*\|.*(bash|sh)", "pipe_exec"),
    (r"sudo\s+", "sudo"),
]

def check_injection(text):
    triggers = []
    for pat, label in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            triggers.append(label)
    return len(triggers) > 0, triggers

def check_dangerous(command):
    triggers = []
    for pat, label in DANGEROUS_PATTERNS:
        if re.search(pat, command):
            triggers.append(label)
    return len(triggers) > 0, triggers

def audit_keys(text):
    key_pat = r"sk-[a-zA-Z0-9]{20,}"
    return re.findall(key_pat, text)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "scan-message":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
        inj, trig = check_injection(text)
        if inj:
            print("WARNING: Injection detected! " + str(trig))
            sys.exit(1)
        print("SAFE")
    
    elif cmd == "scan-command":
        cmd_text = " ".join(sys.argv[2:])
        danger, trig = check_dangerous(cmd_text)
        if danger:
            print("DANGER: " + str(trig))
            sys.exit(1)
        print("SAFE")
    
    elif cmd == "audit-keys":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
        keys = audit_keys(text)
        if keys:
            print("WARNING: " + str(len(keys)) + " key(s)")
            sys.exit(1)
        print("SAFE")
    
    elif cmd == "full-scan":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
        issues = []
        inj, trig = check_injection(text)
        if inj:
            issues.append("INJECTION: " + str(trig))
        keys = audit_keys(text)
        if keys:
            issues.append("KEYS: " + str(len(keys)))
        if issues:
            print("ISSUES: " + "; ".join(issues))
            sys.exit(1)
        print("SAFE")
    
    else:
        print("Usage: scan-message | scan-command | audit-keys | full-scan")
