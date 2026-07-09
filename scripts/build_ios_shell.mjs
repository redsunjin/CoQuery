import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = join(root, "app_shell", "terminal_shell_prototype");
const runtimeSourcePath = join(root, "app_shell", "ios_training_shell", "src", "trainingRuntime.ts");
const packPath = join(root, "practice_packs", "sql_basics.json");
const distDir = join(root, "dist", "ios-shell");

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
  .replace(
    '    <script src="./app.js"></script>',
    '    <script type="module" src="./ios-training-runtime.js"></script>\n    <script type="module" src="./app.js"></script>'
  );

write(join(distDir, "index.html"), html);
cpSync(join(sourceDir, "styles.css"), join(distDir, "styles.css"));
cpSync(join(sourceDir, "app.js"), join(distDir, "app.js"));

mkdirSync(join(distDir, "practice_packs"), { recursive: true });
cpSync(packPath, join(distDir, "practice_packs", "sql_basics.json"));

const practicePack = JSON.parse(read(packPath));
const runtimeSource = read(runtimeSourcePath);
const runtimeOutput = runtimeSource.replace("__COQUERY_SQL_BASICS_PACK__", JSON.stringify(practicePack));
write(join(distDir, "ios-training-runtime.js"), runtimeOutput);

console.log(`built iOS shell assets at ${distDir}`);
