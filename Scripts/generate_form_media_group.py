#!/usr/bin/env python3
"""Run an explicit small group on isolated gflow profiles; settle only with live evidence.

This command never retries. Quotes are operator-observed UI evidence, not invented
prices. A failed/uncertain member keeps the group open for manual reconciliation.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

import form_media as f
from generate_form_media import ui_quote


def reference_files(job, records, round_id):
    if job['kind'] == 'image':
        if job.get('productionDisposition') != 'prompt-reviewed':
            raise ValueError('Review the exact image prompt before group submission.')
        return [f.repo_path(p) for p in job.get('referenceFiles', [])]
    if job.get('productionDisposition') not in {'awaiting-reference', 'prompt-reviewed', 'ready-to-animate'}:
        raise ValueError('Review the exact video prompt before group submission.')
    if job.get('videoMode') == 't2v':
        if job.get('productionDisposition') != 'prompt-reviewed' or not job.get('textOnlyReason') or job.get('referenceFiles') or job.get('referenceShot'):
            raise ValueError('Text-to-video requires an explicitly reviewed text-only job, without reference claims.')
        return []
    refs = [a for a in records['attempts'] if a['shot'] == job['referenceShot']
            and a['exerciseId'] == job['exerciseId'] and a['status'] == 'completed'
            and a.get('actualCredits') is not None]
    if not refs:
        raise ValueError('No settled starting reference.')
    a = refs[-1]
    path = f.repo_path(a['outputPath'])
    reviews = []
    for p in f.MEDIA.glob(f'{round_id}-*reviews.json'):
        reviews.extend(f.read_json(p).get('reviews', []))
    matching = sorted([r for r in reviews if r.get('outputPath') == f.relative(path)
                       and r.get('outputSha256') == f.sha256(path)
                       and r.get('reviewerType') == 'ai'], key=lambda r:r.get('reviewedAt',''))
    if not matching or matching[-1]['status'] != 'ready-to-animate':
        raise ValueError('Latest exact starting-frame review must be ready-to-animate.')
    expected = job.get('adoptedReferenceEvidence')
    resolved = [{'path': f.relative(path), 'sha256': f.sha256(path)}]
    if expected is not None and expected != resolved:
        raise ValueError('Starting reference changed after motion adoption; review and explicitly adopt its matching motion brief.')
    return [path]


def run(args):
    # Config is deliberately just explicit shot/quote pairs. Profile allocation
    # comes from the protected local inventory, never from prompt text.
    config = f.read_json(f.repo_path(args.config))
    (f.MEDIA/'generation-groups').mkdir(exist_ok=True)
    members = config['members']
    if not 1 <= len(members) <= 6 or len({x['shot'] for x in members}) != len(members):
        raise ValueError('Choose one to six distinct shots for this isolated group.')
    with f.locked():
        m=f.read_json(f.MANIFEST);records=f.ledger()
        if m.get('activeGenerationGroup') or any(f.unresolved(a) for a in records['attempts']):
            raise ValueError('Reconcile existing work before opening another group.')
        jobs={j['shot']:j for j in f.read_json(f.MEDIA/f"{m['activeRoundId']}-jobs.json")['jobs']}
        workers=m.get('generationWorkers', [])[:len(members)]
        if len(workers)!=len(members) or len({w['path'] for w in workers})!=len(workers):
            raise ValueError('Not enough separately provisioned gflow workers.')
        prepared=[]
        for member,worker in zip(members,workers):
            job=jobs[member['shot']]
            if job['roundId']!=m['activeRoundId'] or not Path(worker['path']).is_dir():
                raise ValueError('Wrong round or missing isolated profile.')
            prompt=f.repo_path(job['promptFile'])
            if f.sha256(prompt)!=job['promptSha256']:
                raise ValueError('Prompt changed after review.')
            if f.pilot_media_kind(job['model'])!=job['kind']:
                raise ValueError('Job model does not match its media kind.')
            quote_args=argparse.Namespace(exercise=job['exerciseId'],shot=job['shot'],kind=job['kind'],model=job['model'],video_mode=job.get('videoMode','i2v'),aspect=job['aspect'],duration=job['duration'])
            key=f.pilot_model_key(job['model'],job['duration'],'text-only' if job.get('videoMode')=='t2v' else 'start-only',job['aspect'])
            quote_path,_,quote=ui_quote(member['quoteFile'],quote_args,m['projectId'],key)
            refs=reference_files(job,records,m['activeRoundId'])
            for p in refs:
                if not p.is_relative_to((f.MEDIA/'assets').resolve()) or not p.is_file():
                    raise ValueError('Invalid local reference.')
            prior=[a for a in records['attempts'] if a['exerciseId']==job['exerciseId'] and a['shot']==job['shot']]
            if len([a for a in prior if f.counts_toward_shot_limit(a)])>=f.shot_attempt_limit(m,job['roundId'],job['shot']) or f.accepted_shot(m,records,job['exerciseId'],job['shot']):
                raise ValueError('Accepted output or attempt limit prevents generation.')
            prepared.append(dict(exerciseId=job['exerciseId'],shot=job['shot'],profile=worker['name'],promptSha256=job['promptSha256'],quoteFile=f.relative(quote_path),quoteSha256=f.sha256(quote_path),quoteCredits=quote['credits'],balance=quote['balance'],references=[{'path':f.relative(p),'sha256':f.sha256(p)} for p in refs]))
        balances={p['balance'] for p in prepared};total=sum(p['quoteCredits'] for p in prepared)
        available=f.budget(m,records)
        if len(balances)!=1 or total>min(next(iter(balances)),available['remaining']):
            raise ValueError('Group quotes must share the same live balance and fit both budgets.')
        group=dict(id='group_'+uuid.uuid4().hex[:16],status='open',roundId=m['activeRoundId'],createdAt=f.now(),balanceBefore=next(iter(balances)),quotedCredits=total,members=prepared,settlementMethod='Aggregate same-account balance; per-member allocations use frozen quotes only after all outputs succeed and total delta matches exactly.')
        if available['periodId'] is not None:
            group['budgetPeriodId']=available['periodId']
        m['activeGenerationGroup']=group;f.write_json(f.MANIFEST,m)
        f.write_json(f.MEDIA/'generation-groups'/f"{group['id']}.json",group)
    processes=[]
    print(json.dumps({'groupId':group['id'],'members':len(prepared),'quoteCredits':total}),flush=True)
    for member in prepared:
        j=jobs[member['shot']]
        command=[sys.executable,str(f.ROOT/'Scripts/generate_form_media.py'),'--exercise',j['exerciseId'],'--shot',j['shot'],'--kind',j['kind'],'--model',j['model'],'--aspect',j['aspect'],'--ui-quote-file',member['quoteFile'],'--generation-group',group['id'],'--profile',member['profile']]
        if j['duration']:command+=['--duration',str(j['duration'])]
        if j['kind']=='video':command+=['--video-mode',j.get('videoMode','i2v')]
        for ref in member['references']:command+=['--reference',ref['path']]
        # Each subprocess owns a different profile and persistent browser context.
        processes.append((member['shot'],subprocess.Popen(command,cwd=f.ROOT)))
    results={shot:p.wait() for shot,p in processes}
    print(json.dumps({'groupId':group['id'],'exitCodes':results,'status':'awaiting-aggregate-reconciliation'}),flush=True)
    return 0 if all(code==0 for code in results.values()) else 1


def settle(args):
    evidence_path=f.repo_path(args.evidence)
    if not evidence_path.is_relative_to((f.MEDIA/'ui-quotes').resolve()):
        raise ValueError('Evidence must live in ui-quotes.')
    evidence=f.read_json(evidence_path)
    if evidence.get('sourceType')!='flow-ui-observation' or evidence.get('groupId')!=args.group:
        raise ValueError('Evidence does not identify this group.')
    observed=datetime.fromisoformat(evidence['observedAt'].replace('Z','+00:00'))
    if observed.tzinfo is None or not -5 <= (datetime.now(timezone.utc)-observed).total_seconds() <= 300:
        raise ValueError('Observe the post-generation balance freshly before settlement.')
    after=evidence['balance']
    if type(after) is not int or after<0 or not evidence.get('visibleBalanceText'):
        raise ValueError('Missing actual visible balance evidence.')
    with f.locked():
        m=f.read_json(f.MANIFEST);records=f.ledger();group=m.get('activeGenerationGroup')
        if not group or group['id']!=args.group or evidence.get('projectId')!=m['projectId']:
            raise ValueError('Not the active group/project.')
        attempts=[a for a in records['attempts'] if a.get('generationGroupId')==args.group]
        if (group.get('budgetPeriodId')!=m.get('currentBudgetPeriodId')
                or any(a.get('budgetPeriodId')!=group.get('budgetPeriodId') for a in attempts)):
            raise ValueError('Group and attempt budget periods differ; reconcile the period boundary.')
        if len(attempts)!=len(group['members']) or any(a.get('actualCredits') is not None for a in attempts):
            raise ValueError('Every group member must still be unsettled.')
        terminal_failures={}
        for a in attempts:
            if a['status']=='submitted' and a.get('outputPath'):
                continue
            if not args.allow_terminal_failures or a['status']!='uncertain' or a.get('outputPath'):
                raise ValueError('Reconcile the unfinished member before settling this group.')
            response_path=f.ROOT/'reports/form-media'/a['id']/'stdout.json'
            response=f.read_json(response_path)
            if (response.get('status')!='fail' or response.get('succeeded') is not False
                    or response.get('generation_status')!='MEDIA_GENERATION_STATUS_FAILED'
                    or not a.get('mediaId') or response.get('media_id')!=a['mediaId']):
                raise ValueError('Missing an exact provider-terminal failure response; retain the reservation.')
            terminal_failures[a['id']]={'path':f.relative(response_path),'sha256':f.sha256(response_path)}
        if any(f.unresolved(a) and a.get('generationGroupId')!=args.group for a in records['attempts']):
            raise ValueError('An unrelated unsettled attempt prevents aggregate attribution.')
        quoted_total=sum(a['quoteCredits'] for a in attempts)
        total=sum(a['quoteCredits'] for a in attempts if a['id'] not in terminal_failures)
        if quoted_total!=group['quotedCredits'] or group['balanceBefore']-after!=total:
            raise ValueError('Aggregate debit must equal successful frozen quotes with zero debit for evidenced terminal failures. Retain reservations if it differs.')
        for a in attempts:
            member=next(p for p in group['members'] if p['shot']==a['shot'])
            if a['quoteCredits']!=member['quoteCredits'] or a['balanceBefore']!=group['balanceBefore']:
                raise ValueError('Member quote changed.')
            if a['id'] in terminal_failures:
                continue
            path=f.repo_path(a['outputPath']);measured=next(x for x in a['localFiles'] if x['path']==a['outputPath'])
            if not path.is_file() or f.sha256(path)!=measured['sha256'] or not a.get('mediaId'):
                raise ValueError('Missing exact successful output/provider identity.')
        for a in attempts:
            failed=a['id'] in terminal_failures
            a.update(status='failed' if failed else 'completed',actualCredits=0 if failed else a['quoteCredits'],reservedCredits=0,balanceAfter=after,settledAt=f.now(),updatedAt=f.now(),settlementEvidence=f"Aggregate group {args.group}: balance {group['balanceBefore']} → {after}; debit {total} equals the successful outputs' frozen quotes, with {len(terminal_failures)} exact terminal failures charged zero in this reconciliation. Allocation uses frozen quotes and aggregate balance, not independently observed per-job billing. Evidence {f.relative(evidence_path)} sha256:{f.sha256(evidence_path)}",settlementMethod='aggregate-quote-allocation')
            if failed:
                a['terminalFailureEvidence']=terminal_failures[a['id']]
        group.update(status='completed-with-failures' if terminal_failures else 'completed',settledAt=f.now(),balanceAfter=after,actualCredits=total,evidenceFile=f.relative(evidence_path),evidenceSha256=f.sha256(evidence_path),terminalFailureIds=list(terminal_failures))
        f.write_json(f.LEDGER,records)
        f.write_json(f.MEDIA/'generation-groups'/f"{group['id']}.json",group)
        m.pop('activeGenerationGroup');f.write_json(f.MANIFEST,m)
        print(json.dumps({'groupId':args.group,'budget':f.budget(m,records),'attemptIds':[a['id'] for a in attempts]}))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    r=sub.add_parser('run');r.add_argument('--config',required=True)
    s=sub.add_parser('settle');s.add_argument('--group',required=True);s.add_argument('--evidence',required=True);s.add_argument('--allow-terminal-failures',action='store_true',help='Explicitly reconcile exact provider-terminal failures only when the aggregate balance proves no charge for them.')
    args=p.parse_args()
    try:return run(args) if args.command=='run' else settle(args)
    except Exception as error:
        print(f'Group stopped: {error}. No automatic retry or credit release.',file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
