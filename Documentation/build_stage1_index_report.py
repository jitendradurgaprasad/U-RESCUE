from pathlib import Path
import ast
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Project_Report'/'U-RESCUE_StageI_Report_Index_Aligned.docx'
tree=ast.parse((ROOT/'Documentation'/'build_project_report.py').read_text(encoding='utf-8'))
papers=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='papers' for t in node.targets):
        try: papers=ast.literal_eval(node.value)
        except Exception: pass
if len(papers)!=32: raise RuntimeError(f'Expected 32 supplied paper records; found {len(papers)}')
refs=sorted([(i,*v) for i,v in enumerate(papers,1)],key=lambda x:x[1].casefold())
newnum={old:i for i,(old,*_) in enumerate(refs,1)}
def cite(ids): return '['+', '.join(str(newnum[i]) for i in ids)+']'

NAVY='12304A'; BORDER='CBD5DA'
d=Document()
def margins(sec):
    sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
    sec.left_margin=Inches(1.575);sec.right_margin=Inches(.59);sec.top_margin=Inches(1.18);sec.bottom_margin=Inches(1.18)
    sec.header_distance=Inches(.45);sec.footer_distance=Inches(.45)
margins(d.sections[0])
styles=d.styles
n=styles['Normal'];n.font.name='Times New Roman';n.font.size=Pt(12);n.font.color.rgb=RGBColor.from_string('000000');n.paragraph_format.line_spacing=2.0;n.paragraph_format.space_after=Pt(0);n.paragraph_format.first_line_indent=Inches(.5);n.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,size in [('Title',16),('Heading 1',16),('Heading 2',14),('Heading 3',12)]:
    st=styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.bold=True;st.font.color.rgb=RGBColor.from_string('000000');st.paragraph_format.line_spacing=2.0;st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(0);st.paragraph_format.keep_with_next=True

def centered(txt,size=12,bold=False):
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Inches(0);p.paragraph_format.line_spacing=2.0;r=p.add_run(txt);r.font.name='Times New Roman';r.font.size=Pt(size);r.bold=bold;return p
def para(txt,first=True):
    p=d.add_paragraph();p.paragraph_format.first_line_indent=Inches(.5) if first else Inches(0);p.paragraph_format.line_spacing=2.0;p.paragraph_format.space_after=Pt(0);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;p.add_run(txt);return p
def heading(txt,level=1):
    p=d.add_paragraph(style=f'Heading {level}');p.paragraph_format.first_line_indent=Inches(0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER if level==1 else WD_ALIGN_PARAGRAPH.LEFT;p.add_run(txt);return p
def bullet(items):
    for item in items:
        p=d.add_paragraph();p.paragraph_format.left_indent=Inches(.35);p.paragraph_format.first_line_indent=Inches(-.2);p.paragraph_format.line_spacing=2.0;p.paragraph_format.space_after=Pt(0);p.add_run('•  '+item)
def table(headers,rows,widths,size=9):
    t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,txt in zip(t.rows[0].cells,headers):
        c.text='';p=c.paragraphs[0];p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(1);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=p.add_run(txt);r.bold=True;r.font.name='Times New Roman';r.font.size=Pt(size);r.font.color.rgb=RGBColor.from_string('FFFFFF');sh=OxmlElement('w:shd');sh.set(qn('w:fill'),NAVY);c._tc.get_or_add_tcPr().append(sh);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    rep=OxmlElement('w:tblHeader');rep.set(qn('w:val'),'true');t.rows[0]._tr.get_or_add_trPr().append(rep)
    for ri,row in enumerate(rows):
        cs=t.add_row().cells
        if widths:
            for c,w in zip(cs,widths):c.width=Inches(w)
        for c,txt in zip(cs,row):
            c.text='';p=c.paragraphs[0];p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(1);r=p.add_run(str(txt));r.font.name='Times New Roman';r.font.size=Pt(size);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if ri%2:
            for c in cs:sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F3F6F7');c._tc.get_or_add_tcPr().append(sh)
    borders=OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'5');el.set(qn('w:color'),BORDER);borders.append(el)
    t._tbl.tblPr.append(borders);d.add_paragraph().paragraph_format.line_spacing=1;return t
def page_field(p,code='PAGE'):
    r=p.add_run();b=OxmlElement('w:fldChar');b.set(qn('w:fldCharType'),'begin');ins=OxmlElement('w:instrText');ins.set(qn('xml:space'),'preserve');ins.text=code;s=OxmlElement('w:fldChar');s.set(qn('w:fldCharType'),'separate');t=OxmlElement('w:t');t.text='1';e=OxmlElement('w:fldChar');e.set(qn('w:fldCharType'),'end');r._r.extend([b,ins,s,t,e])

