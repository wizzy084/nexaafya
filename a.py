from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,ImageAndFlowables,ListItem,ListFlowable,Table,TableStyle,Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib import pagesizes
from reportlab.rl_config import defaultPageSize
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from fontawesome import icons
from datetime import datetime

#REGISTERING FONTAWESOME ICONS
pdfmetrics.registerFont(TTFont("FontAwesome-Solid","uix/assets/icons/webfonts/fa-solid-900.ttf"))
pdfmetrics.registerFont(TTFont("FontAwesome-Brands","uix/assets/icons/webfonts/fa-brands-400.ttf"))
pdfmetrics.registerFont(TTFont("FontAwesome-Regular","uix/assets/icons/webfonts/fa-regular-400.ttf"))



###

class NexaDoc(SimpleDocTemplate):
  """Generates a PDF document for Prescription Form"""

  def __init__(self,data):
    """Initializes the document with configurations and styles."""
    
    self.facility,self.contacts,self.client,self.medicines,self.prescriber,self.dispenser = data['facility'],data['contacts'],data['client'],data['medicines'],data["prescriber"],data["dispenser"]
    
    super().__init__(filename=data["filename"])
    self.configs()
    self.styles()
    
    self.story:list[Flowable] = [Spacer(0,0)]

    self.build(self.story,onFirstPage=self.main_page)

  def main_page(self,canvas,doc):
    """Displays the page"""

    page_data = [
      self.header(),
      [Paragraph("<hr>",style=ParagraphStyle(name="HRStyle",alignment=TA_CENTER,borderWidth=1,borderColor=colors.darkgrey))],
      self.page_details(),
      [Paragraph("<hr>",style=ParagraphStyle(name="HRStyle",alignment=TA_CENTER,borderWidth=1,borderColor=colors.darkgrey))],
      self.footer()
    ]

    canvas.saveState()
    canvas.restoreState()

    main_grid = Table(
      data=page_data,
      rowHeights=self.rowHeights,
      colWidths=[self.grid_width],
      style=self.main_grid_styles
    )

    self.story.append(main_grid)
  
  def configs(self):
    """general configurations for document"""
    
    #Document
    self.title = "Prescription Form"
    self.author = self.facility['name']
    self.pagesize = pagesizes.portrait(pagesizes.A6)
    self.leftMargin = self.rightMargin = self.topMargin = self.bottomMargin = 1.5

    #Main grid
    grid_height = self.pagesize[1] - self.topMargin - self.bottomMargin
    header_height = grid_height * 0.1
    self.main_content_height = grid_height * 0.75
    footer_height = grid_height * 0.05
    separator_height = grid_height * 0.02
    self.rowHeights = [header_height,separator_height,self.main_content_height,separator_height,footer_height]
    self.grid_width = self.pagesize[0] - self.leftMargin - self.rightMargin

    #Social media tags
    self.socials_str = ""
    socials_colors = {"instagram":"red","facebook":"blue","whatsapp":"darkgreen","x":"black"}
    for i,social in enumerate(self.contacts['socials'][1]):
      try:
        self.socials_str += f"<font name='FontAwesome-Brands' color='{socials_colors[social]}'>{icons[social]}</font>"
      except:
        if social == "x":
          self.socials_str += "<font name='FontAwesome-Brands' color='black'>\ue61b</font>"  #X icon code
      finally:
        self.socials_str +="<font size=5 color='black'>&nbsp;&nbsp;</font>"

  def styles(self):
    """defines styles used in document"""

    #Main Grid
    self.main_grid_styles = TableStyle([
      ("VALIGN",(0,0),(-1,-1),"TOP"),
      
      #Footer
      ("VALIGN",(0,-1),(-1,-1),"MIDDLE"),
      ("TOPPADDING",(0,-1),(-1,-1),3),
      ("BOTTOMPADDING",(0,-1),(-1,-1),0),
    ])

    #Header styles
    self.facility_details_table_styles = TableStyle([
      #All
      ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
      ("ALIGN",(0,0),(-1,-1),"CENTER"),
      ("LEFTPADDING",(0,0),(-1,-1),0),
      ("RIGHTPADDING",(0,0),(-1,-1),0),
      ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

      #Title
      ("TEXTCOLOR",(0,0),(-1,0),colors.midnightblue),
      ("FONTSIZE",(0,0),(-1,0),10),

      #Document Title
      ("VALIGN",(0,1),(-1,1),"BOTTOM"),
      ("TOPPADDING",(0,1),(-1,1),3),
      ("BOTTOMPADDING",(0,1),(-1,1),1),
      ("FONTSIZE",(0,1),(-1,1),10)
    ])
    
    #Main content styles
    self.main_content_table_styles = TableStyle([
      ("VALIGN",(0,0),(-1,-1),"TOP"),
      ("ALIGN",(0,0),(-1,-1),"LEFT"),
      ("LEFTPADDING",(0,0),(-1,-1),5),
      ("RIGHTPADDING",(0,0),(-1,-1),5),
    ])

    #Footer styles
    self.footer_table_styles = TableStyle([
      ("SPAN",(0,0),(-1,0)),
      ("TOPPADDING",(0,0),(-1,-1),0),
      ("BOTTOMPADDING",(0,0),(-1,-1),0),
      ("LEFTPADDING",(0,0),(-1,-1),0),
      ("RIGHTPADDING",(0,0),(-1,-1),0),
    ])

    self.socials_style = ParagraphStyle(
      name="FooterStyle",
      fontSize=8,
      alignment=TA_CENTER,
    )
    
    self.mobile_style = ParagraphStyle(
      name="FooterStyle",
      fontSize=8,
      textColor=colors.darkgoldenrod,
      alignment=TA_LEFT,
    )
    
    self.address_style = ParagraphStyle(
      name="FooterStyle",
      fontSize=8,
      textColor=colors.darkgoldenrod,
      alignment=TA_LEFT,
    )
    
  def header(self):
    """generates header part of document"""

    #Data
    facility_logo = self.facility['logo']
    facility_details = [
      [self.facility['name']],
      ["PRESCRIPTION FORM"]
    ]
    
    #UI
    logo = Image(filename=facility_logo,width=50,height=50)
    details = Table(data=facility_details,style=self.facility_details_table_styles)

    header_container = ImageAndFlowables(logo,details,imageSide="left",imageLeftPadding=0,imageRightPadding=0,imageTopPadding=0,imageBottomPadding=0,imageHref="")

    return [header_container]

  def page_details(self):
    """generates main content part of document"""
    _meds = []
    for index,med in enumerate(self.medicines):
      _meds.append([
        str(index + 1),
        Paragraph(med["name"].upper(),style=ParagraphStyle(wordWrap="LTR",name="MedNameStyle",fontName="Helvetica",fontSize=8,alignment=TA_LEFT)),
        Paragraph(med["dosage"].upper(),style=ParagraphStyle(wordWrap="LTR",name="MedNameStyle",fontName="Helvetica",fontSize=8,alignment=TA_LEFT)),
        med["qty"]
      ])
    
    demographics = [
      Paragraph(
        f'''<font size=10>CLIENT DETAILS</font><br/>
        <font>REG No.</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.client['reg_no']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>NAME</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.client['name']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>SEX</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.client['sex']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>AGE</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.client['age']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>PAYMENT</font><font size=1 color='white'>nsbp;</font><font color='blue'>{" <font color='black'>|</font> ".join(self.client['payment'])}</font>''',
        ParagraphStyle(name="DetailsStyle",fontName="Helvetica-Bold",fontSize=8,alignment=TA_LEFT)
      ),"","",""
    ]
    
    prescriber = [
      Paragraph(
        f'''<font name='Helvetica-Bold' size=10>PRESCRIBER DETAILS</font><br/>
        <font>NAME</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.prescriber['name']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>TITLE</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.prescriber['title']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>DATE</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.prescriber['prescription_time']}</font>
        <font size=5 color='white'>nsbp;</font>''',
        ParagraphStyle(name="DetailsStyle",fontSize=8,alignment=TA_LEFT)
      )
    ]

    dispenser = [
      Paragraph(
        f'''<font name='Helvetica-Bold' size=10>DISPENSER DETAILS</font><br/>
        <font>NAME</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.dispenser['name']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>TITLE</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.dispenser['title']}</font>
        <font size=5 color='white'>nsbp;</font>
        <font>DATE</font><font size=1 color='white'>nsbp;</font><font color='blue'>{self.dispenser['dispensing_time']}</font>
        <font size=5 color='white'>nsbp;</font>''',
        ParagraphStyle(name="DetailsStyle",fontSize=8,alignment=TA_LEFT)
      )
    ]
    
    procedures = [ListFlowable([
      ListItem(Paragraph('niponipo')),
      ListFlowable([
        Paragraph('uo')
      ])
    ])]

    medicines = [Table(
      data=[
        ["MEDICATIONS"],
        ["","NAME","DOSAGE","QTY"],
      ] + _meds,
      colWidths=[self.grid_width*0.07,self.grid_width*0.35,self.grid_width*0.35,self.grid_width*0.1],
      style=TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.slategrey),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(-1,0),(-1,-1),"RIGHT"),
        ("SPAN",(0,0),(-1,0)),
        ("FONTNAME",(0,0),(-1,1),"Helvetica-Bold"),
        ("FONTNAME",(0,2),(-1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,0),10),
        ("FONTSIZE",(0,1),(-1,-1),9),
        ("BACKGROUND",(0,0),(-1,1),colors.lightgrey),
      ])
    )]

    main_content_table = Table(
      data=[demographics,procedures,medicines,prescriber,dispenser],
      colWidths=[self.grid_width],
      style=self.main_content_table_styles
    )

    return [main_content_table]

  def footer(self):
    """generates footer part of document"""

    address_paragraph = Paragraph(f"""
      <font name='FontAwesome-Solid' size=8 color='blue'>{icons['map-marker-alt']}</font><font size=3 color='black'>&nbsp;&nbsp;</font><font name='Helvetica-BoldOblique' color='darkslategrey'>{self.contacts['address']}</font>
      """,style=self.address_style)
    
    mobile_paragraph = Paragraph(f"""
      <font name='FontAwesome-Solid' color='blue'>{icons['phone']}</font><font size=3 color='black'>&nbsp;&nbsp;</font><font name='Helvetica-BoldOblique' color='darkslategrey'>{self.contacts['mobile']}</font>
      """,style=self.mobile_style)
    
    socials_paragraph = Paragraph(f"{self.socials_str}<font name='Helvetica-BoldOblique' size=8 color='darkslategrey'>{self.contacts['socials'][0]}</font>",
      style=self.socials_style
    )

    footer_table = Table(
      data=[[address_paragraph],[mobile_paragraph,socials_paragraph]],
      colWidths=[self.grid_width*0.3,self.grid_width*0.7],
      style=self.footer_table_styles
    )

    return [footer_table]
    
  
