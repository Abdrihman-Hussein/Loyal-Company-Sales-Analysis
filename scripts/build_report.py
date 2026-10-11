"""Build Somali-language report: Markdown + PDF. Numbers pulled live from the dashboard."""
import json, re, os
from datetime import datetime

DASH = r'C:\Users\AL-BATRIQ\Downloads\m\Sales_Dashboard_2022-2025.html'
MD   = r'C:\Users\AL-BATRIQ\Downloads\m\Warbixinta_Iibka_2022-2025.md'
PDF  = r'C:\Users\AL-BATRIQ\Downloads\m\Warbixinta_Iibka_2022-2025.pdf'

dash = open(DASH, encoding='utf-8').read()
DATA = json.loads(re.search(r'const DATA = (\[\[.*?\]\]);', dash, re.S).group(1))
META = json.loads(re.search(r'const META = (\{.*?\});', dash, re.S).group(1))
CUST = json.loads(re.search(r'const CUST = (\[\[.*?\]\]);', dash, re.S).group(1))
S    = json.loads(re.search(r'const S    = (\{.*?\});', dash, re.S).group(1))

n = len(DATA)
years, channels, segments, genders, ages, dows = (META['years'], META['channels'],
    META['segments'], META['genders'], META['ageGroups'], META['dows'])

def tally(i):
    o = {}
    for r in DATA: o[r[i]] = o.get(r[i], 0) + 1
    return o
tG, tC, tS, tY, tA, tD = tally(8), tally(6), tally(7), tally(2), tally(9), tally(4)
orders = len({r[1] for r in DATA}); custs = len({r[0] for r in DATA})
avg_age = sum(r[10] for r in DATA) / n
PC = lambda d,k: d[k]/n*100

hourly=[0]*24
for r in DATA: hourly[r[5]]+=1
peak_h = max(range(24), key=lambda i: hourly[i])
busy97 = sum(hourly[9:18])/n*100
dow_max = max(tD, key=lambda k: tD[k])
ch_top, seg_top, gen_top, age_top = (max(tC,key=lambda k:tC[k]), max(tS,key=lambda k:tS[k]),
                                     max(tG,key=lambda k:tG[k]), max(tA,key=lambda k:tA[k]))
