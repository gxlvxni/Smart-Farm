import serial
import json
import time
import mysql.connector

# --- Configurações ---
porta_serial = '/dev/ttyACM0'   # ajuste se necessário
baud_rate = 9600

# Conexão serial
porta = serial.Serial(porta_serial, baud_rate, timeout=1)
time.sleep(2)

# Conexão com o banco de dados MariaDB
db = mysql.connector.connect(
    host="localhost",
    user="farmuser",        # ou 'root'
    password="1234",
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

        # Leitura conforme novo formato do Arduino
        temperatura = dados["temperatura"]
        luminosidade = dados["luminosidade"]
        umidade_solo = dados["umidade_solo"]

        # Exibe dados no terminal
        print(f"Temp: {temperatura:.1f} °C | Luz: {luminosidade:.1f}% | Solo: {umidade_solo:.1f}%")

        # --- Grava no banco (ajuste: remove 'umidade') ---
        sql = """INSERT INTO sensores (temperatura, luminosidade, umidade_solo)
                 VALUES (%s, %s, %s)"""
        cursor.execute(sql, (temperatura, luminosidade, umidade_solo))
        db.commit()

        # --- Controle automático ---
        comando = None

        # Ventilador (baseado na temperatura)
        if temperatura > 29:
            comando = "VENTILADOR_ON"
        elif temperatura < 25:
            comando = "VENTILADOR_OFF"

        # Irrigação (baseado na umidade do solo)
        if umidade_solo < 30:
            comando = "IRRIGACAO_ON"
        elif umidade_solo > 38:
            comando = "IRRIGACAO_OFF"

        # Iluminação (baseado na luz ambiente)
        if luminosidade < 60:
            comando = "LUZ_ON"
        elif luminosidade > 60:
            comando = "LUZ_OFF"

        # --- Envia comando ao Arduino e registra no log ---
        if comando:
            porta.write((comando + "\n").encode())
            cursor.execute("INSERT INTO logs_comandos (comando) VALUES (%s)", (comando,))
            db.commit()
            print("Comando enviado:", comando)

        print("-" * 50)
        time.sleep(2)

    except json.JSONDecodeError:
        print("Dado inválido recebido:", linha)
    except Exception as e:
        print("Erro:", e)

