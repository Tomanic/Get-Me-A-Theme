# Claude Code mods

Small Claude Code plugins for a homelab workflow.

| Mod | What it does |
| --- | --- |
| `homelab-facts` | Adds homelab hosts, ports and usernames to the system prompt. No passwords are stored. |
| `nas-guard` | Blocks recursive deletes under `/volume*`, Docker prune/volume removal and similar, unless moving to `#recycle`. |
| `ha-guard` | Home Assistant: read an automation before setting one, take a backup before deleting. |
| `needs-you-band` | Band and toast when Claude's last reply ends in a question. |
| `cost-meter` | Status line `$cost · ctx% · 5h% · 7d%`, with warnings at 75%/90% context and $5/$20. |

## Install

```
/plugin install homelab-facts --marketplace Tomanic/Get-Me-A-Theme
```

Answer `y` to add the marketplace, then pick a scope. Repeat for each mod. To try one from a checkout: `claude --plugin-dir mods/<name>`.

`mods/homelab-facts/hooks/facts.ts` lists LAN addresses; edit it to match your network.

Tests: `claude plugin test mods/<name>`.

## Known limits

- `nas-guard` matches on the command text, so a blocked phrase inside a heredoc or echo is blocked too.
- `ha-guard` forgets what it has seen when the mod reloads.
