# SPL basics for PurpleOps

SPL means **Search Processing Language**. It is the language used to ask Splunk questions about stored events. A **query** is the search you write; its **results** are the events or calculated values it returns. Searching does not change the original logs.

This guide uses the SSH logs already imported for Case 1. These are manual file uploads, not a live feed from Ubuntu. The examples use **SPL**, not SPL2.

## 1. Run a search

Open **Search & Reporting**, paste a query into the search bar, choose a time range, and click the search icon. Use **All time** for these small historical samples: **Last 15 minutes** would exclude their original timestamps.

Start with:

```spl
index=purpleops sourcetype="purpleops:ssh:journal"
```

| Term | Meaning in this lab |
|---|---|
| Event | One indexed log entry. Several entries can describe one login attempt. |
| Field | A named piece of information in an event, such as `host`. |
| `index` | The collection where Splunk stores the events: `purpleops`. |
| `sourcetype` | A label associated with parsing settings for the data format: `purpleops:ssh:journal`. |
| `source` | Where the data came from; here, an uploaded filename. |
| `host` | The system that generated the event: `ubuntu`, set during upload. |
| `_raw` | The original event text. |
| `_time` | The event timestamp interpreted by Splunk. Its displayed timezone depends on user settings. |

Use **Events** to inspect log text and **Statistics** to inspect tables or calculated results. Check that `_time` agrees with the timestamp in the log, accounting for timezone.

## 2. Filter events

```spl
index=purpleops source="ssh-baseline.log" "Failed password"
```

This asks for events in `purpleops`, from that file, containing the phrase `Failed password`. Adjacent search conditions imply **AND**: all must match. Quotation marks keep the words together as a phrase.

Changing the source to `ssh-attack-run-01.log` selects the attack sample. In our imported data, the baseline returned **1** matching event and the attack returned **10**.

We count `Failed password` entries rather than every SSH entry: the same failed attempt can also produce a PAM failure and a connection closure. Counting all three would inflate the number of attempts.

To investigate successful password authentication in the attack sample:

```spl
index=purpleops sourcetype="purpleops:ssh:journal" source="ssh-attack-run-01.log" "Accepted password"
```

This returned **0 events**. It means no matching password-success event was found in this imported sample. It does not prove that no access occurred outside the sample or through another authentication method.

## 3. Read a pipeline

The pipe character, `|`, passes the results of one command to the next. Read a query from top to bottom: select events, extract information, calculate, then display.

This is the detection query we tested:

```spl
index=purpleops sourcetype="purpleops:ssh:journal" "Failed password"
| rex field=_raw "Failed password for (?:invalid user )?(?<user>\S+) from (?<src_ip>\S+) port (?<src_port>\d+)"
| sort 0 _time
| streamstats time_window=60s count AS failures_60s BY host src_ip user
| where failures_60s >= 5
| table _time source host user src_ip failures_60s
```

| Command | What it does here |
|---|---|
| Initial search | Selects SSH password failures, without depending on an attack filename. |
| `rex field=_raw` | Extracts fields from the log text using a regular expression. |
| `sort 0 _time` | Orders all matching events from oldest to newest; `0` removes the command's result limit. |
| `streamstats` | Adds a running count to each event. The 60-second window looks back from that event, including it. |
| `AS failures_60s` | Names the calculated count. |
| `BY host src_ip user` | Keeps a separate count for each server, source IP and account combination. |
| `where failures_60s >= 5` | Keeps only rows whose count is at least five. |
| `table ...` | Chooses the displayed columns and their order. It does not group events. |

The rolling calculation requires time-ordered events. A rolling window can include failures on both sides of a minute boundary, such as 17:38:57 and 17:39:02. See the official [streamstats reference](https://help.splunk.com/en/splunk-enterprise/spl-search-reference/10.2/search-commands/streamstats).

### Understanding the extraction

A **regular expression** is a pattern that describes text to match. For this log:

```text
Failed password for ssh-lab from 192.168.50.10 port 36260 ssh2
```

The expression extracts `user=ssh-lab`, `src_ip=192.168.50.10` and `src_port=36260`.

- `(?<user>...)` captures text into a field named `user`; the other named groups work the same way.
- `\S+` matches one or more non-whitespace characters.
- `\d+` matches one or more digits.
- `(?:invalid user )?` optionally matches the words `invalid user ` without creating a field for them.
- Literal words such as `from` and `port` identify where each value appears.

If extracted fields are empty, inspect `_raw`: the event format may differ from this pattern. Test extraction before relying on grouped counts.

## 4. Interpret the result

The tested query returned **six rows**, with counts from **5 to 10**. The first qualifying event was at **2026-11-26 17:38:39.836 UTC**, for `ssh-lab` from `192.168.50.10` on `ubuntu`. The isolated baseline failure did not qualify.

These are six qualifying events within one known test sequence, not six separate attacks or six triggered alerts. Five failures in 60 seconds is a provisional lab threshold. A service retrying an outdated password could also match; slower attempts or attempts spread across accounts could be missed. This small baseline cannot establish a production false-positive rate.

## 5. Save and troubleshoot

- **Report:** saves a search for reuse. Our detection report is named `PurpleOps - SSH repeated authentication failures`.
- **Alert:** requires trigger conditions and an execution configuration. A report returning rows is not evidence that an alert fired.
- Open a **new search** for investigation queries. Do not overwrite the detection report with the `Accepted password` check; if you edit it temporarily, avoid clicking **Save**.
- If a search returns nothing, check the time range, index and source names, then remove filters one at a time. Zero results can mean no matching data or a search/data problem.
- If counts seem too high, check for repeated imports and whether multiple log entries describe the same attempt.

To practise, remove only the `where` line from the detection query. The result should show all **11 password failures**, including the baseline row, with the running counts visible. Explain why filtering on five removes the baseline before changing the threshold.
