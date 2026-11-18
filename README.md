# DevFlow has moved

DevFlow now lives in [enekesabel/dev-env](https://github.com/enekesabel/dev-env), as the
[`devflow`](https://github.com/enekesabel/dev-env/tree/main/skills/devflow) skill. It is no longer a
Claude Code plugin, and this repository is archived.

Install the skill:

```bash
npx skills add enekesabel/dev-env --skill devflow
```

Then invoke `/devflow` to make the agent the DevFlow Coordinator. `system-architecture` and
`use-skill` moved to dev-env as standalone skills, and `recall` is now part of `devflow`.

If you installed the plugin, remove it:

```
/plugin uninstall dev-flow@dev-flow
/plugin marketplace remove dev-flow
```
