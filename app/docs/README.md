# proposta-API-minima--sistema-de-atendimento

## `Sistema Integrado de Atendimento`

## 🔄 Fluxo Completo do Sistema

```
1. Cadastro PessoaRua (obrigatório)
         │
         ▼
2. Atendimento (SEMPRE ocorre — banho, alimentação, escuta)
         │
         ├──────────────────────────────────────┐
         │                                      ▼
         │                          Encaminhamento EMERGÊNCIA
         │                          (sem consentimento, dados mínimos)
         ▼
3. Consentimento?
   ├── NÃO → atendimentos continuam, sem prontuário
   └── SIM → Prontuário Social criado e desbloqueado

```

---


## `PessoaRua`

**Papel no sistema:** É o **núcleo absoluto de todo o sistema**. O cadastro da pessoa é o **primeiro passo obrigatório** antes de qualquer outro fluxo. Como pessoas em situação de rua frequentemente não possuem documentos, o sistema aceita cadastros provisórios com apelido e aparência física, garantindo que **nenhum atendimento seja bloqueado por burocracia** (US01). Todos os outros módulos — consentimento, atendimento, prontuário, encaminhamento e vagas — são vinculados a partir do `pessoa_id` gerado aqui.

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/pessoas` | Cria o cadastro provisório da pessoa usando apenas apelido e aparência física. É o **ponto de entrada obrigatório de toda a jornada** no sistema (US01) |
| `GET` | `/pessoas/:id` | Retorna os dados completos da pessoa. Consultado por profissionais antes de iniciar qualquer atendimento, consentimento ou encaminhamento |
| `GET` | `/pessoas?apelido=X` | Busca pessoas por apelido ou características físicas. Essencial para **evitar cadastros duplicados** quando a pessoa já foi atendida anteriormente |
| `PUT` | `/pessoas/:id` | Atualiza dados conforme novas informações são coletadas (ex: descoberta de documentos reais, atualização de endereço de referência) |
| `PUT` | `/pessoas/:id/risco` | Atualiza especificamente o **status de vulnerabilidade** (baixo/médio/alto/crítico). Alimenta decisões de prioridade de intervenção (US06) |

---

## `Consentimento`

**Papel no sistema:** É o **guardião legal do sistema**, baseado na LGPD. O consentimento funciona como uma **chave de ativação do prontuário social** — sem ele, o prontuário não pode ser criado nem acessado. Porém, é fundamental entender que **a ausência de consentimento nunca impede o atendimento**: banho, alimentação e escuta ocorrem independentemente. O consentimento apenas define **o que pode ser registrado e acessado** sobre a pessoa. Quando revogado, o prontuário torna-se imutável e dados sensíveis são ocultados (US02, US03).

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/consentimentos` | Registra o consentimento formal da pessoa para tratamento de dados. **Desbloqueia a criação e acesso ao prontuário social** (US02) |
| `GET` | `/consentimentos/:pessoa_id` | Verifica se a pessoa possui consentimento ativo. Consultado automaticamente pelo módulo de prontuário antes de qualquer exibição de dados sensíveis |
| `PUT` | `/consentimentos/:id/revogar` | Registra a revogação do consentimento. O prontuário passa a ser **somente leitura** e dados sensíveis são ocultados. **Não impede novos atendimentos simples** (US03) |
| `GET` | `/consentimentos/historico/:pessoa_id` | Retorna o histórico completo de consentimentos e revogações. Essencial para **auditoria e compliance com a LGPD** |

---

## `Atendimento`

