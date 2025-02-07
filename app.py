import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import tempfile
from fpdf import FPDF
import os
import shutil
import zipfile
import io
import csv

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def get_report_text(student_data):
    """Generate report text for SMS"""
    text = f"Attendance Report for {student_data['name']} (ID: {student_data['id']})\n\n"

    # Add attendance summary
    low_attendance = [item for item in student_data['summary'] if item['attendance'] < 75]

    if low_attendance:
        text += "Subjects requiring attention (below 75%):\n"
        for item in low_attendance:
            text += f"- {item['subject']} ({item['component']}): {item['attendance']}%\n"
    else:
        text += "Good attendance in all subjects!\n"

    # Add Telugu summary
    text += "\nసారాంశం:\n"
    if low_attendance:
        text += "శ్రద్ధ అవసరమైన సబ్జెక్టులు (75% కంటే తక్కువ):\n"
        for item in low_attendance:
            text += f"- {item['subject']} ({item['component']}): {item['attendance']}%\n"
    else:
        text += "అన్ని సబ్జెక్టులలో మంచి హాజరు!\n"

    return text

def generate_sample_csv():
    """Generate a sample CSV file"""
    sample_data = """S.No,NAME,ID NUMBER,COURSE CODE,COURSE NAME,COMPONENT,ATTENDANCE,PHONE NUMBER
1,Anubothu Aravind,2200080137,22AD3206A,DATA SCIENCE AND VISUALIZATION,L,85%,8374005347
"""
    return io.BytesIO(sample_data.encode())

def generate_sms_csv(student_data_list):
    """Generate CSV file with phone numbers and messages"""
    csv_data = []
    for i, student_data in enumerate(student_data_list, 1):
        message = get_report_text(student_data)
        csv_data.append({
            'S.No': i,
            'Phone Number': student_data['phone'],
            'Message': message
        })

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['S.No', 'Phone Number', 'Message'])
    writer.writeheader()
    writer.writerows(csv_data)

    return output.getvalue()

