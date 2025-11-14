// ** Código Arduino FINAL: Leds (Ativo-Alto) e Sensores Corrigidos **

// ================= CONFIGURAÇÕES ===================
#define LDR_PIN A0      //
#define SOIL_PIN A1     //
#define LM35_PIN A2     // 💡 LM35 agora está no A2, liberando o A0/A1
#define PIN_VENTILADOR 7
#define PIN_IRRIGACAO 8
#define PIN_ILUMINACAO 9

unsigned long intervaloEnvio = 10000; 
unsigned long ultimoEnvio = 0;

void setup() {
  Serial.begin(9600);
  pinMode(PIN_VENTILADOR, OUTPUT);
  pinMode(PIN_IRRIGACAO, OUTPUT);
  pinMode(PIN_ILUMINACAO, OUTPUT);
  pinMode(LM35_PIN, INPUT); 

  // Todos desligados inicialmente (Lógica Padrão: LOW desliga)
  digitalWrite(PIN_VENTILADOR, LOW); 
  digitalWrite(PIN_IRRIGACAO, LOW);
  digitalWrite(PIN_ILUMINACAO, LOW);

  Serial.println("Sistema SmartFarm iniciado!");
}

void loop() {
  unsigned long agora = millis();
  if (agora - ultimoEnvio >= intervaloEnvio) {
    ultimoEnvio = agora;

    // Leitura dos sensores
    int valorLM35 = analogRead(LM35_PIN);
    // 🌡️ FÓRMULA CORRETA: Tensão/passo * 100 para LM35
    float temperatura = valorLM35 * 0.48828125; 
    
    int valorLuz = analogRead(LDR_PIN);
    // 💡 Lógica corrigida do LDR: Alto analógico (1023) = Escuro. Inverte para % de claridade.
    float luzPercent = 100.0 - ((valorLuz / 1023.0) * 100.0); 
    
    int valorSolo = analogRead(SOIL_PIN);
    // 💧 Lógica corrigida do Solo: Alto analógico (1023) = Seco. Inverte para % de umidade.
    float soloPercent = 100.0 - ((valorSolo / 1023.0) * 100.0); 

    // Monta dados em formato JSON (Sem umidade do ar!)
    String dados = "{";
    dados += "\"temperatura\":" + String(temperatura, 1) + ",";
    dados += "\"luminosidade\":" + String(luzPercent, 1) + ",";
    dados += "\"umidade_solo\":" + String(soloPercent, 1);
    dados += "}";
    Serial.println(dados);
  }

  // ===== RECEBE COMANDOS DA RASPBERRY (LÓGICA PADRÃO) =====
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando.length() > 0) {
      // ATUADORES LÓGICA PADRÃO: ON = HIGH, OFF = LOW
      if (comando == "VENTILADOR_ON") digitalWrite(PIN_VENTILADOR, HIGH);
      else if (comando == "IRRIGACAO_ON") digitalWrite(PIN_IRRIGACAO, HIGH);
      else if (comando == "LUZ_ON") digitalWrite(PIN_ILUMINACAO, HIGH);

      else if (comando == "VENTILADOR_OFF") digitalWrite(PIN_VENTILADOR, LOW);
      else if (comando == "IRRIGACAO_OFF") digitalWrite(PIN_IRRIGACAO, LOW);
      else if (comando == "LUZ_OFF") digitalWrite(PIN_ILUMINACAO, LOW);
    }
  }
}