**Papel no sistema:** É o **registro operacional do dia a dia** e o **único módulo que sempre ocorre**, independente de consentimento ou prontuário. Cada interação entre profissional e pessoa gera um atendimento (escuta, banho, alimentação). Esses registros formam a base estatística da unidade e, quando há consentimento, alimentam o prontuário social com cronologia. O `atendimento_id` também é o **vínculo obrigatório para qualquer encaminhamento** — seja formal ou de emergência (US04, US05).

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/atendimentos` | Registra um novo atendimento com tipo, data/hora e profissional responsável. **Sempre possível, independente de consentimento ou prontuário** (US04) |
| `GET` | `/atendimentos/:pessoa_id` | Lista todos os atendimentos de uma pessoa em ordem cronológica. Base do prontuário integrado quando há consentimento ativo (US05) |
| `GET` | `/atendimentos?unidade=X&data_inicio=Y&data_fim=Z` | Retorna atendimentos filtrados por unidade e período. Usado para **gerar estatísticas e relatórios operacionais** da unidade |
| `PUT` | `/atendimentos/:id` | Permite correção de um atendimento registrado com erro, com registro de auditoria da alteração |
| `DELETE` | `/atendimentos/:id` | Remove atendimento registrado indevidamente. Apenas com permissão de gestor |

---

## `Prontuario` + `Profissional`

**Papel no sistema:** O `Prontuario` é a **visão unificada e consolidada da trajetória da pessoa** — agrega atendimentos, encaminhamentos formais, status de risco e histórico social em uma única consulta. **Só existe se houver consentimento válido registrado.** Se o consentimento for revogado, o prontuário continua existindo no banco, mas fica bloqueado para edições e com dados sensíveis ocultos. É o endpoint mais complexo tecnicamente por exigir **JOINs entre múltiplas tabelas**. O `Profissional` é o ator que opera o sistema, necessário para rastreabilidade de todas as ações (US05).

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/profissionais` | Cadastra um novo profissional no sistema (assistente social, educador, etc.) |
| `GET` | `/profissionais/:id` | Retorna dados do profissional. Usado para exibir o responsável em atendimentos e encaminhamentos |
| `POST` | `/prontuarios` | Cria o prontuário social da pessoa. **Só pode ser criado após consentimento válido** registrado (US02) |
| `GET` | `/prontuarios/:pessoa_id` | Retorna o **prontuário integrado completo** — consolida dados da pessoa, atendimentos, encaminhamentos formais e status atual via múltiplos JOINs. **Bloqueado se não houver consentimento ativo** (US05) |
| `PUT` | `/prontuarios/:id` | Atualiza informações do prontuário (diagnósticos, observações sociais). **Bloqueado se consentimento for revogado** (US03) |

---

## `Abrigo` + `Vaga`

**Papel no sistema:** Gerencia em **tempo real** a disponibilidade de vagas nos abrigos. Profissionais consultam esse módulo para encaminhar pessoas corretamente, e gestores o utilizam para registrar entradas e saídas. O encaminhamento para um abrigo **pode ser gerado com ou sem prontuário**, pois trata-se de uma necessidade imediata de acolhimento. A entrada em um abrigo **não requer prontuário**, mas requer que a pessoa já esteja cadastrada no sistema (US07, US08, US09).

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/abrigos` | Cadastra um novo abrigo no sistema com capacidade total e endereço |
| `GET` | `/abrigos` | Lista todos os abrigos com contagem atual de vagas disponíveis. Visão geral para profissionais |
| `GET` | `/abrigos?vagas=disponivel` | Filtra **apenas abrigos com vagas livres**. Usado no momento do encaminhamento para acolhimento (US07) |
| `POST` | `/vagas/entrada` | Registra a entrada de uma pessoa em um abrigo. Altera status para "Ocupada" e **decrementa automaticamente o contador de vagas** do abrigo (US08) |
| `PUT` | `/vagas/:id/saida` | Registra a saída da pessoa. Libera a vaga e **incrementa automaticamente o contador de vagas** do abrigo (US09) |

---

## `Encaminhamento`

**Papel no sistema:** Formaliza a **ponte entre o sistema e a rede externa de apoio** (CRAS, CREAS, UBS, hospitais, delegacias, etc.). O encaminhamento **sempre exige um atendimento registrado**, mas **não exige prontuário**. Existem dois tipos: o **encaminhamento formal** (vinculado ao prontuário, com dados completos) e o **encaminhamento de emergência** (vinculado apenas ao atendimento, sem necessidade de consentimento, usado em situações urgentes como crises de saúde). O campo `prontuario_id` é opcional — quando `null`, indica encaminhamento de emergência. Sem esse módulo, os encaminhamentos ficam apenas como anotações verbais sem rastreabilidade (US10).

| Método | Endpoint | O que faz no sistema |
|--------|----------|----------------------|
| `POST` | `/encaminhamentos` | Gera um encaminhamento vinculado a um atendimento. Se houver prontuário ativo, é **formal** (dados completos). Se não houver, é **emergência** (dados mínimos). O campo `prontuario_id` é opcional — `null` indica emergência (US10) |
| `GET` | `/encaminhamentos/:pessoa_id` | Lista todos os encaminhamentos de uma pessoa (formais e de emergência). Permite ao profissional ver **o que já foi solicitado** e evitar duplicidade |
| `GET` | `/encaminhamentos?status=pendente` | Filtra encaminhamentos pendentes de resposta. Usado pelo gestor para **monitorar a resolução dos casos** |
| `PUT` | `/encaminhamentos/:id/status` | Atualiza o status do encaminhamento (`pendente → atendido → resolvido`). Mantém o **ciclo de vida rastreável** |
| `DELETE` | `/encaminhamentos/:id` | Cancela um encaminhamento emitido indevidamente, com registro do motivo para auditoria |

---
