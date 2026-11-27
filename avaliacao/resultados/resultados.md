# Resultados da avaliação

Gerado automaticamente por `avaliacao/avaliar.py` em 2026-11-27 14:02 (Google Colab, CPU, `--gerar --llm hf --limiar 0.89`, LLM `Qwen/Qwen2.5-1.5B-Instruct`).

Perguntas: 22 (18 com resposta na base, 4 sem resposta).

## Comparação das configurações de recuperação

| Modelo | Chunk/overlap | Nº trechos | P@1 | P@3 | P@5 | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---|---|---|---|---|---|---|---|
| multilingual-e5-small | 300/60 | 217 | 44.4% | 29.6% | 20.0% | 44.4% | 77.8% | 83.3% | 0.613 |
| multilingual-e5-small | 600/100 | 110 | 66.7% | 46.3% | 27.8% | 66.7% | 88.9% | 88.9% | 0.759 |
| multilingual-e5-small | 1000/150 | 62 | 72.2% | 44.4% | 26.7% | 72.2% | 88.9% | 88.9% | 0.796 |

Obs.: como a maioria das perguntas tem só 1 trecho relevante, o P@3 máximo possível fica perto de 33%. Por isso o Hit@k e o MRR ajudam a comparar as configurações.

**Configuração escolhida (maior MRR; empate → maior Hit@3):** multilingual-e5-small, chunk 1000, overlap 150.

## Limiar de similaridade

Limiar usado: **0.89**. Limiar sugerido pelos dados: **0.89** (acurácia balanceada 84.7%).

| Pergunta | Tem resposta? | Similaridade do 1º trecho | 1º trecho é relevante? |
|---|---|---|---|
| P01 Qual é o prazo para cancelar a compra de um ingresso e ter direito ao reembolso? | sim | 0.918 | sim |
| P02 Comprei 3 ingressos no mesmo pedido. Posso cancelar só um deles? | sim | 0.911 | sim |
| P03 Consigo cancelar meu pedido pelo aplicativo da Sympla? | sim | 0.910 | não |
| P04 Paguei com Pix e cancelei a compra. Em quanto tempo recebo o dinheiro de volta? | sim | 0.902 | sim |
| P05 Como recebo o reembolso de uma compra no cartão se o cancelamento acontecer mais de 180 dias depois da compra? | sim | 0.917 | sim |
| P06 Qual a diferença entre a taxa de serviço e a taxa de processamento? | sim | 0.887 | não |
| P07 Até quando posso trocar o nome do titular do ingresso? | sim | 0.906 | não |
| P08 A Sympla cobra alguma coisa para trocar a titularidade do ingresso? | sim | 0.921 | não |
| P09 Pedi a troca de titularidade ao organizador. Quanto tempo ele tem para responder? | sim | 0.906 | sim |
| P10 Qual o valor máximo que o Seguro Reembolso Garantido devolve? | sim | 0.895 | não |
| P11 Posso contratar o Seguro Reembolso Garantido depois de finalizar a compra? | sim | 0.899 | sim |
| P12 Em quantas vezes posso parcelar no cartão e quanto é o juro? | sim | 0.904 | sim |
| P13 Posso pagar meu ingresso com o cartão iFood Benefícios? | sim | 0.910 | sim |
| P14 Paguei com cartão de crédito e o ingresso ainda não apareceu. Quanto tempo demora? | sim | 0.908 | sim |
| P15 Existe limite de ingressos de meia-entrada para idosos? | sim | 0.927 | sim |
| P16 Que documento o estudante precisa apresentar para ter meia-entrada? | sim | 0.908 | sim |
| P17 Se eu excluir minha conta na Sympla, perco acesso aos meus ingressos? | sim | 0.935 | sim |
| P18 Em quanto tempo o atendimento da Sympla responde? | sim | 0.912 | sim |
| P19 Qual é o número de telefone do SAC da Sympla para eu ligar? | não | 0.868 | — |
| P20 Quanto custa, em reais, a taxa de serviço da Sympla em um ingresso de R$ 100? | não | 0.900 | — |
| P21 Quem é o CEO da Sympla? | não | 0.848 | — |
| P22 A Sympla tem bilheteria física para comprar ingresso em dinheiro? | não | 0.889 | — |

## Falhas de recuperação na configuração escolhida (candidatas à análise de erros)

