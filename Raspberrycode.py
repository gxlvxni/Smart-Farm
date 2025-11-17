import serial
import json
import time
import mysql.connector
from datetime import datetime

# --- Configurações ---
[cite_start]porta_serial = '/dev/ttyACM0'   # ajuste se necessário [cite: 76]
[cite_start]baud_rate = 9600 [cite: 76]

# Conexão serial
[cite_start]porta = serial.Serial(porta_serial, baud_rate, timeout=1) [cite: 76]

# Aguarda o Arduino inicializar completamente
[cite_start]time.sleep(3) [cite: 76]

# Limpa buffers para evitar lixo inicial
[cite_start]porta.reset_input_buffer() [cite: 76]
[cite_start]porta.reset_output_buffer() [cite: 76]

# Conexão com o banco de dados MariaDB
db = mysql.connector.connect(    
    host="127.0.0.1",    
    user="vinicius",    
    password="1134707",    
    [cite_start]database="smartfarm") [cite: 76]
[cite_start]cursor = db.cursor() [cite: 76]
[cite_start]print("Conexões estabelecidas. Iniciando leitura...") [cite: 76]
[cite_start]print("Aguardando dados do Arduino e pronto para enviar comandos...") [cite: 76]

# --- Loop principal ---
while True:    
    [cite_start]linha = porta.readline().decode('utf-8', errors='ignore').strip() [cite: 77]    
    if not linha:       
        continue    
    # Ignora mensagens de inicialização
    if linha == "READY":        
        print("Arduino pronto. Iniciando leitura de dados reais...")        
        continue    
    try:        
        [cite_start]print("Recebido:", linha)  # mostra o que realmente veio da serial [cite: 77]        
        dados = json.loads(linha)        
        # Verifica se o JSON contém as chaves esperadas        
        [cite_start]if not all(k in dados for k in ["temperatura", "luminosidade", "umidade_solo"]): [cite: 78]            
            print("JSON incompleto recebido:", dados)            
            continue        
        [cite_start]temperatura = float(dados["temperatura"]) [cite: 78]
        [cite_start]luminosidade = float(dados["luminosidade"]) [cite: 78]
        [cite_start]umidade_solo = float(dados["umidade_solo"]) [cite: 78]
        
        # Exibe dados no terminal        
        [cite_start]print(f"Temp: {temperatura:.1f} °C | Luz: {luminosidade:.1f}% | Solo: {umidade_solo:.1f}%") [cite: 79]
        
        # --- Grava no banco com timestamp ---        
        [cite_start]timestamp = datetime.now() [cite: 79]
        sql = '''INSERT INTO sensores (temperatura, luminosidade, umidade_solo, data_hora)                 
                 [cite_start]VALUES (%s, %s, %s, %s)''' [cite: 79]
        [cite_start]cursor.execute(sql, (temperatura, luminosidade, umidade_solo, timestamp)) [cite: 79]
        [cite_start]db.commit() [cite: 79]
        
        # --- Controle automático (CORRIGIDO) ---  
        comandos = []        
        
        # **CORREÇÃO 3: Ventilador (temperatura)**
        # LIGA se T > 25. Se T <= 25 (ou seja, não precisa ligar), DESLIGA.
        if temperatura > 25:            
            [cite_start]comandos.append("VENTILADOR_ON") [cite: 80]
        elif temperatura <= 25:
            comandos.append("VENTILADOR_OFF")
            
        # **CORREÇÃO 4: Irrigação (umidade do solo)**
        # LIGA se solo < 45%. Se solo >= 45% (ou seja, umidade OK), DESLIGA.
        if umidade_solo < 45:            
            [cite_start]comandos.append("IRRIGACAO_ON") [cite: 80] 
        elif umidade_solo >= 45:
            comandos.append("IRRIGACAO_OFF")

        # **CORREÇÃO 5: Iluminação (luminosidade)**
        # LIGA se Luz < 70%. Se Luz >= 70% (ou seja, luz OK), DESLIGA.
        if luminosidade < 70:            
            [cite_start]comandos.append("LUZ_ON") [cite: 81]
        elif luminosidade >= 70:
            comandos.append("LUZ_OFF")
            
        # --- Envia comandos e registra log ---       
        [cite_start]for cmd in comandos: [cite: 82]
            try:                
                [cite_start]porta.write((cmd + "\r\n").encode()) [cite: 82]
                [cite_start]porta.flush() [cite: 82]
                [cite_start]time.sleep(0.2) [cite: 82]
                cursor.execute(                  
                   [cite_start]"INSERT INTO logs_comandos (comando, data_hora) VALUES (%s, %s)", [cite: 83]
                    (cmd, timestamp)                
                [cite_start]) [cite: 83]
                [cite_start]db.commit() [cite: 83]
                [cite_start]print("Comando enviado com sucesso:", cmd) [cite: 83]
            except Exception as e:   
                [cite_start]print("Erro ao enviar comando:", e) [cite: 84]
        [cite_start]print("-" * 50) [cite: 84]
        [cite_start]time.sleep(2) [cite: 84]
        
    except json.JSONDecodeError:        
        [cite_start]print("Dado inválido recebido:", linha) [cite: 84]
    except KeyError as e:        
        [cite_start]print("JSON sem chave esperada:", e) [cite: 84]
    except Exception as e:        
        [cite_start]print("Erro:", e) [cite: 84]
        [cite_start]time.sleep(2) [cite: 84]