# Cover and title pages: Stage I manuscript; print instructions distinguish the bound copy.
for _ in range(3):d.add_paragraph()
centered('MNR UNIVERSITY',16,True);centered('SCHOOL OF ENGINEERING AND TECHNOLOGY AND AI',14,True);centered('PROJECT STAGE I REPORT',16,True)
d.add_paragraph();centered('U-RESCUE',16,True);centered('Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System',14,True);centered('Design and Modelling Stage',12,True)
d.add_paragraph();centered('Sangareddy, Telangana',12);centered('Academic Year 2025–2029',12);d.add_page_break()
for _ in range(2):d.add_paragraph()
centered('A PROJECT STAGE I REPORT ON',14,True);centered('U-RESCUE',16,True);centered('Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System',14,True)
d.add_paragraph();centered('Submitted in partial fulfilment of the requirements for the award of',12);centered('Bachelor of Technology in Computer Science and Engineering (AI&ML)',12,True);d.add_paragraph();centered('Submitted by',12,True)
for nm,rn in [('M. Jitendra Durga Prasad','25RBAIM0007'),('T. Gnana Sree','25RBAIM0036'),('K. Narsimha','25RBAIM0008'),('T. Sai Priya','25RBAIM0003')]:centered(f'{nm} ({rn})',12)
d.add_paragraph();centered('Under the guidance of',12,True);centered('Dr. Mahmood Mir Hussain',12,True);centered('Assistant Professor',12);d.add_paragraph();centered('DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING (AI&ML)',12,True);centered('School of Engineering and Technology and AI',12);centered('MNR University',12,True);centered('Sangareddy, Telangana  |  November 2026',12)

# Roman-numbered front matter.
front=d.add_section(WD_SECTION.NEW_PAGE);margins(front);front.footer.is_linked_to_previous=False;front.footer.paragraphs[0].text='';front.footer.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER;page_field(front.footer.paragraphs[0])
pg=front._sectPr.find(qn('w:pgNumType')) or OxmlElement('w:pgNumType')
if pg.getparent() is None:front._sectPr.append(pg)
pg.set(qn('w:fmt'),'lowerRoman');pg.set(qn('w:start'),'1')

heading('CERTIFICATE FROM THE COLLEGE')
para('This is to certify that the Project Stage I Report entitled “U-RESCUE: Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System”, submitted by M. Jitendra Durga Prasad (25RBAIM0007), T. Gnana Sree (25RBAIM0036), K. Narsimha (25RBAIM0008), and T. Sai Priya (25RBAIM0003), in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering (AI&ML), is a record of the design and modelling work carried out under the guidance of Dr. Mahmood Mir Hussain during Academic Year 2025–2029. The work recorded here is limited to the design and modelling stage; implementation and validation remain subsequent project work.')
para('The report is submitted for academic review in accordance with applicable institutional requirements.',False);d.add_paragraph()
table(['Project Guide','Head of Department','Director','External Examiner'],[['Signature: __________','Signature: __________','Signature: __________','Signature: __________'],['Name: Dr. Mahmood Mir Hussain','','',''],['Designation: Assistant Professor','','',''],['Date: __________','Date: __________','Date: __________','Date: __________']],[1.55,1.55,1.5,1.5],8);para('Submitted for Viva-Voce Examination held on: ______________________________',False);d.add_page_break()

heading('CERTIFICATE FROM THE EXTERNAL GUIDE')
para('This page is provided for completion by the external organization and guide, if applicable. External organization and guide particulars are left blank for handwritten completion.')
para('This is to certify that the students named below carried out work entitled “U-RESCUE: Autonomous AI-Powered Disaster Risk Assessment and Safest-Route Recommendation System” under external guidance for the period recorded by the organization. The Stage I material covered here is limited to topic knowledge, scope and objectives, literature review, methodology, analysis and design/modelling.')
para('Student team: M. Jitendra Durga Prasad (25RBAIM0007); T. Gnana Sree (25RBAIM0036); K. Narsimha (25RBAIM0008); T. Sai Priya (25RBAIM0003).',False);d.add_paragraph()
table(['External guide / organization particulars','To be completed by external organization'],[['Name',''],['Designation',''],['Organization',''],['Project duration',''],['Signature and seal',''],['Date','']],[2.5,3.6],10);d.add_page_break()

heading('ACKNOWLEDGEMENT')
para('We express our sincere gratitude to MNR University and the School of Engineering and Technology and AI for providing the academic environment for this Stage I project. We thank our project guide, Dr. Mahmood Mir Hussain, Assistant Professor, for guidance in defining the scope and reviewing the design and modelling direction.')
para('We acknowledge the institutional material supplied for this report, the 32 research-paper records supplied for the literature review, and the open-source and geospatial communities whose tools and data sources informed the proposed system design. The original elevation-data provider, acquisition date, licence and vertical datum remain to be confirmed.')
para('This report records work through the design and modelling stage only. We are responsible for the accuracy of the work presented and for completing source verification and subsequent project stages.')
d.add_paragraph();centered('M. Jitendra Durga Prasad  |  T. Gnana Sree  |  K. Narsimha  |  T. Sai Priya',11,True);centered('Sangareddy, Telangana  |  November 2026',11);d.add_page_break()

