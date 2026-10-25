import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import vm from 'node:vm';
const app = new URL('../app_shell/terminal_shell_prototype/', import.meta.url);
const context = vm.createContext({});
vm.runInContext(readFileSync(new URL('concept-puzzle-catalog.js',app),'utf8'),context);
const {puzzles,evaluate,fresh,coverage}=context.CoqueryPuzzles;
assert.equal(puzzles.length,9);
assert.deepEqual(JSON.parse(JSON.stringify(puzzles)),JSON.parse(readFileSync(new URL('../docs/concept-puzzle-v0.1-puzzles.json',import.meta.url),'utf8')));
const find=id=>puzzles.find(p=>p.id===id);
const plain=x=>JSON.parse(JSON.stringify(x));
assert.deepEqual(plain(evaluate(find('C1'),fresh())),['A']);
assert.deepEqual(plain(evaluate(find('C2'),fresh())),['A','B','C']);
assert.deepEqual(plain(evaluate(find('C3'),fresh())),['Q','R']);
assert.deepEqual(plain(evaluate(find('C3'),{...fresh(),variant:'strict'})),['R']);
assert.equal(evaluate(find('R1'),fresh()).length,3);
assert.equal(evaluate(find('R2'),fresh()).length,4);
assert.equal(evaluate(find('R3'),fresh()).length,7);
assert.equal(evaluate(find('R3'),{...fresh(),variant:'id'}).length,4);
const expected={U1:['1:false','1:true','2:false','2:true'],U2:['2:true'],U3:['2:true','3:false','3:true']};
for(const id of ['U1','U2','U3'])for(const min of [1,2,3,4])for(const newOnly of [false,true])assert.equal(evaluate(find(id),{...fresh(),min,newOnly}).ok,expected[id].includes(`${min}:${newOnly}`));
assert.equal(coverage(find('C3'),{...fresh(),seen:['base']}),false);
assert.equal(coverage(find('C3'),{...fresh(),seen:['base','strict']}),true);
assert.equal(coverage(find('U3'),{...fresh(),rules:[{min:2,newOnly:true}]}),false);
assert.equal(coverage(find('U3'),{...fresh(),rules:[{min:2,newOnly:true},{min:3,newOnly:false}]}),true);
const assets=['concept-puzzle-catalog.js','concept-puzzles.js','concept-puzzles.css','community-demo.html','community-demo.js','community-demo.css'];
const worker=readFileSync(new URL('service-worker.js',app),'utf8');
const build=readFileSync(new URL('../scripts/build_ios_shell.mjs',import.meta.url),'utf8');
for(const a of assets){assert.ok(existsSync(new URL(a,app)));assert.ok((worker.includes(`"./${a}"`) || worker.includes(`"./${a}?v=12"`)));assert.ok(build.includes(`"${a}"`))}
const demo=readFileSync(new URL('community-demo.html',app),'utf8');assert.ok(!demo.includes('pwa-runtime.js'));assert.ok(!demo.includes('src="./app.js"'));
console.log('Concept puzzles: 9 fixed specs, boundary/joins, 24 rule alternatives, coverage and web/iOS asset contracts passed.');

const offline = vm.createContext({
  window: {}, navigator: {},
  document: { querySelector: () => true, documentElement: { lang: "ko" } },
  localStorage: { getItem: () => "[]" }, fetch: async () => { throw new Error("offline"); },
});
vm.runInContext(readFileSync(new URL('pwa-runtime.js',app),'utf8'),offline);
const unavailable = await offline.window.coqueryCommandRuntime.postCommand('practice_query',{sql:'SELECT 1'});
assert.equal(unavailable.ok,false);
assert.equal(unavailable.error.code,'network_unavailable');
assert.deepEqual(plain(unavailable.data),{});
assert.deepEqual(plain(await offline.window.coqueryCommandRuntime.getSessions()),{sessions:[]});

// Separate document navigation must never replace the cached SQL home.
const handlers = {}, pages = new Map([["./index.html",new Response("SQL home")]]);
const workerContext = vm.createContext({
  URL, self: { addEventListener: (name,fn) => { handlers[name]=fn; } },
  caches: { open: async () => ({ put: async (name,response) => pages.set(name,response) }), match: async name => pages.get(name) },
  fetch: async () => new Response("simulation"),
});
vm.runInContext(worker,workerContext);
let pending;
handlers.fetch({ request:{url:"https://example.test/community-demo.html",method:"GET",mode:"navigate"},respondWith:value=>{pending=value} });
await pending;
assert.equal(await pages.get("./index.html").clone().text(),"SQL home");
assert.equal(await pages.get("./community-demo.html").clone().text(),"simulation");
workerContext.fetch=async()=>{throw new Error("offline")};
handlers.fetch({ request:{url:"https://example.test/community-demo.html",method:"GET",mode:"navigate"},respondWith:value=>{pending=value} });
assert.equal(await (await pending).clone().text(),"simulation");
handlers.fetch({ request:{url:"https://example.test/",method:"GET",mode:"navigate"},respondWith:value=>{pending=value} });
assert.equal(await (await pending).clone().text(),"SQL home");