def create_text_report(student_data, filename):
    """Create text report with both English and Telugu summaries"""
    with open(filename, 'w', encoding='utf-8') as f:
        # Write English content
        f.write("Attendance Report\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"Name: {student_data['name']}\n")
        f.write(f"ID: {student_data['id']}\n\n")

        f.write("Subject-wise Attendance:\n")
        f.write("-" * 30 + "\n")
        for item in student_data['summary']:
            f.write(f"Subject: {item['subject']}\n")
            f.write(f"Component: {item['component']}\n")
            f.write(f"Attendance: {item['attendance']}%\n")
            f.write("-" * 20 + "\n")

        # English Summary
        f.write("\nSummary:\n")
        low_attendance = [item for item in student_data['summary'] if item['attendance'] < 75]
        if low_attendance:
            f.write("Subjects requiring attention (below 75%):\n")
            for item in low_attendance:
                f.write(f"- {item['subject']} ({item['component']}): {item['attendance']}%\n")
        else:
            f.write("Good attendance in all subjects!\n")

        # Telugu Summary
        f.write("\nసారాంశం:\n")
        if low_attendance:
            f.write("శ్రద్ధ అవసరమైన సబ్జెక్టులు (75% కంటే తక్కువ):\n")
            for item in low_attendance:
                f.write(f"- {item['subject']} ({item['component']}): {item['attendance']}%\n")
        else:
            f.write("అన్ని సబ్జెక్టులలో మంచి హాజరు!\n")

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
    grouped_data = student_data.groupby(['COURSE NAME', 'COMPONENT'])['ATTENDANCE'].first()

    for (subject, component), attendance in grouped_data.items():
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
    # WhatsApp Web Configuration
    LOGIN_TIME = 30  # Time for login (in seconds)
    NEW_MSG_TIME = 8  # Time to load new message screen
    SEND_MSG_TIME = 5  # Time before sending next message
    COUNTRY_CODE = "91"  # Change as per your country
    st.title("Student Attendance Report Generator")
    with st.sidebar:
        st.header("WhatsApp Web Integration")
        uploaded_file = st.file_uploader("Upload CSV (Phone Number, Message)", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            if "Phone Number" in df.columns and "Message" in df.columns:
                st.success("CSV uploaded successfully! Ready to send messages.")

                if st.button("Send WhatsApp Messages"):
                    # Initialize Chrome WebDriver
                    chrome_options = Options()
                    chrome_options.add_argument("--headless")  # Run in headless mode
                    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
                    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
                    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
                    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)

                    driver.get("https://web.whatsapp.com")
                    st.info("Scan the QR code and wait for login...")
                    time.sleep(LOGIN_TIME)

                    for index, row in df.iterrows():
                        phone_number = str(row["Phone Number"]).strip()
                        message = str(row["Message"]).strip()

                        whatsapp_url = f"https://web.whatsapp.com/send/?phone={COUNTRY_CODE}{phone_number}"
                        driver.get(whatsapp_url)
                        time.sleep(NEW_MSG_TIME)

                        try:
                            # Type and Send Message
                            actions = ActionChains(driver)
                            for line in message.split('\n'):
                                actions.send_keys(line)
                                actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                            actions.send_keys(Keys.ENTER)
                            actions.perform()

                            st.success(f"✅ Message sent to {phone_number}")
                            time.sleep(SEND_MSG_TIME)

                        except Exception as e:
                            st.error(f"❌ Failed to send message to {phone_number}: {str(e)}")

                    driver.quit()
                    st.success("All messages sent successfully! ✅")

            else:
                st.error("Invalid CSV format! Ensure it has 'Phone Number' and 'Message' columns.")
    st.markdown("""
        **Instructions:**
        - Please upload a CSV file in the following format:

        S.No, NAME, ID NUMBER, COURSE CODE, COURSE NAME, COMPONENT, ATTENDANCE, PHONE NUMBER

        - Download a sample file using the button below:
        """)
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
            id_numbers = df['ID NUMBER'].unique()
            pdf_files = []
            text_files = []
            student_data_list = []  # Store all student data for SMS CSV generation

            for selected_id in id_numbers:
                student_data = process_attendance_data(df, selected_id)

                if student_data:
                    # Add to student data list for SMS CSV
                    student_data_list.append(student_data)

                    # Create PDF report
                    pdf_file = create_pdf_report(student_data)
                    pdf_filename = f"attendance_report_{selected_id}.pdf"
                    shutil.copy(pdf_file, pdf_filename)
                    pdf_files.append(pdf_filename)
                    os.unlink(pdf_file)

                    # Create text report
                    text_filename = f"attendance_report_{selected_id}.txt"
                    create_text_report(student_data, text_filename)
                    text_files.append(text_filename)

            if pdf_files:
                # Create ZIP file
                zip_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    # Add PDF files
                    for pdf_file in pdf_files:
                        zipf.write(pdf_file, os.path.basename(pdf_file))
                        os.unlink(pdf_file)

                    # Add text files
                    for text_file in text_files:
                        zipf.write(text_file, os.path.basename(text_file))
                        os.unlink(text_file)

                # Generate SMS CSV data
                sms_csv_data = generate_sms_csv(student_data_list)

                # Create two columns for download buttons
                col1, col2 = st.columns(2)

                # Provide download link for ZIP file
                with open(zip_filename, "rb") as zipf:
                    with col1:
                        st.download_button(
                            label="Download All Reports (PDF and Text) as ZIP",
                            data=zipf,
                            file_name="attendance_reports.zip",
                            mime="application/zip"
                        )

                # Provide download link for SMS CSV
                with col2:
                    st.download_button(
                        label="Download SMS Data (CSV)",
                        data=sms_csv_data,
                        file_name="sms_data.csv",
                        mime="text/csv"
                    )

                # Cleanup ZIP file
                os.unlink(zip_filename)
            else:
                st.error("No student data available to generate reports.")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


if __name__ == "__main__":
    main()