heading('VISION AND MISSION OF THE INSTITUTION AND DEPARTMENT')
heading('MNR University Vision',2);para('At MNR University, we envision a future where limitless academic exploration lays the foundation for sustainable, community-driven global development. Our vision is to build a collaborative ecosystem that transforms eager students into visionary pioneers, guiding them to lead with wisdom, resilience, and empathy.')
heading('MNR University Mission',2);para('Our mission is to provide an immersive, student-centric academic journey that promotes intellectual curiosity, embraces diverse perspectives, and drives real-world problem-solving. We strive to equip our graduates with the specialised skills and ethical grounding necessary to thrive in an ever-evolving world.')
heading('School of Engineering and Technology and AI Vision',2);para('To lead as a pioneering institution in futuristic engineering and technology education, driving societal progress through cutting-edge research, real-world exposure, and hands-on learning for impactful outcomes')
heading('School Mission',2);para('Academic and Research Excellence: To deliver quality education that combines rigorous academics, industry excellence, and extensive research opportunities, fostering critical thinking and innovation.')
para('Experiential Learning and Practical Skills: Through experiential and hands-on learning, enhance skills and knowledge, equipping graduates to tackle complex, multi-disciplinary engineering challenges and contribute positively to society.')
para('Culture and Ethical Practices: We promote a culture of continuous improvement, collaboration, and ethical practices, preparing students to excel in a dynamic & international environment.')
d.add_page_break()

heading('ABSTRACT')
para('U-RESCUE is a Project Stage I design and modelling study for flood-risk decision support in a configured Hyderabad and Sangareddy area of Telangana. The design connects terrain screening, destination assessment and road-network route comparison. Elevation and slope support broad screening but do not establish flood depth, road passability or shelter safety.')
para('Work through Design/Modelling includes scope and objectives, thematic review of 32 supplied paper records, data/methodology design, analysis of available terrain metadata, and a conceptual architecture and route-cost model. The terrain concept weights relative elevation rank (55%) and inverse slope (45%). These uncalibrated values are design assumptions, not predictions.')
para('The available grid has 211 × 331 samples at about 371 m spacing. Its source provenance is incomplete. No local road graph, observed flood or verified closure layers are available; no route validation is claimed. Preliminary code artefacts support design exploration, but the integrated project remains in progress. Implementation, testing and event-based evaluation belong to later stages.')
para('This report covers only work through Design/Modelling. Project Report Submission and Semester II activities are not recorded as complete.',False)
para('Keywords: flood evacuation, digital elevation model, GIS, terrain screening, route modelling, decision support, uncertainty.',False);d.add_page_break()

heading('LIST OF FIGURES')
for x in ['Figure 6.1  Proposed system architecture .................................................... 15','Figure 6.2  Conceptual route-cost model .......................................................... 16']:para(x,False)
d.add_page_break();heading('LIST OF TABLES')
for x in ['Table 2.1  Stage I objectives ...................................................................... 4','Table 3.1  Themes in the 32-paper literature review ...................................... 8','Table 5.1  Available data and analysis findings ............................................. 12','Table 5.2  Data-quality and design risks ....................................................... 13','Table 6.1  Functional design requirements ................................................... 14','Table 6.2  Proposed system components ..................................................... 15']:para(x,False)
d.add_page_break();heading('ABBREVIATIONS')
table(['Abbreviation','Meaning'],[('AI','Artificial Intelligence'),('API','Application Programming Interface'),('CSE','Computer Science and Engineering'),('DEM','Digital Elevation Model'),('GIS','Geographic Information System'),('HGT','Height/elevation tile format used in supplied inputs'),('ML','Machine Learning'),('OSM','OpenStreetMap'),('SAR','Synthetic Aperture Radar'),('U-RESCUE','Flood-risk and route decision-support design'),('WGS 84','World Geodetic System 1984')],[1.4,4.8],10)
d.add_page_break();heading('TABLE OF CONTENTS')
for x in ['Certificate from the College ................................................................. i','Certificate from the External Guide ........................................................ ii','Acknowledgement .................................................................................. iii','Institution and Department Vision/Mission ............................................. iv','Abstract ................................................................................................. vi','List of Figures ....................................................................................... vii','List of Tables ........................................................................................ viii','Abbreviations ......................................................................................... ix','1 Knowledge on Topic/Area ..................................................................... 1','2 Project Scope and Objectives ............................................................... 4','3 Identifying Research Gaps (Literature Review) ..................................... 6','4 Detailed Methodology ............................................................................ 9','5 Analysis ............................................................................................... 12','6 Design/Modelling .................................................................................. 14','References/Bibliography ......................................................................... 18','Appendix A Papers Published / Contribution from the Work ..................... 20']:para(x,False)

# Arabic page numbering begins with Chapter 1.
body=d.add_section(WD_SECTION.NEW_PAGE);margins(body);body.footer.is_linked_to_previous=False;body.footer.paragraphs[0].text='';body.footer.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER;page_field(body.footer.paragraphs[0])
pg=body._sectPr.find(qn('w:pgNumType'))
if pg is None:pg=OxmlElement('w:pgNumType');body._sectPr.append(pg)
pg.set(qn('w:fmt'),'decimal');pg.set(qn('w:start'),'1')

