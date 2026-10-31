"""Create a 10-page EpiScope Sentinel PDF with editable cover-data CLI args.

Usage: python docs/make_report.py --group 'Team Name' --member 'Name|ID'
       --github 'https://github.com/Friend/Repo' --video ''
"""
import argparse,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import ImageOps
from reportlab.pdfbase.pdfmetrics import stringWidth
from sentinel.store import quality
from sentinel.prediction import predict
from sentinel.scenarios import simulate
from sentinel.signals import district_alerts

fontbase=Path('/usr/share/fonts/truetype/lato')
if fontbase.exists():
    pdfmetrics.registerFont(TTFont('Lato',str(fontbase/'Lato-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('LatoBold',str(fontbase/'Lato-Bold.ttf')))
else:
    pdfmetrics.registerFont(TTFont('Lato','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('LatoBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Lato',normal='Lato',bold='LatoBold')
W,H=A4
NAVY=colors.HexColor('#202020');PURPLE=colors.HexColor('#2b2b2b')
TEAL=colors.HexColor('#454545');GREY=colors.HexColor('#5c5c5c')
LIGHT=colors.HexColor('#f7f7f7');LINE=colors.HexColor('#cccccc')
WHITE=colors.white


def para(c,text,x,y,width=480,size=10.2,leading=16,color=NAVY,bold=False,space=0):
    style=ParagraphStyle('body',fontName='LatoBold' if bold else 'Lato',fontSize=size,leading=leading,textColor=color,spaceAfter=0)
    p=Paragraph(text,style)
    _,h=p.wrap(width,1000)
    p.drawOn(c,x,y-h)
    return y-h-space

def text(c,t,x,y,size=10,color=NAVY,bold=False):
    c.setFillColor(color);c.setFont('LatoBold' if bold else 'Lato',size);c.drawString(x,y,t)

def line(c,x1,y1,x2,y2,color=LINE):
    c.setStrokeColor(color);c.setLineWidth(.8);c.line(x1,y1,x2,y2)

def header(c,num,kicker,title,subtitle=None):
    c.setFillColor(WHITE);c.rect(0,0,W,H,fill=1,stroke=0)
    text(c,'EPISCOPE SENTINEL  |  CSE 4345',54,H-47,9,NAVY,True)
    line(c,54,H-60,W-54,H-60,colors.HexColor('#737373'))
    text(c,kicker.upper(),54,H-93,9,GREY,True)
    text(c,title,54,H-136,24,NAVY,True)
    if subtitle:para(c,subtitle,54,H-154,487,10.3,15,GREY)
    line(c,54,62,W-54,62,colors.HexColor('#737373'))
    text(c,'SYNTHETIC DATA  |  ACADEMIC DEMONSTRATION ONLY',54,43,8,GREY)
    text(c,f'{num:02d} / 10',W-95,43,9,NAVY,True)
    return H-192

def box(c,x,y,w,h,fill=WHITE,stroke=LINE,r=12):
    c.setFillColor(fill);c.setStrokeColor(stroke);c.rect(x,y,w,h,fill=1,stroke=1)

def bullet(c,text_value,y,x=64,w=466,sz=10):
    c.setFillColor(TEAL);c.circle(x+3,y-5,2.8,fill=1,stroke=0)
    return para(c,text_value,x+14,y,w-14,size=sz,leading=15,space=9)

def sub(c,s,y,x=54):
    text(c,s,x,y,14,NAVY,True)
    line(c,x,y-10,W-54,y-10)
    return y-26

def image(c,path,x,y,width,maxheight):
    from PIL import Image
    im=ImageOps.grayscale(Image.open(path)).convert('RGB');iw,ih=im.size
    height=min(maxheight,width*ih/iw)
    c.drawImage(ImageReader(im),x,y-height,width=width,height=height,mask='auto')
    return y-height

def labelvalue(c,label,value,x,y,w=150):
    text(c,label.upper(),x,y,8,GREY,True)
    text(c,str(value),x,y-26,21,NAVY,True)

def end(c):c.showPage()

def build_report(outfile,group,members,github,video):
    quality_stats=quality()
    metrics={key:predict(key,'All Districts',8)['backtest'] for key in ['dengue','diarrhea','ili']}
    scm=simulate('dengue','All Districts',30,8)
    alert=district_alerts('ili')
    c=canvas.Canvas(str(outfile),pagesize=A4)
    c.setTitle('EpiScope Sentinel - Complex Engineering Assignment Report')
    c.setAuthor('Student research prototype - group details pending')
    # PAGE 1: plain academic cover (monochrome, no decorative panels)
    c.setFillColor(WHITE);c.rect(0,0,W,H,fill=1,stroke=0)
    text(c,'PREMIER UNIVERSITY',54,H-63,17,NAVY,True)
    text(c,'Department of Computer Science & Engineering',54,H-84,10,GREY)
    line(c,54,H-102,W-54,H-102,colors.HexColor('#737373'))
    text(c,'CSE 4345  |  COMPLEX ENGINEERING ASSIGNMENT',54,H-150,10,GREY,True)
    text(c,'EpiScope Sentinel',54,H-207,29,NAVY,True)
    para(c,'Big Data Surveillance, Forecasting and Response-Planning Platform',54,H-226,475,13,19,NAVY)
    para(c,'Early Warning and Intervention Scenario Lab  |  Project Report',54,H-274,470,11,17,GREY)
    line(c,54,H-321,W-54,H-321,LINE)
    text(c,'GROUP NAME / NUMBER',54,H-350,9,GREY,True)
    para(c,group,54,H-362,480,12,17,NAVY,True)
    text(c,'GROUP MEMBERS AND STUDENT IDs',54,H-411,10,NAVY,True)
    line(c,54,H-423,W-54,H-423,LINE)
    text(c,'Name',64,H-444,9,GREY,True)
    text(c,'Student ID',335,H-444,9,GREY,True)
    line(c,54,H-455,W-54,H-455,LINE)
    y=H-476
    for name,id_ in members:
        text(c,name,64,y,10.4,NAVY)
        text(c,id_,335,y,10.4,NAVY)
        line(c,54,y-11,W-54,y-11,LINE)
        y-=35
    text(c,'GITHUB REPOSITORY URL',54,190,9,GREY,True)
    para(c,github,54,179,480,10.4,15,NAVY)
    text(c,'SHAREABLE VIDEO PRESENTATION URL',54,141,9,GREY,True)
    para(c,video or '_____________________________________________',54,130,480,10.4,15,NAVY)
    line(c,54,84,W-54,84,LINE)
    text(c,'Premier University, Chattogram, Bangladesh',54,67,10,GREY)
    text(c,'SYNTHETIC DATA ONLY  |  NOT FOR CLINICAL OR PUBLIC-HEALTH USE',54,44,8,GREY)
    end(c)
    # PAGE 2
    y=header(c,2,'01 / project overview','Executive summary','A different approach to the same EpiScope brief: emphasize explainable early signals, week-level forecasting, and scenario literacy.')
    y=para(c,'<b>Research aim.</b> EpiScope Sentinel is a standalone, local-first teaching platform that investigates whether syndromic activity may look atypical, estimates near-term aggregate counts, and makes intervention assumptions explicit. The project does not diagnose patients, detect confirmed outbreaks, or prescribe a response.',54,y,485,10.5,16.6,space=20)
    y=sub(c,'Engineering objectives',y)
    for s in ['Produce a reproducible, explicitly synthetic weekly multi-location surveillance dataset.',
              'Validate records and calculate readable four-week trends and abnormality flags.',
              'Evaluate weekly Poisson count forecasts against a time-respecting naive baseline.',
              'Allow users to contrast a model baseline with a non-causal reduction scenario.',
              'Publish a browser dashboard, documented JSON API and repeatable automated tests.']:
        y=bullet(c,s,y)
    y-=4;y=sub(c,'How Sentinel differs from the earlier EpiScope',y)
    for s in ['<b>Primary unit:</b> epidemiological weeks, rather than day-by-day surveillance.',
              '<b>Analytical focus:</b> four-week anomalies and EWMA patterns, instead of only risk ranks.',
              '<b>Forecast model:</b> regularized Poisson GLM with Fourier seasonality, not autoregressive Ridge.',
              '<b>Planning:</b> hypothetical effect simulator rather than optimization of a constrained budget.',
              '<b>Interface:</b> top-navigation visual lab with lightweight SVG graphs and fresh architecture.']:
        y=bullet(c,s,y,sz=9.7)
    box(c,54,96,486,54,colors.HexColor('#ebebeb'),colors.HexColor('#dddddd'))
    para(c,'<b>Scope statement:</b> A functioning educational prototype and reproducible benchmark. The included 4,752 records are <b>not Big Data by volume</b>; separate streaming and optional Spark samples illustrate scalable patterns.',66,136,456,9.5,13,NAVY)
    end(c)
    # PAGE 3
    y=header(c,3,'02 / architecture','System architecture','Clear module boundaries allow validation, analytics, forecasting, scenario exploration and presentation to evolve separately.')
    box(c,54,375,487,248,WHITE)
    # diagram
    def nod(x,y,w,h,t,subtext,fill):
        box(c,x,y,w,h,fill,fill,9)
        text(c,t,x+12,y+h-20,11,WHITE,True)
        para(c,subtext,x+12,y+h-28,w-22,8.6,12,WHITE)
    nod(70,543,210,63,'SYNTHETIC GENERATOR','4,752 labeled weekly rows',colors.HexColor('#545454'))
    nod(314,543,210,63,'OPTIONAL EVENT ETL','bounded CSV -> SQLite / Spark',colors.HexColor('#616161'))
    nod(70,454,210,63,'DATA VALIDATOR','types, composite keys, completeness',colors.HexColor('#737373'))
    nod(314,454,210,63,'ANALYTICS CORE','EWMA, anomaly, GLM + scenarios',colors.HexColor('#737373'))
    nod(192,391,210,43,'FASTAPI + WEB UI','documented routes and SVG views',colors.HexColor('#303030'))
    for x1,x2,y1,y2 in [(175,175,543,517),(419,419,543,517),(280,314,489,489),(175,246,454,434),(419,349,454,434)]:
        c.setStrokeColor(colors.HexColor('#737373'));c.setLineWidth(2);c.line(x1,y1,x2,y2)
    y=350;y=sub(c,'Design decisions',y)
    for s in ['<b>Local-first:</b> FastAPI serves all frontend assets without external chart libraries or cloud accounts.',
              '<b>Observable calculations:</b> each endpoint returns the synthetic label and interpretable method outputs.',
              '<b>Reproducibility:</b> fixed random seed; quality rules applied before any analytics.',
              '<b>Extension point:</b> independent event-streaming exercise demonstrates data engineering beyond the core CSV.']:
        y=bullet(c,s,y,sz=9.6)
    end(c)
    # PAGE 4
    y=header(c,4,'03 / data engineering','Synthetic data & validation','A complete demonstration schema with explicit provenance, consistent keys and zero included patient identifiers.')
    for i,(label,value) in enumerate([('RECORDS',quality_stats['rows']),('DISTRICTS',quality_stats['districts']),('SYNDROMES',quality_stats['syndromes']),('WEEKS',quality_stats['weeks'])]):
        x=54+i*125;box(c,x,y-80,112,75,WHITE)
        labelvalue(c,label,value,x+12,y-22)
    y-=105
    y=sub(c,'Weekly observation schema',y)
    columns=[('week_start','Monday ISO date'),('district','8 named demonstration areas'),('syndrome','dengue / diarrhea / ili'),('cases','nonnegative integer'),('visits','visits >= cases'),('source','SIMULATED_SENTINEL')]
    for col,val in columns:
        text(c,col,66,y,10,NAVY,True);text(c,val,244,y,10,GREY);line(c,62,y-9,W-62,y-9);y-=33
    y-=11
    y=sub(c,'Simulation patterns',y)
    y=para(c,'Three independent syndrome-like signals have deliberately different annual shapes; observations are generated by negative-binomial draws with local multipliers and a small serial contribution. Three brief spikes are injected at predeclared simulated locations and weeks.',54,y,480,9.8,15,space=9)
    y=image(c,ROOT/'assets/disease_trends.png',64,y-4,463,112)-10
    y=para(c,'<b>Important:</b> No included cases, population figures or syndrome-level visit ratios represent real Bangladesh disease trends. The optional encounter generator creates a separate engineering demo, not extra surveillance evidence.',54,y,480,9.5,14,GREY)
    end(c)
    # PAGE 5
    y=header(c,5,'04 / warning signals','Explainable detection engine','A deliberately interpretable rule combines an anomaly statistic with four-week directional change.')
    y=para(c,'<b>Reference:</b> 26 weeks preceding the recent four weeks. <b>Current:</b> mean of the last four weeks. Standardized score uses the older-window standard deviation with a floor to stabilize low counts. EWMA with alpha = 0.35 is displayed as a secondary smoothing statistic.',54,y,485,10.2,16,space=13)
    box(c,54,y-70,486,66,colors.HexColor('#efefef'),colors.HexColor('#dfdfdf'))
    para(c,'<b>WATCH:</b> z-score >= 1.6 AND four-week momentum >= +5%.<br/><b>HIGH:</b> z-score >= 3.0 AND four-week momentum >= +20%.<br/><b>NORMAL:</b> all other combinations.',69,y-13,452,10.3,17,NAVY)
    y-=93
    y=sub(c,'Example output: influenza-like illness',y)
    y=image(c,ROOT/'assets/alert_figure.png',65,y,458,224)-12
    names=[x['district'] for x in alert if x['level']=='watch']
    y=para(c,'<b>Observed simulated watch flags:</b> '+', '.join(names)+'. Flag statuses depend on the synthetic data cutoff of 2026-10-12 and may change if the data generator is rerun with a different seed.',54,y,481,10,15,space=8)
    y=para(c,'<b>Caveat:</b> The rule thresholds are classroom choices and lack sensitivity, specificity or real-world outbreak validation. A signal is a visual prompt for exploration, not an instruction to issue public warnings.',54,y,481,9.8,15,GREY)
    end(c)
    # PAGE 6
    y=header(c,6,'05 / count forecasting','Poisson model & evaluation','Seasonal Fourier features and a chronological holdout make the comparison visible and resistant to simple future leakage.')
    y=para(c,'<b>Model:</b> regularized Poisson regression (log-link) with annual sin/cos terms at harmonics 1 and 2 plus bounded time trend. <b>Evaluation:</b> train on all weeks except the most recent 12; predict those 12 and compute mean absolute error (MAE). <b>Comparator:</b> count from exactly 52 weeks earlier.',54,y,480,9.9,15,space=13)
    text(c,'Syndrome',63,y,10,GREY,True);text(c,'Poisson MAE',260,y,10,GREY,True);text(c,'Seasonal naive MAE',378,y,10,GREY,True);line(c,56,y-13,534,y-13)
    y-=34
    for name,ky in [('Dengue-like','dengue'),('Diarrheal illness','diarrhea'),('Influenza-like','ili')]:
        vals=metrics[ky]
        text(c,name,63,y,10,NAVY);text(c,f"{vals['model_mae']:.2f}",276,y,10,PURPLE,True)
        text(c,f"{vals['seasonal_naive_mae']:.2f}",409,y,10,TEAL,True)
        line(c,56,y-12,534,y-12);y-=38
    y-=12
    y=sub(c,'Eight-week outlook (ILI, all districts)',y)
    y=image(c,ROOT/'assets/forecast_figure.png',60,y,472,214)-10
    y=para(c,'<b>Transparent result:</b> For dengue, Poisson MAE '+str(metrics['dengue']['model_mae'])+' is marginally <b>worse</b> than the seasonal-naive '+str(metrics['dengue']['seasonal_naive_mae'])+'. The model is not presented as universally superior.',54,y,483,9.5,14,space=7)
    y=para(c,'<b>Uncertainty note:</b> the displayed +/- 80th-percentile absolute holdout residual band is descriptive, not a statistically calibrated 80% prediction interval. The empirical holdout coverage for each syndrome was 75% in this small sample.',54,y,483,9.3,13.5,GREY)
    end(c)
    # PAGE 7
    y=header(c,7,'06 / response planning','Hypothetical intervention studio','A what-if calculator promotes transparent assumptions rather than false claims of treatment efficacy.')
    y=para(c,'Let <b>r</b> be the selected final relative reduction, <b>H</b> the number of future weeks, and <b>t</b> the week offset. The simulator assumes <b>hypothetical_cases(t) = baseline_forecast(t) * [1 - r * t / H]</b>. The visualized difference is the arithmetic gap between two assumptions.',54,y,484,10,16.2,space=10)
    y=image(c,ROOT/'assets/scenario_figure.png',64,y,466,220)-12
    box(c,54,y-91,486,79,colors.HexColor('#f7f7f7'),colors.HexColor('#e7e7e7'))
    labelvalue(c,'8-week forecast baseline',round(scm['baseline_total']),69,y-31)
    labelvalue(c,'30% final-week hypothesis',round(scm['hypothetical_total']),247,y-31)
    y-=116
    y=sub(c,'Interpretation & constraints',y)
    for s in ['The selected 30% number is hypothetical; it is <b>not</b> supported by efficacy trials or intervention data.',
              'The engine does not simulate transmission, social behavior, mobility or healthcare capacity.',
              'The same arithmetic structure can support discussion of awareness, sanitation or vector-control strategies without claiming effectiveness.',
              'Counterfactual totals are planning illustrations only: do not use for medical or government allocation decisions.']:
        y=bullet(c,s,y,sz=9.8)
    end(c)
    # PAGE 8
    y=header(c,8,'07 / prototype interface','Product implementation','Accessible top navigation separates live indicators, anomaly exploration, forecast validation and scenario reasoning.')
    y=image(c,ROOT/'assets/dashboard.png',55,y,485,333)-10
    y=para(c,'<b>Pulse dashboard:</b> four-week cases, simulated case-to-visit ratio, count of flagged areas and history length. It uses lightweight SVG graphics and does not need an external dashboard framework, an internet connection or patient information.',54,y,484,10,15,space=12)
    y=sub(c,'API surfaces',y)
    for url,desc in [('/api/overview','case burden, visit ratios and flags'),('/api/signals','anomaly and EWMA per area'),('/api/forecast','8-week Poisson outlook and holdout MAE'),('/api/scenario','arithmetic what-if trajectories'),('/api/quality','provenance and dataset checks'),('/api/export','synthetic CSV download')]:
        text(c,url,63,y,9.4,PURPLE,True);text(c,desc,230,y,9.3,NAVY);y-=29
    end(c)
    # PAGE 9
    y=header(c,9,'08 / tests & ethics','Verification and constraints','A working teaching prototype must say what has been tested - and which safety properties are still missing.')
    box(c,54,y-93,486,87,colors.HexColor('#f5f5f5'),colors.HexColor('#e9e9e9'))
    labelvalue(c,'AUTOMATED TESTS',12,70,y-30)
    labelvalue(c,'FAILED TESTS',0,252,y-30)
    y-=117
    y=sub(c,'Automated verification covers',y)
    for s in ['Dataset completeness (4,752 rows), dates, unique keys and source labeling.',
              'Validation rejects duplicate series entries and false provenance labels.',
              'Simulated spike produces appropriate high alert under the declared rule.',
              'Poisson forecasts are nonnegative with calculable chronological holdout MAE.',
              'Scenario outcomes are monotonic with the selected hypothetical reduction.',
              'Streaming fake-event aggregation conserves a 1,017-event test input.',
              'Web assets, JSON API outputs, CSV export and invalid query handling.']:
        y=bullet(c,s,y,sz=9.6)
    y-=8;y=sub(c,'Ethics, privacy and production gaps',y)
    y=para(c,'<b>Privacy:</b> no identifiers or real patient files are stored. <b>Governance:</b> no real data use or health-ethics clearance is implied. <b>Security:</b> local prototype has no authentication, patient consent flow, encryption policy, rate limits or audit logging. <b>Accuracy:</b> flags, forecast intervals and scenario effects require extensive field evaluation before public-health adoption.',54,y,477,10,15.5,space=12)
    y=para(c,'<b>Scaling caveat:</b> the main CSV is small. Streaming event samples and optional Spark ETL show architectural techniques only; distributed production throughput was not measured.',54,y,480,9.8,15,GREY)
    end(c)
    # PAGE 10
    y=header(c,10,'09 / conclusion','Findings, handover & next steps','A self-contained research prototype that can be run, explained, tested and extended.')
    y=sub(c,'Summary of contributions',y)
    for s in ['A fully simulated weekly sentinel dataset and validation pipeline.',
              'Transparent anomaly indicators and a directly inspectable threshold policy.',
              'Seasonality-aware Poisson count forecast with an honest naive comparison.',
              'An interactive, explicitly non-causal hypothetical scenario lab.',
              'A documented local API, responsive web interface, and twelve passing tests.']:
        y=bullet(c,s,y,sz=9.7)
    y-=3;y=sub(c,'How to run and submit',y)
    for s in ['Extract ZIP; on Windows double-click <b>START_WINDOWS.bat</b> (Python 3.10+ required).',
              'Open <b>http://127.0.0.1:8000</b> and <b>/docs</b> for the API.',
              'Install dev dependencies and run <b>python -m pytest -q</b> to verify locally.',
              'Upload source folders to the friend group\'s own GitHub repository.',
              'Replace <b>all cover placeholders</b>, then submit ZIP/repo URL, PDF and shareable recorded presentation link.']:
        y=bullet(c,s,y,sz=9.6)
    y-=2;y=sub(c,'Directions for future research',y)
    y=para(c,'Secure authorized epidemiological feeds; external weather and mobility covariates; calibrated count intervals; geographic equity analysis; cross-validated threshold selection; encrypted role-based data access; and production-scale stream processing.',54,y,484,9.8,15,space=12)
    y=sub(c,'Technical reading',y)
    for s in ['scikit-learn: PoissonRegressor API documentation and generalized linear models.',
              'FastAPI: Request validation, interactive API documentation and TestClient.',
              'Apache Spark: SQL and DataFrame documentation (optional ETL demonstration).',
              'Project README, DATA_DICTIONARY.md, METHODS.md and TEST_RESULTS.md.']:
        y=bullet(c,s,y,sz=9.1)
    end(c)
    c.save()
    return outfile

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--group',default='[GROUP NAME / NUMBER - TO BE FILLED]')
    p.add_argument('--member',action='append',default=[],help='Provide as Name|Student ID; repeat')
    p.add_argument('--github',default='[FRIEND GITHUB REPOSITORY URL]')
    p.add_argument('--video',default='')
    p.add_argument('--output',default=str(ROOT/'EpiScope_Sentinel_Friend_Report.pdf'))
    a=p.parse_args()
    members=[tuple((v.split('|',1)+['[STUDENT ID]'])[:2]) for v in a.member]
    out=build_report(Path(a.output),a.group,members,a.github,a.video)
    print('Generated report:',out)
