"""Generate the U-RESCUE academic project report (DOCX master)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
import json, math, textwrap

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Project_Report"
ASSETS=OUT/"assets"
OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)
NAVY="12304A"; BLUE="216B8A"; TEAL="117C83"; PALE="EAF3F6"; GOLD="E2AA4A"; GREY="526575"; LIGHT="F4F7F8"

def font(size,bold=False):
    options=[r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"]
    for path in options:
        if Path(path).exists(): return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def image_base(w=1500,h=690):
    im=Image.new("RGB",(w,h),"white"); return im,ImageDraw.Draw(im)

def rounded(draw,xy,fill,outline=None,r=22,width=3): draw.rounded_rectangle(xy,radius=r,fill="#"+fill,outline="#"+outline if outline else None,width=width)

def make_cover_art():
    im=Image.new("RGB",(1500,520),"#"+NAVY); d=ImageDraw.Draw(im)
    # Topographic contour pattern on the right; decorative only.
    for k in range(14):
        box=(780+k*10,35+k*4,1460-k*14,465-k*7)
        d.arc(box,195,535,fill="#2b7281",width=3)
    d.rectangle((0,0,25,520),fill="#"+TEAL)
    d.text((90,88),"U-RESCUE",font=font(74,True),fill="white")
    d.text((96,192),"FLOOD RISK AND ROUTE DECISION SUPPORT",font=font(27,True),fill="#b9dce2")
    d.text((96,265),"Hyderabad and Sangareddy · Telangana",font=font(25),fill="white")
    d.line((96,335,610,335),fill="#"+GOLD,width=5)
    d.text((96,375),"PROJECT STAGE I REPORT",font=font(24,True),fill="#f4d18a")
    im.save(ASSETS/"cover.png")

def make_figures():
    # Figure 1: configured study boundary, clearly marked as schematic.
    im,d=image_base(); x0,y0,x1,y1=130,95,1360,570
    d.rectangle((x0,y0,x1,y1),outline="#"+BLUE,width=6)
    d.text((x0+28,y0+22),"Configured study boundary",font=font(28,True),fill="#"+NAVY)
    d.text((x0+25,y1+19),"77.5°E",font=font(20),fill="#"+GREY); d.text((x1-115,y1+19),"78.6°E",font=font(20),fill="#"+GREY)
    d.text((40,y0+6),"17.8°N",font=font(19),fill="#"+GREY); d.text((40,y1-24),"17.1°N",font=font(19),fill="#"+GREY)
    pts=[("Sangareddy",78.08,17.63),("Hyderabad",78.49,17.39)]
    for name,lon,lat in pts:
        x=x0+(lon-77.5)/(78.6-77.5)*(x1-x0); y=y0+(17.8-lat)/(.7)*(y1-y0)
        d.ellipse((x-15,y-15,x+15,y+15),fill="#"+TEAL,outline="white",width=3); d.text((x+22,y-12),name,font=font(24,True),fill="#"+NAVY)
    d.text((x0,y1+58),"Schematic using configured coordinates; not a navigation map.",font=font(20),fill="#"+GREY)
    im.save(ASSETS/"study_area.png")
    # Figure 2: processing pipeline.
    im,d=image_base(); labels=[("HGT elevation\ntiles","HGT"),("Validate and clip\nstudy extent","GIS"),("Derive elevation,\nslope and rank","GRID"),("FastAPI routes\nand map layers","API"),("Map display and\nroute comparison","UI")]
    xs=[45,345,645,945,1245]
    for i,(title,tag) in enumerate(labels):
        x=xs[i]; rounded(d,(x,205,x+210,425),PALE,BLUE,24,4); d.text((x+26,235),tag,font=font(25,True),fill="#"+TEAL)
        for j,line in enumerate(title.split("\n")): d.text((x+25,300+j*42),line,font=font(22,True),fill="#"+NAVY)
        if i<4:
            d.line((x+215,315,x+285,315),fill="#"+GOLD,width=7); d.polygon([(x+285,302),(x+308,315),(x+285,328)],fill="#"+GOLD)
    d.text((80,500),"Implemented chain for the terrain layer; a road graph and current hazard feeds are separate inputs and are not presently available.",font=font(20),fill="#"+GREY)
    im.save(ASSETS/"pipeline.png")
    # Figure 3: application architecture.
    im,d=image_base(); blocks=[(70,115,400,250,"Browser interface","MapLibre GL JS"),(570,115,900,250,"Application API","FastAPI"),(1070,115,1400,250,"Routing engine","NetworkX graph"),(300,380,630,525,"Terrain grid","NumPy arrays"),(850,380,1180,525,"Hazard polygons","Optional GeoJSON")]
    for x0,y0,x1,y1,a,b in blocks:
        rounded(d,(x0,y0,x1,y1),LIGHT,BLUE,22,4); d.text((x0+22,y0+33),a,font=font(26,True),fill="#"+NAVY); d.text((x0+22,y0+85),b,font=font(22),fill="#"+TEAL)
    arrows=[((400,180),(565,180)),((900,180),(1065,180)),((735,255),(465,375)),((735,255),(1015,375))]
    for (ax,ay),(bx,by) in arrows:
        d.line((ax,ay,bx,by),fill="#"+GOLD,width=6); ang=math.atan2(by-ay,bx-ax); p1=(bx-17*math.cos(ang-.5),by-17*math.sin(ang-.5));p2=(bx-17*math.cos(ang+.5),by-17*math.sin(ang+.5));d.polygon([p1,p2,(bx,by)],fill="#"+GOLD)
    d.text((360,585),"Request and response flow; local road JSON cache is required for route calculation.",font=font(20),fill="#"+GREY)
    im.save(ASSETS/"architecture.png")
    # Figure 4: conceptual cost equation.
    im,d=image_base(); d.text((120,80),"Route selection combines distance and available terrain evidence",font=font(31,True),fill="#"+NAVY)
    rounded(d,(140,180,1360,340),PALE,BLUE,25,4)
    d.text((220,235),"Edge cost = edge length × (distance weight + risk weight × terrain score)",font=font(29,True),fill="#"+NAVY)
    d.text((180,410),"Terrain score",font=font(25,True),fill="#"+TEAL); d.rectangle((400,414,705,470),fill="#"+BLUE); d.text((438,427),"Elevation rank 55%",font=font(21,True),fill="white")
    d.rectangle((705,414,1010,470),fill="#"+TEAL); d.text((735,427),"Inverse slope 45%",font=font(21,True),fill="white")
    d.text((180,520),"Unknown terrain adds a configured penalty. The score is a heuristic, not a probability or observed flood value.",font=font(19),fill="#"+GREY)
    im.save(ASSETS/"cost_model.png")

def shade(cell,fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)

def set_repeat_table_header(row):
    trPr=row._tr.get_or_add_trPr(); repeat=OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true'); trPr.append(repeat)

def no_split(row):
    trPr=row._tr.get_or_add_trPr(); el=OxmlElement('w:cantSplit'); trPr.append(el)

def add_field(paragraph,code):
    run=paragraph.add_run(); begin=OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'),'begin'); instr=OxmlElement('w:instrText'); instr.set(qn('xml:space'),'preserve'); instr.text=code; sep=OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'),'separate'); txt=OxmlElement('w:t'); txt.text='1'; end=OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'),'end'); run._r.extend([begin,instr,sep,txt,end])

def set_cell_text(cell,text,bold=False,color=NAVY,size=9):
    cell.text=''; p=cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.space_after=Pt(2); r=p.add_run(str(text)); r.bold=bold;r.font.name='Arial';r.font.size=Pt(size);r.font.color.rgb=RGBColor.from_string(color)

def build_doc():
    make_cover_art();make_figures()
    d=Document(); sec=d.sections[0]; sec.page_width=Inches(8.27);sec.page_height=Inches(11.69);sec.top_margin=Inches(.78);sec.bottom_margin=Inches(.72);sec.left_margin=Inches(1.18);sec.right_margin=Inches(.78)
    sec.header_distance=Inches(.34);sec.footer_distance=Inches(.35);sec.different_first_page_header_footer=True
    styles=d.styles
    normal=styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10.4);normal.font.color.rgb=RGBColor.from_string('243746');normal.paragraph_format.line_spacing=1.14;normal.paragraph_format.space_after=Pt(5);normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for name,size,color in [('Title',29,NAVY),('Heading 1',19,NAVY),('Heading 2',13,BLUE),('Heading 3',11,TEAL)]:
        s=styles[name];s.font.name='Arial';s.font.size=Pt(size);s.font.bold=True;s.font.color.rgb=RGBColor.from_string(color);s.paragraph_format.keep_with_next=True;s.paragraph_format.space_before=Pt(12 if name!='Title' else 0);s.paragraph_format.space_after=Pt(6)
    if 'Caption' not in styles:
        styles.add_style('Caption',WD_STYLE_TYPE.PARAGRAPH)
    styles['Caption'].font.name='Arial';styles['Caption'].font.size=Pt(9);styles['Caption'].font.italic=True;styles['Caption'].font.color.rgb=RGBColor.from_string(GREY)
    # Header and footer.
    hp=sec.header.paragraphs[0];hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT;r=hp.add_run('U-RESCUE  |  PROJECT STAGE I');r.font.name='Arial';r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY)
    fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=fp.add_run('U-RESCUE  •  ');r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY);add_field(fp,'PAGE')
    # helpers
    def p(text='',bold_lead=None,align=None,style=None):
        para=d.add_paragraph(style=style)
        if align is not None: para.alignment=align
        if bold_lead and text.startswith(bold_lead): para.add_run(bold_lead).bold=True;para.add_run(text[len(bold_lead):])
        else: para.add_run(text)
        return para
    def center(text,size=12,bold=False,color=NAVY):
        para=d.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(7);run=para.add_run(text);run.bold=bold;run.font.name='Arial';run.font.size=Pt(size);run.font.color.rgb=RGBColor.from_string(color);return para
    def placeholder(label):
        para=d.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_before=Pt(3);para.paragraph_format.space_after=Pt(6);r=para.add_run(f'[[{label}]]');r.bold=True;r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('8B5D00');shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'FFF1C7');r._r.get_or_add_rPr().append(shd);return para
    def heading(text,level=1): d.add_heading(text,level=level)
    def page(): d.add_page_break()
    def table(headers,rows,widths=None,font_size=8.6):
        t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.style='Table Grid';t.autofit=False
        if widths:
            for col,w in zip(t.columns,widths): col.width=Inches(w)
        for c,h in zip(t.rows[0].cells,headers):set_cell_text(c,h,True,'FFFFFF',font_size);shade(c,NAVY)
        set_repeat_table_header(t.rows[0]);no_split(t.rows[0])
        for ri,row in enumerate(rows):
            cells=t.add_row().cells;no_split(t.rows[-1])
            if widths:
                for c,w in zip(cells,widths):c.width=Inches(w)
            for c,val in zip(cells,row):set_cell_text(c,val,False,NAVY,font_size);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri%2==1:
                for c in cells:shade(c,'F1F6F8')
        d.add_paragraph().paragraph_format.space_after=Pt(1)
        return t
    def figure(path,caption,width=6.25):
        para=d.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(1);para.add_run().add_picture(str(ASSETS/path),width=Inches(width));cap=d.add_paragraph(caption,style='Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    def bullets(items):
        for item in items:
            para=d.add_paragraph(style='List Bullet');para.paragraph_format.space_after=Pt(3);para.add_run(item)
    def numbered(items):
        for index,item in enumerate(items,1):
            para=d.add_paragraph();para.paragraph_format.left_indent=Inches(.3);para.paragraph_format.first_line_indent=Inches(-.24);para.paragraph_format.space_after=Pt(3);para.add_run(f'{index}.  {item}')

    # Cover
    para=d.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(20);para.add_run().add_picture(str(ASSETS/'cover.png'),width=Inches(6.25))
    center('AUTONOMOUS AI-POWERED DISASTER RISK ASSESSMENT',19,True,NAVY);center('AND SAFEST-ROUTE RECOMMENDATION SYSTEM',18,True,NAVY)
    center('Design and modelling study for flood-risk route decision support',12,False,TEAL)
    d.add_paragraph();center('MNR SCHOOL OF ENGINEERING AND TECHNOLOGY',17,True,NAVY);center('PROJECT STAGE I',12,True,BLUE);center('Academic year 2025–2029',10,False,GREY)
    page()
    # Title page
    center('MNR SCHOOL OF ENGINEERING AND TECHNOLOGY',17,True,NAVY);center('B.TECH CSE (AI&ML)',13,True,BLUE);center('PROJECT STAGE I REPORT',12,True,TEAL)
    d.add_paragraph();center('U-RESCUE',30,True,NAVY);center('Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System',16,True,NAVY);center('Hyderabad and Sangareddy, Telangana',12,False,GREY)
    d.add_paragraph();center('Submitted in partial fulfilment of the requirements for the award of',10,False,GREY);center('BACHELOR OF TECHNOLOGY (B.TECH)',13,True,BLUE)
    t=d.add_table(rows=0,cols=2);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False;t.columns[0].width=Inches(3.05);t.columns[1].width=Inches(3.05)
    for a,b in [('Submitted by','Project guide'),('M. Jitendra Durga Prasad – 25RBAIM0007\nT. Gnana Sree – 25RBAIM0036\nK. Narsimha – 25RBAIM0008\nT. Sai Priya – 25RBAIM0003','Dr. Mahmood Mir Hussain\nAssistant Professor'),('Batch 2025–2029, Section A','B.Tech CSE (AI&ML)\nMNR School of Engineering and Technology')]:
        cells=t.add_row().cells;cells[0].width=Inches(3.05);cells[1].width=Inches(3.05);set_cell_text(cells[0],a,True,BLUE,10);set_cell_text(cells[1],b,True,BLUE,10)
    d.add_paragraph();center('Sangareddy, Telangana  |  November 2026',10,True,GREY)
    page()
    # College certificate
    heading('Certificate from the College',1);center('CERTIFICATE',13,True,BLUE)
    p('This is to certify that the project report entitled “U-RESCUE: Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System” is a bona fide record of work carried out by the student team listed below, under the supervision of the project guide, during Project Stage I in partial fulfilment of the requirements for the Bachelor of Technology (B.Tech) degree at MNR School of Engineering and Technology.')
    p('M. Jitendra Durga Prasad (25RBAIM0007), T. Gnana Sree (25RBAIM0036), K. Narsimha (25RBAIM0008), and T. Sai Priya (25RBAIM0003), Batch 2025–2029, Section A.')
    p('The work presented in this report is submitted for academic review. The signatories below verify this certification in accordance with the institution’s normal review and approval process.')
    d.add_paragraph();table(['Role','Name and designation','Signature','Date'],[['Project guide','Dr. Mahmood Mir Hussain, Assistant Professor','________________','__________'],['Head of Department','','________________','__________'],['Principal / authorised signatory','','________________','__________']],[1.35,2.45,1.25,1.0],9)
    center('Department seal / institutional stamp',9,False,GREY)
    page()
    # External guide certificate
    heading('Certificate from the External Guide',1);center('EXTERNAL GUIDE CERTIFICATE',13,True,BLUE)
    p('This certificate is provided for completion by the external organisation and guide, if applicable. The project team and work are identified below; external organisation and guide particulars are intentionally left blank for handwritten completion.')
    p('This is to certify that M. Jitendra Durga Prasad (25RBAIM0007), T. Gnana Sree (25RBAIM0036), K. Narsimha (25RBAIM0008), and T. Sai Priya (25RBAIM0003), B.Tech CSE (AI&ML), MNR School of Engineering and Technology, carried out Stage I design and modelling work for the project entitled “U-RESCUE: Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System” under external guidance. The technical description and observations are subject to the limitations and source acknowledgements recorded in this report.')
    d.add_paragraph();table(['External guide','Details'],[['Name',''],['Designation',''],['Organisation',''],['Signature',''],['Date','']],[2.0,4.0],10)
    page()
    # Acknowledgement
    heading('Acknowledgement',1)
    p('We express our sincere gratitude to MNR School of Engineering and Technology and the Department of B.Tech CSE (AI&ML) for providing the academic setting in which this Stage I project was developed. We thank Dr. Mahmood Mir Hussain, Assistant Professor, for guidance on the project scope, review of the project scope, design and modelling approach, and advice on presenting the engineering work clearly.')
    p('We acknowledge the maintainers of the open-source software used in the prototype, including Python, NumPy, NetworkX, FastAPI and MapLibre GL JS, and the OpenStreetMap community and OpenFreeMap for the map data and visualisation services described in the implementation. The elevation raster files were supplied with the project materials; their original provider, licence and acquisition date were not embedded in the files and remain to be confirmed before external redistribution.')
    p('We also thank our classmates, family members and all others who offered feedback during the project. Any remaining errors in the design, preliminary artefacts or report are our responsibility.')
    d.add_paragraph();center('M. Jitendra Durga Prasad · T. Gnana Sree · K. Narsimha · T. Sai Priya',10,True,BLUE);center('November 2026  ·  Sangareddy, Telangana',10,False,GREY)
    page()
    # Vision and mission
    heading('Vision and Mission of the Institution and Department',1)
    p('The following statements must be replaced with the officially published vision and mission of the institution and department. They are intentionally not inferred from the project topic.')
    for title,label in [('Institution vision','OFFICIAL INSTITUTION VISION'),('Institution mission','OFFICIAL INSTITUTION MISSION'),('Department vision','OFFICIAL DEPARTMENT VISION'),('Department mission','OFFICIAL DEPARTMENT MISSION')]:
        heading(title,2);placeholder(label)
    p('Project alignment. U-RESCUE applies software engineering and geospatial analysis to a public-safety problem. Its educational value lies in data handling, algorithm design, interface development, testing and communicating uncertainty. Operational decisions remain with emergency authorities and people on the ground.')
    page()
    # Abstract
    heading('Abstract',1)
    p('Flood evacuation decisions depend on both destination and route. A shortest-distance route can pass through low terrain, while an apparently elevated destination may have no accessible path or may be affected by hazards that the available data do not describe. U-RESCUE is currently a Stage I design and modelling project for a future web-based decision-support system in the configured Hyderabad and Sangareddy study area of Telangana.')
    p('Stage I defines the proposed data workflow, terrain-screening concept, graph-based route-cost model, system architecture and map interaction. Preliminary workspace artefacts include HGT processing outputs, route and API code, and a draft MapLibre interface. These artefacts support design exploration; they are not a completed integrated project or validated flood-evacuation system. The conceptual terrain score combines relative elevation rank (55%) with inverse slope (45%), but these weights are not calibrated. The route design includes distance, terrain, unknown-data penalties and optional observed-flood and closure inputs.')
    p('The processed grid contains 211 by 331 samples at an approximate 371 m spacing, with elevations from 424 m to 727 m and no missing sampled cells in the current metadata. The source elevation provenance and date are unknown. The current workspace does not contain a road cache or configured observed-flood, rainfall, drainage, river or closure layers. Therefore, route calculation is unavailable until a road extract is acquired, and no result can establish current passability or safety. At this Stage I, the model is a heuristic design and preliminary data-processing artefact, not a trained machine-learning model, flood forecast, emergency dispatch service or validated safe-route navigator.')
    p('The report documents the Stage I design and modelling work, preliminary data/software artefacts, proposed algorithms and architecture, readiness analysis, limitations and staged plan for completing subsequent project work. It recommends treating outputs as preliminary screening information and verifying every operational decision with current official information and field conditions.')
    center('Keywords: flood risk, evacuation routing, digital elevation model, terrain susceptibility, GIS, decision support, uncertainty',9,False,GREY)
    page()
    # Lists
    heading('List of Figures',1)
    figs=[('Figure 1.1','Configured study boundary schematic','13'),('Figure 4.1','Terrain processing and application workflow','19'),('Figure 5.1','U-RESCUE software architecture','20'),('Figure 5.2','Illustrative route cost composition','20')]
    for label,title,page_no in figs:p(f'{label}    {title}    {page_no}')
    p('Page references reflect the final 29-page Stage I design and modelling report.',style='Caption')
    page();heading('List of Tables',1)
    tablelist=[('Table 3.1','Functional requirements','16'),('Table 3.2','Non-functional requirements','16'),('Table 4.1','Dataset inventory and status','18'),('Table 4.2','Terrain grid summary','19'),('Table 5.1','API summary','21'),('Table 6.1','Verification matrix','22'),('Table 7.1','Prioritised future work','24')]
    for label,title,page_no in tablelist:p(f'{label}    {title}    {page_no}')
    p('Page references reflect the final 29-page Stage I design and modelling report.',style='Caption')
    page();heading('Abbreviations',1)
    table(['Abbreviation','Meaning'],[
      ('API','Application Programming Interface'),('CRS','Coordinate Reference System'),('DEM','Digital Elevation Model'),('GIS','Geographic Information System'),('HGT','Height/elevation tile binary format used by the supplied data'),('HTTP','Hypertext Transfer Protocol'),('JSON','JavaScript Object Notation'),('MVP','Minimum Viable Product'),('OSM','OpenStreetMap'),('ODbL','Open Database License'),('UI','User Interface'),('U-RESCUE','Project name for the flood-risk and route decision-support prototype'),('UTC','Coordinated Universal Time'),('WGS 84','World Geodetic System 1984, geographic coordinate reference')],[1.35,4.75],9)
    page();heading('Table of Contents',1)
    toc=[('Front matter',''),('1 Introduction','12'),('2 Background and related approaches','14'),('3 Requirements and project scope','16'),('4 Data and geospatial methodology','18'),('5 System design and modelling','20'),('6 Analysis and Stage I design status','22'),('7 Stage I conclusion and work remaining','24'),('References','25'),('Appendix A Preliminary prototype notes','27'),('Appendix B API and data dictionary','28'),('Appendix C Validation checklist','29')]
    for title,num in toc:p(title+('  ............................................................  '+num if num else ''))
    p('Page references reflect the final 29-page Stage I design and modelling report.',style='Caption')
    page()
    # Chapter 1
    heading('1 Introduction',1)
    heading('1.1 Background',2)
    p('Flooding can disrupt roads, isolate neighbourhoods and make normal navigation unreliable. A route planner that optimises only distance or travel time does not account for the fact that road conditions can change during an event. A useful early-stage decision-support tool should make the evidence behind route choices visible, identify what is missing, and avoid presenting a computed line as proof that a route is safe.')
    heading('1.2 Problem statement',2)
    p('This Stage I project is in the design and modelling phase. It defines how elevation-based terrain screening, candidate destination assessment and road-network route comparison could support flood evacuation decisions in the configured study area. Preliminary code and a draft interface exist as supporting engineering artefacts, but they do not constitute a completed project or validated system. Event flood observations, verified closures and a usable local road graph are unavailable, so end-to-end route modelling and evaluation remain outstanding.')
    heading('1.3 Aim and objectives',2)
    p('The Stage I aim is to produce and review the system design and conceptual models for terrain screening and flood-aware route comparison, while documenting preliminary implementation work and the data and validation needed for later stages.')
    bullets(['Define intended users, problem boundaries and functional requirements.','Review the 32 supplied research-paper records and identify a cautious, evidence-based project gap.','Specify the terrain-data workflow and a transparent conceptual score using elevation and slope.','Design a road-graph route-cost model that accounts for distance, terrain, unknown data and optional hazard inputs.','Develop system architecture, data-flow, interface and API models to guide subsequent implementation.','Document preliminary code assets, missing inputs, modelling assumptions and the evaluation plan for later stages.'])
    heading('1.4 Scope and contribution',2)
    p('The design scope uses the configured extent 77.5°–78.6° E and 17.1°–17.8° N, labelled Hyderabad and Sangareddy, Telangana. Stage I focuses on requirements, literature review, data assessment, methodology, system architecture and conceptual terrain and routing models. Preliminary terrain processing and UI/code artefacts are available for illustration, but are provisional and do not mean that the project is complete. Real-time monitoring, verified shelters, live hazard feeds and trained AI inference are outside the present stage.')
    figure('study_area.png','Figure 1.1 Configured study boundary schematic. The rectangle shows the configured bounding coordinates; labels are illustrative and do not represent administrative boundaries.',5.6)
    heading('1.5 Report organisation',2)
    p('Chapter 2 outlines the principles behind DEM screening, graph routing and hazard-aware decision support. Chapter 3 defines users, requirements and scope. Chapter 4 records data sources and terrain processing. Chapter 5 presents the proposed architecture, data flow, cost model and preliminary design artefacts. Chapter 6 analyses data readiness and the current design/model status. Chapter 7 concludes the Stage I design work and lists the development, implementation and validation work that remains.')
    heading('1.6 Responsible use and safety',2)
    p('A route line is a model output, not an instruction from an emergency authority. Flooding changes rapidly, map data can be incomplete, and a route that was passable earlier may become dangerous. A person using the prototype must follow current official warnings, avoid entering moving or standing floodwater, and seek help through established emergency channels. The interface should preserve uncertainty next to the result, including where observations are missing. Location information is sensitive; users should understand that the browser location feature requires permission and should be able to decline it. The project must not store or publish an individual location history without a clearly defined need and consent.')
    page()
    # Chapter 2
    heading('2 Background and Related Approaches',1)
    heading('2.1 Terrain as a screening signal',2)
    p('The first eight papers in the supplied review are titled as machine-learning flood-susceptibility mapping or assessment studies [1–8]. The completed comparison summaries for papers [9–15] describe geospatial conditioning variables, remote sensing, machine learning or weighted-overlay methods across Indian basins and cities; paper [16] concerns future susceptibility under climate scenarios. These topics point to elevation, slope, rainfall, drainage, land cover and satellite observations as possible assessment inputs, while mapped susceptibility or inundation remains distinct from street-level route safety. The review includes Hyderabad, Telangana and Godavari-focused studies, whose reported outputs are risk/vulnerability or inundation maps rather than user-specific escape instructions [9–15]. Elevation and slope can help characterise relative terrain, but neither directly measures water depth, flow speed or road passability. A DEM is a sampled surface representation with spatial resolution, vertical error, date and coverage that affect interpretation. A coarse terrain grid can show broad elevation patterns but may smooth embankments, channels, retaining walls and street-scale grade changes. Elevation may also represent a surface model rather than bare earth depending on the source product. The present source metadata do not identify the provider or acquisition date, so the terrain layer is treated as static and of uncertain provenance.')
    heading('2.2 Route planning on a graph',2)
    p('A transport network can be represented as a directed graph: intersections or road points become vertices, while traversable road segments become edges. An edge can carry distance and descriptive attributes. A shortest-path algorithm finds a low-cost connected sequence between a start and destination. To account for hazards, the edge cost can include penalties or exclusions. The quality of a route recommendation depends not only on the graph algorithm but also on network coverage, directionality, access restrictions, turn rules, data freshness and the correctness of the hazard overlays.')
    page()
    heading('2.3 Hazard-aware cost models',2)
    p('The supplied papers on shelter suitability and selection use risk assessment, clustering, geospatial suitability and statistical or machine-learning methods to rank candidate locations [17–23]. They establish that destination selection is a distinct decision from route calculation. A high relative elevation point alone is not a verified shelter: capacity, access, exposure, land ownership and current conditions still matter. A weighted cost model can compare distance with a risk proxy. This offers a transparent baseline when calibrated event labels are unavailable, but it does not become a predictive flood model merely because its output is called a score. Weight selection controls trade-offs and should be justified using local observations and stakeholder needs. When a hazard value is missing, explicitly penalising and reporting unknown coverage is safer than silently treating unknown as zero risk; however, a penalty cannot substitute for direct observation.')
    heading('2.4 Related data and technology',2)
    p('Evacuation-planning literature spans reviews, GIS least-cost paths, integrated prediction-and-routing, heuristic path search, hydrodynamic optimisation, agent-based simulation, responder dispatch, and pedestrian behaviour [24–32]. This body of work means U-RESCUE should not claim novelty for flood-aware routing or for combining GIS and machine learning with evacuation planning. Stage I therefore defines a locally scoped design for linking terrain screening, candidate destination assessment and route comparison, with explicit treatment of missing data. The design remains to be implemented and evaluated as a complete workflow. The implementation uses a local HGT elevation input, a Python terrain pipeline, NetworkX graph operations, FastAPI endpoints and a MapLibre browser map. OpenStreetMap is the intended source of road-network features and carries database attribution and licensing obligations. The current road downloader documented in this workspace uses the public Overpass API, but public service failures prevented creation of a complete local road graph. Map tiles are supplied by OpenFreeMap and the application displays attribution to the service and OpenStreetMap contributors.')
    heading('2.5 Positioning of this project',2)
    p('U-RESCUE is currently a Stage I design and modelling project, not a completed evacuation platform. Its contribution at this stage is a documented problem definition, literature-grounded scope, system architecture, conceptual route-cost model and data-readiness analysis. Preliminary software artefacts provide design context but the integrated workflow is not complete. Its principal research and engineering gap is the lack of observed flood and passability data for model calibration and evaluation. The supplied 32-paper table is the basis for this thematic review; it provides DOI/source links, but omits full author and publication metadata, and its first eight analytical rows are unfilled. Bibliographic details should therefore be checked against the original publications before final academic binding. The report therefore separates Stage I design outputs, preliminary code artefacts, available data and work planned for later stages.')
    page()
    # Chapter 3
    heading('3 Requirements and Project Scope',1)
    heading('3.1 Intended users and operating context',2)
    p('The primary user is a person or analyst who needs to compare possible paths between two locations in the configured study area. A secondary user is a project developer or GIS analyst who prepares source layers, verifies data quality and configures the service. In a real flood event, users may be under time pressure and may have limited connectivity. The prototype is designed as a browser interface, but the current map depends on online tile services and the application server runs locally unless separately deployed.')
    heading('3.2 Functional requirements',2)
    table(['ID','Requirement','Stage I design status'],[
      ('FR-01','Display an interactive map with visible source attribution.','Design requirement; preliminary map UI artefact exists.'),('FR-02','Allow origin and destination selection by coordinate fields, map clicks or browser location.','Specified; draft UI controls exist and require review.'),('FR-03','Provide elevation/terrain screening and candidate terrain cells.','Terrain processing artefact exists; candidate cells are unverified.'),('FR-04','Calculate multiple route alternatives over a mapped road graph.','Route model is designed and code exists; no local road graph is available.'),('FR-05','Rank routes using distance and terrain proxy evidence.','Conceptual weighted cost is specified; calibration and evaluation remain.'),('FR-06','Allow optional observed-flood and closure polygon inputs.','Included in the design; no evidence layers are configured.'),('FR-07','Show route details, uncertainty and spoken turn guidance.','Specified; preliminary UI/API artefacts require integrated review.')],[.6,2.45,3.05],8.1)
    heading('3.3 Non-functional requirements',2)
    table(['Quality attribute','Design target and present constraint'],[
      ('Clarity','Make map selection, route comparison and limitations understandable; the present interface exposes multiple controls and needs usability review.'),('Reproducibility','Keep processing scripts, config and metadata with the project; raw input tiles are not currently in this workspace.'),('Performance','Use local cached graph and spatially limited evaluation in future; current route implementation scans the graph and may be slow at large scale.'),('Reliability','Report missing sources and return unavailable status rather than asserting safety.'),('Privacy','Browser location is requested only by user action; any external routing service would require explicit disclosure. Current local route endpoint uses server cache.'),('Maintainability','Separate settings, terrain processing, roads, routing, hazards and web UI into modules.')],[1.25,4.85],8.5)
    heading('3.4 Constraints and assumptions',2)
    p('The application assumes longitude/latitude coordinates in EPSG:4326 for requests and stored layers. The study boundary and raster coordinates are geographic, while the configuration names EPSG:32643 as the study CRS; the current processing path calculates approximate metres per degree rather than reprojecting the raster. The source HGT tiles are assumed to be structurally readable based on their reported dimensions. The system assumes that road attributes in a successfully acquired OSM snapshot are suitable for a basic graph, although access, turn restrictions and temporal closures require additional validation.')
    heading('3.5 Out of scope',2)
    bullets(['Automatic flood forecasting, hydrodynamic simulation or calibrated machine-learning classification.','Official emergency dispatch, verified shelter capacity or public warning issuance.','Live road closures, flood depth, river level, rainfall ingestion and crowdsourced incident verification.','Guaranteeing pedestrian accessibility, bridge safety, emergency vehicle access or road passability.','National coverage; the configured scope is a limited Telangana study area.'])
    p('These boundaries define what the prototype can responsibly demonstrate at this stage. A later implementation may add these capabilities only when suitable data, operational ownership, validation and user safeguards are available. They are not implied by the architecture or by the “AI-powered” wording of the initial project title.')
    heading('3.6 Stage I acceptance criteria',2)
    p('Stage I design acceptance is based on a reviewed problem statement, literature synthesis, requirements, data inventory, methodology, system architecture, conceptual route-cost model, explicit assumptions and a feasible evaluation plan. Existing code, a terrain grid and a draft interface are preliminary artefacts that can inform review; they are not the Stage I completion claim and do not establish end-to-end behaviour. Later implementation milestones should separately verify data processing, graph routing, hazard handling and interface integration. None of these checks certifies a route as safe.')
    p('A later operational acceptance decision requires separate evidence: complete road coverage, current and authoritative hazard layers, clear destination and travel-mode definitions, robust response under network outages, user accessibility review, event-based validation and approval by responsible emergency-management stakeholders. Performance claims must state the geographic coverage, data timestamps, test environment and failure cases. If any essential feed is stale or unavailable, the system should visibly downgrade its recommendation and direct the user to current official sources rather than hide the gap.')
    page()
    # Chapter 4
    heading('4 Data and Geospatial Methodology',1)
    heading('4.1 Study area and coordinate handling',2)
    p('The configured bounding box is [77.5, 17.1, 78.6, 17.8] in west, south, east, north order. It spans approximately 1.1 degrees of longitude and 0.7 degrees of latitude and is labelled “Hyderabad and Sangareddy, Telangana.” The raster and map layers are stored in geographic coordinates. The terrain processor estimates local east-west and north-south spacing using metres per degree at about 17.5° N. This is an approximation and differs from carrying out processing in the configured projected CRS, EPSG:32643.')
    heading('4.2 Dataset inventory',2)
    table(['Dataset','Coverage / resolution','Status and quality note'],[
      ('HGT elevation tiles n17e077 and n17e078','Adjacent tiles spanning 17–18° N and 77–79° E; reported 3601 × 3601 input tiles.','User-supplied in the original dataset folder. Provider, acquisition date and licence are not embedded; raw files are absent from this workspace.'),('Processed terrain grid','Study boundary; 211 × 331 sampled grid; about 371 m spacing.','Present as NPZ with elevation, slope, risk, coordinates and validity mask. Metadata reports full sample validity.'),('OpenStreetMap road network','Configured study extent; variable detail.','Downloader and graph conversion exist. No local road JSON cache is present; earlier Overpass attempts failed with truncation and HTTP 504.'),('Observed flood and closures','No configured extent.','Unavailable. Configuration values are null.'),('Rivers, drainage, rainfall and shelters','No project layer configured in current workspace.','Unavailable; the application cannot assess these conditions.')],[1.25,1.55,3.3],8.1)
    heading('4.3 Elevation processing',2)
    numbered(['Locate the two expected HGT tiles by their tile names and validate each raster dimensions against supported square tile sizes.','Mosaic adjacent tiles, retaining the shared boundary column once.','Clip the mosaic to the configured study-area bounding box.','Replace invalid elevation samples with no-data and calculate terrain gradients using local metric approximations.','Sample the elevation and slope surfaces at the configured stride of 12 source pixels.','Compute an empirical relative elevation rank for each valid sample and combine it with inverse slope to produce a heuristic terrain score.','Write the sampled arrays to terrain_risk_grid.npz and summarize source paths, dimensions, bounds, resolution, valid fraction and score method in terrain_metadata.json.'])
    heading('4.4 Proposed relative terrain score',2)
    p('For each valid sampled cell, elevation rank is estimated from its position in the distribution of sampled elevations. The Stage I conceptual model defines a terrain-screening proxy as:')
    center('Terrain proxy = 0.55 × (1 − elevation rank) + 0.45 × clip(1 − slope / 25°, 0, 1)',11,True,BLUE)
    p('The score is designed so that relatively low and gentle terrain receives a larger susceptibility value than relatively high or steep terrain. The term “susceptibility” is a modelling label, not an empirically calibrated flood probability. The score has no direct rainfall, drainage, river, soil, land-cover, observed inundation or road-condition component.')
    heading('4.5 Derived grid summary',2)
    table(['Measure','Current metadata'],[['Raster dimensions processed before sampling','2,521 × 3,961'],['Sampled grid dimensions','211 × 331'],['Configured geographic bounds','77.5–78.6° E; 17.1–17.8° N'],['Approximate sample spacing','371 m'],['Elevation range','424–727 m'],['Median sampled elevation','578 m'],['Valid fraction / sampled no-data','100% / 0%'],['Terrain score composition','55% relative elevation rank; 45% inverse slope']],[2.6,3.45],9)
    p('These statistics describe the stored grid, not current conditions. The native DEM provider, vertical datum, acquisition date, vertical accuracy and independent validation are not documented, so the values should be treated as approximate screening information.',style='Caption')
    figure('pipeline.png','Figure 4.1 Terrain processing and application workflow. The road graph is a separate dependency and is not currently cached.',6.05)
    heading('4.6 Consequences of missing inputs',2)
    p('The absence of river, drainage, observed flood and current road information means that the map cannot identify active inundation or determine whether a road is passable. A high elevation sample is only a relative terrain indication. It may be private land, inaccessible, isolated by a channel or unsuitable for shelter. The data quality record should therefore travel with any map export or route response, rather than being separated from the visual result. Before additional datasets are combined, their coordinate systems, dates, spatial accuracy, licences and no-data conventions must be checked.')
    page()
    # Chapter 5
    heading('5 System Design and Modelling',1)
    heading('5.1 Architecture',2)
    p('The proposed system follows a client-server architecture. The browser is designed to load a map and request terrain, status and route information from a FastAPI service. The backend design separates terrain preparation, road graph creation, route scoring, hazard geometry checks, configuration and presentation. Preliminary code artefacts illustrate portions of this architecture; the integrated design has not completed full data-to-route validation.')
    figure('architecture.png','Figure 5.1 U-RESCUE software architecture and data dependencies.',6.15)
    heading('5.2 Route cost and alternatives',2)
    p('The proposed route model represents road ways as a directed graph. Each road segment would carry endpoints, geometry, length, road class, name and available access attributes. For candidate edges, the model would sample the terrain grid and record whether hazard values are unknown. The conceptual generalized cost combines edge distance with a weighted terrain term and a nonzero unknown-data penalty. A configured observed-flood polygon would add cost, while a confirmed closure would exclude the edge. The design compares alternative paths with a distance-only reference. Preliminary code artefacts explore portions of this logic; the complete data-to-route model has not been integrated or evaluated.')
    figure('cost_model.png','Figure 5.2 Proposed conceptual route-cost model. The relative weighting is a design assumption and requires calibration before evaluation.',6.0)
    heading('5.3 Proposed API and data flow',2)
    table(['Proposed endpoint','Purpose','Design behaviour'],[
      ('GET /api/status','Report readiness and available data.','Should report when the required road graph is missing.'),('GET /api/layers','Return sampled terrain GeoJSON.','Would expose elevation, slope, terrain score and layer kind.'),('GET /api/safe-zones','Return terrain screening cells.','Would return low-confidence investigation candidates, not verified safe locations.'),('GET /api/hazards','Return configured flood/closure polygons.','Would indicate whether dated hazard files are configured.'),('GET /api/roads','Return road features from a cache.','Requires a complete road extract and populated local cache.'),('POST /api/routes','Request a route comparison.','Designed for origin, destination and alternatives; response would include route details, freshness and warnings.')],[1.25,1.75,3.0],8.15)
    heading('5.4 Draft user interface',2)
    p('The draft interface design includes coordinate entry, a browser live-location action, map-based origin/destination selection, route comparison and optional spoken directions. A planned status region reports data readiness and a results region displays candidate alternatives. The browser location API requires user permission. Before external deployment or service integration, the design must explain what location data are transmitted and to whom.')
    page()
    # Chapter 6
    heading('6 Analysis and Stage I Design Status',1)
    heading('6.1 Stage I review and later evaluation plan',2)
    p('Stage I analysis examines the research framing, requirements, data inventory, methodology, model assumptions and system architecture. The repository also contains test definitions for preliminary code components; their existence is not evidence of a complete or freshly verified implementation. Later implementation work should record test commands, data versions, dates, outcomes and failure cases, and should be conducted after the required source data are available.')
    table(['Design / model area','Evidence available in current workspace','Stage I interpretation'],[
      ('Terrain data','Processed NPZ arrays and metadata record dimensions, bounds, spacing and valid fraction.','Supports preliminary data analysis; source provenance and independent accuracy remain unverified.'),('Road network','No data/osm_roads.json cache is present.','The routing design depends on a road dataset that is not yet available locally.'),('Flood / closure inputs','No configured hazard features are loaded.','Hazard inputs remain planned; actual conditions are not assessed.'),('Evaluation design','Test definitions and validation checklist are present.','These describe future checks; no complete system or flood-safety validation is claimed.'),('Interface design','A draft web interface contains map and route-related controls.','Design artefact needs review and later integration with verified inputs.')],[1.25,2.55,2.2],8)
    heading('6.2 Data readiness findings',2)
    p('The current processed terrain grid has 69,841 samples (211 × 331 = 69,841) and reports full validity for the sampled study extent. Its approximate 371 m spacing is much coarser than a road or neighbourhood block. This limits its use for route-level hazard claims. Metadata gives a minimum of 424 m, maximum of 727 m and median of 578 m. The HGT source paths in metadata refer to an original Desktop dataset location outside the current repository; the raw tiles must be restored or separately archived to reproduce preprocessing.')
    p('The current road fetch workflow is based on the public Overpass API and its initial attempts, recorded in the project documentation, failed due to truncated JSON and HTTP 504 responses. The server starts without the cache and reports routing unavailable. The system therefore has no end-to-end route result to report from the supplied environment. This is a dependency gap, not proof that the route algorithm works across the full target region.')
    heading('6.3 Evaluation status',2)
    p('There are no labelled flood events, road-level water observations, historical closure records, verified shelter destinations or field inspection results in the project data inventory. Accordingly, the terrain score cannot be evaluated for discrimination, calibration, recall, precision or warning lead time. Route quality cannot be measured against an authoritative safe-route reference. Performance under event conditions, mobile connectivity and changing road access has not been established.')
    heading('6.4 Discussion',2)
    p('The Stage I design describes how a transparent terrain heuristic could be incorporated into a route-cost model and map interface. Preliminary code artefacts illustrate some components but do not demonstrate a completed, integrated flood-evacuation system. Its strongest design choice is separating the available static proxy from unavailable observations and returning warnings rather than silently substituting synthetic data. The main risk is user over-trust: map colours, precise coordinates and a route line can look authoritative even when their data are stale, coarse or incomplete. The UI and every export should keep the uncertainty visible, and should not use “safe route” as an unqualified label.')
    heading('6.5 Evaluation plan for later stages',2)
    p('After the design stage, the team should implement and integrate the system, then run and record the documented tests with actual data. For a later technical demonstration, obtain a road extract and verify route coverage, directions, closures, coordinate snapping, missing-data handling and map behaviour against manually checked sample cases. Record each test case, expected result, observed result and evidence artefact. Do not represent a passing software test as validation of flood safety.')
    p('A useful validation sequence begins with unit-level checks of raster dimensions, mask behaviour, coordinate ordering and score bounds. API checks should confirm malformed coordinates are rejected, missing road data is reported, closure inputs remove affected edges, observed-flood inputs apply the configured cost, and unknown terrain remains identifiable in the response. A map review should compare a set of known graph paths with their displayed geometry and verify that route labels and spoken guidance use the same route. Finally, only a dated, independently documented flood-event dataset can support analysis of whether routes avoided affected segments. The test record should include the data snapshot, software revision, environment and limitations so that results can be reproduced.')
    page()
    # Chapter 7
    heading('7 Stage I Conclusion and Work Remaining',1)
    heading('7.1 Stage I conclusion',2)
    p('U-RESCUE is in the design and modelling stage. Stage I defines a geospatial decision-support concept that links a sampled elevation surface, relative terrain screening, graph-based route comparison and a browser map. Preliminary code and data artefacts support exploration of this design, but the integrated project is not complete. The processed grid covers the configured Hyderabad and Sangareddy bounding box and contains 211 × 331 samples with approximate 371 m spacing. The score is a transparent elevation-and-slope heuristic. The route engine is designed to account for distance, terrain risk, unknown terrain, configured flood polygons and configured closures.')
    p('The present project state does not contain the road cache required for real route calculations, nor observed flood, river, drainage, rainfall or verified closure layers. The elevation source metadata is incomplete. No field or event validation establishes route safety. The report concludes that Stage I has established a design baseline for the subsequent development stages. Implementation, data integration, evaluation and validation remain in progress; the project is not ready for operational flood evacuation use. The title’s “AI-powered” phrase reflects the original project brief; the implemented model described here is rule-based and does not contain a trained AI model.')
    heading('7.2 Prioritised future work',2)
    table(['Priority','Work package','Completion evidence'],[
      ('1','Restore and identify the source DEM; document provider, date, licence, datum and resolution. Reproject processing to EPSG:32643 or justify the geographic approximation.','Manifest, checksums, CRS checks and independent elevation comparison.'),('2','Acquire and cache a legal, complete OSM road extract; assess walking/vehicle classes, access restrictions and graph coverage.','Acquisition timestamp, license attribution, graph coverage report and route samples.'),('3','Add authoritative, dated flood, river, drainage, rainfall and closure data where available; define staleness and source quality rules.','Data catalogue, update mechanism, validity checks and visible timestamps.'),('4','Define intended walking versus motor-vehicle routing and verified destination criteria.','User stories, route-network policy and reviewed destinations.'),('5','Evaluate candidate sites and routes against historical events and field records; calibrate weights.','Documented validation set, metrics, uncertainty analysis and independent review.'),('6','Conduct accessibility and usability testing, including screen-reader support, mobile layout and low-connectivity behaviour.','Task-based usability results and defect log.'),('7','Threat-model and deploy only after operational ownership, privacy, reliability and incident response are defined.','Security review, service monitoring, backup and update policy.')],[.65,3.25,2.1],8)
    heading('7.3 Final statement',2)
    p('The project establishes a useful technical foundation for flood-aware decision support, but the safety value of any route depends on current and verified geographic evidence. Until those data and validations are available, outputs must be treated as exploratory estimates and checked against local emergency instructions and conditions.')
    page()
    # References
    heading('References',1)
    p('References [1]–[32] are the 32 research-paper records supplied in the literature comparison document. That document provides titles, years and DOI/source links but not full author names, journal volume/issue/pages; verify and complete each record from the publisher before final binding. Citations in Chapter 2 refer to these records by number.')
    papers=[
      ('Geospatial and machine learning-based flood susceptibility assessment in Nagaon District, Assam, India','2026','https://doi.org/10.1080/10106049.2026.2677319'),
      ('Flood susceptibility mapping in the Kaljani River Basin, West Bengal, India using machine learning','2026','https://doi.org/10.1007/s44288-026-00410-y'),
      ('Comparative assessment of ensemble machine learning and Google Earth Engine for flood susceptibility mapping in the Dipota River Basin, Assam, India','2026','https://doi.org/10.1007/s44288-026-00638-8'),
      ('Integrating Machine Learning and Geospatial Analysis for Flood Hazard, Vulnerability, and Risk Assessment in Odisha, India','2026','https://doi.org/10.1007/s11269-026-04709-w'),
      ('Machine learning model optimization for flood susceptibility zonation over the Kosi Megafan, India','2025','https://doi.org/10.1038/s41598-025-07403-w'),
      ('Flood susceptibility mapping using optimized deep learning models: a non-structural framework','2025','https://doi.org/10.1007/s13201-025-02548-5'),
      ('Integrating machine learning and geospatial data analysis for comprehensive flood hazard assessment','2024','https://doi.org/10.1007/s11356-024-34286-7'),
      ('Flood susceptibility mapping using machine learning boosting algorithms techniques in Idukki district of Kerala, India','2023','https://doi.org/10.1016/j.uclim.2023.101503'),
      ('Flood Risk Assessment Using GIS and Remote Sensing Technology in Telangana State, India','2026','https://indianjournals.com/article/ije1-53-1-027'),
      ('Urban flood vulnerability assessment for Hyderabad city, India','2025','https://doi.org/10.1007/s44327-025-00161-4'),
      ('A holistic methodology for evaluating flood vulnerability, generating flood risk map and conducting detailed flood inundation assessment','2025','https://doi.org/10.1038/s41598-025-13025-z'),
      ('Flood Inundation Mapping of a River Stretch Using Machine Learning Algorithms in the Google Earth Engine Environment','2025','https://doi.org/10.1111/jfr3.70062'),
      ('Integration of multi-temporal SAR data and robust machine learning models for improvement of flood susceptibility assessment in the southwest coast of India','2024','https://www.sciencedirect.com/science/article/pii/S2590197424000363'),
      ('Development of an automated method for flood inundation monitoring, flood hazard, and soil erosion susceptibility assessment using machine learning and AHP-MCE techniques','2024','https://doi.org/10.1186/s40677-024-00275-8'),
      ('A novel machine learning tool for current and future flood susceptibility mapping by integrating remote sensing and geographic information systems','2024','https://doi.org/10.1016/j.jhydrol.2024.130936'),
      ('Impact of climate change on future flood susceptibility projections under shared socioeconomic pathway scenarios in South Asia using artificial intelligence algorithms','2024','https://doi.org/10.1016/j.jenvman.2024.121764'),
      ('Integrated machine-learning and clustering framework for selecting temporary shelters in flood-prone cities','2026','https://doi.org/10.1007/s11069-026-08371-8'),
      ('A Gaussian Process Regression-Based Geospatial Framework for Emergency Shelter Suitability Assessment','2026','https://doi.org/10.5194/isprs-annals-XI-M-1-2026-55-2026'),
      ('Modeling flood susceptibility and identifying optimal flood shelters for effective flood management in the Mahananda River Basin','2025','https://doi.org/10.1016/j.asr.2025.11.084'),
      ('Enhancing evacuation shelter suitability in compound hazard-prone regions with a Bayesian optimized convolutional neural network approach','2025','https://doi.org/10.1016/j.ijdrr.2025.105306'),
      ('An integrated statistical-geospatial approach for the delineation of flood-vulnerable sub-basins and identification of suitable areas for flood shelters in a tropical river basin, Kerala','2024','https://doi.org/10.1016/j.geogeo.2024.100251'),
      ('Selection of urban-flood-shelter locations based on risk assessment','2024','https://doi.org/10.1016/j.wen.2024.04.003'),
      ('Assessing critical flood-prone districts and optimal shelter zones in the Brahmaputra Valley: Strategies for effective flood risk management','2024','https://doi.org/10.1016/j.pce.2024.103772'),
      ('An overview of flood evacuation planning: Models, methods, and future directions','2025','https://doi.org/10.1016/j.jhydrol.2025.133026'),
      ('Dynamic Evacuation Route Planning for Flood-Prone Coastal Odisha Using GIS and Least-Cost Path Analysis','2026','https://doi.org/10.17485/IJST/v19i29.1052'),
      ('A GIS and Machine Learning Based Framework for Flood Risk Prediction and Dynamic Evacuation Routing in Chennai','2026','https://doi.org/10.1109/icssit69151.2026.11656607'),
      ('Simulating optimal flood evacuation using heuristic algorithms and path-choice behaviors','2025','https://doi.org/10.1016/j.simpat.2025.103167'),
      ('A novel emergency evacuation route optimization model in flood disasters using hydrodynamic model and intelligent algorithm','2025','https://doi.org/10.1016/j.ssci.2024.106709'),
      ('Large-scale real-time evacuation modeling during urban floods: A coupled agent-based multi-model framework','2025','https://doi.org/10.1016/j.simpat.2025.103075'),
      ('Shortest path planning and dynamic rescue forces dispatching for urban flood disasters','2025','https://doi.org/10.1038/s41598-025-06374-2'),
      ('An Integrated QGIS-Based Evacuation Route Optimization Approach for Disaster Preparedness Against Urban Flood in Japan','2025','https://doi.org/10.3390/geographies5040074'),
      ('Evacuation information methodology that combined a flooded environment and pedestrian behavioral model','2024','https://doi.org/10.1016/j.ijdrr.2024.104438')]
    for i,(title,year,url) in enumerate(papers,1):
        if i==17:
            page();heading('References (continued)',1)
        para=d.add_paragraph();para.paragraph_format.left_indent=Inches(.24);para.paragraph_format.first_line_indent=Inches(-.24);para.paragraph_format.space_after=Pt(2);para.paragraph_format.line_spacing=1.0
        run=para.add_run(f'[{i}] {title}. ({year}). ');run.font.size=Pt(8.2)
        run=para.add_run(url);run.font.size=Pt(8.2)
    other_refs=[
      '[33] Project team, “U-RESCUE project repository documentation and source code,” local project records, 2026.',
      '[34] OpenStreetMap contributors, “Copyright and License,” https://www.openstreetmap.org/copyright.',
      '[35] MapLibre, “MapLibre GL JS Documentation,” https://maplibre.org/maplibre-gl-js/docs/.',
      '[36] OpenFreeMap, “Getting Started,” https://openfreemap.org/.',
      '[37] FastAPI, “FastAPI Documentation,” https://fastapi.tiangolo.com/.',
      '[38] NetworkX developers, “NetworkX Documentation,” https://networkx.org/documentation/stable/.',
      '[39] NumPy developers, “NumPy Documentation,” https://numpy.org/doc/.',
      '[40] Python Software Foundation, “Python 3 Documentation,” https://docs.python.org/3/.'
    ]
    for ref in other_refs:
        para=d.add_paragraph();para.paragraph_format.left_indent=Inches(.24);para.paragraph_format.first_line_indent=Inches(-.24);para.paragraph_format.space_after=Pt(2);para.paragraph_format.line_spacing=1.0;run=para.add_run(ref);run.font.size=Pt(8.2)
    page()
    # Appendices
    heading('Appendix A Preliminary Prototype Notes',1)
    heading('A.1 Optional preliminary prototype setup',2)
    p('This appendix describes preliminary workspace artefacts for technical review only. Running local code does not mean that the Stage I project is complete, and the current workspace cannot generate a validated real-world evacuation route. A compatible Python installation and dependencies listed in requirements.txt are required. The raw HGT source files need to be restored to a directory configured through URESCUE_DATA_DIR before terrain processing can be reproduced. The road cache is required for route generation and is not currently available.')
    numbered(['Create and activate a virtual environment using the operating system’s standard Python commands.','Install the packages in requirements.txt.','Confirm that data/processed/terrain_risk_grid.npz and terrain_metadata.json exist. If they do not, restore the original HGT inputs and run scripts/process_terrain.py.','Acquire a complete, properly licensed road extract for the configured bbox and populate the expected cache at data/osm_roads.json; inspect /api/status after acquisition.','Review config.json and ensure hazard paths point only to authoritative, current and licensed GeoJSON polygon files.','Start the service with uvicorn app:app --reload and open http://127.0.0.1:8000/.','Check /api/status before routing. If road readiness is false, route requests are expected to return service unavailable.'])
    heading('A.2 Draft interface workflow',2)
    numbered(['Open the map and allow it to load.','Enter an origin and destination as longitude, latitude, or use the map selection controls. Browser geolocation is optional and permission is requested by the browser.','Select the route comparison action. Review the recommended route, alternatives, shortest-distance comparison, distance, terrain proxy and unknown-segment information.','Treat spoken directions as generated from the road graph and verify them with current conditions.','Do not rely on this prototype as the sole evacuation instruction; use official alerts, emergency services and on-the-ground information.'])
    heading('A.3 Reproducibility and data stewardship',2)
    p('For every input, preserve the source URL or handover record, acquisition date, provider, licence, checksum, spatial extent, CRS, units, temporal validity and processing command. Retain raw inputs unchanged and record derived outputs separately. Record software versions and logs for every report or demonstration release. Do not commit private credentials, user location histories or unlicensed data.')
    page()
    heading('Appendix B API and Data Dictionary',1)
    heading('B.1 Route request',2)
    p('POST /api/routes accepts a JSON object containing start and destination as two-number [longitude, latitude] arrays and an optional alternatives integer. Coordinates are expected in the configured study region and geographic coordinate order. Invalid values should be rejected. The route engine requires a loaded road graph.')
    table(['Request field','Type','Description'],[['start','array[number, number]','Origin longitude and latitude.'],['destination','array[number, number]','Destination longitude and latitude.'],['alternatives','integer, optional','Requested candidate route count, bounded by the API implementation.']],[1.55,1.65,3.1],9)
    heading('B.2 Route response concepts',2)
    table(['Response field','Meaning'],[['recommended','Lowest configured-cost returned candidate route. Not a verified safe route.'],['alternatives','Other generated graph paths for comparison.'],['shortest_route_comparison','Shortest-distance reference candidate under a distance-only cost setting.'],['distance_m','Summed distance of graph edges on the route.'],['predicted_risk_mean','Mean terrain proxy where terrain samples are available; not probability.'],['unknown_segments','Segments for which the terrain value could not be read.'],['observed_flood_segments','Segments whose sampled points intersect configured flood polygons.'],['directions','Turn text generated from edge geometry and road names.'],['data_freshness','Available road cache time and terrain source description.'],['warning','Decision-support uncertainty statement.']],[1.8,4.5],8.7)
    heading('B.3 Terrain grid variables',2)
    table(['Array','Shape / type','Description'],[['elevation','211 × 331, float32','Sampled elevation in metres as supplied/processed; datum/provider not verified.'],['slope','211 × 331, float32','Derived slope in degrees using local metric approximation.'],['risk','211 × 331, float32','Relative heuristic from elevation rank and inverse slope.'],['valid','211 × 331, Boolean','Validity mask for sampled elevation values.'],['lons','331, float64','Longitude coordinate for each grid column.'],['lats','211, float64','Latitude coordinate for each grid row.']],[1.25,1.55,3.5],8.5)
    p('The grid contains 69,841 sampled cells. Pixel spacing is approximate and values should not be interpreted as street-scale flood depth or a current hazard observation.',style='Caption')
    page()
    heading('Appendix C Pre-submission and Validation Checklist',1)
    table(['Check','Evidence required','Status'],[
      ('Institution details','Official institution and department names, vision, mission, degree, batch and academic year.','Names and programme supplied; official vision/mission text pending.'),('Certificates','Approved wording, signatures, dates and institutional seal; confirm any external guide details.','For institutional review.'),('References','Complete author, publication, volume, issue, pages and access details; verify citation mapping.','Publisher verification pending.'),('Terrain provenance','Provider, source link, acquisition date, licence, vertical datum, checksums and independent quality check.','Incomplete.'),('Road network','Successful extract, timestamp, licence attribution, graph coverage and route examples.','No cache in this workspace.'),('Hazard evidence','Authoritative flood/river/closure source, timestamp, spatial accuracy and freshness rules.','Not configured.'),('Algorithm validation','Historical event cases, field observations, baseline comparison and calibrated cost weights.','Not available.'),('Software verification','Actual test command, environment, pass/fail output and browser end-to-end evidence.','Run before final submission.'),('Safety/usability review','Reviewed wording, location permission behaviour, accessibility and user testing.','Not recorded.'),('Print preparation','Repaginate contents/lists, confirm 25–30 page rule, then prepare three thermal-bound copies.','After final review.')],[1.35,3.55,1.3],8.0)
    heading('C.1 Suggested staged validation protocol',2)
    numbered(['Choose several representative origin/destination pairs across the study area, including near-boundary points and areas where terrain samples are missing or flat.','Confirm the road graph connects each pair, route edge geometries match the map, and distance totals are consistent with edge lengths.','Create synthetic test polygons only in a non-production test fixture to verify the flood penalty and closure exclusion behaviour; never label a synthetic case as an observed event.','Compare the terrain proxy against independent, documented elevation or hydrological references and quantify spatial mismatch.','When event records become available, compare route rankings with recorded inundation and closure observations using a held-out evaluation set.','Conduct a field and emergency-management review before describing any destination or route as operationally suitable.'])
    p('This checklist is an academic and engineering aid. It does not certify the system for emergency use.',style='Caption')
    # Save
    d.core_properties.title='U-RESCUE Project Stage I Report'
    d.core_properties.subject='Stage I design and modelling for terrain screening and flood-aware route decision support'
    d.core_properties.author='[[STUDENT NAME(S)]]'
    d.core_properties.keywords='U-RESCUE, flood risk, GIS, terrain, route planning'
    path=OUT/'U-RESCUE_Project_Report_StageI_Design_Modelling.docx';d.save(path)
    print(path)

if __name__=='__main__':build_doc()