# Chapter 1: Knowledge on topic/area.
d.add_heading('1 KNOWLEDGE ON TOPIC/AREA',0)
heading('1.1 Flood evacuation as a spatial decision problem',2)
para('Flooding can make usual travel routes unsafe or unusable. A decision-support system for evacuation must consider where a person starts, which destination may be appropriate, and which connecting route has lower exposure to known hazards. Distance alone does not represent water, terrain, closures, bridge conditions, access restrictions or shelter capacity. Conditions may change during a flood, so a model must communicate when its data are incomplete or stale.')
heading('1.2 Terrain and elevation',2)
para('A digital elevation model stores elevation values at sampled locations. Elevation and slope help describe broad terrain patterns. Lower, flatter terrain may warrant further assessment because water can accumulate there, while slope and drainage context affect water movement. However, elevation is not a measurement of flood depth or flow velocity. A coarse DEM also smooths street-level structures, embankments, channels and small grade changes. Terrain is therefore a screening input and must be combined with hydrology, rainfall, drainage, flood observations and local knowledge before drawing safety conclusions.')
heading('1.3 GIS and road-network routing',2)
para('A geographic information system brings spatial layers together using coordinates and geometry. A road network can be modelled as a graph: junctions or road points are nodes, and traversable segments are edges. Edges can have lengths and properties such as road class and access. A shortest-path algorithm minimizes distance or another defined cost. A risk-aware model can add costs for terrain exposure, observed inundation or uncertain information, and exclude confirmed closures. Reliability depends on network coverage, connectivity, directionality, access rules and data freshness as much as on the algorithm.')
heading('1.4 AI, statistical models and transparent heuristics',2)
para('Machine-learning flood-susceptibility models are commonly trained using conditioning variables and event labels. Their usefulness depends on representative training data, feature quality, validation design and transferability to the local area. U-RESCUE Stage I does not include a trained or evaluated AI model. Its proposed terrain score is a transparent heuristic. The “AI-powered” wording follows the original project title, but this report does not describe a completed AI prediction system.')
heading('1.5 Study-area context and responsible interpretation',2)
para('The project materials configure a bounding extent of 77.5–78.6 degrees east and 17.1–17.8 degrees north, described in the repository as Hyderabad and Sangareddy, Telangana. This is a configured study extent rather than a verified administrative boundary. The project is intended to develop design and modelling knowledge relevant to flood-related route decisions. It is not an emergency warning authority, shelter registry or navigation service.')
heading('1.6 Core concepts learned',2)
bullet(['A high point is not automatically a safe or reachable shelter.','A terrain susceptibility score is not a flood probability.','A low-cost route is only as credible as the road and hazard data used to calculate it.','Unknown information must remain visible and must not be silently treated as safe.','Operational flood decisions require current authoritative alerts and field conditions.'])
para('The knowledge area supports a bounded design: use terrain to screen and compare, use road graphs to represent connectivity, and keep uncertainty and verification requirements attached to proposed outputs.',False)
d.add_page_break()

# Chapter 2: Project scope and objectives.
d.add_heading('2 PROJECT SCOPE AND OBJECTIVES',0)
heading('2.1 Project aim',2)
para('The aim of Stage I is to define a transparent system design and conceptual models that connect elevation-based terrain screening, candidate destination assessment and road-network route comparison for flood-related decision support in the configured Telangana study extent. The Stage I deliverable is the problem definition, literature-grounded scope, methodology, analysis of available data and proposed design/modelling. Full system implementation, execution, testing and validation remain later project work.')
heading('2.2 Objectives completed through Design/Modelling',2)
para('Table 2.1 Stage I objectives',False)
table(['No.','Objective'],[('1','Study the flood-evacuation problem, terrain concepts, GIS, DEM limitations and graph routing.'),('2','Define intended users, geographic scope, assumptions, exclusions and responsible-use boundaries.'),('3','Review 32 supplied research-paper records and formulate a cautious local design/evaluation need.'),('4','Specify terrain-data processing and a transparent relative screening model.'),('5','Analyze data readiness, spatial resolution, provenance gaps and unavailable route/hazard inputs.'),('6','Design the system architecture, data flow, conceptual terrain score and route-cost model.')],[.6,5.6],10)
heading('2.3 Scope',2)
para('The design covers the configured Hyderabad/Sangareddy bounding extent and an intended browser-based interface. It includes assessment of user needs, elevation and slope screening, conceptual candidate locations for investigation, road-network route modelling, missing-data penalties, optional hazard layers, API/data flow and uncertainty communication. Existing scripts, terrain arrays and interface elements in the workspace are preliminary artefacts that may inform the design; they do not constitute a complete integrated project.')
heading('2.4 Out of scope at this stage',2)
bullet(['Validated flood forecasting, hydrodynamic simulation and trained machine-learning classification.','Official shelter designation, capacity, accessibility or landowner approval.','Live river, rainfall, flood-depth, drainage, satellite-event or road-closure feeds.','A verified road graph and live route recommendations.','Field validation, emergency dispatch, public alerts and guarantees of road passability.','Project Report Submission and Semester II activities as completed work.'])
heading('2.5 Assumptions and constraints',2)
para('The available terrain metadata are assumed to describe the current processed grid but do not identify the original provider, acquisition date, licence or vertical datum. Processing is stored in geographic coordinates and uses approximate local metric spacing rather than a fully reprojected analysis grid. A road graph is assumed to be obtainable later from a properly licensed source, but the present workspace has no cached graph. Model weights are conceptual and uncalibrated. These assumptions limit the strength of conclusions drawn at this stage.')
heading('2.6 Stage boundary',2)
para('Progress recorded for the current semester ends at index item 6, Design/Modelling. Item 7, Project Report Submission, and all Semester II activities are not recorded as completed. This report is a working Stage I manuscript documenting the work through design/modelling; its existence does not assert that formal submission activity has already been completed.')
d.add_page_break()

