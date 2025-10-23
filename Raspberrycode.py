import serial
import json
import time
import mysql.connector
from datetime import datetime

# --- Configurações ---
porta_serial = '/dev/ttyACM0'   # ajuste se necessário
baud_rate = 9600

# Conexão serial
porta = serial.Serial(porta_serial, baud_rate, timeout=1)
time.sleep(2)

# Conexão com o banco de dados MariaDB
db = mysql.connector.connect(
    host="10.1.25.78",
    user="vinicius",
    password="1134707",
    database="smartfarm"
)
cursor = db.cursor()

print("Conexões estabelecidas. Iniciando leitura...")

# --- Loop principal ---
while True:
    linha = porta.readline().decode('utf-8').strip()
    if not linha:
        continue

    try:
        dados = json.loads(linha)

        temperatura = dados["temperatura"]
        luminosidade = dados["luminosidade"]
        umidade_solo = dados["umidade_solo"]

        # Exibe dados no terminal
        print(f"Temp: {temperatura:.1f} °C | Luz: {luminosidade:.1f}% | Solo: {umidade_solo:.1f}%")

        # --- Grava no banco com timestamp ---
        timestamp = datetime.now()
        sql = """INSERT INTO sensores (temperatura, luminosidade, umidade_solo, data_hora)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (temperatura, luminosidade, umidade_solo, timestamp))
        db.commit()

        # --- Controle automático ---
        comandos = []

        # Ventilador (temperatura)
        if temperatura > 25:
            comandos.append("VENTILADOR_ON")
        elif temperatura < 20:
            comandos.append("VENTILADOR_OFF")

        # Irrigação (umidade do solo)
        if umidade_solo < 45:
            comandos.append("IRRIGACAO_ON")
        elif umidade_solo > 50:
            comandos.append("IRRIGACAO_OFF")

        # Iluminação (luminosidade)
        if luminosidade < 70:
            comandos.append("LUZ_ON")
        elif luminosidade > 80:
            comandos.append("LUZ_OFF")

        # --- Envia comandos e registra log ---
        for cmd in comandos:
            porta.write((cmd + "\n").encode())
            cursor.execute("INSERT INTO logs_comandos (comando, data_hora) VALUES (%s, %s)", (cmd, timestamp))
            db.commit()
            print("Comando enviado:", cmd)

        print("-" * 50)
        time.sleep(2)

    except json.JSONDecodeError:
        print("Dado inválido recebido:", linha)
    except Exception as e:
        print("Erro:", e)
        time.sleep(2)
