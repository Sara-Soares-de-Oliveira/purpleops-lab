# PurpleOps

**A hands-on Purple Team laboratory connecting offensive activity with defensive evidence.**

PurpleOps is a cybersecurity laboratory designed to study the complete security lifecycle:

**Attack → Telemetry → Detection → Investigation → Threat Intelligence → Containment → Remediation → Retest**

The focus is on understanding what happens at each stage of an attack, what evidence it produces, and how offensive and defensive security teams use that evidence to assess and improve security.

## Objective

Build a controlled, reproducible environment where I personally perform attacks against systems I own, collect the resulting telemetry, develop detections, investigate the activity, remediate weaknesses, and repeat the tests to validate the remediation.

The project aims to demonstrate both offensive and defensive understanding through documented decisions, observable evidence, and reproducible results. Each case should explain how the attack worked, why the detection logic is appropriate, and whether remediation addressed the underlying weakness while preserving legitimate activity.

## How I approach each case

For each case, I’ll work through both sides: carry out the attack, then investigate it using the logs it leaves behind. I’ll use those logs to build a detection and check whether normal activity could trigger it too.

After fixing the weakness, I’ll repeat the attack to see what changed. The write-up will include the evidence, what worked, what failed, and what I learned. Where useful, I’ll add threat intelligence context and map the observed behavior to MITRE ATT&CK.

All testing takes place against my own lab machines.

## Current Status

**In progress — building and validating the laboratory environment.**

Current work focuses on preparing dedicated virtual machines, configuring isolated networking, and verifying the foundations for reproducible experiments. A dedicated Kali VM has been prepared, and its IP addressing and routing configuration have been checked.

The proposed architecture is being documented. Communication between lab machines and full isolation validation remain unverified. No attack exercises have been performed or detections implemented yet.

## Documentation

| Document | Contents |
|---|---|
| [Kali VM setup](docs/kali-vm.md) | Configuration steps, commands, verification results, and lessons learned. |
| [Proposed architecture](docs/proposed-architecture.md) | Component roles, communication flows, isolation boundaries, and design decisions. |

These documents are being written incrementally and distinguish implemented configuration from proposed design.

## License

This project is licensed under the [MIT License](LICENSE).
