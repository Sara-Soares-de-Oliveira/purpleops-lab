# SSH dictionary exercise

`ssh_lab_dictionary.py` is the script used for Case 1. It attempts password authentication against the lab Ubuntu VM at `192.168.50.20`, using the dedicated `ssh-lab` account. It does not execute remote commands.

Run it from Kali on the isolated PurpleOps network, with the Ubuntu VM and SSH service running. Use only systems you own and have configured for this exercise.

## Setup

From this directory on Kali:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp lab-passwords.example.txt lab-passwords.txt
```

The virtual environment keeps dependencies separate from system Python. The requirements file specifies Paramiko 4.0.0, the version used in the original exercise.

The supplied wordlist contains ten fictional demonstration candidates. It is not the original run's wordlist and does not reproduce its exact inputs. `lab-passwords.txt` must be next to the script; keep actual credentials out of the repository.

## Run and inspect

Choose a new output filename for each execution so earlier evidence is preserved:

```bash
python3 ssh_lab_dictionary.py > ssh-attack-run-02.jsonl
cat ssh-attack-run-02.jsonl
```

The script reads at most ten nonempty candidates. It attempts them sequentially, waits one second between completed failed attempts, and stops on success, a connection error, or interruption. Authentication processing adds to the delay, so this does not mean one attempt per second. Connection, banner and authentication timeout settings are each five seconds.

Output is JSON Lines: one JSON object per line, containing a UTC timestamp, target, account and event details. Passwords are not logged. Inspect `attempt_finished` and `run_finished` to establish the result; an input error is recorded as `input_error`.

`authentication_failed` describes a rejected authentication attempt, not proof that the password alone caused rejection. Compare client results with Ubuntu's journal.

## Host identity and evidence limits

The script uses `AutoAddPolicy` and creates a new SSH client for each attempt. It does not verify a previously trusted server key or persist that trust between attempts. This reflects the lab exercise's lack of prior host-key knowledge; it is unsuitable as a trusted administrative SSH client.

The [original run](../docs/case%201/evidence/ssh-attack-run-01.jsonl) contains ten authentication failures and ends with `wordlist_exhausted`. No successful access was demonstrated. Guest clock synchronization was not confirmed, so compare the two machines' timestamps with that limitation in mind.
