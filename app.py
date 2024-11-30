import io
import os
import json
import pathlib
import requests
from uuid import uuid4
from time import sleep
from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF
import qrcode


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        record_id = request.form.get('id-input')
        request_id = uuid4().hex
        qr_path, pdf_path, data_path = f"{request_id}_qr.png", f"/home/printer/data/{request_id}.pdf", f'/home/printer/data/{request_id}.json'
        response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}', params={'request_id': request_id, 'idmagazzino': record_id})
        for _ in range(100):
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    data = json.loads(f.read())
                    url = f"https://ff.wpboy.it/edit-item/?record={data['idURL']}"
                    img = qrcode.make(url, box_size=30, border=1)
                    img.save(qr_path)
                    #
                    pdf = FPDF(format=(103, 40))
                    pdf.set_margin(0.5)
                    pdf.add_page()
                    pdf.set_font('helvetica', size=12)
                    pdf.set_font(style="U")
                    pdf.cell(text=f"{data['titolo']}\n\n", align="C", w=103)
                    pdf.image(qr_path, x=0, y=5, w=30, h=30)
                    pdf.set_y(5)
                    pdf.set_x(40)
                    pdf.set_font('helvetica', size=12)
                    label_text = f"""#Maga {data['idmagazzino']} --- posizione: {data['posizione']}
Tipo: {data['tipo']} --- FEID: {data['FEID']}
Tiratura: {data['tiratura']}
Commentario: {data['commentario']}
                    """
                    pdf.multi_cell(text=label_text, align="L", w=93)
                    pdf.output(pdf_path)
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_file_buffer = io.BytesIO(pdf_file.read())
                        pdf_file_buffer.seek(0)
                        for file in [data_path, qr_path, pdf_path]:
                            os.remove(file)
                        return send_file(pdf_file_buffer, attachment_filename=f"{data['idURL']}_label.pdf", as_attachment=True)
            sleep(1)
        return jsonify({'error': 'Request timed out'})
    return render_template('index.html')

@app.route('/callback', methods=['POST'])
def callback():
    pathlib.Path('/home/printer/data').mkdir(exist_ok=True)
    data = request.form
    with open(f'/home/printer/data/{data["request_id"]}.json', 'w') as f:
        f.write(json.dumps(data))
    return data
