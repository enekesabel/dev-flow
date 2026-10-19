// Checks pull request titles, which become the commit on main when a pull request is squash-merged.
// release-please reads those commits to choose the next version and write the changelog.
//
// A change to what the plugin ships (agents/, skills/, references/, the manifests) is a `feat` or
// a `fix`, because users run that text. Only `feat` and `fix` trigger a release.

import { readdirSync } from "node:fs";

const skills = readdirSync(new URL("./skills/", import.meta.url), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name);

export default {
  extends: ["@commitlint/config-conventional"],
  // Check every title, including ones commitlint skips by default (`fixup!`, `Revert "…"`,
  // `v1.2.3`): release-please reads none of them, so a shipped change merged under one would never
  // be released.
  defaultIgnores: false,
  rules: {
    "type-enum": [2, "always", ["feat", "fix", "docs", "ci", "chore"]],
    // One scope per skill, `devflow` for the Coordinator and its references, `skills` for a change
    // spanning several skills, `plugin` for the manifests. A cross-cutting change has no scope.
    "scope-enum": [2, "always", [...skills, "devflow", "skills", "plugin"]],
  },
};
