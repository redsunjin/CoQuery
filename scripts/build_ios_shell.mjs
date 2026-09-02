import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = join(root, "app_shell", "terminal_shell_prototype");
const runtimeSourcePath = join(root, "app_shell", "ios_training_shell", "src", "trainingRuntime.ts");
const packPath = join(root, "practice_packs", "sql_basics.json");
const distDir = join(root, "dist", "ios-shell");
const shellAssets = [
  "styles.css",
  "onboarding.css",
  "practice-focus.css",
  "learning-path.css",
  "coquery-icon.svg",
  "app.js",
  "onboarding.js",
  "practice-focus.js",
  "learning-path.js",
  "curriculum-expansion.js",
];

function read(path) {
  return readFileSync(path, "utf8");
}

function write(path, text) {
  writeFileSync(path, text, "utf8");
}

rmSync(distDir, { recursive: true, force: true });
mkdirSync(distDir, { recursive: true });

const html = read(join(sourceDir, "index.html"))
  .replace('value="provider_list_presets"', 'value="practice_list"')
  .replace('    <script src="./pwa-runtime.js"></script>\n', "")
  .replace(
    '    <script src="./app.js"></script>',
    '    <script src="./ios-training-runtime.js"></script>\n    <script src="./app.js"></script>'
  );

write(join(distDir, "index.html"), html);
for (const asset of shellAssets) {
  cpSync(join(sourceDir, asset), join(distDir, asset));
}

mkdirSync(join(distDir, "practice_packs"), { recursive: true });
cpSync(packPath, join(distDir, "practice_packs", "sql_basics.json"));

const practicePack = JSON.parse(read(packPath));
const runtimeSource = read(runtimeSourcePath);
const runtimeOutput = runtimeSource
  .replace("__COQUERY_SQL_BASICS_PACK__", JSON.stringify(practicePack))
  .replaceAll("export async function ", "async function ")
  .replaceAll("export function ", "function ")
  .replaceAll("export const ", "const ");
write(join(distDir, "ios-training-runtime.js"), runtimeOutput);

console.log(`built iOS shell assets at ${distDir}`);