# Chapter 3: Literature review.
d.add_heading('3 IDENTIFYING RESEARCH GAPS (LITERATURE REVIEW)',0)
heading('3.1 Review basis and organization',2)
para(f'The supplied comparison table contains 32 paper records with titles, years and DOI/source links. The records are organized into flood susceptibility and mapping {cite(range(1,17))}, shelter suitability and selection {cite(range(17,24))}, and evacuation planning and route methods {cite(range(24,33))}. The comparison document leaves the analysis fields for its first eight entries unfilled and omits complete author/publication details. This review therefore uses its titles and completed summaries as a thematic guide; specific claims and bibliography metadata must be verified against original papers before final binding.')
heading('3.2 Flood susceptibility and inundation mapping',2)
para('The first group concerns flood susceptibility, hazard and inundation mapping in Indian basins and cities. Methods indicated by the supplied records include machine learning, ensemble and boosting methods, deep-learning approaches, remote sensing, Google Earth Engine, SAR imagery and weighted geospatial analysis. Telangana and Hyderabad studies make the theme regionally relevant. These works show how elevation, slope, rainfall, drainage, land cover, flow accumulation and satellite observations can contribute to spatial hazard assessment. Mapped susceptibility or inundation should not be conflated with a user-specific route or verified street passability.')
heading('3.3 Shelter suitability research',2)
para('The shelter-focused group studies suitable locations using geospatial risk, terrain and other selection criteria. The supplied comparison indicates methods such as clustering, statistical/geospatial analysis and machine learning. These works show that deciding where people should go is distinct from mapping flood risk. A high-elevation cell alone is not an operational shelter: capacity, access, ownership, surrounding hazards and current conditions require separate evidence. U-RESCUE can design a candidate-screening concept but cannot label locations as verified shelters with current information.')
heading('3.4 Evacuation planning and routing research',2)
para('The evacuation group covers review work, GIS least-cost paths, combined flood-risk prediction and dynamic routing, heuristic path choice, hydrodynamic optimization, agent-based simulation, rescue-force dispatch and pedestrian behaviour. This literature shows that flood-aware routing and integration of GIS with prediction have already been studied. U-RESCUE therefore makes no broad novelty claim. A defensible contribution is to define a locally configured, transparent design that brings terrain screening, candidate destination assessment and route comparison into one workflow while keeping missing evidence visible, then evaluate that design in later stages.')
heading('3.5 Identified project gap',2)
para('The Stage I gap is framed as a design and evaluation need, not an assertion that no related system exists: a locally scoped workflow must specify how available elevation evidence, candidate destinations, road connectivity and hazard uncertainty would be combined, while distinguishing terrain screening from observed flood conditions and verified shelter safety. The current project also faces an engineering readiness gap: source provenance is incomplete, terrain resolution is coarse for street-level decisions, no local road graph is available, and no authoritative event or closure layers are configured. These conditions prevent empirical evaluation at this stage.')
heading('3.6 Stage I response to the gap',2)
para('The current semester addresses this gap through problem framing, requirements, thematic comparison of the supplied literature, data inventory, terrain and route methodology, conceptual cost models and architecture. It does not claim to close the implementation or validation gap. Subsequent work must acquire and verify data, complete integration, test model behaviour and compare outputs with documented flood and closure observations.')
para('Table 3.1 Literature themes in the supplied paper set',False)
table(['Literature theme','Typical output described in source review','Relevance to U-RESCUE Stage I'],[(f'Susceptibility / inundation {cite(range(1,17))}','Risk classes, susceptibility maps or event inundation maps.','Informs terrain/environment factors; not a personal route.'),(f'Shelter suitability {cite(range(17,24))}','Candidate shelter zones or suitability rankings.','Shows destination selection needs multiple criteria and verification.'),(f'Evacuation routing {cite(range(24,33))}','Routes, evacuation scenarios, travel behaviour or resource allocation.','Informs route-cost and graph design; no novelty claim for routing itself.')],[1.45,2.25,2.5],9)
d.add_page_break()