data = {
  "filename": "a.pdf",
  "facility": {
    "name": "FUTURE SPECIALIZED DENTAL CLINIC",
    "logo": "uix/assets/images/logos/future1.PNG"
  },
  "contacts": {
    "address": "Morogoro Mjini,Ghorofa la Equity,Floor No. 3",
    "mobile": "+255 717 006 007",
    "socials": ["futurespecialisedentalclinic",("whatsapp","instagram","x","facebook")]
  },
  "client": {
    "name": "abdulrahman kalingagh Nehru".upper(),
    "reg_no": "2512003",
    "age": "29Y8M".upper(),
    "sex":"MALE",
    "payment":{"CASH","STRATEGIS"}
  },
  "prescriber": {
    "name": "Jane L. Smith",
    "title": "MO",
    "prescription_time":datetime.now().strftime("%d %b %Y %H:%M")
  },
  "dispenser": {
    "name": "Alex X. Brown",
    "title": "BPharm",
    "dispensing_time":datetime.now().strftime("%d %b %Y %H:%M")
  },
  "medicines": [
    {
      "name":"nystatin 200000IU/ml 10ml susp",
      "dosage":"5ml po qid for 7 days",
      "qty":f"{1:,.0f}"
    },
    {
      "name":"amoxicillin 500mg cap",
      "dosage":"500mg po tds for 5 days",
      "qty":f"{30:,.0f}"
    },
    {
      "name":"ibuprofen 400mg tab",
      "dosage":"400mg po tds for 5 days",
      "qty":f"{1308:,.0f}"
    }
  ]
}

NexaDoc(data)



