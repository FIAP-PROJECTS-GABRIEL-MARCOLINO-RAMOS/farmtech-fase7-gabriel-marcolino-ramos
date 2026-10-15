# Direção do painel

Pesquisa Refero em 15/10/2026. Painel web Streamlit para o gestor de uma fazenda demonstrativa. Objetivo: acompanhar leituras, cadastrar talhões e transformar ocorrências em ações verificáveis.

## Referências e decisão antes da implementação

Referência dominante: [shadcn/ui](https://ui.shadcn.com), estilo Refero `c14c0a94-1037-449e-bf5b-4cb972656ac7`. Preservar fundo branco, tipografia sans-serif compacta, bordas cinza finas, ações escuras e cartões sem sombras fortes. Usar o sistema de componentes Streamlit da entrega anterior.

Referências secundárias consultadas: Arva (`c588152a-fa6b-42b5-bd25-01f79478a3a5`) e Open Collective (`f72e18d0-98f4-4e88-9754-5426589564ea`). Da Arva, adotar somente verde #07503f para a marca agrícola; não importar fotografia de campanha, tons creme ou tipografia decorativa. Open Collective reforça hierarquia de dados e contraste, sem importar sua cor de ação.

Padrões de produto: [Stellate Metrics](https://refero.design/pages/20fd86b0-d60e-4e06-b9de-911cd2b94280): navegação persistente, filtro antes de indicadores/gráfico e tabela de ocorrências abaixo. [Weights & Biases System](https://refero.design/pages/eba7517e-dcc0-4a82-891f-548c4489346a): gráficos separados por unidade e escala, sem somar grandezas incompatíveis.

| Decisão | Origem | Papel |
|---|---|---|
| Branco #ffffff, texto #0a0a0a, borda #e5e5e5 | shadcn/ui | Superfície, texto e separação |
| Sans-serif, corpo 14–16 px, título 32 px | shadcn/ui + restrição Streamlit | Leitura de dados e controles |
| Marca verde #07503f | Arva | Identidade; não substitui os estados semânticos |
| Preto para ação principal | shadcn/ui | Uma ação principal por formulário |
| Navegação por serviço e filtros locais | Stellate | Encontrar serviços sem duplicar telas |
| Gráficos com unidade explícita | W&B | Interpretar sensores e tendências |
| Etiquetas “Simulado”, “Pendente”, “Aceito pelo SNS” | Enunciado + evidência | Distinguir origem do dado e estágio real da entrega |

Não usar gradientes, cartões decorativos, fotografias sem função, textos gigantes nem percentual de disponibilidade fictício. O detalhe central é a trilha de uma leitura: origem → persistência → regra → ação → estado de notificação.
