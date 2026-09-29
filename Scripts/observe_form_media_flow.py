#!/usr/bin/env python3
"""Observe live Flow UI through the installed gflow browser client; never submit."""
import argparse,asyncio,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
import form_media as media

class ObservationRefused(ValueError):
 def __init__(self,message,evidence):
  super().__init__(message)
  self.evidence=dict(evidence,sourceType='flow-ui-observation-diagnostic',quoteUsable=False,failure=message)

async def observe(kind, *, aspect='9:16', duration=8, profile=None, model=None):
 from gflow_cli.api.client import FlowApiClient
 from gflow_cli.api.transports.migrated_composer import MigratedComposer
 from gflow_cli.api.image import Aspect as ImageAspect,GenerateImageRequest,Model
 from gflow_cli.api.video import Aspect as VideoAspect,GenerateVideoRequest,Mode,VideoModel
 if kind in {'video','text-video'} and aspect not in {'9:16','16:9'}:
  raise ValueError('Video observations require portrait 9:16 or landscape 16:9.')
 if duration not in {6,8,10}:
  raise ValueError('Video observation duration must be 6, 8 or 10 seconds.')
 effective_model=model or ('nano-pro' if kind=='image' else 'omni-flash')
 if kind:
  expected_kind='image' if kind=='image' else 'video'
  if media.pilot_media_kind(effective_model)!=expected_kind:
   raise ValueError('Observation model does not match the selected media kind.')
  frame_mode='text-only' if kind=='text-video' else 'start-only'
  model_key=media.pilot_model_key(effective_model,None if kind=='image' else duration,frame_mode,aspect)
 root=Path(__file__).resolve().parents[1]
 m=json.loads((root/'form-media/manifest.json').read_text())
 profile_name=profile or 'shouburu'
 profile_path=Path.home()/'Library/Application Support/gflow-cli/profile_shouburu'
 if profile is not None:
  workers=[w for w in m.get('generationWorkers',[]) if w.get('name')==profile]
  if len(workers)!=1:raise ValueError('Choose exactly one worker name from manifest generationWorkers.')
  profile_path=Path(workers[0]['path']).resolve()
 if not profile_path.is_dir():raise ValueError('The selected observer profile does not exist.')
 async with FlowApiClient(profile_path,transport='ui_automation') as client:
  class ObserverComposer(MigratedComposer):
   captured = None
   async def _close_pane(self,page,*,strict=True):
    if strict:
     pane=page.locator('.cdk-overlay-pane').filter(has=page.locator('[role="radiogroup"]')).last
     if await pane.count() and await pane.is_visible():
      self.captured=(await pane.inner_text(),await pane.locator('[aria-checked="true"]').all_text_contents())
    await super()._close_pane(page,strict=strict)
  page=client._page;composer=ObserverComposer();await composer.ensure_editor(page,m['projectId'])
  result=dict(sourceType='flow-ui-observation',observer='gflow CLI browser DOM observer',source='Live Flow composer and account-panel visible DOM; no generation submitted',projectId=m['projectId'],profile=profile_name)
  resolution_failure=None
  if kind:
   if kind=='image':await composer.apply_image_settings(page,GenerateImageRequest(prompt='Observation only; never submitted',model=Model.GEM_PIX_2,aspect=ImageAspect.from_cli(aspect),count=1))
   else:await composer.apply_video_settings(page,GenerateVideoRequest(prompt='Observation only; never submitted',mode=Mode.T2V if kind=='text-video' else Mode.I2V,model=VideoModel.from_cli(effective_model),aspect=VideoAspect.from_cli(aspect),duration=duration,count=1,start_image=None if kind=='text-video' else Path('unused-observation-only.jpg')))
   if not composer.captured:raise ValueError('No settings observed')
   visible,selected=composer.captured
   if media.PILOT_MODEL_LABELS[effective_model] not in visible:
    raise ObservationRefused('Selected model label is absent from the captured settings; do not infer its quote.',dict(result,settingsText=visible,selectedSettings=selected,requestedModel=effective_model,expectedFamily=media.PILOT_MODEL_LABELS[effective_model]))
   matches=re.findall(r'Generating will use\s*([\d,]+)\s*credits',visible,re.I)
   if len(matches)!=1:raise ValueError('No unambiguous live UI price; do not generate')
   result.update(kind='video' if kind=='text-video' else kind,videoMode='t2v' if kind=='text-video' else 'i2v',aspect=aspect,count=1,durationSeconds=None if kind=='image' else duration,model=effective_model,modelKey=model_key,family=media.PILOT_MODEL_LABELS[effective_model],credits=int(matches[0].replace(',','')),visiblePriceText='Generating will use '+matches[0]+' credits',settingsText=visible,selectedSettings=selected)
   if effective_model in {'veo-fast','veo-quality'}:result['modelKeySource']='flow-ui-settings-identity'
   result['resolutions']=[] if kind=='image' else ['720p']
   if effective_model in {'veo-fast','veo-quality'}:
    labels=list(dict.fromkeys(re.findall(media.RESOLUTION_LABEL_PATTERN,visible,re.I)))
    result.update(resolutions=[],resolutionPolicy='provider-default',visibleResolutionLabels=labels,resolutionControlObserved=bool(labels),resolutionObservation='No resolution label or control is visible in the captured composer settings; provider default is requested and downloaded dimensions must be measured.' if not labels else 'Resolution controls are visible; provider-default policy cannot be assumed.')
    try:media.require_veo_default_resolution(result,effective_model,duration,aspect,result['videoMode'])
    except ValueError as error:resolution_failure=str(error)
   elif kind in {'video','text-video'} and not any('720p' in x for x in selected):
    labels=list(dict.fromkeys(re.findall(media.RESOLUTION_LABEL_PATTERN,visible,re.I)))
    result.update(resolutions=[],requestedSettingsIdentity=result.pop('modelKey'),visibleResolutionLabels=labels,resolutionObservation='No resolution label is visible in the captured composer settings.' if not labels else 'Resolution labels are visible, but 720p is not selected.')
    resolution_failure='720p is not selected; captured settings do not establish the output resolution. No usable quote was issued.'
  await page.get_by_role('button',name='Account details',exact=True).click()
  label=await page.get_by_role('link',name=re.compile(r'^[\d,]+ Google Flow credits$')).inner_text()
  match=re.search(r'([\d,]+)\s+Google Flow credits',label)
  if not match:raise ValueError('Unrecognized visible account balance')
  result.update(balance=int(match[1].replace(',','')),visibleBalanceText=label,observedAt=datetime.now(timezone.utc).isoformat())
  if resolution_failure:raise ObservationRefused(resolution_failure,result)
  return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=['image','video','text-video']);p.add_argument('--model',choices=list(media.PILOT_MODEL_LABELS),help='Exact picker model; defaults to nano-pro for image, omni-flash for video.');p.add_argument('--aspect',choices=['9:16','16:9','4:3','1:1'],default='9:16');p.add_argument('--duration',type=int,choices=[6,8,10],default=8,help='Exact video duration; Veo is limited to 6 or 8 seconds here.');p.add_argument('--profile',help='A configured generationWorkers name; omitted uses the normal shouburu observer profile.');p.add_argument('--output',required=True);a=p.parse_args()
 try:result=asyncio.run(observe(a.kind,aspect=a.aspect,duration=a.duration,profile=a.profile,model=a.model))
 except ObservationRefused as error:
  out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(error.evidence,indent=2)+'\n')
  raise SystemExit(str(error)+' Diagnostic: '+str(out))
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
