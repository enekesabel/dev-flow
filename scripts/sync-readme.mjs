#!/usr/bin/env node
// Fills the `<!-- include: ... -->` blocks of every README.md with the file they name, so
// content shown in a README is maintained in one place.
//
//   <!-- include: path/to/file.md from="## Context" to="## Environments" shift=1 -->
//   ...replaced on every run...
//   <!-- /include -->
//
// `path` is relative to the README. `from` (inclusive) and `to` (exclusive) are whole lines
// of the file, compared after trimming; both are optional. `shift` demotes headings by that
// many levels. `code` wraps the content in a fenced code block of that language.
//
// Usage: node scripts/sync-readme.mjs          rewrite stale READMEs
//        node scripts/sync-readme.mjs --check  exit 1 if any README is stale

import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const check = process.argv.includes("--check");

const OPEN = /^[ \t]*<!-- include: (\S+)((?: \w+=(?:"[^"]*"|\S+))*) -->[ \t]*$/;
const CLOSE = /^[ \t]*<!-- \/include -->[ \t]*$/;

function* readmes(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const path = join(dir, entry.name);
    if (entry.isDirectory()) yield* readmes(path);
    else if (entry.name === "README.md") yield path;
  }
}

function parseAttrs(text) {
  const attrs = {};
  for (const m of text.matchAll(/(\w+)=(?:"([^"]*)"|(\S+))/g)) attrs[m[1]] = m[2] ?? m[3];
  return attrs;
}

function slice(lines, { from, to }) {
  let start = 0;
  let end = lines.length;
  if (from !== undefined) {
    start = lines.findIndex((line) => line.trim() === from);
    if (start < 0) throw new Error(`from="${from}" not found`);
  }
  if (to !== undefined) {
    end = lines.findIndex((line, i) => i > start && line.trim() === to);
    if (end < 0) throw new Error(`to="${to}" not found after from`);
  }
  return lines.slice(start, end);
}

function shiftHeadings(lines, by) {
  let inFence = false;
  return lines.map((line) => {
    if (/^```/.test(line)) inFence = !inFence;
    return !inFence && /^#{1,6} /.test(line) ? "#".repeat(by) + line : line;
  });
}

function trimBlank(lines) {
  let start = 0;
  let end = lines.length;
  while (start < end && lines[start].trim() === "") start++;
  while (end > start && lines[end - 1].trim() === "") end--;
  return lines.slice(start, end);
}

function render(readme, text) {
  const lines = text.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    out.push(lines[i]);
    const open = OPEN.exec(lines[i]);
    if (!open) continue;
    const close = lines.findIndex((line, j) => j > i && CLOSE.test(line));
    if (close < 0) throw new Error(`${readme}:${i + 1}: include is never closed`);
    const [, path, attrText] = open;
    const attrs = parseAttrs(attrText);
    const source = readFileSync(resolve(dirname(readme), path), "utf8").split("\n");
    let body;
    try {
      body = slice(source, attrs);
    } catch (error) {
      throw new Error(`${readme}:${i + 1}: ${error.message} in ${path}`);
    }
    body = trimBlank(shiftHeadings(body, Number(attrs.shift ?? 0)));
    if (attrs.code !== undefined) body = ["```" + attrs.code, ...body, "```"];
    out.push("", ...body, "", lines[close]);
    i = close;
  }
  return out.join("\n");
}

const stale = [];
for (const readme of readmes(root)) {
  const current = readFileSync(readme, "utf8");
  const rendered = render(readme, current);
  if (rendered === current) continue;
  stale.push(relative(root, readme));
  if (!check) writeFileSync(readme, rendered);
}

if (stale.length === 0) {
  console.log("All READMEs are in sync.");
} else if (check) {
  console.error(`Out of date, run \`node scripts/sync-readme.mjs\`:\n  ${stale.join("\n  ")}`);
  process.exit(1);
} else {
  console.log(`Updated:\n  ${stale.join("\n  ")}`);
}
