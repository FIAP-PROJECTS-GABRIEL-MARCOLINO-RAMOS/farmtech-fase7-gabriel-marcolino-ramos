# Base de dados

`crop_yield.csv` é a base analisada neste projeto. Contém as seis variáveis
descritas no enunciado: cultura, precipitação, umidade específica, umidade relativa,
temperatura e rendimento.

- 156 registros e 6 colunas; quatro culturas com 39 registros cada.
- 39 combinações climáticas únicas; nenhuma linha totalmente duplicada.
- SHA-256: `07b3335f497e08e705b5835ee334426ac16cb24732c1bfaa994254d39f771b1b`.
- O arquivo foi preservado sem conversão de valores ou unidades.
- A licença de redistribuição da base não acompanha o arquivo. A atribuição do
  template não se aplica automaticamente ao dataset.

Os valores de precipitação e rendimento precisam de confirmação das unidades.
O notebook registra essa limitação e reporta erros na escala original do CSV.
