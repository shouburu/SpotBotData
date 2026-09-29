#!/usr/bin/env python3
"""Resume an active round in bounded parallel groups with live UI accounting.

Never automatically retries, bypasses reference reviews, or approves media.
An exact settled attempt may receive one explicitly authored correction.
Ambiguous failures leave durable unresolved records and stop the runner.
An explicit option reconciles evidenced terminal failures before other jobs continue.
"""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
import form_media as f
from generate_form_media_group import reference_files

GFLOW_PYTHON=Path.home()/'.local/share/uv/tools/gflow-cli/bin/python'
def command(args):
 subprocess.run([str(x) for x in args],cwd=f.ROOT,check=True)

def observe(kind=None, aspect='9:16', duration=8, model=None):
 path=f.MEDIA/'ui-quotes'/('observed-'+uuid.uuid4().hex[:16]+'.json')
 args=[GFLOW_PYTHON,f.ROOT/'Scripts/observe_form_media_flow.py','--output',path]
 if kind:args+=['--kind',kind,'--aspect',aspect,'--duration',duration]
 if model:args+=['--model',model]
 command(args)
 return path,f.read_json(path)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--round',required=True);p.add_argument('--max-groups',type=int,default=150);p.add_argument('--kind',choices=['image','video'],help='Restrict this run to reviewed still references or motion jobs.');p.add_argument('--settle-terminal-failures',action='store_true',help='Reconcile exact provider-terminal failures against a fresh balance, then continue other jobs without retrying failed shots.');args=p.parse_args()
 if not 1<=args.max_groups<=150:raise ValueError('Choose 1–150 groups.')
 (f.MEDIA/'generation-groups').mkdir(exist_ok=True)
 for _ in range(args.max_groups):
  with f.locked():
   m=f.read_json(f.MANIFEST);records=f.ledger()
  if m['activeRoundId']!=args.round:raise ValueError('Active round changed.')
  if m.get('activeGenerationGroup') or any(f.unresolved(a) for a in records['attempts']):raise ValueError('Reconcile previous submissions first.')
  jobs=f.read_json(f.MEDIA/f'{args.round}-jobs.json')['jobs'];used={a['shot'] for a in records['attempts']}
  candidates=[]
  for kind in ([args.kind] if args.kind else ['video','image']):
   for j in jobs:
    if j['exerciseId'] not in m['exercises']:continue
    if j['kind']!=kind or m['exercises'][j['exerciseId']].get('reviewStatus')=='accepted':continue
    if j['shot'] in used:
     prior=[a for a in records['attempts'] if a['shot']==j['shot']]
     if sum(f.counts_toward_shot_limit(a) for a in prior)>=f.shot_attempt_limit(m,args.round,j['shot']):continue
     # A reviewed correction authorizes exactly one new attempt, never a loop.
     settled_terminal = bool(prior and prior[-1]['status']=='failed' and prior[-1].get('terminalFailureEvidence') and prior[-1].get('actualCredits')==0)
     # An operator may deliberately retry one exact, evidenced zero-charge
     # provider failure without pretending its prompt needs a form correction.
     terminal_retry = bool(settled_terminal and j.get('terminalRetryAfterAttemptId')==prior[-1]['id'] and j.get('terminalRetryReason'))
     if not prior or j.get('correctAfterAttemptId')!=prior[-1]['id'] or (prior[-1]['status']!='completed' and not settled_terminal) or prior[-1].get('actualCredits') is None or (j['promptSha256']==prior[-1].get('promptSha256') and not terminal_retry):continue
    if j.get('productionDisposition') not in {'prompt-reviewed','awaiting-reference','ready-to-animate'}:continue
    try:reference_files(j,records,args.round)
    except ValueError:continue
    candidates.append(j)
  if not candidates:
   print(json.dumps({'status':'awaiting-editorial-or-final-single-job','eligibleJobs':[j['shot'] for j in candidates]}),flush=True);return
  # Give untouched exercises their first trial before repeatedly revisiting
  # earlier corrections. Stable ordering retains catalog priority within a tier.
  attempt_counts={j['shot']:sum(f.counts_toward_shot_limit(a) for a in records['attempts'] if a['shot']==j['shot']) for j in candidates}
  candidates.sort(key=lambda j:attempt_counts[j['shot']])
  quote_settings=lambda j:('text-video' if j.get('videoMode')=='t2v' else j['kind'],j['aspect'],j.get('duration') or 8,j['model'])
  # Keep the first eligible job's priority, then fill its workers with matching
  # settings where possible. Each exact settings cohort needs a fresh visible
  # quote; packing cohorts avoids repeated browser setup without reusing prices.
  first_settings=quote_settings(candidates[0])
  first_count=attempt_counts[candidates[0]['shot']]
  matching=[j for j in candidates if quote_settings(j)==first_settings and attempt_counts[j['shot']]==first_count]
  matching_shots={j['shot'] for j in matching}
  others=[j for j in candidates if j['shot'] not in matching_shots]
  candidates=(matching+others)[:min(4,len(m['generationWorkers']))]
  quotes={settings:observe(*settings)[1] for settings in dict.fromkeys(quote_settings(j) for j in candidates)};members=[]
  for j in candidates:
   quote=quotes[quote_settings(j)]
   key=f.pilot_model_key(j['model'],j['duration'],'text-only' if j.get('videoMode')=='t2v' else 'start-only',j['aspect'])
   if (quote['aspect']!=j['aspect'] or quote['durationSeconds']!=j['duration'] or quote['count']!=1
       or quote.get('model')!=j['model'] or quote.get('modelKey')!=key
       or quote.get('family')!=f.PILOT_MODEL_LABELS[j['model']]):raise ValueError('Live observed settings differ from the planned job.')
   q=dict(quote,exerciseId=j['exerciseId'],shot=j['shot'])
   qp=f.MEDIA/'ui-quotes'/(j['shot']+'-'+uuid.uuid4().hex[:8]+'.json');f.write_json(qp,q);members.append({'shot':j['shot'],'quoteFile':f.relative(qp)})
  config=f.MEDIA/'generation-groups'/('config-'+uuid.uuid4().hex[:12]+'.json');f.write_json(config,{'members':members})
  try:
   command([sys.executable,f.ROOT/'Scripts/generate_form_media_group.py','run','--config',f.relative(config)])
  except subprocess.CalledProcessError:
   if not args.settle_terminal_failures or not f.read_json(f.MANIFEST).get('activeGenerationGroup'):raise
   # Settlement below still refuses uncertain outcomes, mismatched media IDs,
   # missing masters, or any balance delta not explained by successful quotes.
  m=f.read_json(f.MANIFEST);group=m['activeGenerationGroup'];evidence,after=observe();after['groupId']=group['id'];f.write_json(evidence,after)
  settle=[sys.executable,f.ROOT/'Scripts/generate_form_media_group.py','settle','--group',group['id'],'--evidence',f.relative(evidence)]
  if args.settle_terminal_failures:settle+=['--allow-terminal-failures']
  command(settle)
  jobmap={j['shot']:j for j in candidates}
  failed_shots=set()
  for a in f.ledger()['attempts']:
   if a.get('generationGroupId')!=group['id']:continue
   if a['status']=='failed':failed_shots.add(a['shot']);continue
   j=jobmap[a['shot']]
   command([sys.executable,f.ROOT/'Scripts/prepare_form_media_asset.py','--attempt',a['id'],'--title',j['title'],'--alt',j['alt']])
  with f.locked():
   m=f.read_json(f.MANIFEST)
   for j in candidates:
    e=m['exercises'][j['exerciseId']]
    if j['shot'] in failed_shots:
     e.update(productionStatus='provider-failed',productionNote='Exact provider failure reconciled at zero credits; no video was produced. A deliberate retry requires a new authorization tied to this attempt.');continue
    e['productionStatus']='ready-for-review' if j['kind']=='video' else 'awaiting-reference-review'
    e['productionNote']='New delivered video; human review required. AI review is recorded separately.' if j['kind']=='video' else 'Starting reference generated; exact-frame editorial review required before video.'
   f.write_json(f.MANIFEST,m)
  print(json.dumps({'groupComplete':group['id'],'kinds':[j['kind'] for j in candidates],'exercises':[j['exerciseId'] for j in candidates],'budget':f.budget(m,f.ledger())}),flush=True)
 print(json.dumps({'status':'group-ceiling-reached'}),flush=True)

if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit(f'Round stopped without retries: {type(e).__name__}: {e}')