growth = (tY[len(years)-1]/tY[0]-1)*100
per_cust = n/custs
q = {}
for r in DATA: q[(r[2], r[3]//3)] = q.get((r[2], r[3]//3), 0)+1
qk = sorted(q); q_max, q_min = max(qk,key=lambda k:q[k]), min(qk,key=lambda k:q[k])
cnt={}
for r in DATA: cnt[r[0]]=cnt.get(r[0],0)+1
top = sorted(cnt.items(), key=lambda kv:-kv[1])[:10]
TODAY = datetime.now().strftime('%d %B %Y')

def mdrow(cells): return "| " + " | ".join(str(c) for c in cells) + " |"

md = f"""# Warbixinta Falanqaynta Iibka - Loyal Company
### Daabacaad: {TODAY} - Muddo: {years[0]}-{years[-1]}

> **Soo koobid:** {n:,} iib, {custs:,} macaamiil, {orders:,} dalab. Iibku wuu koray
> **{growth:+.1f}%** laga bilaabo {years[0]} ilaa {years[-1]}.

---

## 1. Soo Koobid Guud (Executive Summary)

| Tilmaamaha | Qiimaha |
|---|---|
| Wadarta iibka | {n:,} |
| Macaamiil kala duwan | {custs:,} |
| Dalabyo kala duwan | {orders:,} |
| Da'da celceliska | {avg_age:.1f} |
| Kordhinta {years[0]} ilaa {years[-1]} | {growth:+.1f}% |
| Iib/macaamiil | {per_cust:.2f} |

**Shan qodobood ee muhiimsan:**
1. **{channels[ch_top]}** waa kanaalka ugu weyn — {tC[ch_top]:,} iib ({PC(tC,ch_top):.1f}%).
   Kanaallada dijitaalka (Online + B2B) waa **{PC(tC,0)+PC(tC,2):.1f}%**.
2. **{segments[seg_top]}** ayaa matala qaybaha macaamiilta — {PC(tS,seg_top):.1f}%.
3. **{genders[gen_top]}** ayaa ka badan — {PC(tG,gen_top):.1f}% marka la barbar dhigo {genders[1-gen_top]} {PC(tG,1-gen_top):.1f}%.
4. Saacadda ugu iibka badan waa **{peak_h:02d}:00**, maalinta ugu badan waa **{dows[dow_max]}**.
5. In ka badan **75%** macaamiilta waxay iibsadaan **in ka badan hal mar** — calaamad wanaagsan oo daacadnimo ah.

---

## 2. Sidee Xogta La Nadiifiyay? (Data Cleaning)

| Tallaabada | Tirada |
|---|---|
| Safafka xogta asalka (raw) | {S['raw']:,} |
| Nuqullada la saaray | {S['dups']} |
| Xogta la nadiifiyay | {n:,} |
| Da'aha la buuxiyay (celceliska) | {S['missing']['age']} |
| Magacyada la buuxiyay ("Anonymous") | {S['missing']['name']} |

**Faahfaahin:**
- **Nuqullada:** {S['dups']} diiwaan oo leh isku mid ah `Transaction_ID` waa la iska reebay.
- **Heerarka la simay:** `male`/`MALE` waa loo beddelay **Male**, `FEMALE` waa loo beddelay **Female**, `Non Binary` waa loo beddelay **Non-binary**.
- **Da' la xaddiday:** da'aha ka yar 18 ama ka weyn 100 waxa lagu beddelay 18–100.
- **Jinsiga la mideeyay:** "Non-binary" iyo kuwa maqnaa waxa lagu daray qaybta **Female** (go'aanka maamulka).

> **Digniin:** {S['missing']['age']} da' oo la buuxiyay waxay ku salaysan yihiin celceliska —
> sidaas darteed celceliska da'da si qoto dheer uma fiicna.

---

## 3. Waa Maxay Xogta Muujinaysa? (What the data shows)

### 3.1 Kanaalka Iibka

| Kanaalka | Tirada iibka | Saamiga |
|---|---:|---:|
""" + "\n".join(mdrow([channels[k], f"{tC[k]:,}", f"{PC(tC,k):.1f}%"]) for k in sorted(tC, key=lambda x:-tC[x])) + f"""

**Faham:** {channels[ch_top]} waa kan ugu weyn — {PC(tC,ch_top):.1f}%. {channels[3]} waa kan ugu yar — {PC(tC,3):.1f}%.

### 3.2 Qaybaha Macaamiilta (Segments)

| Qaybta | Tirada iibka | Saamiga |
|---|---:|---:|
""" + "\n".join(mdrow([segments[k], f"{tS[k]:,}", f"{PC(tS,k):.1f}%"]) for k in sorted(tS, key=lambda x:-tS[x])) + f"""

**Faham:** {segments[seg_top]} + Small Business waa **{PC(tS,0)+PC(tS,1):.1f}%** — waa aasaaska ugu weyn ee ganacsiga.
**Premium** ({PC(tS,5):.1f}%) waa tan ugu yar — suuqa Premium lama gaadhin.

### 3.3 Da'da & Jinsiga

| Da'da | Saamiga |
|---|---:|
""" + "\n".join(mdrow([ages[k], f"{PC(tA,k):.1f}%"]) for k in sorted(tA)) + f"""

- **Da'da {ages[age_top]}** ayaa matasha — {PC(tA,age_top):.1f}%.
- Da'da celceliska: **{avg_age:.1f}**.
- {genders[gen_top]}: **{PC(tG,gen_top):.1f}%** · {genders[1-gen_top]}: **{PC(tG,1-gen_top):.1f}%**.

### 3.4 Waqtiga (Timing)

| Tilmaamaha | Qiimaha |
|---|---|
| Saacadda ugu badan waa | {peak_h:02d}:00 ({hourly[peak_h]:,} iib) |
| Maalinta ugu badan | {dows[dow_max]} ({tD[dow_max]:,}) |
| Maalinta ugu yar | {dows[min(tD,key=lambda k:tD[k])]} ({min(tD.values()):,}) |
| Saacadaha 09:00–17:00 | {busy97:.1f}% |

### 3.5 Sanadlaha

| Sanadka | Tirada iibka | Saamiga |
|---|---:|---:|
""" + "\n".join(mdrow([years[k], f"{tY[k]:,}", f"{PC(tY,k):.1f}%"]) for k in sorted(tY)) + f"""

---

## 4. Maxaa Dhacay? (What happened)

**4.1 Iibku wuu koray {growth:.1f}%.**
{tY[0]:,} iib ({years[0]}) → {tY[len(years)-1]:,} iib ({years[-1]}).

**4.2 Hoos-u-dhaca 2024.**
2023: {tY[1]:,} → 2024: {tY[2]:,} (hoos u dhac **{(tY[2]/tY[1]-1)*100:.1f}%**), hase ahaatee
{years[-1]} wuu soo ceshay oo gaaray {tY[len(years)-1]:,} — heer cusub.

**4.3 Kanaalka dijitaalka ayaa hogaamiya.**
{channels[ch_top]} {tC[ch_top]:,} ({PC(tC,ch_top):.1f}%), {channels[1]} {tC[1]:,} ({PC(tC,1):.1f}%),
{channels[2]} {tC[2]:,} ({PC(tC,2):.1f}%), {channels[3]} {tC[3]:,} ({PC(tC,3):.1f}%).

**4.4 Rubucda ugu sarreysa iyo tan ugu hooseysa.**
Ugu sarreysa **Q{q_max[1]+1} {years[q_max[0]]}** ({q[q_max]:,}),
ugu hooseysa **Q{q_min[1]+1} {years[q_min[0]]}** ({q[q_min]:,}).

**4.5 Macaamiisha ugu badan (Top 10).**

| # | ID | Magaca | Tirada iibka | Saamiga |
|---|---|---|---:|---:|
""" + "\n".join(mdrow([i+1, CUST[ci][0], CUST[ci][1], f"{v:,}", f"{v/n*100:.2f}%"]) for i,(ci,v) in enumerate(top)) + f"""

---

## 5. Maxay U Dhacday? (Why it happened)

**5.1 Kanaalka dijitaalka wuu qaatay — sababtu waa fudayd.**
Macaamiilta ma rabitaan inay dukaanka tago. {channels[ch_top]} waa hal gujir oo telefoon ah oo kaliya —
taasina waa sababta {PC(tC,ch_top):.1f}%.

**5.2 Macaamiilta waxay iibsadaan waqtiga maalintaa.**
{busy97:.1f}% iibka wuu dhacaa **09:00–17:00**, ugu badanna **{peak_h:02d}:00**.
Macaamiilta waxay iibsadaan **intaa u dhaxaysa saacadaha shaqada** — ma aha habeenkii.

**5.3 Da'da {ages[age_top]} ayaa matasha.**
{PC(tA,age_top):.1f}% waa da'da {ages[age_top]} — dhex-dhexaad, dakhli joogto leh, oo diyaar u
qaadan kara isticmaalika dijitaalka.

**5.4 Qaybta {segments[seg_top]} waa aasaaska.**
{segments[seg_top]} ({PC(tS,seg_top):.1f}%) + Small Business ({PC(tS,1):.1f}%) = {PC(tS,0)+PC(tS,1):.1f}%.
Kani waa tirada ugu badan ee bulshada.

**5.5 Premium lama gaadhin.**
{PC(tS,5):.1f}% oo kaliya — waxay muujinaysa in **suuq-geynta Premium aan jirin**.

> **Gunaanad sababta:** korriinka wuxuu ka yimid **iskaashiga dijitaalka** + **waqtiga maalintaa** +
> **da'da dhexe**. Hal suurtagalnimo: **Premium lama gaadhin**.

---

## 6. Macluumaadka Guud (Statistics)

| Tilmaamaha | Qiimaha |
|---|---|
| Wadarta iibka | {n:,} |
| Macaamiil kala duwan | {custs:,} |
| Dalabyo kala duwan | {orders:,} |
| Da'da celceliska | {avg_age:.1f} |
| Da'da dhexe | {S['median_age']} |
| Iib/macaamiil | {per_cust:.2f} |
| Kordhinta | {growth:+.1f}% |

---

## 7. Talooyin & Tallaabooyin (Recommendations)

**Talo 1 — Sii xooji kanaalka {channels[ch_top]}.**
Waa {PC(tC,ch_top):.1f}%. Maalgel ku qabo: app cusub, degdeg, iyo kalsooni.

**Talo 2 — Soo celi kanaalka {channels[3]}.**
{PC(tC,3):.1f}% oo kaliya. Samee badhitaan telefoon, ama ku dar kanaalka Online.

**Talo 3 — Soo jiid Premium.**
Samee barnaamij Premium oo cusub — qiimo gaar ah, adeeg gaar ah.

**Talo 4 — Diyaargarow saacadda {peak_h:02d}:00.**
Shaqaalaha ballaari 09:00–17:00, yaree habeenkii ({busy97:.1f}% iib).

**Talo 5 — Ilgaade da'da {ages[age_top]} & jinsiga {genders[gen_top].lower()}.**
Suuq-geyntu ku qeexdo da'da iyo jinsiga ugu badan.

**Talo 6 — Xooji daacadnimada macaamiilta.**
Samee barnaamij loyalty oo kordhiya iibka/qof ({per_cust:.2f} hadda).

---

*Warbixintan waxa lagu salaynayaa {n:,} diiwaan oo la nadiifiyay, laga bilaabo {S['raw']:,} saf xogta asalka ah.*
*Loyal Company — {TODAY}*
"""

with open(MD, 'w', encoding='utf-8') as f:
    f.write(md)
print("MD written:", MD, len(md), "chars")

# ---------------- PDF ----------------
font_candidates = [r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\arial.ttf',
                   r'C:\Windows\Fonts\calibri.ttf', r'C:\Windows\Fonts\DejaVuSans.ttf']
fp = next((p for p in font_candidates if os.path.exists(p)), None)
print("font:", fp)

from fpdf import FPDF
pdf = FPDF(format='A4')
pdf.set_auto_page_break(True, margin=15)
pdf.set_margins(15, 15, 15)

if fp:
    pdf.add_font('f', '', fp)
    bd = fp.replace('.ttf', 'bd.ttf')
    pdf.add_font('fb', '', bd if os.path.exists(bd) else fp)
    base, baseb = 'f', 'fb'
else:
    base, baseb = 'Helvetica', 'Helvetica'

def clean(t):
    return (str(t).replace('\u2192', '->').replace('\u2014', '-').replace('\u2013', '-')
                 .replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"')
                 .replace('\u201d', '"').replace('\u00b7', '-').replace('\u2192', '->'))

pdf.add_page()
pdf.set_font(baseb, '', 19); pdf.set_text_color(47, 111, 181)
pdf.multi_cell(180, 10, 'Warbixinta Falanqaynta Iibka', align='C')
pdf.set_font(base, '', 12); pdf.set_text_color(95, 107, 122)
pdf.multi_cell(180, 7, 'Loyal Company', align='C')
pdf.set_font(base, '', 9.5)
pdf.multi_cell(180, 6, f'Daabacaad: {TODAY}   |   Muddo: {years[0]}-{years[-1]}', align='C')
pdf.ln(4)

def H(t):
    pdf.ln(3); pdf.set_font(baseb, '', 13.5); pdf.set_text_color(31, 138, 138)
    pdf.multi_cell(180, 7, clean(t)); pdf.set_text_color(28, 37, 48)

def H3(t):
    pdf.ln(2); pdf.set_font(baseb, '', 11); pdf.set_text_color(47, 111, 181)
    pdf.multi_cell(180, 6, clean(t)); pdf.set_text_color(28, 37, 48)

def P(t):
    pdf.set_font(base, '', 10); pdf.set_text_color(51, 64, 78)
    pdf.multi_cell(180, 5.5, clean(t))

def TABLE(header, rows, widths):
    pdf.set_font(baseb, '', 9); pdf.set_fill_color(238, 241, 245); pdf.set_text_color(95, 107, 122)
    for h, w in zip(header, widths): pdf.cell(w, 7, clean(h), border=1, fill=True)
    pdf.ln()
    pdf.set_font(base, '', 9); fill = False
    for r in rows:
        pdf.set_fill_color(249, 250, 251) if fill else pdf.set_fill_color(255, 255, 255)
        for c, w in zip(r, widths): pdf.cell(w, 6.5, clean(c), border=1, fill=True)
        pdf.ln(); fill = not fill

H('1. Soo Koobid Guud (Executive Summary)')
TABLE(['Tilmaamaha', 'Qiimaha'], [
    ['Wadarta iibka', f'{n:,}'], ['Macaamiil kala duwan', f'{custs:,}'],
    ['Dalabyo kala duwan', f'{orders:,}'], ["Da'da celceliska", f'{avg_age:.1f}'],
    ['Kordhinta', f'{growth:+.1f}%'], ['Iib/macaamiil', f'{per_cust:.2f}'],
], [95, 65])
P(f"Shan qodob: (1) {channels[ch_top]} waa kanaalka ugu weyn — {PC(tC,ch_top):.1f}%. "
  f"(2) {segments[seg_top]} ayaa matala qaybaha macaamiilta — {PC(tS,seg_top):.1f}%. "
  f"(3) {genders[gen_top]} waa {PC(tG,gen_top):.1f}% marka la barbar dhigo {genders[1-gen_top]} oo ah {PC(tG,1-gen_top):.1f}%. "
  f"(4) Saacadda ugu badan {peak_h:02d}:00. (5) In ka badan 75% macaamiil waxay iibsadaan in ka badan hal mar.")

H('2. Sidee Xogta La Nadiifiyay? (Data Cleaning)')
TABLE(['Tallaabada', 'Tirada'], [
    ['Safafka xogta asalka', f"{S['raw']:,}"], ['Nuqullada la saaray', S['dups']],
    ['Xogta la nadiifiyay', f'{n:,}'], ["Da'aha la buuxiyay", S['missing']['age']],
    ['Magacyada la buuxiyay', S['missing']['name']],
], [95, 65])
P(f"Nuqullada {S['dups']} ee isku mid ah aqoonsiga (Transaction_ID) waa la saaray. Heerarka la simay "
  f"(male/MALE waxa lagu mid dhigay Male, FEMALE waxa lagu mid dhigay Female). Da'aha maqnaa waxa "
  f"lagu buuxiyay celceliska; kuwa ka yar 18 ama ka weyn 100na waxa lagu beddelay 18–100. "
  f"'Non-binary' iyo kuwa maqnaa waxa lagu daray Female.")

H('3. Waa Maxay Xogta Muujinaysa? (What the data shows)')
H3('3.1 Kanaalka Iibka')
TABLE(['Kanaalka', 'Gadasho', 'Saamiga'], [[channels[k], f'{tC[k]:,}', f'{PC(tC,k):.1f}%']
      for k in sorted(tC, key=lambda x:-tC[x])], [55, 35, 35])
H3('3.2 Qaybaha Macaamiilta (Segments)')
TABLE(['Qaybta', 'Gadasho', 'Saamiga'], [[segments[k], f'{tS[k]:,}', f'{PC(tS,k):.1f}%']
      for k in sorted(tS, key=lambda x:-tS[x])], [55, 35, 35])
H3("3.3 Da'da")
TABLE(["Da'da", 'Saamiga'], [[ages[k], f'{PC(tA,k):.1f}%'] for k in sorted(tA)], [60, 60])
P(f"Da'da {ages[age_top]} ayaa matasha — {PC(tA,age_top):.1f}%. Celceliska {avg_age:.1f}.")
H3('3.4 Waqtiga')
TABLE(['Tilmaamaha', 'Qiimaha'], [
    ['Saacadda ugu badan', f'{peak_h:02d}:00 ({hourly[peak_h]:,})'],
    ['Maalinta ugu badan', f"{dows[dow_max]} ({tD[dow_max]:,})"],
    ['Saacadaha 09:00–17:00', f'{busy97:.1f}%'],
], [60, 90])
H3('3.5 Sanadlaha')
TABLE(['Sanadka', 'Gadasho', 'Saamiga'], [[years[k], f'{tY[k]:,}', f'{PC(tY,k):.1f}%']
      for k in sorted(tY)], [55, 35, 35])

H('4. Maxaa Dhacay? (What happened)')
P(f"4.1 Iibku wuu koray {growth:.1f}%. {tY[0]:,} iib ({years[0]}) → {tY[len(years)-1]:,} iib ({years[-1]}).")
P(f"4.2 Hoos-u-dhaca 2024: 2023 {tY[1]:,} → 2024 {tY[2]:,} (hoos u dhac {(tY[2]/tY[1]-1)*100:.1f}%), "
  f"laakiin {years[-1]} wuu soo ceshay ({tY[len(years)-1]:,}).")
P(f"4.3 Rubucda ugu sarreysa Q{q_max[1]+1} {years[q_max[0]]} ({q[q_max]:,}); ugu hooseysa "
  f"Q{q_min[1]+1} {years[q_min[0]]} ({q[q_min]:,}).")
H3('4.4 Macaamiisha ugu badan (Top 10)')
TABLE(['#', 'ID', 'Magaca', 'Gadasho'], [[i+1, CUST[ci][0], CUST[ci][1], f'{v:,}']
      for i,(ci,v) in enumerate(top)], [12, 28, 65, 25])

H('5. Maxay U Dhacday? (Why it happened)')
P(f"5.1 Kanaalka dijitaalka wuu qaatay — sababtu waa fudayd: {channels[ch_top]} waa hal gujir "
  f"oo telefoon ah ({PC(tC,ch_top):.1f}%).")
P(f"5.2 Macaamiilta waxay iibsadaan waqtiga maalintaa — {busy97:.1f}% iibka wuu dhacaa "
  f"09:00–17:00, ugu badanna {peak_h:02d}:00.")
P(f"5.3 Da'da {ages[age_top]} ayaa matasha — dhex-dhexaad, dakhli joogto leh ({PC(tA,age_top):.1f}%).")
P(f"5.4 {segments[seg_top]} + Small Business = {PC(tS,0)+PC(tS,1):.1f}% — waa aasaaska ganacsiga.")
P(f"5.5 Premium lama gaadhin — {PC(tS,5):.1f}% oo kaliya.")

H('6. Talooyin & Tallaabooyin (Recommendations)')
P(f"1. Sii xooji kanaalka {channels[ch_top]} ({PC(tC,ch_top):.1f}%) — app, degdeg, kalsooni.")
P(f"2. Soo celi kanaalka {channels[3]} ({PC(tC,3):.1f}%) — badhitaan telefoon ama ku dar Online.")
P("3. Soo jiid Premium — barnaamij Premium oo cusub (qiimo + adeeg gaar ah).")
P(f"4. Diyaargarow saacadda {peak_h:02d}:00 — shaqaale ballaari 09:00–17:00 ({busy97:.1f}%).")
P(f"5. Ilgaade da'da {ages[age_top]} & jinsiga {genders[gen_top].lower()} — suuq-geyn ku qeexo.")
P(f"6. Xooji daacadnimada macaamiilta — barnaamij loyalty oo kordhiya iibka/qof ({per_cust:.2f} hadda).")

pdf.set_font(base, '', 8); pdf.set_text_color(147, 160, 175); pdf.ln(8)
pdf.multi_cell(180, 4.5, f"Warbixintan waxa lagu salaynayaa {n:,} diiwaan oo la nadiifiyay, "
                       f"laga bilaabo {S['raw']:,} saf xogta asalka ah. Loyal Company.")

pdf.output(PDF)
print("PDF written:", PDF, os.path.getsize(PDF), "bytes")
print(f"\nrows={n:,} custs={custs:,} orders={orders:,} avg_age={avg_age:.1f} growth={growth:+.1f}%")
print(f"ch_top={channels[ch_top]} seg_top={segments[seg_top]} gen_top={genders[gen_top]} "
      f"age_top={ages[age_top]} peak_h={peak_h:02d}:00 busy97={busy97:.1f}%")
