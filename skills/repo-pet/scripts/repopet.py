#!/usr/bin/env python3
"""Local README pets from real JUnit/CI evidence. Only Pillow is required."""
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

MOODS = ('passing', 'failing', 'running', 'skipped', 'unknown')
COLORS = {
    'passing': '#99efad', 'failing': '#ff9b93', 'running': '#ffd489',
    'skipped': '#c8b5ff', 'unknown': '#a9c2d9',
}
LINES = {
    'passing': ('ALL GREEN.', 'SNACK TIME.'),
    'failing': ('BUILD BROKEN.', 'STILL CUTE.'),
    'running': ('HOLD ON.', 'DRAGON AT WORK.'),
    'skipped': ('ALL SKIPPED.', 'NAP TIME.'),
    'unknown': ('NO TEST SIGNAL.', 'JUST VIBES.'),
}
THEMES = {'mint': ('#91dfb6', '#d9f7cf'), 'lilac': ('#bfacfa', '#f2dbff'),
          'peach': ('#f2b29d', '#ffe5bf')}
START, END = '<!-- repopet:start -->', '<!-- repopet:end -->'


def font(size, bold=False):
    names = (['DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/segoeuib.ttf'] if bold else
             ['DejaVuSans.ttf', 'C:/Windows/Fonts/segoeui.ttf'])
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def junit_evidence(path):
    try:
        payload = Path(path).read_bytes()
        if len(payload) > 5_000_000 or re.search(br'<!\s*(?:DOCTYPE|ENTITY)', payload, re.I):
            raise ValueError('unsupported XML')
        root = ET.fromstring(payload)
        if root.tag.split('}')[-1] not in {'testsuites', 'testsuite'}:
            raise ValueError('not JUnit')
        cases = [e for e in root.iter() if e.tag.split('}')[-1] == 'testcase']
        if not cases:
            return {'mood': 'unknown', 'source': 'junit', 'reason': 'No individual test cases recorded',
                    'tests': 0, 'passed': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
        counts = dict(tests=len(cases), failures=0, errors=0, skipped=0)
        for case in cases:
            tags = {e.tag.split('}')[-1] for e in case}
            flags = [tag in tags for tag in ['failure', 'error', 'skipped']]
            if sum(flags)>1:
                raise ValueError('conflicting test outcomes')
            for tag,key in [('failure','failures'),('error','errors'),('skipped','skipped')]:
                counts[key] += int(tag in tags)
        counts['passed'] = counts['tests']-counts['failures']-counts['errors']-counts['skipped']
        mood = ('failing' if counts['failures']+counts['errors'] else
                'skipped' if counts['skipped']==counts['tests'] else 'passing')
        return {'mood':mood,'source':'junit','reason':'Individual recorded test cases',**counts}
    except (OSError,ValueError,ET.ParseError):
        # A typo, missing report or unreadable XML must never paint a green badge.
        return {'mood':'unknown','source':'junit','reason':'Report missing or invalid','tests':None}


def checks_evidence(path):
    try:
        p=Path(path)
        if p.stat().st_size>5_000_000:
            raise ValueError('oversized check data')
        value=json.loads(p.read_text(encoding='utf-8'))
        value=value.get('workflow_run',value)
        status,conclusion=value.get('status'),value.get('conclusion')
        if status in {'queued','in_progress','waiting','pending','requested'}:
            mood='running'
        elif status=='completed' and conclusion=='success':
            mood='passing'
        elif status=='completed' and conclusion in {'failure','timed_out','action_required','startup_failure'}:
            mood='failing'
        elif status=='completed' and conclusion=='skipped':
            mood='skipped'
        else:
            mood='unknown'
        return {'mood':mood,'source':'ci','reason':'Workflow status; test count not supplied','tests':None}
    except (OSError,ValueError,AttributeError,TypeError):
        return {'mood':'unknown','source':'ci','reason':'Workflow evidence missing or invalid','tests':None}


def git_count(repo):
    try:
        r=subprocess.run(['git','-C',str(Path(repo).resolve()),'rev-list','--count','HEAD'],
                         capture_output=True,text=True,timeout=8,check=True)
        return int(r.stdout.strip())
    except (OSError,ValueError,subprocess.SubprocessError):
        return None


def make_snapshot(repo, *, junit=None, checks=None, name='Patch', theme='mint', stage='auto'):
    if junit and checks:
        raise ValueError('Choose JUnit or workflow evidence, not both')
    if not name.strip() or len(name)>24 or any(ord(c)<32 for c in name):
        raise ValueError('Pet name must be 1–24 printable characters')
    if theme not in THEMES or stage not in {'auto','egg','baby','dragon'}:
        raise ValueError('Unknown palette or evolution stage')
    if junit:
        evidence=junit_evidence(junit)
    elif checks:
        evidence=checks_evidence(checks)
    else:
        candidates=[Path(repo)/p for p in ['junit.xml','test-results.xml','reports/junit.xml']]
        found=next((p for p in candidates if p.is_file()),None)
        evidence=junit_evidence(found) if found else {
            'mood':'unknown','source':'none','reason':'No test report supplied','tests':None}
    commits=git_count(repo)
    evolved = ('egg' if commits is not None and commits<3 else
               'dragon' if commits is not None and commits>=25 else 'baby') if stage=='auto' else stage
    return {'schema_version':1,'name':name,'theme':theme,'stage':evolved,
            'stage_source':'commit_count' if stage=='auto' and commits is not None else 'cosmetic',
            'commits':commits,'evidence':evidence,'demo':False}


def dragon(mood, frame, *, theme='mint', stage='baby'):
    """Original pixel geometry; feet, tail, wings, eyes and effects animate separately."""
    im=Image.new('RGBA',(64,64)); d=ImageDraw.Draw(im)
    ink='#172d38'; body,belly=THEMES[theme]; shade='#65ac95' if theme=='mint' else '#947bb5'
    cycle=frame%24; bob=int(round(math.sin(cycle*math.pi/12)))
    wag=int(round(2*math.sin(cycle*math.pi/6)))
    y=bob
    if stage=='egg':
        d.ellipse((16,15+y,43,49+y),fill=ink)
        d.ellipse((18,17+y,41,47+y),fill=belly)
        for xx,yy in [(24,21),(33,34),(21,39)]:d.rectangle((xx,yy+y,xx+4,yy+4+y),fill=body)
        d.line([(18,31+y),(23,29+y),(28,33+y),(33,30+y),(41,32+y)],fill=ink,width=2)
        for xx in [25,34]:d.rectangle((xx,26+y,xx+2,29+y),fill=ink)
        d.rectangle((27,38+y,33,39+y),fill=ink)
    else:
        # Tail and wings sit behind a shared head/body anchor.
        d.polygon([(21,38+y),(12,44+y),(6,38+wag+y),(9,32+wag+y),(12,38+wag+y),(19,34+y)],fill=ink)
        d.polygon([(20,39+y),(12,42+y),(8,37+wag+y),(10,35+wag+y),(13,39+y),(19,36+y)],fill=body)
        wing=2 if cycle<12 else -1
        if stage=='dragon':
            d.polygon([(20,32+y),(6,18+wing+y),(8,37+y),(18,40+y)],fill=ink)
            d.polygon([(18,32+y),(9,22+wing+y),(11,35+y),(18,38+y)],fill='#f4c6a0')
            d.polygon([(36,31+y),(51,18-wing+y),(49,37+y),(37,40+y)],fill=ink)
            d.polygon([(38,31+y),(48,23-wing+y),(46,35+y),(38,38+y)],fill='#f4c6a0')
        else:
            d.polygon([(20,29+y),(13,25+wing+y),(12,36+y),(20,38+y)],fill=ink)
            d.polygon([(18,30+y),(15,29+wing+y),(15,35+y),(18,36+y)],fill='#e8b898')
        d.rounded_rectangle((19,29+y,38,48+y),radius=5,fill=ink)
        d.rounded_rectangle((21,31+y,36,46+y),radius=4,fill=body)
        d.rounded_rectangle((27,34+y,35,45+y),radius=3,fill=belly)
        d.rectangle((21,45+y+(cycle//6%2),27,49+y+(cycle//6%2)),fill=ink)
        d.rectangle((32,45+y+((cycle//6+1)%2),39,49+y+((cycle//6+1)%2)),fill=ink)
        d.rectangle((22,45+y+(cycle//6%2),26,47+y+(cycle//6%2)),fill=body)
        d.rectangle((33,45+y+((cycle//6+1)%2),37,47+y+((cycle//6+1)%2)),fill=body)
        d.polygon([(22,17+y),(21,9+y),(25,11+y),(28,18+y)],fill=ink)
        d.polygon([(23,15+y),(23,11+y),(25,13+y),(26,17+y)],fill='#ffd48d')
        d.polygon([(32,16+y),(35,8+y),(38,10+y),(37,18+y)],fill=ink)
        d.polygon([(34,15+y),(36,11+y),(36,16+y)],fill='#ffd48d')
        d.rounded_rectangle((19,14+y,40,35+y),radius=6,fill=ink)
        d.rounded_rectangle((21,16+y,38,33+y),radius=5,fill=body)
        d.rounded_rectangle((33,24+y,47,33+y),radius=3,fill=ink)
        d.rectangle((34,25+y,45,31+y),fill=body)
        d.rectangle((23,30+y,32,33+y),fill=shade)
        sleepy=mood=='skipped' or cycle in (20,21)
        for xx in [25,34]:
            if sleepy:
                d.line((xx,23+y,xx+4,23+y),fill=ink,width=2)
            else:
                d.rectangle((xx,21+y,xx+3,25+y),fill=ink)
                d.point((xx,21+y),fill='#fff7df')
        if mood=='failing':
            d.line((24,18+y,29,20+y),fill=ink,width=2)
            d.line((34,20+y,39,18+y),fill=ink,width=2)
            d.rectangle((39,30+y,43,30+y),fill=ink)
            d.polygon([(44,17+y),(42,21+y),(43,23+y),(46,22+y)],fill='#7ad4fb')
        elif mood=='passing':
            d.line([(39,29+y),(41,30+y),(44,28+y)],fill=ink,width=1)
            d.rectangle((23,27+y,26,28+y),fill='#f29fa7')
        else:
            d.rectangle((40,29+y,43,29+y),fill=ink)
    # Small drifting effects give each mood a different silhouette in motion.
    if mood=='passing':
        for x0,y0,k in [(10,17,0),(50,35,8),(48,12,16)]:
            n=(cycle+k)%24; yy=y0-(n//6)
            if n<16:
                d.line((x0-2,yy,x0+2,yy),fill='#ffe6a6')
                d.line((x0,yy-2,x0,yy+2),fill='#ffe6a6')
    elif mood=='failing':
        xx=49+(cycle//6%2)
        d.polygon([(xx,30),(xx+5,25),(xx+3,29),(xx+7,31),(xx+3,35)],fill='#ff9b93')
    elif mood=='running':
        for i in range(3):
            if (cycle//4+i)%3!=0:d.rectangle((10+i*6,55,12+i*6,56),fill='#ffd489')
    elif mood=='unknown':
        d.text((46,7-(cycle//8%2)),'?',font=font(12,True),fill='#a9c2d9')
    elif mood=='skipped':
        d.text((43,11-cycle//8),'z',font=font(10,True),fill='#c8b5ff')
    return im


def background(size):
    im=Image.new('RGB',size,'#101b29'); d=ImageDraw.Draw(im)
    for yy in range(0,size[1],28):
        for xx in range(0,size[0],28):d.point((xx,yy),fill='#263447')
    return im


def evidence_line(e):
    if e.get('tests') is not None:
        return (f"{e['tests']} total / {e.get('passed',0)} pass / "
                f"{e.get('failures',0)+e.get('errors',0)} fail / {e.get('skipped',0)} skip")
    if e['source']=='demo':
        return 'Preview mood / synthetic example'
    if e['source']=='ci':
        return 'CI evidence / test count not supplied'
    return 'No test evidence / status unknown'


def card(snapshot, frame=0):
    e=snapshot['evidence']; mood=e['mood']; accent=COLORS[mood]
    im=background((600,340));d=ImageDraw.Draw(im)
    d.rounded_rectangle((10,10,589,329),radius=24,outline='#344559',width=2)
    d.text((30,26),'REPOPET',font=font(18,True),fill='#dde8ef')
    d.rounded_rectangle((444,24,568,55),radius=14,fill=accent)
    d.text((506,39),mood.upper(),font=font(12,True),anchor='mm',fill='#152b32')
    d.ellipse((43,239,243,259),fill='#0a131f')
    pet=dragon(mood,frame,theme=snapshot['theme'],stage=snapshot['stage']).resize((256,256),Image.Resampling.NEAREST)
    im.paste(pet,(13,26),pet)
    name_font=font(34,True)
    for size in range(34,11,-1):
        name_font=font(size,True)
        if d.textbbox((0,0),snapshot['name'],font=name_font)[2]<=280:
            break
    d.text((280,93),snapshot['name'],font=name_font,fill='#f0f5f5')
    for i,line in enumerate(LINES[mood]):d.text((282,147+25*i),line,font=font(18,True),fill=accent)
    count=snapshot.get('commits')
    d.text((282,219),f"{snapshot['stage'].upper()}  /  "+(f'{count} commits' if count is not None else 'git optional'),
           font=font(13),fill='#a5b9c7')
    d.line((30,274,568,274),fill='#344559')
    d.text((30,290),evidence_line(e),font=font(14),fill='#b9cbd5')
    if snapshot.get('demo'):d.text((568,310),'DEMO DATA',font=font(10,True),anchor='ra',fill='#93a7b7')
    return im


def save_animation(frames,path, *, duration=90):
    # Shared palette avoids per-frame color flicker in GIF readers.
    sample=Image.new('RGB',(frames[0].width*3,frames[0].height))
    for i,n in enumerate([0,len(frames)//2,len(frames)-1]):sample.paste(frames[n],(i*frames[0].width,0))
    palette=sample.quantize(colors=192)
    converted=[f.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    converted[0].save(path,format='GIF',save_all=True,append_images=converted[1:],duration=duration,
                      loop=0,disposal=2,optimize=False)


def render(snapshot,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    frames=[card(snapshot,i) for i in range(24)]
    # Only known generated filenames are replaced, never user reports or directories.
    with tempfile.TemporaryDirectory(prefix='repopet-',dir=out) as temporary:
        temp=Path(temporary)
        frames[0].save(temp/'pet.png')
        save_animation(frames,temp/'pet.gif')
        (temp/'status.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        for name in ['pet.png','pet.gif','status.json']:
            (out/name).write_bytes((temp/name).read_bytes())
    return out/'pet.gif'


def update_readme(readme,asset, *, name):
    readme=Path(readme)
    value=readme.read_text(encoding='utf-8') if readme.exists() else ''
    if value.count(START)!=value.count(END) or value.count(START)>1:
        raise ValueError('Ambiguous RepoPet markers; README left unchanged')
    import os
    relative=Path(os.path.relpath(Path(asset).resolve(),readme.resolve().parent)).as_posix()
    # Escape authored names; URL spaces/parentheses are percent-encoded for Markdown.
    from urllib.parse import quote
    label=html.escape(name).replace('[','\\[').replace(']','\\]')
    block=f'{START}\n![{label} the RepoPet]({quote(relative,safe="/._-")})\n{END}'
    if START in value:
        a,b=value.index(START),value.index(END)
        if b<a:
            raise ValueError('Reversed RepoPet markers; README left unchanged')
        value=value[:a]+block+value[b+len(END):]
    else:
        value=value.rstrip()+'\n\n'+block+'\n'
    readme.parent.mkdir(parents=True,exist_ok=True)
    readme.write_text(value,encoding='utf-8')


def demo_snapshot(mood, *, stage='baby',theme='mint'):
    if mood not in MOODS:raise ValueError('Unknown demo mood')
    counts={'passing':(12,12,0,0),'failing':(12,9,2,1),'skipped':(12,0,0,12)}
    e={'mood':mood,'source':'demo','reason':'Explicit synthetic example','tests':None}
    if mood in counts:
        total,passed,failed,skipped=counts[mood]
        e.update(tests=total,passed=passed,failures=failed,errors=0,skipped=skipped)
    return {'schema_version':1,'name':'Patch','stage':stage,'theme':theme,'stage_source':'cosmetic',
            'commits':None,'evidence':e,'demo':True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    real=sub.add_parser('render',help='use local Git + test/CI evidence')
    real.add_argument('--repo',type=Path,default=Path.cwd())
    real.add_argument('--junit',type=Path)
    real.add_argument('--checks',type=Path)
    real.add_argument('--name',default='Patch')
    real.add_argument('--theme',choices=THEMES,default='mint')
    real.add_argument('--stage',choices=['auto','egg','baby','dragon'],default='auto')
    real.add_argument('--out',type=Path,default=Path('assets/repopet'))
    real.add_argument('--readme',type=Path,help='update only the owned RepoPet marker block')
    demo=sub.add_parser('demo',help='render explicitly labeled sample moods')
    demo.add_argument('--out',type=Path,default=Path('repopet-demo'))
    args=p.parse_args()
    if args.command=='demo':
        for mood in MOODS:render(demo_snapshot(mood),args.out/mood)
        print(json.dumps({'demo':True,'moods':list(MOODS),'output':'five GIF/PNG pairs'}))
    else:
        try:
            snapshot=make_snapshot(args.repo,junit=args.junit,checks=args.checks,
                                   name=args.name,theme=args.theme,stage=args.stage)
            asset=render(snapshot,args.out)
            if args.readme:update_readme(args.readme,asset,name=args.name)
        except ValueError as error:
            p.error(str(error))
        print(json.dumps({'mood':snapshot['evidence']['mood'],'stage':snapshot['stage'],
                          'evidence':snapshot['evidence']['source'],'files':['pet.gif','pet.png','status.json']}))


if __name__=='__main__':
    main()
