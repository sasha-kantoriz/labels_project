import io
import os
import json
import shutil
import pathlib
import requests
from time import sleep
from uuid import uuid4
from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import qrcode


app = Flask(__name__)


@app.route('/', methods=['GET'])
def print_label():
    request_id = uuid4().hex
    request_data_path = f'/home/printer/data/{request_id}'
    pathlib.Path(request_data_path).mkdir(exist_ok=True, parents=True)
    if request.args.get('id-input'):
        records = request.args.get('id-input')
        if '-' in records:
            record_boundaries = records.replace(' ', '').split('-')
            record_ids = range(int(record_boundaries[0]), int(record_boundaries[-1])+1)
        elif ',' in records:
            record_ids = list(map(int, records.replace(' ', '').split(',')))
        else:
            record_ids = [int(records)]
        for record_id in record_ids:
            response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}', params={'idmagazzino': record_id, 'request_id': request_id})
            sleep(0.5)
        qr_path, pdf_path, data_path, last_record_data_path = "qr-{record_id}.png", f"{request_data_path}/label.pdf", "{request_data_path}/{record_id}.json", f"{request_data_path}/{record_ids[-1]}.json"
        for _ in range(1000):
            if os.path.exists(last_record_data_path):
                records_presence = []
                for record_id in record_ids:
                    with open(data_path.format(request_data_path=request_data_path, record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        records_presence.append(data["idURL"] == "ERROR")
                if all(records_presence):
                    for record_id in record_ids:
                        os.remove(data_path.format(request_data_path=request_data_path, record_id=record_id))
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
                    with open(data_path.format(request_data_path=request_data_path, record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        if data["idURL"] == "ERROR": continue
                        url = f"https://ff.wpboy.it/edit-item/?record={data['idURL']}"
                        img = qrcode.make(url, box_size=30, border=1)
                        img.save(qr_path.format(record_id=record_id))
                        # PDF
                        pdf.add_page()
                        pdf.set_font('dejavu-sans-bold', style="B", size=13)
                        pdf.multi_cell(h=4.5, align='C', w=100, text=f"{data['titolo']}", border=1)
                        pdf.image(qr_path.format(record_id=record_id), x=2, y=11, w=22, h=22)
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
                    shutil.rmtree(request_data_path, ignore_errors=True)
                return send_file(pdf_file_buffer, download_name="label-magazzino.pdf", as_attachment=True)
            sleep(0.5)
    elif request.args.get('id-po'):
        records = request.args.get('id-po')
        if '-' in records:
            record_boundaries = records.replace(' ', '').split('-')
            record_ids = range(int(record_boundaries[0]), int(record_boundaries[-1]) + 1)
        elif ',' in records:
            record_ids = list(map(int, records.replace(' ', '').split(',')))
        else:
            record_ids = [int(records)]
        for record_id in record_ids:
            response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}',
                                    params={'idmagazzino': record_id, 'request_id': request_id})
            sleep(0.5)
        pdf_path, data_path, last_record_data_path = f"{request_data_path}/label-po.pdf", "{request_data_path}/{record_id}.json", f"{request_data_path}/{record_ids[-1]}.json"
        for _ in range(1000):
            if os.path.exists(last_record_data_path):
                records_presence = []
                for record_id in record_ids:
                    with open(data_path.format(request_data_path=request_data_path, record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        records_presence.append(data["idURL"] == "ERROR")
                if all(records_presence):
                    for record_id in record_ids:
                        os.remove(data_path.format(request_data_path=request_data_path, record_id=record_id))
                    return jsonify(
                        {
                            "error": "All records are missing from the database"
                        }
                    )
                pdf = FPDF(format=(103, 52))
                pdf.add_font('dejavu-sans', style="", fname="assets/DejaVuSans.ttf")
                pdf.add_font('dejavu-sans-bold', style="B", fname="assets/dejavu-sans.bold.ttf")
                pdf.set_margin(0)
                for record_id in record_ids:
                    with open(data_path.format(request_data_path=request_data_path, record_id=record_id), 'r') as f:
                        data = json.loads(f.read())
                        if data["idURL"] == "ERROR": continue
                        # PDF
                        pdf.add_page()
                        pdf.set_font('dejavu-sans-bold', style="B", size=15)
                        pdf.set_y(4)
                        pdf.set_x(0)
                        pdf.cell(text=f"PO#: {data['po']}", align="C", w=100)
                        pdf.set_font('dejavu-sans', size=10)
                        pdf.set_y(10)
                        pdf.set_x(0)
                        pdf.multi_cell(h=4.5, align='C', w=100, text=f"{data['titolo']}", border=0)
                        pdf.set_y(20)
                        pdf.cell(text="facsimile", align="C", w=100)
                        pdf.set_font('dejavu-sans-bold', style="B", size=15)
                        pdf.set_y(28)
                        pdf.set_x(0)
                        pdf.cell(text=f"PO#: {data['po']}", align="C", w=100)
                        pdf.set_font('dejavu-sans', size=13)
                        pdf.set_y(34)
                        pdf.set_x(0)
                        pdf.multi_cell(h=4.5, align='C', w=100, text=f"{data['titolo']}", border=0)
                        pdf.set_y(44)
                        pdf.set_font('dejavu-sans', size=10)
                        pdf.cell(text="commentary", align="C", w=100)
                pdf.output(pdf_path)
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_file_buffer = io.BytesIO(pdf_file.read())
                    pdf_file_buffer.seek(0)
                    shutil.rmtree(request_data_path, ignore_errors=True)
                return send_file(pdf_file_buffer, download_name="label-po.pdf", as_attachment=True)
            sleep(0.5)
    else:
        return jsonify({'error': 'Missing input parameters'})
    return jsonify({'error': 'Request timed out'})


@app.route('/callback', methods=['POST'])
def callback():
    data = request.form
    with open(f'/home/printer/data/{data["request_id"]}/{data["idmagazzino"]}.json', 'w') as f:
        f.write(json.dumps(data))
    return data