# Chapter 4: Detailed methodology.
d.add_heading('4 DETAILED METHODOLOGY',0)
heading('4.1 Design workflow',2)
para('The Stage I methodology is specified as a sequence of data and modelling decisions. It begins with documenting input provenance and spatial coverage, proceeds through terrain screening and route-graph design, and ends with a planned evaluation framework. The proposed data-to-output chain is: elevation inputs; coordinate and quality checks; terrain derivatives; candidate-screening rules; road graph; route-cost model; map/API design; and later evaluation against authoritative evidence.')
heading('4.2 Study extent and coordinate system',2)
para('The configured bounding box is 77.5–78.6 degrees east and 17.1–17.8 degrees north. Its label in project configuration is Hyderabad and Sangareddy, Telangana. Coordinates are handled geographically in WGS 84. Project documentation names EPSG:32643 as a projected study CRS, but the available terrain processing uses approximate metres-per-degree calculations. A later implementation should reproject terrain into an appropriate metric CRS before deriving local slope and distance-sensitive quantities, and record the CRS and transformations.')
heading('4.3 Elevation input and preparation',2)
para('Two adjacent HGT elevation tiles were supplied in the original dataset location and are reflected in processed metadata. Their source/provider, acquisition date, licence and vertical datum are not confirmed. The planned reproducible workflow validates file sizes and raster dimensions, combines adjoining tiles while handling the shared boundary, clips the mosaic to the configured extent, identifies no-data values, and records processing parameters and checksums. Raw inputs should remain unchanged, with derived surfaces and metadata stored separately.')
heading('4.4 Terrain derivatives and screening model',2)
para('The available metadata describe a sampled terrain grid of 211 by 331 cells. For each valid cell, elevation rank is a relative position within the sampled elevation distribution. Slope is derived from elevation change and approximate horizontal spacing. The conceptual terrain-screening score is:')
centered('T = 0.55 × (1 − elevation rank) + 0.45 × clip(1 − slope / 25°, 0, 1)',11,True)
para('The score assigns larger values to relatively lower and gentler terrain. It is a heuristic proxy, not flood probability or predicted water depth. Its weights are design choices requiring sensitivity analysis and calibration against local evidence. Candidate cells selected with low proxy values or a slope threshold are points for further investigation, not verified safe destinations.')
heading('4.5 Road graph and route-cost model',2)
para('The proposed road model represents junctions as vertices and road segments as directed edges. An edge may carry length, geometry, road class, name and available access attributes. The planned generalized route cost for an edge combines its distance with a weighted terrain term and a penalty for unknown terrain. If authoritative flood polygons later become available, intersecting edges can receive a high cost; verified closure polygons can remove edges. Alternative routes can be compared against a distance-only route. Each result should report what evidence and timestamps informed it.')
centered('C(edge) = length(edge) × [w_d + w_t × terrain_score(edge) + w_u × unknown(edge)] + hazard_cost(edge)',11,True)
para('The terms and weights require specification, sensitivity analysis and later calibration. Missing data must remain visible and must not be interpreted as a low-risk observation. The project currently has no cached road graph or configured hazard polygons, so these calculations are a design model and preliminary code exploration rather than a validated study-area result.')
heading('4.6 Proposed system architecture and user flow',2)
para('The proposed architecture separates the browser map, API service, terrain data, road-graph routing and optional hazard inputs. A user would select an origin, select a destination or candidate location, request a comparison, and review candidate paths alongside terrain layers, data-readiness status and uncertainty. Browser geolocation would require explicit user permission. Before external deployment, the system design must specify location-data handling, service availability and map/data attribution.')
heading('4.7 Planned evaluation method',2)
para('Later evaluation should verify data coverage, coordinate transformations, graph connectivity, route geometry and distance totals on documented test cases. The terrain score should be compared with an independent elevation reference. If dated flood and road-closure records become available, route rankings can be assessed against affected and unaffected segments using held-out cases and clearly reported measures. Candidate locations require independent access and suitability review. Unit or API tests alone cannot validate flood safety.')
d.add_page_break()

