# Integrações e origem dos materiais

Os repositórios já entregues foram preservados. As adaptações pertencem exclusivamente à Fase 7.

| Fase | Material recuperado | Integração e melhoria |
|---|---|---|
| 1 | ZIP histórico `FarmTech_Solutions.zip`; cópias Python/R em `docs/legado/` | Cálculos de retângulo/trapézio, dose por hectare e por ruas; validação de finitude; persistência relacional; previsão Open-Meteo |
| 2 | `gabrielmarcolino23/FIAP-IA`, `fase2/cap1/` | Evolução do MER para esquema SQLite com produtor, cultura, talhão, sensor, leitura, operação, visão, alerta e notificação; chaves estrangeiras e índices |
| 3 | Mesmo repositório, `fase3/esp32/` e `fase3/python/` | Painel de sensores e CRUD integrados; ingestão atômica; evento único por sensor; firmware JSON Lines e ponte serial; origem explícita e separação solo/ar |
| 4 | Enunciado e feedback do portal sobre visão geral, correlação, previsão e métricas | Fluxos reimplementados no painel integrado, agora com conjunto de dados, treinamento e pesos reproduzíveis. Recuperação dos cinco arquivos antigos pelo navegador não foi concluída; não se declara adaptação direta de um `app.py` que não foi lido |
| 5 | `farmtech-fase5` (CSV e metodologia) | Treino de cinco regressores e baseline, avaliação agrupada por cenário, clusterização e outliers; integração SNS implementada nesta fase |
| 6 | `farmtech-fase6`, checkpoints YOLOv5n padrão, 30/60 épocas, CNN e oito imagens de teste | Inferência dos quatro modelos no painel, caixas YOLO, classificação CNN, histórico e ocorrência quando há veículo; não se interpreta gato/carro como praga ou doença |

O repositório histórico `FIAP-IA` foi consultado no commit `f17cd0269a8bf693758fd35589242be725245996`. A existência de arquivos nele não comprova que as atividades correspondentes tenham sido enviadas ao portal.

## Limitações preservadas

- DHT22 mede umidade do ar. Umidade do solo simulada é outra variável. Um ESP32 sem sensor próprio envia solo ausente.
- A leitura de LDR representa uma simulação de pH; não possui calibração química.
- Regras de solo abaixo de 30% e faixa de pH 5,5–7,5 são parâmetros didáticos para exercitar o fluxo. Não acionam relé físico nem prescrevem insumos.
- A base da Fase 5 tem 156 registros, 39 cenários e unidades de Yield/precipitação não confirmadas. A interface não associa automaticamente esses valores às leituras do solo.
- O modelo visual possui somente duas classes, gato e carro, com as limitações da Fase 6.
- Sem hardware físico validado nesta fase. Nenhuma mensagem AWS ou implantação é declarada como concluída sem evidência real.
