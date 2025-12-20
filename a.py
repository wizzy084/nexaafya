from fpdf import FPDF



from fpdf import FPDF
from datetime import datetime

class PrescriptionPDF(FPDF):
  def __init__(self, hospital_name="GENERAL HOSPITAL"):
      super().__init__()
      self.hospital_name = hospital_name
      self.left_margin = 15
      self.right_margin = 15
      self.top_margin = 15
      
  def header(self):
      # Hospital header with logo area
      self.set_font('Arial', 'B', 16)
      self.set_text_color(13, 71, 161)  # Blue color
      
      # Hospital name and title
      self.cell(0, 10, self.hospital_name.upper(), 0, 1, 'C')
      self.set_font('Arial', 'B', 12)
      self.set_text_color(0, 0, 0)
      self.cell(0, 8, 'MEDICAL PRESCRIPTION', 0, 1, 'C')
      
      # Separator line
      self.set_line_width(0.5)
      self.set_draw_color(13, 71, 161)
      self.line(self.left_margin, self.get_y(), 200-self.right_margin, self.get_y())
      self.ln(5)
      
  def footer(self):
      # Page footer
      self.set_y(-15)
      self.set_font('Arial', 'I', 8)
      self.set_text_color(128, 128, 128)
      
      # Footer text
      footer_text = "This prescription is valid for 30 days from date of issue. Not for controlled substances."
      self.cell(0, 10, footer_text, 0, 0, 'C')
      
      # Page number
      self.set_y(-10)
      self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
  
  def add_patient_info_section(self, patient_data):
      """Add patient information section"""
      self.set_font('Arial', 'B', 12)
      self.set_text_color(0, 0, 0)
      self.set_fill_color(240, 248, 255)  # Light blue background
      self.cell(0, 8, 'PATIENT INFORMATION', ln=1, fill=True)
      
      self.set_font('Arial', '', 10)
      self.set_text_color(0, 0, 0)
      
      # Patient details in two columns
      col_width = 85
      y_start = self.get_y()
      
      # Left column
      self.set_xy(self.left_margin, y_start)
      self.cell(col_width, 6, f"Name: {patient_data.get('name', '')}")
      self.ln(6)
      self.cell(col_width, 6, f"Date of Birth: {patient_data.get('dob', '')}")
      self.ln(6)
      self.cell(col_width, 6, f"Gender: {patient_data.get('gender', '')}")
      self.ln(6)
      
      # Right column
      self.set_xy(self.left_margin + col_width, y_start)
      self.cell(col_width, 6, f"Patient ID: {patient_data.get('patient_id', '')}")
      self.ln(6)
      self.cell(col_width, 6, f"Date: {patient_data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
      self.ln(6)
      self.cell(col_width, 6, f"Allergies: {patient_data.get('allergies', 'None known')}")
      
      self.ln(10)
      
  def add_prescriber_info_section(self, doctor_data):
      """Add prescriber information section"""
      self.set_font('Arial', 'B', 12)
      self.set_fill_color(240, 248, 255)
      self.cell(0, 8, 'PRESCRIBER INFORMATION', ln=1, fill=True)
      
      self.set_font('Arial', '', 10)
      
      col_width = 85
      y_start = self.get_y()
      
      # Left column
      self.set_xy(self.left_margin, y_start)
      self.cell(col_width, 6, f"Doctor: Dr. {doctor_data.get('name', '')}")
      self.ln(6)
      self.cell(col_width, 6, f"Specialty: {doctor_data.get('specialty', 'General Medicine')}")
      self.ln(6)
      
      # Right column
      self.set_xy(self.left_margin + col_width, y_start)
      self.cell(col_width, 6, f"License No: {doctor_data.get('license', '')}")
      self.ln(6)
      self.cell(col_width, 6, f"Contact: {doctor_data.get('contact', '')}")
      
      self.ln(10)
      
  def add_prescription_table(self, medications):
      """Add prescription medications table"""
      self.set_font('Arial', 'B', 12)
      self.set_fill_color(240, 248, 255)
      self.cell(0, 8, 'PRESCRIPTION DETAILS', ln=1, fill=True)
      
      # Table headers
      self.set_font('Arial', 'B', 10)
      self.set_fill_color(220, 230, 242)
      
      headers = ['Medication', 'Dosage', 'Frequency', 'Duration', 'Instructions']
      col_widths = [40, 30, 30, 30, 50]
      
      # Draw header cells
      x = self.left_margin
      for i, header in enumerate(headers):
          self.set_xy(x, self.get_y())
          self.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
          x += col_widths[i]
      
      self.ln(8)
      
      # Table rows
      self.set_font('Arial', '', 9)
      self.set_fill_color(255, 255, 255)
      
      for med in medications:
          x = self.left_margin
          row_height = 8
          
          # Check if we need a new page
          if self.get_y() > 250:
              self.add_page()
              self.set_font('Arial', '', 9)
              x = self.left_margin
          
          # Draw medication row
          self.set_xy(x, self.get_y())
          self.multi_cell(col_widths[0], row_height, med.get('name', ''), border=1, align='L')
          
          x += col_widths[0]
          self.set_xy(x, self.get_y() - row_height)  # Reset y position
          self.cell(col_widths[1], row_height, med.get('dosage', ''), border=1, align='C')
          
          x += col_widths[1]
          self.set_xy(x, self.get_y())
          self.cell(col_widths[2], row_height, med.get('frequency', ''), border=1, align='C')
          
          x += col_widths[2]
          self.set_xy(x, self.get_y())
          self.cell(col_widths[3], row_height, med.get('duration', ''), border=1, align='C')
          
          x += col_widths[3]
          self.set_xy(x, self.get_y())
          self.multi_cell(col_widths[4], row_height, med.get('instructions', ''), border=1, align='L')
          
          self.ln(row_height)
      
      self.ln(10)
      
  def add_signature_section(self):
      """Add signature and stamp area"""
      self.set_font('Arial', 'B', 12)
      self.set_fill_color(240, 248, 255)
      self.cell(0, 8, 'AUTHORIZATION', ln=1, fill=True)
      
      self.set_font('Arial', '', 10)
      
      # Signature area
      self.ln(15)
      self.cell(80, 6, "Doctor's Signature: _________________________")
      self.cell(80, 6, "Date: _________________________", ln=1)
      
      self.ln(10)
      
      # Stamp area
      self.set_font('Arial', 'B', 10)
      self.cell(0, 6, "HOSPITAL STAMP", ln=1, align='C')
      
      # Draw stamp box
      stamp_y = self.get_y()
      self.rect(self.left_margin + 70, stamp_y, 60, 30)
      
      # Add text inside stamp
      self.set_font('Arial', 'I', 8)
      self.set_xy(self.left_margin + 75, stamp_y + 12)
      self.cell(50, 5, "Authorized Prescriber", align='C')
      
      self.set_xy(self.left_margin + 75, stamp_y + 18)
      self.cell(50, 5, self.hospital_name, align='C')
      
      self.ln(35)
      
  def add_notes_section(self, notes):
      """Add additional notes section"""
      if notes:
          self.set_font('Arial', 'B', 12)
          self.set_fill_color(240, 248, 255)
          self.cell(0, 8, 'ADDITIONAL NOTES', ln=1, fill=True)
          
          self.set_font('Arial', '', 10)
          self.multi_cell(0, 6, notes)
          self.ln(10)
          
  def add_warning_section(self):
      """Add prescription warnings"""
      self.set_font('Arial', 'I', 8)
      self.set_text_color(139, 0, 0)  # Dark red
      
      warnings = [
          "IMPORTANT: This prescription is for the above-named patient only.",
          "Do not share medication with others.",
          "Complete the full course of treatment unless otherwise directed.",
          "Contact your doctor if symptoms worsen or side effects occur.",
          "Keep all medications out of reach of children."
      ]
      
      for warning in warnings:
          self.cell(0, 4, f"• {warning}", ln=1)
      
      self.ln(5)

def generate_prescription(output_path="prescription.pdf"):
    """Generate a sample prescription"""
    
    # Create PDF object
    pdf = PrescriptionPDF(hospital_name="CITY GENERAL HOSPITAL")
    pdf.add_page()
    
    # Patient information
    patient_data = {
        'name': 'John A. Smith',
        'dob': '1985-03-15',
        'gender': 'Male',
        'patient_id': 'CGH-2023-78945',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'allergies': 'Penicillin, Sulfa drugs'
    }
    
    # Doctor information
    doctor_data = {
        'name': 'Sarah Johnson, MD',
        'specialty': 'Internal Medicine',
        'license': 'MED-789654-2023',
        'contact': '555-123-4567'
    }
    
    # Medications
    medications = [
        {
            'name': 'Amoxicillin 500mg',
            'dosage': '1 tab',
            'frequency': 'Every 8 hours',
            'duration': '10 days',
            'instructions': 'Take with food. Complete full course.'
        },
        {
            'name': 'Ibuprofen 400mg',
            'dosage': '1-2 tabs',
            'frequency': 'Every 6-8 hours',
            'duration': '5 days',
            'instructions': 'As needed for pain. Take with food.'
        },
        {
            'name': 'Loratadine 10mg',
            'dosage': '1 tab',
            'frequency': 'Once daily',
            'duration': '30 days',
            'instructions': 'For allergy relief. Take in morning.'
        }
    ]
    
    # Additional notes
    notes = "Patient advised to follow up in 2 weeks if symptoms persist. Avoid alcohol while taking antibiotics. Monitor for any signs of allergic reaction."
    
    # Build the prescription
    pdf.add_patient_info_section(patient_data)
    pdf.add_prescriber_info_section(doctor_data)
    pdf.add_prescription_table(medications)
    pdf.add_notes_section(notes)
    pdf.add_warning_section()
    pdf.add_signature_section()
    
    # Output the PDF
    pdf.output(output_path)
    print(f"Prescription generated: {output_path}")

def create_blank_prescription_template(output_path="prescription_template.pdf"):
    """Create a blank prescription template"""
    pdf = PrescriptionPDF(hospital_name="[HOSPITAL NAME]")
    pdf.add_page()
    
    # Patient information (blank)
    patient_data = {
        'name': '[PATIENT NAME]',
        'dob': '[DATE OF BIRTH]',
        'gender': '[GENDER]',
        'patient_id': '[PATIENT ID]',
        'date': '[DATE]',
        'allergies': '[ALLERGIES]'
    }
    
    # Doctor information (blank)
    doctor_data = {
        'name': '[DOCTOR NAME]',
        'specialty': '[SPECIALTY]',
        'license': '[LICENSE NUMBER]',
        'contact': '[CONTACT]'
    }
    
    # Empty medications table
    medications = [
        {
            'name': '[MEDICATION NAME]',
            'dosage': '[DOSAGE]',
            'frequency': '[FREQUENCY]',
            'duration': '[DURATION]',
            'instructions': '[SPECIAL INSTRUCTIONS]'
        }
    ]
    
    # Build the template
    pdf.add_patient_info_section(patient_data)
    pdf.add_prescriber_info_section(doctor_data)
    pdf.add_prescription_table(medications)
    
    # Add blank notes section
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(0, 8, 'ADDITIONAL NOTES', ln=1, fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "[ADDITIONAL INSTRUCTIONS OR NOTES]")
    
    pdf.ln(10)
    pdf.add_warning_section()
    pdf.add_signature_section()
    
    pdf.output(output_path)
    print(f"Blank template generated: {output_path}")

if __name__ == "__main__":
    print("Hospital Prescription Form Generator")
    print("=" * 40)
    
    # Generate sample prescription
    generate_prescription("a.pdf")
    
    # Generate blank template
    create_blank_prescription_template("blank_prescription_form.pdf")
    
    print("\nFiles created successfully!")
    print("1. sample_prescription.pdf - Example with sample data")
    print("2. blank_prescription_form.pdf - Blank template for use")