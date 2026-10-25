import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
const require=createRequire(import.meta.url);
const root=new URL('../',import.meta.url);
const read=path=>readFileSync(new URL(path,root),'utf8');
const lock=JSON.parse(read('package-lock.json'));
const version=name=>lock.packages[`node_modules/${name}`].version;
const atLeast=(actual,min)=>{
 const a=actual.split('.').map(Number),b=min.split('.').map(Number);
 for(let i=0;i<3;i++){if(a[i]!==b[i])return a[i]>b[i]}return true;
};
const cap=version('@capacitor/ios');
assert.ok(atLeast(cap,'8.4.3'));
for(const name of ['@capacitor/core','@capacitor/cli'])assert.equal(version(name),cap);
assert.equal(require('@capacitor/ios/package.json').version,cap);
assert.equal(JSON.parse(read('package.json')).dependencies['@capacitor/ios'],cap);
assert.ok(read('ios/App/CapApp-SPM/Package.swift').includes(`exact: "${cap}"`));
const nativeLock=JSON.parse(read('ios/App/App.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'));
assert.equal(nativeLock.pins.find(x=>x.identity==='capacitor-swift-pm').state.version,cap);
for(const [name,min]of [['@xmldom/xmldom','0.9.12'],['brace-expansion','5.0.12'],['tar','7.5.21']])assert.ok(atLeast(version(name),min),name);
// Check the installed native patch is present before plugin/host allow decisions.
const navigation=read('node_modules/@capacitor/ios/Capacitor/Capacitor/WebViewDelegationHandler.swift');
const proxyGuard=navigation.indexOf('if navURL.path.starts(with: CapacitorBridge.httpInterceptorStartIdentifier)');
assert.ok(proxyGuard>=0 && proxyGuard<navigation.indexOf('for pluginObject in bridge.plugins'));
assert.ok(navigation.slice(proxyGuard,proxyGuard+220).includes('decisionHandler(.cancel)'));
const handler=read('node_modules/@capacitor/ios/Capacitor/Capacitor/WebViewAssetHandler.swift');
assert.ok(handler.includes('getPluginConfig("CapacitorHttp").getBoolean("enabled", false) == true'));
assert.ok(handler.includes('urlSchemeTask.didFailWithError(URLError(.unsupportedURL))'));
const {DOMImplementation,XMLSerializer}=require('@xmldom/xmldom');
const doc=new DOMImplementation().createDocument(null,'root',null),serializer=new XMLSerializer();
assert.equal(serializer.serializeToString(doc.createEntityReference('safe'),{requireWellFormed:true}),'&safe;');
for(const name of ['safe; <injected/> &x','bad name','x\nother'])assert.throws(()=>doc.createEntityReference(name));
const mutated=doc.createEntityReference('safe');mutated.nodeName='safe; <injected/> &x';
assert.throws(()=>serializer.serializeToString(mutated,{requireWellFormed:true}));
const plist=require('plist');assert.equal(plist.parse(plist.build({name:'CoQuery',enabled:true})).name,'CoQuery');
// Isolate intentionally adversarial parser inputs; never extract an archive.
const child=spawnSync(process.execPath,['--input-type=module','-e',`
 import assert from 'node:assert/strict';
 import {expand}from'brace-expansion';import * as tar from'tar';
 assert.deepEqual(expand('asset-{a,b}.js'),['asset-a.js','asset-b.js']);
 for(const pattern of ['{a}'+'}'.repeat(32000)+',z}', '{'.repeat(4000)+'x'+'}'.repeat(4000)])assert.ok(Array.isArray(expand(pattern)));
 function archive(path){
  const name=Buffer.from(path+'\\0');const header=new tar.Header({path:'././@LongLink',type:'NextFileHasLongPath',size:name.length,mode:420});header.encode();
  const member=new tar.Header({path:'member',type:'File',size:0,mode:420});member.encode();
  return Buffer.concat([header.block,name,Buffer.alloc((512-name.length%512)%512),member.block,Buffer.alloc(1024)]);
 }
 for(const path of ['safe/file.txt','a/'.repeat(12000)+'file.txt'])await new Promise((resolve,reject)=>{const parser=tar.t({},['selected']);parser.on('error',reject);parser.on('end',resolve);parser.end(archive(path));});
`],{cwd:new URL('../',import.meta.url),encoding:'utf8',timeout:10000,maxBuffer:1024*1024});
assert.equal(child.error,undefined,child.error?.message);
assert.equal(child.status,0,child.stderr);
console.log('Dependency security: aligned npm/SPM native patch, proxy guards, XML creation/mutation rejection, normal plist/brace behavior, and bounded malformed brace/long-path tar controls passed.');
