# Mensageria AWS

Arquitetura: leitura ou inferência → transação SQLite (ocorrência + fila) → publicador Boto3 → tópico SNS Standard → e-mail com ação sugerida.

O código e o template estão preparados. **A implantação e o recebimento de e-mail ainda não foram comprovados.** Os testes automatizados usam um cliente simulado e não substituem evidência da AWS.

## Preparar o ambiente autorizado

1. Selecionar a conta/laboratório e região autorizados. A Fase 5 tinha uma estimativa de infraestrutura, sem implantação: este projeto não presume recursos anteriores existentes.
2. Usar credenciais temporárias do laboratório/SSO no perfil local. Não colocar chaves, tokens ou senhas no código, no Git ou em capturas.
3. Antes de criar recursos, conferir as permissões e o custo aplicável. O template cria um SNS Standard, uma assinatura de e-mail e uma política que exige TLS; não cria EC2, RDS, SMS ou usuários IAM. Criptografia KMS está habilitada por padrão; restrições do laboratório devem ser documentadas, sem contorná-las.
4. Implantar `infra/alertas.yaml` pelo console CloudFormation, com a região e o e-mail autorizados. Alternativa por CLI:

```bash
aws cloudformation deploy --template-file infra/alertas.yaml \
  --stack-name farmtech-fase7-alertas \
  --parameter-overrides EmailDestino=EMAIL_AUTORIZADO UsarKMS=true \
  --region REGIAO_AUTORIZADA --profile fiap
```

5. Confirmar a assinatura pelo link recebido no e-mail autorizado. Enquanto estiver `PendingConfirmation`, a existência do tópico não comprova entrega de mensagens.
6. Obter o TopicArn nos outputs da stack e configurar `FARMTECH_SNS_TOPIC_ARN` no terminal antes de iniciar o painel. O SDK usa a cadeia de credenciais AWS; nenhuma credencial é solicitada pelo dashboard.
7. Em “Sensores e IoT”, registrar uma leitura de demonstração com solo abaixo de 30%. Em “Alertas e AWS”, selecionar a ocorrência e usar “Enviar notificação pela AWS”. Também é possível executar `python -m farmtech notificar --id ID_DA_NOTIFICACAO --aws`.
8. Conferir o MessageId, assinatura confirmada e chegada do e-mail com a ação. O retorno do SNS comprova aceitação, não recebimento nem leitura do e-mail.

## Evidência exigida

Salvar capturas reais do tópico, assinatura confirmada, ocorrência no painel com MessageId e e-mail recebido. Ocultar endereços pessoais completos, identificadores de conta e parâmetros de confirmação. Registrar data, região, origem do evento e limitações em `docs/aws-validacao.md` somente após execução real.

O envio é explícito por ocorrência, evitando publicar todo o histórico simulado. A fila impede reenvio de itens já aceitos. Erros de rede são classificados como resultado incerto e exigem revisão; o SNS Standard não oferece garantia de entrega exatamente uma vez. Itens presos em “enviando” após encerramento do processo também precisam de conferência, sem retentativa cega.

## Referências oficiais

- [Assinaturas de e-mail SNS e confirmação](https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html).
- [Publicação e entrega](https://docs.aws.amazon.com/sns/latest/dg/sns-publishing.html).
- [Boas práticas de segurança](https://docs.aws.amazon.com/sns/latest/dg/sns-security-best-practices.html).
- [Criptografia do tópico](https://docs.aws.amazon.com/sns/latest/dg/sns-enable-encryption-for-topic.html).
- [Preços SNS](https://aws.amazon.com/sns/pricing/) e [custos KMS](https://docs.aws.amazon.com/sns/latest/dg/sns-key-management.html), consultados em 15/10/2026. Não há promessa de gratuidade; depende da conta, região, volume e créditos.
