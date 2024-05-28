import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime


def wrap_text(text, width, font_name, font_size):
    lines = simpleSplit(text, font_name, font_size, width)
    return lines


def create_pdf(employee_name, tasks):
    buffer = BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("HeiseiKakuGo-W5", 12)
    width, height = A4
    margin = 50
    text_width = width - 2 * margin

    p.drawString(100, height - 40, "引き継ぎ内容")
    y = height - 80
    p.drawString(100, height - 60, f"社員名: {employee_name}")
    y -= 30

    p.line(50, y + 30, width - 50, y + 30)
    for i, task in enumerate(tasks):
        p.drawString(100, y, f"発生頻度: {task['frequency']}")
        y -= 20
        p.drawString(100, y, f"タスク {i+1}:")
        task_lines = wrap_text(f"{task['task']}", text_width, "HeiseiKakuGo-W5",12)
        for line in task_lines:
            p.drawString(150, y, line)
            y -= 15

        y -= 5
        p.drawString(100, y, f"期間 {task['start_date']} 〜 {task['end_date']}")
        y -= 30
        p.line(50, y + 5, width - 50, y + 5)
        y -= 30

    p.showPage()
    p.save()

    buffer.seek(0)

    return buffer


if __name__ == '__main__':

    st.title('業務引き継ぎ内容 PDF 出力アプリ')

    st.sidebar.header('引き継ぎ内容入力フォーム')
    employee_name = st.sidebar.text_input('社員名:')

    if 'tasks' not in st.session_state:
        st.session_state.tasks = []

    if st.sidebar.button('➕ タスクを追加'):
        st.session_state.tasks.append(
            {'task': '', 'frequency': '高', 'start_date': datetime.date.today(), 'end_date': datetime.date.today()})

    for i, task in enumerate(st.session_state.tasks):
        task_text = st.sidebar.text_area(f'タスク内容 {i + 1}:', value=task['task'])
        frequency = st.sidebar.selectbox(f'発生頻度 {i + 1}:', ['高', '中', '低'],
                                         index=['高', '中', '低'].index(task['frequency']))
        start_date = st.sidebar.date_input(f'開始日 {i + 1}:', value=task['start_date'])
        end_date = st.sidebar.date_input(f'終了日 {i + 1}:', value=task['end_date'])

        st.session_state.tasks[i] = {'task': task_text, 'frequency': frequency, 'start_date': start_date,
                                     'end_date': end_date}

        st.sidebar.markdown("---")

    if st.button('タスクをPDF化'):
        pdf_buffer = create_pdf(employee_name, st.session_state.tasks)

        # PDFをダウンロードリンクとして提供
        st.download_button(label="PDFをダウンロード", data=pdf_buffer, file_name=f"{employee_name}_handover_report.pdf",
                           mime="application/pdf")
