import sys
import json
import os
import subprocess
from datetime import datetime

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"

# Path to the schema
EXECUTION_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../docs/execution_interface.json")

BANNER = f"""{RED}{BOLD}
  ____             ____              __ 
 |  _ \\  __ _ _ __/ ___|  __ _  ___ / _| ___
 | |_) |/ _` | '_ \\___ \\ / _` |/ _ \\ |_ / _ \\
 |  _ <| (_| | | | |___) | (_| |  __/  _|  __/
 |_| \\_\\\\__,_|_| |_|____/ \\__,_|\\___|_|  \\___|
{RESET}"""

runtime_logs = []

def log_info(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    runtime_logs.append(f"{BLUE}[{timestamp}] [INFO] {msg}{RESET}")

def log_warn(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    runtime_logs.append(f"{YELLOW}[{timestamp}] [WARN] {msg}{RESET}")

def log_err(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    runtime_logs.append(f"{RED}[{timestamp}] [ERROR] {msg}{RESET}")

def log_success(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    runtime_logs.append(f"{GREEN}[{timestamp}] [SUCCESS] {msg}{RESET}")

def render_ui(action, target, token="", reasoning="", logs=[]):
    """Clears screen and draws a high-fidelity, colored cybersecurity console."""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    print(f"{CYAN}{BOLD}=" * 80 + f"{RESET}")
    print(f" {WHITE}{BOLD}🛡️  RANSAFE SRE ORCHESTRATOR — ACTIVE CONTAINMENT ENGINE  🛡️{RESET}")
    print(f"{CYAN}=" * 80 + f"{RESET}")
    
    # Format labels
    module = f"{BLUE}execution/handler.py (Core Engine){RESET}"
    monitored_node = f"{YELLOW}{target}{RESET}"
    auth_token = f"{MAGENTA}{token if token else 'N/A'}{RESET}"
    
    if action == "AIRGAP_NODE":
        action_str = f"{RED}{BOLD}AIRGAP_NODE{RESET}"
        switch_str = f"{BG_RED}{WHITE}{BOLD} 🚨 OPENED - CRITICAL ANOMALY AIRGAP ACTIVE {RESET}"
        integrity_str = f"{RED}{BOLD}🔥 ATTACK VECTOR MITIGATED IN REAL-TIME{RESET}"
    elif action == "REALLOCATE_RESOURCES":
        action_str = f"{GREEN}{BOLD}REALLOCATE_RESOURCES{RESET}"
        switch_str = f"{BG_YELLOW}{WHITE}{BOLD} 🟢 CLOSED - ACTIVE RESOURCE AUTOMATION {RESET}"
        integrity_str = f"{YELLOW}{BOLD}📈 HIGH PRODUCTION WORKLOAD BALANCING{RESET}"
    elif action == "MONITOR_INTENSE":
        action_str = f"{YELLOW}{BOLD}MONITOR_INTENSE{RESET}"
        switch_str = f"{BG_YELLOW}{WHITE}{BOLD} ⚠️ WARN - HIGH FREQUENCY OBSERVABILITY {RESET}"
        integrity_str = f"{CYAN}{BOLD}🔍 DEEPER METRIC SIGNATURE ANALYSIS{RESET}"
    else:
        action_str = f"{CYAN}{BOLD}NOMINAL / AWAITING PAYLOAD{RESET}"
        switch_str = f"{BG_GREEN}{WHITE}{BOLD} 🟢 CLOSED - STEADY NOMINAL STATE {RESET}"
        integrity_str = f"{GREEN}{BOLD}✅ NO MALICIOUS DISK BEHAVIOR DETECTED{RESET}"

    print(f" {BOLD}• CONTEXT MODULE{RESET}   : {module}")
    print(f" {BOLD}• MONITORED NODE{RESET}   : {monitored_node}")
    print(f" {BOLD}• AUTH TOKEN{RESET}       : {auth_token}")
    print(f" {BOLD}• DISPATCH ACTION{RESET}  : {action_str}")
    print(f" {BOLD}• CIRCUIT SWITCH{RESET}   : {switch_str}")
    print(f" {BOLD}• SYSTEM INTEGRITY{RESET} : {integrity_str}")
    print(f"{CYAN}-" * 80 + f"{RESET}")
    
    if reasoning:
        print(f" {BOLD}🧠 AI REASONING SUMMARY:{RESET}")
        print(f"  \"{ITALIC}{WHITE}{reasoning}{RESET}\"")
        print(f"{CYAN}-" * 80 + f"{RESET}")
        
    print(f" {BOLD}📜 LIVE EXECUTION LOG PIPELINE:{RESET}")
    if logs:
        for log in logs[-8:]: # Show last 8 logs
            print(f"  {log}")
    else:
        print(f"  {BLUE}[INFO] Pipeline active. Awaiting autonomous evaluation matrix...{RESET}")
    print(f"{CYAN}=" * 80 + f"{RESET}")

if __name__ == "__main__":
    # Check for jsonschema availability
    try:
        import jsonschema
        HAS_JSONSCHEMA = True
    except ImportError:
        HAS_JSONSCHEMA = False

    # Load schemas
    try:
        with open(EXECUTION_SCHEMA_PATH, "r") as f:
            EXECUTION_SCHEMA = json.load(f)
    except Exception as e:
        EXECUTION_SCHEMA = None
        log_warn(f"Could not load execution interface schema: {e}")

    # Render baseline monitoring view
    log_info("RanSafe Execution Orchestrator Daemon initialized.")
    render_ui("NOMINAL", "k8s-pod-node-dummy-app-xyz", "", "", runtime_logs)

    # Stream payload records from standard input
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            payload = json.loads(line.strip())
            
            # Validate schema
            if HAS_JSONSCHEMA and EXECUTION_SCHEMA:
                try:
                    jsonschema.validate(instance=payload, schema=EXECUTION_SCHEMA)
                    log_success("Payload successfully validated against execution_interface.json schema.")
                except jsonschema.exceptions.ValidationError as ve:
                    log_err(f"Schema Validation Failed: {ve.message}")
                    render_ui("NOMINAL", "unknown-node", "", "", runtime_logs)
                    continue
            else:
                # Basic validation fallback
                required = ["action", "target_node_id", "authorization_token", "reasoning_summary"]
                missing = [f for f in required if f not in payload]
                if missing:
                    log_err(f"Payload missing required fields: {missing}")
                    render_ui("NOMINAL", "unknown-node", "", "", runtime_logs)
                    continue

            action_token = payload.get("action")
            target_asset = payload.get("target_node_id")
            auth_token = payload.get("authorization_token")
            ai_reasoning = payload.get("reasoning_summary")
            
            if action_token in ["AIRGAP_NODE", "REALLOCATE_RESOURCES", "MONITOR_INTENSE"]:
                log_info(f"Routing action {action_token} to airgap_rules.sh...")
                
                # Locate and execute airgap script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                airgap_script = os.path.join(script_dir, "airgap_rules.sh")
                
                # Make script executable
                try:
                    os.chmod(airgap_script, 0o755)
                except Exception:
                    pass
                
                # Execute physical system changes using the bash script
                proc = subprocess.run(
                    [airgap_script, target_asset, action_token, auth_token, ai_reasoning],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Process script output into live logs
                for outline in proc.stdout.splitlines():
                    if outline.strip():
                        if "Success" in outline or "verified" in outline or "✅" in outline:
                            log_success(outline.strip())
                        elif "ERROR" in outline or "❌" in outline:
                            log_err(outline.strip())
                        elif "WARNING" in outline or "⚠️" in outline:
                            log_warn(outline.strip())
                        else:
                            log_info(outline.strip())
                            
                for errline in proc.stderr.splitlines():
                    if errline.strip():
                        log_err(errline.strip())
                
                if proc.returncode == 0:
                    log_success(f"Execution engine successfully applied action: {action_token}")
                else:
                    log_err(f"Execution script exited with error code {proc.returncode}")
                
                render_ui(action_token, target_asset, auth_token, ai_reasoning, runtime_logs)
                
                if action_token == "AIRGAP_NODE":
                    print(f"\n{RED}{BOLD}🎯 DEMO CHECKPOINT: Ransomware lateral movement isolated successfully via Cloud APIs.{RESET}\n")
                    break
            else:
                log_warn(f"Received unknown action code: {action_token}. No state mutation triggered.")
                render_ui("NOMINAL", target_asset, auth_token, ai_reasoning, runtime_logs)
                
        except json.JSONDecodeError:
            log_err("Received malformed non-JSON data stream.")
            render_ui("NOMINAL", "unknown-node", "", "", runtime_logs)
            continue