# Dados do projeto

`crop_yield.csv` preserva a base da Fase 5; origem e ressalvas em `ORIGEM_FASE5.md`. A unidade de Yield e a escala temporal da precipitação precisam de confirmação. O treinamento mantém os valores originais.

`imagens/` contém as oito fotografias de teste da Fase 6, oriundas do COCO val2017. O manifesto registra fonte, licença individual e SHA-256. São usadas para demonstração de inferência, sem retreinar o detector. As licenças podem incluir restrições não comerciais e compartilhamento pela mesma licença.

As leituras de demonstração são geradas por `telemetria.seed_demo` com semente 565717. Os horários se referem aos três dias anteriores à criação do banco; nenhuma leitura foi adquirida por hardware. O banco operacional em `runtime/` não é versionado.

Imagens e dados importados pelo usuário não são enviados à AWS. O SNS recebe somente o texto da ocorrência selecionada e sua ação. Não há envio de fotos, dados completos do banco ou credenciais no corpo da mensagem.
