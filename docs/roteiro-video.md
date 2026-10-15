# Roteiro de demonstração · até 10 minutos

Narração com a voz de Gabriel, como na Fase 6. Usar números em algarismos no texto de leitura. Não gravar o trecho de AWS como concluído antes da evidência real.

| Tempo estimado | Tela e demonstração |
|---|---|
| 0:00–0:35 | Identificação, objetivo e visão geral do painel |
| 0:35–1:35 | Calcular/cadastrar um talhão; editar; mostrar persistência e operações |
| 1:35–2:10 | Meteorologia: consultar 7 dias e distinguir previsão de sensor |
| 2:10–3:20 | Histórico de sensores, nova leitura, regra e alerta; explicar solo/ar/pH simulado |
| 3:20–4:45 | Cinco regressores e duas baselines; validação agrupada; previsão, correlação e erro por cultura |
| 4:45–6:10 | YOLO de 30/60 épocas, padrão e CNN; mesma imagem e histórico; limitações |
| 6:10–7:40 | AWS: tópico, assinatura confirmada, publicação pela aplicação, MessageId e e-mail recebido — somente após validação real |
| 7:40–8:30 | Estrutura única do projeto, execução por CLI, testes e limitações finais |

Os tempos são planejamento, não duração medida. Mostrar somente telas realmente executadas. Nas capturas da AWS, ocultar dados de conta, e-mail completo e links de confirmação. Não exibir credenciais temporárias nem configurações privadas.

## Texto de leitura — parte local

Olá, eu sou Gabriel Marcolino Ramos, RM565717. Este é o projeto da Fase 7, a consolidação de um sistema FarmTech. A proposta é reunir os serviços das fases anteriores em 1 projeto Python, com um painel que permite acompanhar a fazenda, registrar dados, executar análises e organizar ações a partir das ocorrências.

Na visão geral, aparecem os talhões cadastrados, a área total, as leituras e as ocorrências abertas. O cenário inicial contém dados simulados, identificados na interface. Esses números servem para demonstrar o funcionamento do sistema e não representam uma fazenda monitorada por equipamentos reais.

Aqui estão as funções da Fase 1. Eu posso calcular a área de um retângulo ou de um trapézio, informar uma dose de referência e obter o volume correspondente. Para o café, também existe o cálculo por comprimento e número de ruas. O sistema faz as contas a partir da dose informada; ele não prescreve um produto ou uma dosagem.

O cadastro é salvo em um banco relacional. A estrutura integra produtor, cultura, talhão, sensor, leitura, operação, análise visual, alerta e notificação. Posso consultar e atualizar um talhão ou arquivá-lo, preservando seu histórico. As chaves estrangeiras e as validações ajudam a impedir registros sem relacionamento válido.

A tela de meteorologia consulta a Open-Meteo e mostra uma previsão de 7 dias para a localização selecionada. Essa informação é uma previsão modelada, separada das medições locais. Uma falha na consulta externa não altera as leituras já registradas no banco.

Na parte de sensores, posso acompanhar o histórico, registrar uma leitura ou importar um lote. O lote é validado antes de ser salvo. Um evento repetido com o mesmo conteúdo não duplica a leitura; se o mesmo identificador trouxer outro conteúdo, o lote é rejeitado. Existe também um firmware para ESP32 e uma ponte serial em Python.

Uma distinção importante é que o DHT22 mede umidade do ar, e não umidade do solo. O LDR representa somente uma simulação de pH. Quando não existe um sensor de solo próprio, essa medição permanece ausente. O sistema não converte uma grandeza na outra.

Ao registrar uma umidade do solo abaixo de 30%, uma regra demonstrativa cria uma ocorrência com uma ação sugerida. Nesse caso, a ação é verificar a leitura, a calibração e o sistema de irrigação antes de decidir o acionamento. Não há acionamento de bomba física nem recomendação automática de aplicação de insumos.

A análise utiliza a base da Fase 5, com 156 registros e 39 cenários climáticos. Comparei 5 regressores e 2 baselines. Os cenários de treino e teste são separados, e a escolha do modelo usa validação cruzada apenas no treinamento. Assim, a mesma condição climática não aparece nas 2 partições.

A tabela apresenta os erros e o R². A comparação com a média por cultura ajuda a avaliar o ganho além das diferenças de escala entre culturas. O erro por cultura também é apresentado. As unidades de rendimento e a escala temporal da precipitação precisam de confirmação, então a previsão conserva a escala original do arquivo. Ela não é convertida em toneladas, doses ou decisões de irrigação.

Na visão computacional, o painel reutiliza os checkpoints da Fase 6. Posso executar o YOLO customizado de 30 épocas, o de 60 épocas, o YOLO padrão e a CNN treinada do zero. Os YOLOs localizam objetos; a CNN classifica a imagem inteira. Portanto, seus resultados não devem ser interpretados como a mesma tarefa.

As classes continuam sendo gato e carro. O projeto não diagnostica pragas ou doenças da plantação. Uma detecção de veículo pode gerar uma ocorrência para verificar se o acesso é esperado. A imagem processada e o resultado ficam disponíveis na trilha de execução. A comparação original da Fase 6 usa somente 8 imagens de teste e tem limitações, sem comprovar superioridade robusta de um modelo.

## Trecho de AWS — completar após a validação real

Mostrar o tópico Standard, a assinatura confirmada, a ocorrência publicada pela aplicação e o e-mail recebido. Descrever a região efetivamente usada, o estado da criptografia e eventuais restrições reais do laboratório. Distinguir o retorno MessageId da comprovação de chegada ao e-mail. Não inventar evidências se houver bloqueio de permissões.

## Encerramento

Todos esses serviços estão organizados na mesma pasta, com comandos de terminal e acesso pelo painel. O projeto inclui os dados, os pesos, o treinamento reproduzível e os testes da integração. As limitações continuam documentadas: sensores demonstrativos, hardware não validado nesta fase, regras didáticas, unidades da base a confirmar e reconhecimento visual restrito às classes treinadas.
