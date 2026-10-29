"""Render the original RepoPet launch gallery and shareable hero assets."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/repo-pet/scripts'))
from repopet import background,dragon,font,save_animation,MOODS,COLORS,LINES,render,demo_snapshot
from PIL import Image,ImageDraw


def hero(mood,frame):
    im=background((1200,650)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((42,34,232,69),radius=16,outline='#40566a',width=1)
    d.text((61,43),'AN AGENT SKILL',font=font(13,True),fill='#bad0d8')
    d.text((46,103),'Your repo',font=font(76,True),fill='#f0f5f5')
    d.text((46,191),'has feelings.',font=font(76,True),fill='#a7f1c1')
    d.text((49,302),'Meet Patch. Feed it green checks.',font=font(23),fill='#bdcfd8')
    d.text((49,340),'A tiny pixel dragon for your README.',font=font(20),fill='#8ea6b7')
    d.rounded_rectangle((49,405,443,455),radius=13,fill='#a7f1c1')
    d.text((70,421),'ONE SKILL. FIVE LITTLE MOODS.',font=font(17,True),fill='#173335')
    # Soft radar rings make the code-native pixel pet feel like a collectible.
    for rr in [150,180,212]:
        d.ellipse((899-rr,245-rr,899+rr,245+rr),outline='#293e50',width=1)
    d.ellipse((769,382,1057,408),fill='#09121d')
    pet=dragon(mood,frame,stage='baby').resize((384,384),Image.Resampling.NEAREST)
    im.paste(pet,(705,40),pet)
    accent=COLORS[mood]
    d.rounded_rectangle((778,412,1067,470),radius=17,fill='#1e2c3c',outline=accent,width=2)
    d.text((923,441),' '.join(LINES[mood]),anchor='mm',font=font(13,True),fill=accent)
    for i,m in enumerate(MOODS):
        x=49+i*225
        d.rounded_rectangle((x,518,x+209,601),radius=15,fill='#192838',
                            outline=COLORS[m] if m==mood else '#304356',width=2)
        mini=dragon(m,frame).resize((82,82),Image.Resampling.NEAREST)
        im.paste(mini,(x+1,515),mini)
        d.text((x+82,551),m.upper(),font=font(12,True),fill=COLORS[m])
        sub={'passing':'happy dance','failing':'tiny tantrum','running':'on a mission',
             'skipped':'nap time','unknown':'just vibes'}[m]
        d.text((x+82,574),sub,font=font(11),fill='#a2bac8')
    d.text((50,624),'Original sprites  /  Local rendering  /  No model or API key',font=font(13),fill='#8fa5b5')
    d.text((1150,624),'DEMO MOODS',font=font(12,True),anchor='ra',fill='#8fa5b5')
    return im


def main():
    out=ROOT/'examples';out.mkdir(exist_ok=True)
    for mood in MOODS:render(demo_snapshot(mood),out/'gallery'/mood)
    frames=[hero(m,i*2) for m in MOODS for i in range(12)]
    save_animation(frames,out/'repopet-hero.gif',duration=150)
    frames[0].save(out/'repopet-hero.png')
    # Show the actual evolution options, with cosmetic-stage labels.
    evolution=background((1080,340));d=ImageDraw.Draw(evolution)
    for i,stage in enumerate(['egg','baby','dragon']):
        snap=demo_snapshot('passing',stage=stage)
        pet=dragon('passing',0,stage=stage).resize((256,256),Image.Resampling.NEAREST)
        evolution.paste(pet,(55+i*350,5),pet)
        d.text((180+i*350,290),stage.upper(),font=font(22,True),anchor='mm',fill='#b3ebc8')
    d.text((540,325),'Automatic stages use reachable commit counts. Looks can also be selected manually.',
           font=font(13),anchor='mm',fill='#9eb5c1')
    evolution.save(out/'evolution.png')
    print({'hero_bytes':(out/'repopet-hero.gif').stat().st_size,'moods':len(MOODS)})


if __name__=='__main__':main()
