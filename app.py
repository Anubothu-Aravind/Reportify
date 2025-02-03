import streamlit as st
import pandas as pd
import tempfile
from fpdf import FPDF
import os
import shutil
import zipfile
import io


def generate_sample_csv():
    """Generate a sample CSV file"""
    sample_data = """S.No,NAME,ID NUMBER,COURSE CODE,COURSE NAME,COMPONENT,ATTENDANCE,PHONE NUMBER
"""
    return io.BytesIO(sample_data.encode())

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def create_pdf_report(student_data):
    """Create PDF report in English"""
    pdf = CustomPDF()
    pdf.add_page()
    pdf.alias_nb_pages()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Attendance Report', 0, 1, 'C')

    # Student details
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Name: {student_data['name']}", 0, 1)
    pdf.cell(0, 10, f"ID: {student_data['id']}", 0, 1)
    pdf.ln(5)

    # Table header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 12)

    col_widths = [100, 30, 30]
    headers = ['Subject', 'Component', 'Attendance']

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
    pdf.ln()

    # Table data
    pdf.set_font('Arial', '', 12)
    for item in student_data['summary']:
        if item['attendance'] < 75:
            pdf.set_text_color(255, 0, 0)
        else:
            pdf.set_text_color(0, 0, 0)

        pdf.cell(col_widths[0], 10, str(item['subject']), 1)
        pdf.cell(col_widths[1], 10, str(item['component']), 1)
        pdf.cell(col_widths[2], 10, f"{item['attendance']}%", 1)
        pdf.ln()

    # Reset text color
    pdf.set_text_color(0, 0, 0)

    # Summary section
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Summary:', 0, 1)
    pdf.set_font('Arial', '', 12)

    low_attendance = [item for item in student_data['summary'] if item['attendance'] < 75]
    if low_attendance:
        pdf.cell(0, 10, 'Subjects requiring attention (below 75%):', 0, 1)
        for item in low_attendance:
            pdf.cell(0, 10, f"- {item['subject']} ({item['component']}): {item['attendance']}%", 0, 1)
    else:
        pdf.cell(0, 10, 'Good attendance in all subjects!', 0, 1)

    # Save to temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_pdf.name)
    return temp_pdf.name

def process_attendance_data(df, id_number):
    """Process attendance data for a specific ID number"""
    student_data = df[df['ID NUMBER'] == id_number]

    if len(student_data) == 0:
        return None

    # Get student details
    student_name = student_data['NAME'].iloc[0]
    phone_number = student_data['PHONE NUMBER'].iloc[0]

    # Create attendance summary
    attendance_summary = []
    # Group by subject and component
    grouped_data = student_data.groupby(['COURSE NAME', 'COMPONENT'])['ATTENDANCE'].first()

    for (subject, component), attendance in grouped_data.items():
        # Remove % symbol and convert to float
        attendance_value = float(attendance.rstrip('%'))
        attendance_summary.append({
            'subject': subject.strip(),
            'component': component,
            'attendance': attendance_value
        })

    return {
        'name': student_name,
        'id': id_number,
        'phone': phone_number,
        'summary': attendance_summary
    }

def main():
    st.title("Student Attendance Report Generator")
    # Instructions for CSV format
    # st.subheader("CSV File Format")
    st.markdown("""
        **Instructions:**
        - Please upload a CSV file in the following format:

        S.No, NAME, ID NUMBER, COURSE CODE, COURSE NAME, COMPONENT, ATTENDANCE, PHONE NUMBER

        - Download a sample file using the button below:
        """)
    # Provide a download button for the sample CSV file
    st.download_button(
        label="Download Sample CSV File",
        data=generate_sample_csv(),
        file_name="sample_attendance_data.csv",
        mime="text/csv"
    )
    uploaded_file = st.file_uploader("Upload attendance data (CSV)", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)

            # Get unique ID numbers
            id_numbers = df['ID NUMBER'].unique()

            # Prepare to collect all PDFs
            pdf_files = []

            for selected_id in id_numbers:
                student_data = process_attendance_data(df, selected_id)

                if student_data:
                    # Create PDF report
                    pdf_file = create_pdf_report(student_data)

                    # Rename file as 'attendance_report_<id_number>.pdf'
                    pdf_filename = f"attendance_report_{selected_id}.pdf"
                    shutil.copy(pdf_file, pdf_filename)  # Copy file to current directory

                    # Add to the list of generated files
                    pdf_files.append(pdf_filename)
                    os.unlink(pdf_file)

            if pdf_files:
                # Create ZIP file
                zip_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for pdf_file in pdf_files:
                        zipf.write(pdf_file, os.path.basename(pdf_file))
                        os.unlink(pdf_file)  # Cleanup PDF file after adding to ZIP

                # Provide download link for ZIP file
                with open(zip_filename, "rb") as zipf:
                    st.download_button(
                        label="Download All Attendance Reports as ZIP",
                        data=zipf,
                        file_name="attendance_reports.zip",
                        mime="application/zip"
                    )

                # Cleanup ZIP file
                os.unlink(zip_filename)
            else:
                st.error("No student data available to generate reports.")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()