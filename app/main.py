# encoding=utf8
import os
import tempfile
import math
import re
from flask import Flask, Blueprint, render_template, request, jsonify

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template("home.html", errMsg=None, flightInfo=None, contract03=None, contract07=None, contract14=None, contract10=None, contract0D=None, contract0E=None)
    else:
        filename = request.form.get('filename')
        fileDir = tempfile.gettempdir()
        filepath = fileDir + os.sep + filename
        if os.path.isfile(filepath) == False or os.path.exists(filepath) == False:
            return render_template("home.html", errMsg='文件不存在', flightInfo=None, contract03=None, contract07=None, contract14=None, contract10=None, contract0D=None, contract0E=None)

        flightInfo, contract03, contract07, contract14, contract10, contract0D, contract0E = parser(
            filepath)

        if flightInfo == None:
            return render_template("home.html", errMsg='此文件非 ADS 报文', flightInfo=None, contract03=None, contract07=None, contract14=None, contract10=None, contract0D=None, contract0E=None)

        return render_template("home.html", errMsg=None, flightInfo=flightInfo, contract03=contract03, contract07=contract07, contract14=contract14, contract10=contract10, contract0D=contract0D, contract0E=contract0E)


def transToComplement(source):  # 转换为补码
    last_1 = source.rfind('1')
    complement = ''
    for i in source[:last_1]:
        if i == '0':
            complement += '1'
        else:
            complement += '0'

    complement += source[last_1:]
    return complement