- **P03** (Consigo cancelar meu pedido pelo aplicativo da Sympla?): nenhum trecho relevante no top-3. Recuperados: 05_politica_de_cancelamento_de_pedidos#00, 01_cancelar_ingressos_e_reembolso#03, 05_politica_de_cancelamento_de_pedidos#01.
- **P06** (Qual a diferença entre a taxa de serviço e a taxa de processamento?): trecho relevante não ficou em 1º lugar (1º: 06_taxas_na_compra_de_ingressos#01).
- **P07** (Até quando posso trocar o nome do titular do ingresso?): trecho relevante não ficou em 1º lugar (1º: 07_troca_de_titularidade#02).
- **P08** (A Sympla cobra alguma coisa para trocar a titularidade do ingresso?): nenhum trecho relevante no top-3. Recuperados: 07_troca_de_titularidade#00, 07_troca_de_titularidade#01, 07_troca_de_titularidade#02.
- **P10** (Qual o valor máximo que o Seguro Reembolso Garantido devolve?): trecho relevante não ficou em 1º lugar (1º: 08_seguro_reembolso_garantido#00).
- **P20** (Quanto custa, em reais, a taxa de serviço da Sympla em um ingresso de R$ 100?): sem resposta na base, mas o trecho 06_taxas_na_compra_de_ingressos#00 passou do limiar (0.900); o LLM precisa recusar.

## Respostas geradas pelo LLM

Comportamento esperado (responder quando há resposta / recusar quando não há): **19/22**. A exatidão do conteúdo deve ser conferida manualmente comparando com a resposta esperada.

Marcação automática: P06, P08 e P10 = VERIFICAR (recusou, mas havia resposta); as demais = ok.

### P01 – Qual é o prazo para cancelar a compra de um ingresso e ter direito ao reembolso?

**Resposta do sistema:** O prazo para cancelar a compra de um ingresso e ter direito ao reembolso é de até 7 dias corridos a partir da data da compra. Este prazo deve ser cumprido para garantir o direito ao cancelamento com reembolso conforme o Código de Defesa do Consumidor.

**Esperada:** Até 7 dias corridos a partir da data da compra (direito de arrependimento do CDC); recomenda-se pedir com 48 horas de antecedência do evento.

Fontes recuperadas: Como cancelar ingressos e solicitar reembolso (01_cancelar_ingressos_e_reembolso.md, 2026-11-13); Como cancelar ingressos e solicitar reembolso (01_cancelar_ingressos_e_reembolso.md, 2026-11-13); Posso cancelar uma compra de um evento online ou presencial? (03_cancelar_compra_evento_online_ou_presencial.md, 2026-11-10) · tempo: 94.5 s

### P02 – Comprei 3 ingressos no mesmo pedido. Posso cancelar só um deles?

**Resposta do sistema:** Não, você não pode cancelar apenas um ingresso de um pedido com múltiplos ingressos. Todos os ingressos do pedido serão cancelados juntos.

**Esperada:** Não. O cancelamento é sempre do pedido inteiro; todos os ingressos do pedido são reembolsados.

Fontes recuperadas: Como cancelar ingressos e solicitar reembolso (01_cancelar_ingressos_e_reembolso.md, 2026-11-13) · tempo: 45.1 s

### P03 – Consigo cancelar meu pedido pelo aplicativo da Sympla?

**Resposta do sistema:** Sim, você pode cancelar seu pedido pelo aplicativo da Sympla. No momento de criar o seu evento, você tem acesso ao box onde está a política de cancelamento de pedidos. Você também pode encontrar mais detalhes dessa política no "Painel do evento". Para acessar, basta acessar seu evento no campo "Visão geral", no box "Detalhes do evento". Ao clicar em "Políticas do evento", você consegue ver todos os detalhes da política de cancelamento de pedidos.

**Esperada:** Não. O cancelamento deve ser feito pelo site, em Meus Ingressos > Cancelar Pedido.

Fontes recuperadas: Como funciona a política de cancelamento de pedidos nos eventos publicados na Sympla? (05_politica_de_cancelamento_de_pedidos.md, 2026-11-11); Como cancelar ingressos e solicitar reembolso (01_cancelar_ingressos_e_reembolso.md, 2026-11-13); Como funciona a política de cancelamento de pedidos nos eventos publicados na Sympla? (05_politica_de_cancelamento_de_pedidos.md, 2026-11-11) · tempo: 119.3 s

### P04 – Paguei com Pix e cancelei a compra. Em quanto tempo recebo o dinheiro de volta?

**Resposta do sistema:** Fonte: Como funciona o reembolso do meu pedido? (02_como_funciona_o_reembolso.md, 2026-11-13).

Se você pagau com Pix e cancela a compra, o reembolso será feito automaticamente para a mesma conta em que o pagamento foi realizado, em até 7 dias contados a partir da data de cancelamento da compra.

**Esperada:** Se o cancelamento for até 90 dias da compra, a devolução é automática para a mesma conta em até 7 dias; após 90 dias, por transferência após cadastrar dados bancários.

Fontes recuperadas: Como funciona o reembolso do meu pedido? (02_como_funciona_o_reembolso.md, 2026-11-13) · tempo: 74.5 s

### P05 – Como recebo o reembolso de uma compra no cartão se o cancelamento acontecer mais de 180 dias depois da compra?

**Resposta do sistema:** Para quem tiver cancelamento após 180 dias da compra, o reembolso deve ser realizado via conta bancária. Basta entrar em contato com o time de atendimento para cadastrar os dados bancários.

**Esperada:** O reembolso é feito via conta bancária; é preciso cadastrar os dados bancários com o atendimento.

Fontes recuperadas: Como funciona o reembolso do meu pedido? (02_como_funciona_o_reembolso.md, 2026-11-13); Como funciona o reembolso do meu pedido? (02_como_funciona_o_reembolso.md, 2026-11-13) · tempo: 60.9 s

### P06 – Qual a diferença entre a taxa de serviço e a taxa de processamento?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** A taxa de serviço cobre a operação da plataforma e os serviços da Sympla; a de processamento cobre os custos da transação financeira com o meio de pagamento e é devida pelo comprador.

Fontes recuperadas: nenhuma · tempo: 0.1 s

### P07 – Até quando posso trocar o nome do titular do ingresso?

**Resposta do sistema:** Até 24 horas antes do início do evento ou conforme prazo definido pela organização do evento. Se o ingresso não chegar para a nova pessoa após a troca, verifique se o e-mail foi preenchido corretamente no formulário e entre em contato com o suporte.

**Esperada:** Até 24 horas antes do início do evento (ou conforme prazo do organizador).

Fontes recuperadas: Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07) · tempo: 89.1 s

### P08 – A Sympla cobra alguma coisa para trocar a titularidade do ingresso?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** Não, a troca de titularidade é gratuita.

Fontes recuperadas: Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07) · tempo: 58.0 s

### P09 – Pedi a troca de titularidade ao organizador. Quanto tempo ele tem para responder?

**Resposta do sistema:** O organizador tem até 48 horas úteis para responder por e-mail após receber sua solicitação de troca de titularidade.

**Esperada:** Até 48 horas úteis; se não responder, é possível pedir mediação da Sympla.

Fontes recuperadas: Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07); Como trocar a titularidade do ingresso (07_troca_de_titularidade.md, 2026-11-07) · tempo: 69.2 s

