"""Original accessible SVG artwork, using only local geometry and catalog metadata."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]


def save(name, title, desc, body, width=960, height=460):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><defs><linearGradient id="sea" x2="1" y2="1"><stop stop-color="#13575a"/><stop offset="1" stop-color="#0b3541"/></linearGradient><linearGradient id="paper" x2="1" y2="1"><stop stop-color="#f4f5ea"/><stop offset="1" stop-color="#dfece3"/></linearGradient><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#217a6d"/></marker></defs><g font-family="system-ui, sans-serif">{body}</g></svg>'''
    (ROOT / 'assets' / name).write_text(svg+'\n',encoding='utf-8')


def main():
    (ROOT/'assets').mkdir(exist_ok=True)
    save('atlas-mark.svg','Learning Atlas mark','Original globe and open notebook symbol.', '<rect width="64" height="64" rx="16" fill="#116c61"/><circle cx="32" cy="28" r="17" fill="none" stroke="#f5f4ed" stroke-width="2"/><ellipse cx="32" cy="28" rx="8" ry="17" fill="none" stroke="#f5f4ed" stroke-width="1.5"/><path d="M16 23H48M16 33H48M12 44L32 49L52 44V51L32 57L12 51Z" fill="#f3bd5c"/>',64,64)
    body='''<rect x="20" y="20" width="700" height="590" rx="36" fill="url(#paper)"/><path d="M60 500C150 380 210 580 360 480S590 330 680 440M45 150C190 65 230 180 390 120S610 60 700 120" fill="none" stroke="#c0d8cb" stroke-width="1.5"/><circle cx="381" cy="300" r="203" fill="none" stroke="#c0d8cb" stroke-dasharray="3 8"/><circle cx="381" cy="300" r="177" fill="url(#sea)"/><ellipse cx="381" cy="300" rx="82" ry="177" fill="none" stroke="#568780"/><ellipse cx="381" cy="300" rx="142" ry="177" fill="none" stroke="#568780"/><ellipse cx="381" cy="300" rx="177" ry="68" fill="none" stroke="#568780"/><ellipse cx="381" cy="300" rx="177" ry="127" fill="none" stroke="#568780"/><path d="M204 300H558M381 123V477" stroke="#568780"/><path d="M280 181L319 160L353 181L340 213L374 240L361 283L332 300L340 337L315 366L297 323L281 290L249 279L233 249L253 219ZM423 181L475 188L499 219L480 247L506 268L496 304L462 320L447 351L432 329L413 298L417 262L396 243L411 214ZM471 366L500 357L517 378L504 400L474 395Z" fill="#92b698" stroke="#afd0ad" stroke-width="2" opacity=".85"/><path d="M170 220L310 291L535 425M310 291L553 186" stroke="#f3bd5c" stroke-dasharray="5 7" stroke-width="2" fill="none"/><g fill="#f3bd5c"><circle cx="310" cy="291" r="8"/><circle cx="170" cy="220" r="5"/><circle cx="553" cy="186" r="5"/><circle cx="535" cy="425" r="5"/></g>
<g transform="translate(55 76)"><rect width="238" height="152" rx="13" fill="#fffefa" stroke="#b7cbbd"/><path d="M0 32H238" stroke="#d5dfd4"/><circle cx="17" cy="16" r="4" fill="#d9a249"/><circle cx="31" cy="16" r="4" fill="#91b49a"/><circle cx="45" cy="16" r="4" fill="#91b49a"/><text x="22" y="59" font-size="11" fill="#116c61" letter-spacing="1.5">01 / ASK A QUESTION</text><path d="M22 80H174M22 94H127M22 108H158" stroke="#aac6b6" stroke-width="5" stroke-linecap="round"/><path d="M22 134L52 119L82 126L112 108L142 115L181 89" stroke="#14786b" stroke-width="3" fill="none"/></g>
<g transform="translate(477 155)"><rect width="191" height="157" rx="13" fill="#fffefa" stroke="#b7cbbd"/><text x="19" y="29" font-size="11" fill="#116c61" letter-spacing="1.5">02 / LAYER EVIDENCE</text><path d="M24 100L95 65L166 100L95 136Z" fill="#bfd6bd" stroke="#217a6d"/><path d="M24 83L95 48L166 83L95 119Z" fill="#dce7c5" stroke="#217a6d"/><path d="M24 67L95 32L166 67L95 103Z" fill="#f6d28d" stroke="#217a6d"/><path d="M95 32V103M59 50L130 85M130 50L59 85" stroke="#9b985a"/></g>
<g transform="translate(396 435)"><rect width="279" height="126" rx="13" fill="#fffefa" stroke="#b7cbbd"/><text x="20" y="28" font-size="11" fill="#116c61" letter-spacing="1.5">03 / LEARN TOGETHER</text><g fill="#217a6d"><circle cx="47" cy="62" r="10"/><circle cx="92" cy="62" r="10"/><circle cx="137" cy="62" r="10"/></g><path d="M30 101Q47 69 64 101M75 101Q92 69 109 101M120 101Q137 69 154 101" fill="#b8d0bc"/><path d="M177 61H247M177 77H235M177 93H222" stroke="#b0c4b4" stroke-width="5" stroke-linecap="round"/></g><text x="54" y="575" font-size="12" fill="#53676b">AN ILLUSTRATIVE WORLD · NOT A GEOGRAPHIC DATASET</text>'''
    save('splash.svg','The JupyterLite Learning Atlas','An illustrative globe connects asking a question, layering evidence, and learning together. All geography is original abstract artwork, not actual boundaries.',body,760,650)
    cards=[('BROWSER NOTEBOOKS','Small, inspectable Python','Stdlib + local SVG output','#e4eee5'),('VISUAL EXPLORATION','2D, extrusions and scenes','Assumptions stay visible','#f5e5bf'),('HUMAN REVIEW','Sources, privacy and empathy','Learn through participation','#e5e5f0')]
    b='<rect width="960" height="400" rx="20" fill="#f5f4ed"/><text x="32" y="48" font-size="25" fill="#153740">Start small. Know where each tool runs.</text>'
    for i,(label,title,sub,color) in enumerate(cards):
        x=32+i*302
        b+=f'<rect x="{x}" y="82" width="280" height="182" rx="14" fill="{color}" stroke="#c4d1c5"/><text x="{x+20}" y="116" font-size="11" letter-spacing="1.3" fill="#116c61">{label}</text><text x="{x+20}" y="164" font-size="18" fill="#153740">{title}</text><text x="{x+20}" y="196" font-size="13" fill="#53676b">{sub}</text><text x="{x+20}" y="235" font-size="13" fill="#153740">Predict → run → interpret</text>'
    b+='<path d="M35 294H925" stroke="#c4d1c5"/><text x="35" y="327" font-size="16" fill="#153740">Continue separately: native GIS · GPU inference · authenticated model services</text><text x="35" y="358" font-size="13" fill="#53676b">First browser load needs network. Default exercises need no credentials or remote datasets.</text>'
    save('capabilities.svg','Browser capabilities and continuation paths','Three browser learning activities connect to separate native GIS, GPU and model services. Default exercises are small, synthetic and credential-free.',b,960,400)
    b='<rect width="960" height="480" rx="20" fill="#f3f5ec"/><text x="35" y="48" font-size="25" fill="#153740">Evidence becomes useful through accountable review.</text>'
    stages=[('QUESTION','Who is affected?'),('EVIDENCE','Origin · date · units'),('ANALYSIS','Assumptions · limits'),('REVIEW','Privacy · community'),('ACTION','Owner · stopping rule')]
    for i,(label,sub) in enumerate(stages):
        x=28+i*188
        b+=f'<rect x="{x}" y="110" width="166" height="135" rx="12" fill="{ "#f6d48f" if i==3 else "#dcebe0" }" stroke="#7ea98e"/><text x="{x+16}" y="151" font-size="13" font-weight="650" fill="#153740">{label}</text><text x="{x+16}" y="186" font-size="11" fill="#153740">{sub}</text><text x="{x+16}" y="222" font-size="22" fill="#217a6d">0{i+1}</text>'
        if i<4:b+=f'<path d="M{x+169} 176H{x+185}" stroke="#217a6d" stroke-width="2" marker-end="url(#arrow)"/>'
    b+='<path d="M863 260V322H110V260" fill="none" stroke="#217a6d" stroke-width="2" marker-end="url(#arrow)"/><text x="290" y="310" font-size="16" fill="#116c61">Listen · measure consequences · revise the next question</text><text x="35" y="389" font-size="17" fill="#153740">A persuasive map, a prediction and a causal claim need different evidence.</text><text x="35" y="424" font-size="14" fill="#53676b">Synthetic teaching results are not observed health effects or validated policy advice.</text>'
    save('evidence-to-action.svg','Evidence to action and back to learning','Question, evidence, analysis, review and action form a learning loop. Community review and privacy precede accountable action.',b,960,480)
    b='<rect width="960" height="430" rx="20" fill="#f5f4ed"/><text x="35" y="48" font-size="26" fill="#153740">Empathy changes the experiment.</text>'
    stages=[('LISTEN','Whose experience is missing?'),('FRAME','Name a shared question.'),('PROTOTYPE','Try one reversible change.'),('LEARN','Invite critique and revise.')]
    for i,(label,sub) in enumerate(stages):
        x=30+i*235
        b+=f'<circle cx="{x+25}" cy="119" r="24" fill="#116c61"/><text x="{x+25}" y="125" text-anchor="middle" font-size="17" fill="#fff">{i+1}</text><text x="{x}" y="185" font-size="18" fill="#153740">{label}</text><text x="{x}" y="220" font-size="13" fill="#53676b">{sub}</text>'
        if i<3:b+=f'<path d="M{x+64} 119H{x+205}" stroke="#217a6d" stroke-width="2" marker-end="url(#arrow)"/>'
    b+='<path d="M859 251V302H56V251" fill="none" stroke="#217a6d" stroke-width="2" marker-end="url(#arrow)"/><text x="237" y="289" font-size="15" fill="#116c61">Record disagreement. Share authority. Change course when needed.</text><text x="35" y="364" font-size="15" fill="#53676b">Original interpretation informed by IDEO.org Design Kit and WHO AI governance.</text>'
    save('empathy-iteration.svg','Empathy and iterative experimentation','Listen, frame, prototype and learn, with feedback returning to listening. Affected people can challenge and change the experiment.',b,960,430)
    make_repository_overview()
    print('Generated six original accessible SVG assets.')


def make_repository_overview():
    """Refresh catalog-derived artwork without replacing other original assets."""
    data=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
    counts={}
    for r in data:counts[r['theme']]=counts.get(r['theme'],0)+1
    b='<rect width="960" height="445" rx="20" fill="#f5f4ed"/><text x="35" y="45" font-size="25" fill="#153740">A connected collection, with distinct questions.</text>'
    for i,(theme,n) in enumerate(counts.items()):
        y=80+i*48
        b+=f'<text x="35" y="{y+21}" font-size="16" fill="#153740">{escape(theme)}</text><rect x="345" y="{y}" width="{n*40}" height="31" rx="4" fill="#217a6d"/><text x="{355+n*40}" y="{y+21}" font-size="16" fill="#153740">{n}</text>'
    prefixed=sum(r['category']=='jupyterlite' for r in data)
    related=sum(r['category']=='related' for r in data)
    b+=f'<text x="35" y="410" font-size="13" fill="#53676b">{len(data)} public project chapters · {prefixed} JupyterLite-named + {related} related · reef addition, 2026-11-02</text>'
    save('repository-overview.svg','Repository overview by learning theme',f'Actual curated catalog metadata, not synthetic observations. Counts group {len(data)} public project chapters into {len(counts)} themes.',b,960,445)


if __name__=='__main__':main()
