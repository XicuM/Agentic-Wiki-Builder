import sys
import os
import urllib.parse

# List of pre-approved domains for literature searches and standard APIs
APPROVED_DOMAINS = {
    "api.semanticscholar.org",
    "arxiv.org",
    "export.arxiv.org",
    "api.openalex.org",
    "eutils.ncbi.nlm.nih.gov",
    "www.googleapis.com",
    "api.unpaywall.org",
    "www.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov"
}

def check_permission(action_type: str, details: str) -> bool:
    """
    Enforces authorization check for system and network operations.
    Raises PermissionError if the action is denied or fails safe.
    """
    if action_type == "network":
        # Parse host/domain from URL details
        try:
            parsed_url = urllib.parse.urlparse(details)
            domain = parsed_url.netloc.split(":")[0]  # strip port if present
        except Exception:
            raise PermissionError(f"Gating Error: Invalid URL details: {details}")

        # Check if domain is pre-approved
        if domain in APPROVED_DOMAINS:
            return True

        # Check bypass flag
        if os.environ.get("HARNESS_BYPASS_GATE") == "1":
            print(f"⚠️  [Permission Gate] Bypass active. Allowing unapproved network request to {domain}")
            return True

        # For unapproved domains, request user consent
        prompt = f"\n⚠️  [Permission Gate] Script is attempting an outbound network request to an unapproved domain: {domain}\nURL: {details}\nAllow this connection? (y/n): "
        
        # If running in non-interactive mode, fail safe
        if not sys.stdin.isatty():
            raise PermissionError(f"Permission Denied: Outbound request to {domain} blocked in non-interactive environment.")

        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            response = sys.stdin.readline().strip().lower()
            if response in ("y", "yes"):
                return True
            else:
                raise PermissionError(f"Permission Denied: Connection to {domain} refused by user.")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise
            raise PermissionError(f"Permission Gate Error: Failed to prompt user. Outbound request to {domain} blocked.")

    elif action_type == "shell":
        if os.environ.get("HARNESS_BYPASS_GATE") == "1":
            print(f"⚠️  [Permission Gate] Bypass active. Allowing shell execution: {details}")
            return True

        # Check command execution
        prompt = f"\n⚠️  [Permission Gate] Script is attempting to execute a shell command:\nCommand: {details}\nAllow this execution? (y/n): "
        
        if not sys.stdin.isatty():
            raise PermissionError(f"Permission Denied: Shell execution blocked in non-interactive environment: {details}")

        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            response = sys.stdin.readline().strip().lower()
            if response in ("y", "yes"):
                return True
            else:
                raise PermissionError(f"Permission Denied: Shell command execution refused by user.")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise
            raise PermissionError(f"Permission Gate Error: Failed to prompt user. Shell execution blocked.")
            
    else:
        raise PermissionError(f"Gating Error: Unknown action type: {action_type}")