# Chapter 5: Analysis.
d.add_heading('5 ANALYSIS',0)
heading('5.1 Available terrain-data analysis',2)
para('Processed metadata describe a 211 × 331 grid, or 69,841 sampled cells, with approximate spacing of 371 metres. Elevation values range from 424 metres to 727 metres, with a reported median of 578 metres and no sampled no-data cells. These figures describe the stored terrain product only. The source provider, date, datum, independent vertical accuracy and reproducible raw inputs have not been established. The spatial spacing is much coarser than a road or neighbourhood block, so the grid cannot support street-level flood-depth or passability conclusions.')
para('Table 5.1 Available data and analysis findings',False)
table(['Analysis item','Current finding','Implication for Stage I design'],[('Terrain extent','77.5–78.6°E; 17.1–17.8°N configured bounds.','Confirm local projection and actual administrative coverage.'),('Grid size','211 × 331 samples; 69,841 cells.','Suitable for broad screening only, not street-level detail.'),('Approximate spacing','About 371 m.','Small channels, roads and embankments may not be resolved.'),('Elevation range','424–727 m; median 578 m.','Relative values lack verified datum/provenance.'),('Road network','No local road cache.','Study-area route generation cannot be demonstrated.'),('Hazard/shelter observations','No observed flood, closure, river, rainfall, drainage or verified shelter layers.','No empirical hazard or safety assessment can be made.')],[1.25,2.2,2.75],9)
heading('5.2 Model and data limitations',2)
para('The terrain proxy combines only relative elevation and slope. It omits rainfall, soil, land cover, flow accumulation, drainage capacity, observed water, river level, road elevation and infrastructure condition. The 55/45 weighting has not been fitted to event records. A candidate location may be inaccessible or unsuitable even if its terrain is higher. A road may be flooded even if the surrounding terrain score is low. These limitations are central to interpreting the model and must be visible in presentation and future interface design.')
heading('5.3 Readiness analysis',2)
para('The project has sufficient information to define the study extent, inspect the processed grid and design a modular system. It does not have the minimum evidence needed for a study-area route demonstration: a complete local road graph and current or historical hazard data. Consequently, this stage can analyze spatial-data readiness and model assumptions but cannot report route performance, flood-prediction accuracy, safety improvement or validation metrics.')
heading('5.4 Risk analysis and mitigation',2)
para('Table 5.2 Data-quality and design risks',False)
table(['Risk','Why it matters','Stage I response / later action'],[('Unverified elevation source','Datum, date or quality may differ from assumptions.','Record provenance; independently compare elevations before relying on values.'),('Coarse terrain sampling','May hide local channels, walls or road grades.','Treat output as regional screening; acquire finer DEM for local routing.'),('Missing road graph','No connected path can be computed.','Acquire a legal dated extract and report coverage/access assumptions.'),('No active hazard feed','Flooded/closed links cannot be identified.','Use authoritative dated feeds or event records; expose staleness.'),('User over-trust','A precise map line may look safe.','Use qualified language, visible uncertainty and emergency-source guidance.')],[1.25,2.2,2.75],9)
heading('5.5 Analysis conclusion',2)
para('Current evidence supports continued design and data preparation. It does not support operational conclusions. The main analytical result at this stage is identification of missing evidence and spatial-resolution limits, together with a model structure that can be reviewed and refined before later implementation.')
d.add_page_break()

