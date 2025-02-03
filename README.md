# Reportify - Student Attendance Report Generator

Reportify is an easy-to-use tool for generating detailed attendance reports for students. It allows educators to upload attendance data in CSV format, process it, and generate PDF reports with insights into attendance performance. These reports can be downloaded individually or as a zip file for multiple students.

## Features

- Upload attendance data in CSV format.
- Automatically process attendance and generate personalized reports for each student.
- Detailed PDF reports with subject-wise attendance and summary of low attendance.
- Option to download all reports in a zip file.
- A simple and user-friendly interface powered by Streamlit.

## CSV File Format

The CSV file should follow the format below:

```
S.No, NAME, ID NUMBER, COURSE CODE, COURSE NAME, COMPONENT, ATTENDANCE, PHONE NUMBER
```

### Example:

| S.No | NAME  | ID NUMBER | COURSE CODE | COURSE NAME | COMPONENT | ATTENDANCE | PHONE NUMBER |
|------|-------|-----------|-------------|-------------|-----------|------------|--------------|
| 1    | John  | 2200080234| CS101       | Data Science| Lecture   | 85%        | 1234567890   |
| 2    | Alice | 2200080235| CS102       | AI Basics   | Lab       | 70%        | 1234567891   |

## How to Use

1. Upload your CSV file with the required data.
2. The app will automatically process the file and generate PDF reports for each student.
3. You can preview the generated reports.
4. Download individual PDF reports or download all reports in a zip file.

## Installation

To run this app locally, follow the steps below:

1. Clone the repository:
    ```bash
    git clone https://github.com/Anubothu-Aravind/Reportify.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    streamlit run app.py
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Streamlit: For creating a simple and effective framework for building web apps.
- FPDF: For generating PDFs with custom formatting.