### P10 – Qual o valor máximo que o Seguro Reembolso Garantido devolve?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** O valor nominal do ingresso, limitado a R$ 10.000 por participante (taxas não são reembolsadas).

Fontes recuperadas: Seguro Reembolso Garantido: mais segurança para sua compra! (08_seguro_reembolso_garantido.md, 2026-11-11) · tempo: 33.0 s

### P11 – Posso contratar o Seguro Reembolso Garantido depois de finalizar a compra?

**Resposta do sistema:** Não, após finalizar a compra, não é possível adicionar o Seguro Reembolso Garantido ao pedido. Você deve adicionar o seguro durante o checkout, antes de confirmar o pagamento.

**Esperada:** Não, o seguro só pode ser contratado durante a compra.

Fontes recuperadas: Seguro Reembolso Garantido: mais segurança para sua compra! (08_seguro_reembolso_garantido.md, 2026-11-11) · tempo: 56.5 s

### P12 – Em quantas vezes posso parcelar no cartão e quanto é o juro?

**Resposta do sistema:** Você pode parcelar seu pagamento em até 12x usando um cartão de crédito de bandeira Mastercard, Visa, Elo e American Express. O valor total da compra é acrescido de juros de 3.49% ao mês, cobrados no regime composto. O valor mínimo por parcela é R$5,00.

**Esperada:** Em até 12x, com juros de 3,49% ao mês (compostos) e parcela mínima de R$ 5,00.

Fontes recuperadas: Posso parcelar meu pagamento com cartão de crédito? (10_parcelamento_cartao_de_credito.md, 2026-11-01) · tempo: 73.5 s

### P13 – Posso pagar meu ingresso com o cartão iFood Benefícios?

**Resposta do sistema:** Sim, você pode pagar seu ingresso com o cartão iFood Benefícios se ele estiver disponível nas modalidades Cultura ou Saldo Livre.

**Esperada:** Sim, se o evento aceitar e houver saldo nas modalidades Cultura ou Saldo Livre.

Fontes recuperadas: Quais são as formas de pagamento disponíveis? (09_formas_de_pagamento.md, 2026-10-28); Quais são as formas de pagamento disponíveis? (09_formas_de_pagamento.md, 2026-10-28) · tempo: 53.9 s

### P14 – Paguei com cartão de crédito e o ingresso ainda não apareceu. Quanto tempo demora?

**Resposta do sistema:** Fonte: Como acessar meus ingressos (11_como_acessar_meus_ingressos.md, 2026-11-12)

