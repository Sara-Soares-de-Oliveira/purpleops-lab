# Case 1: SSH authentication analysis

**Status: in progress.** Reconnaissance, a controlled dictionary attack, log collection and retrospective detection testing have been performed. Containment, remediation and retesting have not been completed.

## Environment and exercise

Kali (`192.168.50.10`) tested an Ubuntu SSH server (`192.168.50.20`) on the VirtualBox internal network `purpleops-lab`. The account `ssh-lab` was created for the exercise and was known in advance; account enumeration was not demonstrated. All targets belong to this laboratory.

Host discovery found the two expected machines. A targeted service scan found TCP port 22 open and reported OpenSSH 10.2p1 on Ubuntu. A service banner alone does not establish a vulnerability.

```bash
nmap -sn 192.168.50.0/24 -oN discovery.txt
nmap -sT -sV -p 22 192.168.50.20 -oN ssh-service.txt
```

A Python/Paramiko script tried a ten-entry wordlist against `ssh-lab`. It recorded UTC timestamps and attempt outcomes without passwords. All ten attempts returned authentication failures and the run ended when the wordlist was exhausted. The script and original client JSONL are not included in this publication; the server evidence is available below.

## Evidence

The Ubuntu journal was exported using the `sshd-session` identifier. Files were transferred through a temporary host-only adapter and their SHA-256 hashes matched between Ubuntu and the host. This transfer network was a maintenance exception to the internal exercise network.

| Sample | Entries | Failed password | Accepted password |
|---|---:|---:|---:|
| [Baseline](evidence/ssh-baseline.log) | 21 | 1 | 3 |
| [Attack run 01](evidence/ssh-attack-run-01.log) | 30 | 10 | 0 |

One failed attempt produces multiple entries: a PAM failure, a `Failed password` event and a connection closure. The detection counts only `Failed password` events to avoid counting the same attempt multiple times.

The samples contain laboratory account names and private IP addresses. No passwords are present. The original timestamps and contents are preserved.

```text
8eb7fe2cd09b10764dfe9144564f29ef7d96848cd8fa5b789557430c51d3b124  ssh-baseline.log
e9494d06e110c70f3912a8d84c6bcdd5d11b3cb2e5efff1799dff28630244118  ssh-attack-run-01.log
```

Example baseline failure:

```text
2026-11-23T21:52:22+00:00 ubuntu sshd-session[2652]: Failed password for ubuntu from 192.168.50.10 port 53222 ssh2
```

Example attack failure:

```text
2026-11-26T17:38:23.089836+00:00 ubuntu sshd-session[4614]: Failed password for ssh-lab from 192.168.50.10 port 36260 ssh2
```

## Detection in Splunk

Both files were uploaded manually to index `purpleops`, with sourcetype `purpleops:ssh:journal` and host `ubuntu`. This is not continuous forwarding or a demonstrated scheduled alert.

The [tested SPL query](ssh-repeated-failures.spl) extracts the account, source IP and source port, orders events by time, and counts failures in a rolling 60-second window for each server/source-IP/account combination. It retains events with at least five failures in that window. Run it in Search & Reporting with a time range covering both samples. The [SPL guide](../splunk/spl-basics.md) explains each command.

Five failures in 60 seconds is a provisional lab threshold: it catches this short burst before the tenth attempt while excluding the single baseline error. The rolling window also avoids splitting the sequence at the minute boundary. It has not been tuned against representative production activity.

The query returned six rows, with running counts from five through ten. These are six qualifying events in one known test sequence, not six separate attacks or six triggered alerts.

## Timeline and triage

Times below are UTC from the Ubuntu evidence.

| Time | Observation |
|---|---|
| 2026-11-23 21:32–21:38 | Three successful baseline password authentications for `ubuntu`. |
| 2026-11-23 21:52:22 | One isolated baseline failure. |
| 2026-11-26 17:38:23.089836 | First failed password event for `ssh-lab` in run 01. |
| 2026-11-26 17:38:39.836953 | Fifth failure; detection threshold reached. |
| 2026-11-26 17:39:02.015293 | Tenth failure, about 38.93 seconds after the first. |

The source, account and repeated failures are consistent with the known controlled dictionary test. A search for `Accepted password` in the attack file returned zero results. This sample therefore demonstrates repeated failed authentication, not successful compromise. The earlier baseline successes are separate activity, not success following the attack.

Outside this controlled exercise, I would investigate whether the source is expected, whether an application is retrying stale credentials, and whether authentication succeeds before or after the selected interval. I would also examine other authentication methods and session/process activity before making a compromise determination.

## Limitations

- The baseline is small and cannot establish a production false-positive rate. Legitimate retries can match the rule.
- Attempts spread across accounts or over longer intervals may not meet this threshold.
- Guest clock synchronization was not confirmed. The detection uses Ubuntu event times; precise ordering across Kali and Ubuntu remains uncertain.
- Zero password-success events in this export does not exclude access outside its interval or through other methods.
- The observations do not establish password weakness: none of the tested candidates succeeded.
- Remediation effectiveness and preservation of legitimate access remain untested.