def parser(filepath):
    flightInfo = None
    contract03 = None
    contract07 = None
    contract10 = None
    contract14 = None
    contract0D = None
    contract0E = None

    with open(filepath, 'r') as f:
        data = f.readlines()

    planeNo = re.search(r'(?<= )\w-\d{4}', data[4])
    flightNo = re.search(r'(?<= )\w{6}(?=/)', data[4])
    code = re.search(r'-  ADS\.[\w,-]{10,}', data[6])
    if planeNo and flightNo and code:
        flightInfo = {
            "飞机号": planeNo.group(),
            "航班号":flightNo.group()
        }
    else:
        return (None,)*7

    code = code.group()[13:-5]
    codeOffest = 0
    while (codeOffest < len(code)):
        code_num = code[codeOffest:codeOffest+2]
        if code_num == '03':
            contract03 = {}
            byte = code[codeOffest: codeOffest + 4]
            codeOffest += 4
            binary = bin(int(byte, 16))[2:]
            binary = 6 * '0' + binary

            contractNo = binary[:8]
            contract03["合同号"] = "03"

            contractADS = str(int(binary[8:], 2))
            contract03["ADS Contract Request Number"] = contractADS

        elif code_num == '07':
            contract07 = {}
            byte = code[codeOffest: codeOffest + 22]
            codeOffest += 22
            binary = bin(int(byte, 16))[2:]
            binary = 5 * '0' + binary

            contractNo = binary[:8]
            contract07["合同号"] = "07"

            if binary[8] == '0':
                latitudeDirect = 'N'
                latitude = binary[9:29]
            else:
                latitudeDirect = 'S'
                latitude = transToComplement(binary[9:29])

            latitude = int(latitude, 2)
            latitude *= 180
            latitude /= 2 ** 20
            b, a = math.modf(latitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract07["latitude"] = latitudeDirect + a + "° " + b + "′"

            if binary[29] == '0':
                longitudeDirect = 'E'
                longitude = binary[30:50]
            else:
                longitudeDirect = 'W'
                longitude = transToComplement(binary[30:50])

            longitude = int(longitude, 2)
            longitude *= 180
            longitude /= 2 ** 20
            b, a = math.modf(longitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract07["longitude"] = longitudeDirect + a + "° " + b + "′"

            if binary[50] == '0':
                altitude = binary[51:66]
                aD = '+'
            else:
                altitude = transToComplement(binary[51:66])
                aD = '-'
            altitude = int(altitude, 2)
            altitude *= 4
            if aD == '-':
                altitude = -altitude
            altitude = str(altitude) + ' ft'
            contract07["altitude"] = altitude

            timestamp = binary[66:81]
            timestamp = int(timestamp, 2) * 0.125 / 60
            b, a = math.modf(timestamp)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract07["timestamp"] = a + ":" + b + " sec"

        elif code_num == '14':
            contract14 = {}
            byte = code[codeOffest: codeOffest + 22]
            codeOffest += 22
            binary = bin(int(byte, 16))[2:]
            binary = 3 * '0' + binary

            contractNo = binary[:8]
            contract14["合同号"] = "14"

            if binary[8] == '0':
                latitudeDirect = 'N'
                latitude = binary[9:29]
            else:
                latitudeDirect = 'S'
                latitude = transToComplement(binary[9:29])

            latitude = int(latitude, 2)
            latitude *= 180
            latitude /= 2 ** 20
            b, a = math.modf(latitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract14["latitude"] = latitudeDirect + a + "° " + b + "′"

            if binary[29] == '0':
                longitudeDirect = 'E'
                longitude = binary[30:50]
            else:
                longitudeDirect = 'S'
                longitude = transToComplement(binary[30:50])

            longitude = int(longitude, 2)
            longitude *= 180
            longitude /= 2 ** 20
            b, a = math.modf(longitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract14["longitude"] = longitudeDirect + a + "° " + b + "′"

            if binary[50] == '0':
                altitude = binary[51:66]
                aD = '+'
            else:
                altitude = transToComplement(binary[51:66])
                aD = '-'
            altitude = int(altitude, 2)
            altitude *= 4
            if aD == '-':
                altitude = -altitude
            altitude = str(altitude) + ' ft'
            contract14["altitude"] = altitude

            timestamp = binary[66:81]
            timestamp = int(timestamp, 2) * 0.125 / 60
            b, a = math.modf(timestamp)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract14["timestamp"] = a + ":" + b + " sec"

        elif code_num == '10':
            contract10 = {}
            byte = code[codeOffest: codeOffest + 10]
            codeOffest += 10
            binary = bin(int(byte, 16))[2:]
            binary = 3 * '0' + binary

            contractNo = binary[:8]
            contract10["合同号"] = "10"

            WS = binary[8:17]
            WS = round(int(WS, 2) * 0.5)
            WS = str(WS) + ' knots'
            contract10["Wind Speed"] = WS

            if binary[17] == '0':
                DD = "+"
                D = binary[18:27]
            else:
                DD = "-"
                D = transToComplement(binary[18:27])

            D = int(D, 2)
            D *= 180
            D /= 2 ** 8
            D = round(D)
            if DD == '-':
                D = -D
            D = str(D) + ' deg'
            contract10["Direction"] = D

            if binary[27] == '0':
                TemD = "+"
                Tem = binary[28:39]
            else:
                TemD = '-'
                Tem = transToComplement(binary[28:39])

            Tem = int(Tem, 2)
            Tem *= 0.25
            Tem = round(Tem)
            if TemD == '-':
                Tem = -Tem
            Tem = str(Tem) + ' deg C'
            contract10["Temperature"] = Tem

        elif code_num == '0D':
            contract0D = {}
            byte = code[codeOffest: codeOffest + 36]
            codeOffest += 36
            binary = bin(int(byte, 16))[2:]
            binary = 4 * '0' + binary

            contractNo = binary[:8]
            contract0D['合同号'] = "0D"

            if binary[8] == '0':
                N1latitudeD = 'N'
                N1latitude = binary[9:29]
            else:
                N1latitudeD = 'S'
                N1latitude = transToComplement(binary[9:29])

            N1latitude = int(N1latitude, 2)
            N1latitude *= 180
            N1latitude /= 2 ** 20
            b, a = math.modf(N1latitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract0D["N1latitude"] = N1latitudeD + a + "° " + b + "′"

            if binary[29] == '0':
                N1longitudeD = 'E'
                N1longitude = binary[30:50]
            else:
                N1longitudeD = 'W'
                N1longitude = transToComplement(binary[30:50])

            N1longitude = int(N1longitude, 2)
            N1longitude *= 180
            N1longitude /= 2 ** 20
            b, a = math.modf(N1longitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract0D["N1longitude"] = N1longitudeD + a + "° " + b + "′"

            if binary[50] == '0':
                N1altitude = binary[51:66]
                aD = '+'
            else:
                N1altitude = transToComplement(binary[51:66])
                aD = '-'
            N1altitude = int(N1altitude, 2)
            N1altitude *= 4
            if aD == '-':
                N1altitude = -N1altitude
            N1altitude = str(N1altitude) + ' ft'
            contract0D["N1altitude"] = N1altitude

            N1ETA = binary[66:80]
            N1ETA = int(N1ETA, 2)
            N1ETA *= 1
            N1ETA = str(N1ETA) + ' sec'
            contract0D["N1ETA"] = N1ETA

            # N2
            if binary[80] == '0':
                N2latitudeD = 'N'
                N2latitude = binary[81:101]
            else:
                N2latitudeD = 'S'
                N2latitude = transToComplement(binary[81:101])

            N2latitude = int(N2latitude, 2)
            N2latitude *= 180
            N2latitude /= 2 ** 20
            b, a = math.modf(N2latitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract0D["N2latitude"] = N2latitudeD + a + "° " + b + "′"

            if binary[101] == '0':
                N2longitudeD = 'E'
                N2longitude = binary[102:122]
            else:
                N2longitudeD = 'W'
                N2longitude = transToComplement(binary[102:122])

            N2longitude = int(N2longitude, 2)
            N2longitude *= 180
            N2longitude /= 2 ** 20
            b, a = math.modf(N2longitude)
            a = str(round(a))
            b = str(round(b * 60, 1))
            contract0D["N2longitude"] = N2longitudeD + a + "° " + b + "′"

            if binary[122] == '0':
                N2altitude = binary[123:138]
                aD = '+'
            else:
                N2altitude = transToComplement(binary[123:138])
                aD = '-'
            N2altitude = int(N2altitude, 2)
            N2altitude *= 4
            if aD == '-':
                N2altitude = -N2altitude
            N2altitude = str(N2altitude) + ' ft'
            contract0D["N2altitude"] = N2altitude

        elif code_num == '0E':
            contract0E = {}
            byte = code[codeOffest: codeOffest + 12]
            codeOffest += 12
            binary = bin(int(byte, 16))[2:]
            binary = 4 * '0' + binary
            contractNo = binary[:8]
            contract0E["合同号"] = "0E"

            if binary[8] == '0':
                TT = binary[9:21]
                D = '+'
            else:
                TT = transToComplement(binary[9:21])
                D = '-'
            TT = int(TT, 2)
            TT *= 180
            TT /= 2 ** 11
            TT = round(TT)
            if D == '-':
                TT = -TT
            TT = str(TT) + " deg"
            contract0E["True Track"] = TT

            GS = binary[21:34]
            GS = int(GS, 2)
            GS *= 0.5
            GS = str(round(GS)) + ' knots'
            contract0E["Ground Speed"] = GS

            if binary[34] == '0':
                VR = binary[35:46]
                D = '+'
            else:
                VR = transToComplement(binary[35:46])
                D = '-'

            VR = int(VR, 2)
            VR *= 16
            if D == '-':
                VR = -VR
            VR = str(VR) + ' fpmclimb'
            contract0E["Vertical Rate"] = VR

    return flightInfo, contract03, contract07, contract14, contract10, contract0D, contract0E


@main.route('/upload', methods=['POST'])
def fileupload():
    fileDir = tempfile.gettempdir()
    files = request.files.to_dict()

    key = 'file'
    file = files[key]
    filename = file.filename
    if 'Content-Range' in request.headers:
        range = request.headers['Content-Range']
        startBytes = int(range.split(' ')[1].split('-')[0])

        with open(os.path.join(fileDir, filename), 'a') as f:
            f.seek(startBytes)
            f.write(file.stream.read())
    else:
        file.save(os.path.join(fileDir, filename))

    return jsonify({
        'msg': 'ok',
        'filename': filename,
    })
