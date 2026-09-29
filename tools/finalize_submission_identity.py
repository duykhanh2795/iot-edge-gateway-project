from pathlib import Path
import shutil

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


SOURCE = Path(r"F:\iot-edge-gateway-project\output\midterm-beehive\2324802010251_NguyenDuyKhanh.docx")
OUTPUT = Path(r"F:\iot-edge-gateway-project\output\midterm-beehive\IoT_2324802010251_NguyenDuyKhanh_GiamSatToOng.docx")


def set_run_font(run, size=11, bold=None, italic=None):
    run.font.name = "Times New Roman"
    rfonts = run._element.get_or_add_rPr().rFonts
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    rfonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_cell_text(cell, text, size=10.5, centered=True):
    paragraph = cell.paragraphs[0]
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)
    if centered:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    set_run_font(run, size=size)


def clear_paragraph(paragraph):
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)


def enable_field_updates(doc):
    settings = doc.settings.element
    current = settings.find(qn("w:updateFields"))
    if current is None:
        current = OxmlElement("w:updateFields")
        settings.append(current)
    current.set(qn("w:val"), "true")


def main():
    shutil.copy2(SOURCE, OUTPUT)
    doc = Document(OUTPUT)

    # Hoàn thiện dòng địa danh và ngày tháng ở cuối trang bìa.
    date_line = doc.paragraphs[12]
    if not date_line.runs:
        date_line.add_run()
    date_line.runs[0].text = "Thủ Dầu Một, ngày 24 tháng 9 năm 2026"
    set_run_font(date_line.runs[0], size=11, italic=True)
    for run in date_line.runs[1:]:
        run.text = ""

    # Làm sạch toàn bộ khối xác nhận vì bản làm việc có thể chứa tên bị lặp
    # hoặc các dấu xuống dòng do người dùng vừa nhập trong Word.
    signature = next(p for p in doc.paragraphs if "Sinh viên thực hiện" in p.text)
    clear_paragraph(signature)
    signature.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    signature.paragraph_format.space_after = Pt(6)
    signature.paragraph_format.line_spacing = 1.2
    role_run = signature.add_run("Sinh viên thực hiện")
    set_run_font(role_run, size=11, bold=True)
    role_run.add_break()
    hint_run = signature.add_run("Ký và ghi rõ họ tên")
    set_run_font(hint_run, size=11, italic=True)
    hint_run.add_break()
    hint_run.add_break()
    name_run = signature.add_run("Nguyễn Duy Khánh")
    set_run_font(name_run, size=11, bold=True)

    # Hoàn thiện tổng điểm tự đánh giá và xác nhận mục đầu báo cáo đã điền.
    self_assessment = doc.tables[1]
    set_cell_text(self_assessment.rows[10].cells[3], "10,0")

    checklist = doc.tables[20]
    set_cell_text(checklist.rows[15].cells[0], "☒")

    doc.core_properties.author = "Nguyễn Duy Khánh"
    doc.core_properties.last_modified_by = "Nguyễn Duy Khánh"
    enable_field_updates(doc)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
