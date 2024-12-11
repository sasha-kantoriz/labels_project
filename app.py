import io
import os
import json
import pathlib
import requests
from uuid import uuid4
from time import sleep
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from fpdf import FPDF
import qrcode


app = Flask(__name__)


@app.route('/', methods=['GET'])
def print_label():
    if not request.args.get('id-input'):
        return redirect(url_for('index'))
    records = request.args.get('id-input')
    if '-' in records:
        record_boundaries = records.replace(' ', '').split('-')
        record_ids = range(int(record_boundaries[0]), int(record_boundaries[-1])+1)
    elif ',' in records:
        record_ids = list(map(int, records.replace(' ', '').split(',')))
    else:
        record_ids = [int(records)]
    for record_id in record_ids:
        response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}', params={'idmagazzino': record_id})
        sleep(0.5)
    qr_path, pdf_path, data_path, last_record_data_path = "qr.png", "/home/printer/data/label.pdf", '/home/printer/data/{record_id}.json', f'/home/printer/data/{record_ids[-1]}.json'
    for _ in range(1000):
        if os.path.exists(last_record_data_path):
            records_presence = []
            for record_id in record_ids:
                with open(data_path.format(record_id=record_id), 'r') as f:
                    data = json.loads(f.read())
                    records_presence.append(data["idURL"] == "ERROR")
            if all(records_presence):
                for record_id in record_ids:
                    os.remove(f'/home/printer/data/{record_id}.json')
                return jsonify(
                    {
                        "error": "All records are missing from the database"
                    }
                )
            pdf = FPDF(format=(103, 40))
            pdf.add_font('dejavu-sans', style="", fname="assets/DejaVuSans.ttf")
            pdf.add_font('dejavu-sans-bold', style="B", fname="assets/dejavu-sans.bold.ttf")
            pdf.set_margin(0.5)
            for record_id in record_ids:
                with open(data_path.format(record_id=record_id), 'r') as f:
                    data = json.loads(f.read())
                    if data["idURL"] == "ERROR": continue
                    url = f"https://ff.wpboy.it/edit-item/?record={data['idURL']}"
                    img = qrcode.make(url, box_size=30, border=1)
                    img.save(qr_path)
                    # PDF
                    pdf.add_page()
                    pdf.set_font('dejavu-sans-bold', style="B", size=13)
                    pdf.multi_cell(h=4.5, align='C', w=100, text=f"{data['titolo']}", border=1)
                    pdf.image("qr.png", x=2, y=11, w=22, h=22)
                    pdf.set_y(13)
                    pdf.set_x(22)
                    pdf.set_font('dejavu-sans-bold', style="B", size=12)
                    pdf.cell(text=f"#Maga: {data['idmagazzino']} <> FE-id: {data['FEID']}", align="C", w=78)
                    pdf.set_y(18)
                    pdf.set_x(22)
                    pdf.set_font('dejavu-sans')
                    pdf.cell(text=f"Tipo: {data['tipo']} <> Pos: {data['posizione']}", align="C", w=78)
                    pdf.set_y(23)
                    pdf.set_x(22)
                    pdf.cell(text=f"Tiratura: {data['tiratura']}", align="C", w=78)
                    pdf.set_y(28)
                    pdf.set_x(22)
                    pdf.cell(text=f"Commentario: {data['commentario']}", align="C", w=78)
            pdf.output(pdf_path)
            with open(pdf_path, 'rb') as pdf_file:
                pdf_file_buffer = io.BytesIO(pdf_file.read())
                pdf_file_buffer.seek(0)
                for file in [qr_path, pdf_path]:
                    os.remove(file)
                for record_id in record_ids:
                    os.remove(f'/home/printer/data/{record_id}.json')
            return send_file(pdf_file_buffer, download_name=f"label.pdf", as_attachment=True)
        sleep(0.5)
    return jsonify({'error': 'Request timed out'})


@app.route('/print', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        records = request.form.get('id-input')
        if '-' in records:
            record_boundaries = records.replace(' ', '').split('-')
            record_ids = range(int(record_boundaries[0]), int(record_boundaries[-1])+1)
        elif ',' in records:
            record_ids = list(map(int, records.replace(' ', '').split(',')))
        else:
            record_ids = [int(records)]
        for record_id in record_ids:
            response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}', params={'idmagazzino': record_id})
            sleep(0.5)
        qr_path, pdf_path, data_path, last_record_data_path = "qr.png", "/home/printer/data/label.pdf", '/home/printer/data/{record_id}.json', f'/home/printer/data/{record_ids[-1]}.json'
        for _ in range(1000):
            if os.path.exists(last_record_data_path):
                records_presence = []
                for record_id in record_ids:
                    with open(data_path.format(record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        records_presence.append(data["idURL"] == "ERROR")
                if all(records_presence):
                    for record_id in record_ids:
                        os.remove(f'/home/printer/data/{record_id}.json')
                    return jsonify(
                        {
                            "error": "All records are missing from the database"
                        }
                    )
                pdf = FPDF(format=(103, 40))
                pdf.add_font('dejavu-sans', style="", fname="assets/DejaVuSans.ttf")
                pdf.add_font('dejavu-sans-bold', style="B", fname="assets/dejavu-sans.bold.ttf")
                pdf.set_margin(0.5)
                for record_id in record_ids:
                    with open(data_path.format(record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        if data["idURL"] == "ERROR": continue
                        url = f"https://ff.wpboy.it/edit-item/?record={data['idURL']}"
                        img = qrcode.make(url, box_size=30, border=1)
                        img.save(qr_path)
                        # PDF
                        pdf.add_page()
                        pdf.set_font('dejavu-sans-bold', style="B", size=13)
                        pdf.multi_cell(h=4.5, align='C', w=100, text=f"{data['titolo']}", border=1)
                        pdf.image("qr.png", x=2, y=11, w=22, h=22)
                        pdf.set_y(13)
                        pdf.set_x(22)
                        pdf.set_font('dejavu-sans-bold', style="B", size=12)
                        pdf.cell(text=f"#Magazzino: {data['idmagazzino']} <> FE-id: {data['FEID']}", align="C", w=78)
                        pdf.set_y(18)
                        pdf.set_x(22)
                        pdf.set_font('dejavu-sans')
                        pdf.cell(text=f"Tipo: {data['tipo']} <> Pos: {data['posizione']}", align="C", w=78)
                        pdf.set_y(23)
                        pdf.set_x(22)
                        pdf.cell(text=f"Tiratura: {data['tiratura']}", align="C", w=78)
                        pdf.set_y(28)
                        pdf.set_x(22)
                        pdf.cell(text=f"Commentario: {data['commentario']}", align="C", w=78)
                pdf.output(pdf_path)
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_file_buffer = io.BytesIO(pdf_file.read())
                    pdf_file_buffer.seek(0)
                    for file in [qr_path, pdf_path]:
                        os.remove(file)
                    for record_id in record_ids:
                        os.remove(f'/home/printer/data/{record_id}.json')
                return send_file(pdf_file_buffer, download_name=f"{data['idURL']}_label.pdf", as_attachment=True)
            sleep(0.5)
        return jsonify({'error': 'No data came back from Make.com'})
    return render_template('index.html')

@app.route('/callback', methods=['POST'])
def callback():
    pathlib.Path('/home/printer/data').mkdir(exist_ok=True)
    data = request.form
    with open(f'/home/printer/data/{data["idmagazzino"]}.json', 'w') as f:
        f.write(json.dumps(data))
    return data
