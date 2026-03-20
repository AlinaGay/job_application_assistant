# tests/create_test_pdf.py
from reportlab.pdfgen import canvas

c = canvas.Canvas("tests/fixtures/test_resume.pdf")
c.drawString(100, 750, "Python Developer with 5 years of experience")
c.drawString(100, 730, "Skills: Python, Django, FastAPI, PostgreSQL")
c.save()