Se você pagou com cartão de crédito e o ingresso ainda não apareceu, o processo pode levar até 72 horas úteis após o pagamento.

**Esperada:** Até 72 horas úteis (a compra pode estar em análise de segurança).

Fontes recuperadas: Como acessar meus ingressos (11_como_acessar_meus_ingressos.md, 2026-11-12) · tempo: 69.7 s

### P15 – Existe limite de ingressos de meia-entrada para idosos?

**Resposta do sistema:** Não existe limite de ingressos de meia-entrada para idosos. Todos os ingressos devem estar disponíveis com 50% de desconto para idosos, sem qualquer limitação de quantidade.

**Esperada:** Não. Idosos (60+) têm 50% de desconto sem limite de quantidade, diferente do limite de 40% para estudantes e PCD.

Fontes recuperadas: Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12); Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12); Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12) · tempo: 75.4 s

### P16 – Que documento o estudante precisa apresentar para ter meia-entrada?

**Resposta do sistema:** Para ter meia-entrada como estudante, o estudante deve apresentar a CIE - Carteira de Identificação Estudantil, que deve conter:

- Nome completo e data de nascimento;
- Foto;
- Grau de escolaridade;
- Nome da instituição de ensino na qual o estudante está matriculado;
- Data de validade até o dia 31 de março do ano subsequente ao de sua expedição;
- Certificação digital.

**Esperada:** A CIE (Carteira de Identificação Estudantil), apresentada no dia do evento.

Fontes recuperadas: Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12); Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12); Meia-entrada: confira tudo o que você precisa saber para produzir seu evento (18_meia_entrada.md, 2026-11-12) · tempo: 118.2 s

### P17 – Se eu excluir minha conta na Sympla, perco acesso aos meus ingressos?

**Resposta do sistema:** Sim, ao excluir sua conta na Sympla, você perderá o acesso aos seus ingressos e aos outros conteúdos adquiridos com o e-mail vinculado à conta excluída. Não será mais possível acessar o seu histórico ou informações de eventos passados.

**Esperada:** Sim, perde o acesso aos ingressos e ao histórico vinculados ao e-mail da conta excluída.

Fontes recuperadas: Como excluir minha conta da plataforma Sympla? (14_excluir_conta.md, 2026-11-01); Como acessar meus ingressos (11_como_acessar_meus_ingressos.md, 2026-11-12); Como excluir minha conta da plataforma Sympla? (14_excluir_conta.md, 2026-11-01) · tempo: 83.0 s

### P18 – Em quanto tempo o atendimento da Sympla responde?

**Resposta do sistema:** Fonte: Como falar com a Sympla? (15_como_falar_com_a_sympla.md, 2026-11-13)

O time de atendimento da Sympla dá um retorno em até 1 dia útil em qualquer um dos canais abaixo:

- E-mail (formulário)
- Chat ou redes sociais

Para questões que precisem de acompanhamento detalhado e envio de documentos ou comprovantes, clique em "Enviar uma solicitação" (no canto superior direito da Central de Ajuda) ou acesse diretamente https://ajuda.sympla.com.br/hc/pt-br/requests/new. Preencha o formulário com o máximo de detalhes possível para obter um retorno mais preciso e rápido.

**Esperada:** Em até 1 dia útil, por formulário, chat ou redes sociais.

Fontes recuperadas: Como falar com a Sympla? (15_como_falar_com_a_sympla.md, 2026-11-13); Qual a política de reembolso da Sympla? (04_politica_de_reembolso_organizador.md, 2026-11-11) · tempo: 139.5 s

### P19 – Qual é o número de telefone do SAC da Sympla para eu ligar?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** Não encontrei essa informação nos documentos da Sympla.

Fontes recuperadas: nenhuma · tempo: 0.1 s

### P20 – Quanto custa, em reais, a taxa de serviço da Sympla em um ingresso de R$ 100?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** Não encontrei essa informação nos documentos da Sympla.

Fontes recuperadas: Entendendo as taxas na compra de ingressos (06_taxas_na_compra_de_ingressos.md, 2026-11-05); Entendendo as taxas na compra de ingressos (06_taxas_na_compra_de_ingressos.md, 2026-11-05) · tempo: 44.4 s

### P21 – Quem é o CEO da Sympla?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** Não encontrei essa informação nos documentos da Sympla.

Fontes recuperadas: nenhuma · tempo: 0.0 s

### P22 – A Sympla tem bilheteria física para comprar ingresso em dinheiro?

**Resposta do sistema:** Não encontrei essa informação nos documentos da Sympla.

**Esperada:** Não encontrei essa informação nos documentos da Sympla.

Fontes recuperadas: nenhuma · tempo: 0.0 s
