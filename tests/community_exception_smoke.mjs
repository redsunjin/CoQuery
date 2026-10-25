import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
let sourceHandler;
const app={innerHTML:'',contains:()=>false,querySelector:()=>null,addEventListener:(name,fn)=>{sourceHandler=fn}};
const context=vm.createContext({
 document:{getElementById:()=>app,activeElement:null,querySelector:()=>({kind:'의견',claim:'보존',evidence:'근거',counter:'한계',alt:''})},window:{scrollTo:()=>{}},
 FormData:class {constructor(fields){this.fields=fields}get(key){return this.fields[key]??null}*[Symbol.iterator](){yield* Object.entries(this.fields)}}
});
vm.runInContext(readFileSync(new URL('../app_shell/terminal_shell_prototype/community-demo.js',import.meta.url),'utf8'),context);
context.requestAnimationFrame=fn=>fn();
const run=code=>vm.runInContext(code,context);
for(const field of ['claim','evidence','counter']){
 run(`c=newCommunity();c.step=2;queueAnswer({preventDefault(){},target:{kind:'사실',claim:'주장',evidence:'근거',counter:'한계',alt:'',${field}:' \\n '}})`);
 assert.equal(run('c.pending'),null);
 assert.match(run('c.error'),/공백/);assert.equal(run('c.answerDraft.kind'),'사실');
}
run(`c=newCommunity();c.step=2;queueAnswer({preventDefault(){},target:{kind:'의견',claim:' 주장 ',evidence:' 근거 ',counter:' 한계 ',alt:''}})`);
assert.equal(run('c.pending.claim'),'주장');assert.equal(run('c.answerState'),'waiting');
run('cancelAnswer()');assert.equal(run('c.pending'),null);assert.equal(run('c.answerDraft.claim'),'주장');
run(`fileReport({preventDefault(){},target:{target:'A1',reason:'근거',detail:'  '}})`);
assert.equal(run('c.report'),null);assert.match(run('c.error'),/공백/);
run(`fileAppeal({preventDefault(){},target:{appeal:'\\n '}})`);
assert.equal(run('c.appeal'),null);assert.match(run('c.error'),/공백/);
run(`fileReport({preventDefault(){},target:{target:'A1',reason:'근거',detail:' 유효한 이유 '}})`);assert.equal(run('c.report.detail'),'유효한 이유');
run(`fileAppeal({preventDefault(){},target:{appeal:' 추가 맥락 '}})`);assert.equal(run('c.appeal.text'),'추가 맥락');
run(`c=newCommunity();c.checkOutcome='pending';runCheck()`);
assert.equal(run('c.published'),false);assert.equal(run('c.checkState'),'pending');
run('cancelCheck()');assert.equal(run('c.step'),0);assert.ok(run('c.question.length')>0);
console.log('Community exceptions: whitespace rejection, valid structured answer, cancellation/draft retention and no auto-publication passed.');

run("c=newCommunity();c.step=2;c.summary=true;c.confirmed=true;preserveAnswerDraft()");
assert.equal(run('c.step'),2);assert.equal(run('c.summary'),true);assert.equal(run('c.confirmed'),true);assert.equal(run('c.answerDraft.claim'),'보존');
const details={open:false};let focused=false;
context.document.getElementById=()=>({closest:()=>details,setAttribute(){},focus(){focused=true}});
sourceHandler({target:{closest:()=>({getAttribute:()=> '#source-A1'})}});
assert.equal(details.open,true);assert.equal(focused,true);
console.log('Draft cancellation preserves the stage and summary; source links open details and focus the source.');

context.document.getElementById=()=>app;
run("c=newCommunity();c.step=4;c.answers=[{id:'A1',claim:'첫 주장'},{id:'A2',claim:'두 번째 주장'}];fileReport({preventDefault(){},target:{target:'A2',reason:'인신공격·괴롭힘',detail:'  '}})");
assert.equal(run('c.report'),null);assert.equal(run('c.reportDraft.target'),'A2');assert.equal(run('c.reportDraft.reason'),'인신공격·괴롭힘');
assert.match(app.innerHTML,/<option value="A2" selected>/);assert.match(app.innerHTML,/<option selected>인신공격·괴롭힘/);
run("fileReport({preventDefault(){},target:{...c.reportDraft,detail:'다시 작성한 이유'}})");assert.equal(run('c.report.target'),'A2');assert.equal(run('c.report.reason'),'인신공격·괴롭힘');
console.log('Report validation preserves non-default target/reason and resubmits to the intended answer.');