# Chapter 6: Design and modelling.
d.add_heading('6 DESIGN/MODELLING',0)
heading('6.1 Functional design requirements',2)
para('Table 6.1 Functional design requirements',False)
table(['ID','Design requirement','Stage I status'],[('FR1','Display a spatial map with clear source attribution.','Specified; draft interface artefact exists.'),('FR2','Allow origin and destination selection, with optional browser geolocation.','Specified; interaction design requires review.'),('FR3','Display elevation/slope screening and candidate investigation locations.','Concept defined; candidates are not verified safe zones.'),('FR4','Compare route alternatives using a road graph.','Route model specified; graph data unavailable.'),('FR5','Include distance, terrain and unknown-data terms in route cost.','Conceptual model defined; weights uncalibrated.'),('FR6','Support future observed-flood and closure layers.','Design requirement; no layers configured.'),('FR7','Show readiness, uncertainty and route details.','Specified; integrated behaviour remains later work.')],[.65,3.2,2.35],9)
heading('6.2 System architecture model',2)
para('The proposed system has five logical components. The data-preparation component validates and transforms elevation sources. The terrain-analysis component derives slope and relative terrain screening values. The road-network component stores a directed graph. The routing component calculates distance and terrain-related generalized costs while accepting future hazard overlays. The presentation component provides the map, inputs, status, results and explanatory warnings. A FastAPI service is proposed between browser and spatial-processing components; MapLibre is proposed for map display. Existing code artefacts cover parts of this structure but are not a completed integrated system.')
ip=d.add_paragraph();ip.alignment=WD_ALIGN_PARAGRAPH.CENTER;ip.paragraph_format.first_line_indent=Inches(0);ip.paragraph_format.line_spacing=1;ip.add_run().add_picture(str(ROOT/'Project_Report'/'assets'/'architecture.png'),width=Inches(5.2))
cap=d.add_paragraph('Figure 6.1 Proposed U-RESCUE system architecture and data dependencies');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.paragraph_format.first_line_indent=Inches(0);cap.paragraph_format.line_spacing=1
para('Table 6.2 Proposed system components',False)
table(['Component','Input','Designed output'],[('Terrain preparation','HGT tiles and configuration','Clipped terrain grid and provenance metadata.'),('Terrain screening','Elevation, slope, validity mask','Relative score and candidate cells for investigation.'),('Road graph','Licensed road extract','Directed graph and edge attributes.'),('Route model','Origin, destination, graph, terrain, optional hazards','Ranked candidate paths and evidence summary.'),('Browser/API','User selections and model outputs','Map layers, status, route comparison and uncertainty text.')],[1.25,2.1,3.0],9)
heading('6.3 Data-flow model',2)
para('A planned request begins when a user chooses an origin and destination. The application checks whether required data are available. If road data are missing, it should return a clear unavailable status rather than an empty or falsely safe route. If inputs exist, coordinates are associated with graph nodes, candidate routes are generated, edge costs are evaluated, and route geometry and evidence metadata are returned to the map. The interface should distinguish static terrain proxies from current observations and show unknown segments and data timestamps.')
heading('6.4 Conceptual route model',2)
para('The routing design compares two notions of cost. A distance-only path gives a baseline. A generalized path cost adds terrain and uncertainty terms and may later incorporate flood and closure evidence. The lowest configured generalized cost is only the preferred candidate under stated model assumptions. It is not a probability that the route is safe. Weight changes can change route ranking; later work should perform sensitivity analysis and compare outcomes against observed cases.')
ip=d.add_paragraph();ip.alignment=WD_ALIGN_PARAGRAPH.CENTER;ip.paragraph_format.first_line_indent=Inches(0);ip.paragraph_format.line_spacing=1;ip.add_run().add_picture(str(ROOT/'Project_Report'/'assets'/'cost_model.png'),width=Inches(5.2))
cap=d.add_paragraph('Figure 6.2 Conceptual route-cost model specified for later calibration');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.paragraph_format.first_line_indent=Inches(0);cap.paragraph_format.line_spacing=1
heading('6.5 Interface and output model',2)
para('The intended map view contains a basemap with attribution, a terrain-screening overlay, an origin marker, a selected destination or candidate location, and route alternatives when the required network is available. A status panel should show road-data readiness, hazard-data availability and freshness. A result panel should describe distance, terrain evidence, unknown data and any configured hazard intersections. Candidate terrain points must be labelled for investigation rather than as safe shelters. Browser location should be requested only after a user action.')
heading('6.6 Stage I design decisions and remaining modelling work',2)
para('Stage I establishes the design boundary, conceptual equations, system components, inputs, outputs and major assumptions. Remaining design work includes selecting a metric processing CRS, defining walking versus vehicle routing, specifying candidate-destination suitability criteria, documenting edge-cost weights and unknown-data behaviour, defining API schemas, and setting evaluation measures. Later implementation and testing will determine whether the proposed system behaves as designed; flood-event validation remains separate.')
heading('6.7 Chapter conclusion',2)
para('The design and modelling stage yields a reviewable system concept for terrain screening and route comparison and identifies conditions needed for later implementation. It does not conclude the overall U-RESCUE project. Experimental setup, implementation, execution/testing, further documentation, findings/validation, report submission and viva remain subsequent activities.')

# References follow alphabetical title order because the supplied comparison file omits authors.
d.add_page_break();heading('REFERENCES / BIBLIOGRAPHY')
para('The supplied comparison table gives titles, years and DOI/source links but omits full author and publication metadata. To follow the handbook’s alphabetical arrangement as far as available information permits, entries are alphabetized by title in this Stage I draft. Add verified authors, journal/conference, volume, issue and page numbers from the original publications before final binding. The original comparison number is retained for traceability.',False)
for new,(old,title,year,url) in enumerate(refs,1):
    p=d.add_paragraph();p.paragraph_format.left_indent=Inches(.3);p.paragraph_format.first_line_indent=Inches(-.3);p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(4);p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    rr=p.add_run(f'[{new}] {title}. ({year}). {url} [Original comparison no. {old}]');rr.font.name='Times New Roman';rr.font.size=Pt(10)

d.add_page_break();heading('APPENDIX A PAPERS PUBLISHED / CONTRIBUTION FROM THE WORK')
heading('A.1 Papers published from the current project stage',2)
para('No paper publication from U-RESCUE is recorded as of November 2026. No manuscript, conference submission or acceptance is claimed in this Stage I report.')
heading('A.2 Contribution recorded at the Design/Modelling boundary',2)
bullet(['A documented problem definition and configured local study extent.','A thematic literature review of 32 supplied research-paper records and a restrained gap statement.','A data inventory and analysis of terrain resolution and missing evidence.','A proposed terrain-screening heuristic and conceptual route-cost formulation with explicit uncertainty terms.','A proposed component architecture, data flow and user-facing output design.','A staged plan for implementation, experimental setup, testing and validation in later project work.'])
para('These are Stage I design and modelling contributions. They do not establish a completed operational application or validated safe route.',False)

d.core_properties.title='U-RESCUE Project Stage I Report through Design and Modelling'
d.core_properties.subject='Report aligned to the supplied project index and MNR Stage I guidelines'
d.core_properties.author='MNR School of Engineering and Technology and AI student team'
d.core_properties.keywords='U-RESCUE, Stage I, design, modelling, flood evacuation, GIS'
d.save(OUT)
print(OUT)


