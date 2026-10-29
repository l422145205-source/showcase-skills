# Evidence and small CI adapters

## Mood rules

| Input | Mood | Display |
|---|---|---|
| JUnit individual cases, any failure/error | failing | Actual recorded counts |
| JUnit individual cases, at least one executed pass, no failures/errors | passing | Actual counts, including skips in status.json |
| Every recorded JUnit case skipped | skipped | Never a green test-success badge |
| No cases, malformed/missing/oversized report | unknown | No invented passes |
| Workflow queued/in_progress/waiting | running | CI evidence, no test count |
| Workflow completed + success | passing | CI success, not proof of executed tests |
| Workflow completed + failure/timed_out/action_required/startup_failure | failing | CI failure |
| Workflow completed + skipped | skipped | CI skipped |
| Cancelled, neutral or unrecognized workflow result | unknown | Never silently converted to success |

JUnit uses individual testcase elements rather than summing parent suite counters; nested suites must not double counts. Namespace-qualified JUnit is accepted. Explicit DOCTYPE/entity declarations and files over 5 MB are rejected as unknown. A report is a snapshot, not a live subscription: rerender after new results.

Pass one evidence input:

```bash
python <skill-dir>/scripts/repopet.py render --repo . --checks workflow-result.json --out assets/repopet
```

Simplified workflow result:

```json
{"status":"completed","conclusion":"success"}
```

The same fields inside GitHub's workflow_run object are accepted. Other event fields, including actors, URLs and commit identities, are discarded. Do not turn a secret-bearing event payload into a public example.

## Existing CI

Add rendering after the project's actual test command has produced JUnit. Use the installed skill's path, or copy the skill folder into the project if the user requests a self-contained setup. For a Python project, the steps look like:

```yaml
- run: python -m pytest --junitxml=junit.xml
- if: always()
  run: python path/to/repo-pet/scripts/repopet.py render --repo . --junit junit.xml --out assets/repopet
- if: always()
  uses: actions/upload-artifact@v4
  with:
    name: repo-pet
    path: assets/repopet/
```

This example uploads an artifact; it does not commit images or grant write access. Setting up automated README updates needs an explicit user request and a review of that repository's workflow permissions. Keep the original test exit status; rendering a cute failing pet must not make a failing CI run green.

## Privacy and output

The helper reads reachable commit count only, never commit authors/messages/remotes. Output status JSON contains a pet name, palette/stage, aggregate counts and a generic evidence reason. A custom pet name is visible on the image; use a fictional name for public demos.

There are three generated files: pet.gif, pet.png, status.json. Generated filenames can be regenerated. Existing reports and arbitrary folders are not deleted. README text outside the owned marker block is preserved. The skill never pushes automatically.
