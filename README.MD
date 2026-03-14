## Estrutura básica do projeto
```
FlaskProject/
│
├── app/
│   ├── __init__.py                  # Application Factory (create_app)
│   │
│   ├── controllers/                 # Blueprints — rotas de cada membro
│   │   ├── __init__.py
│   │   ├── pessoa_controller.py     # Membro 1
│   │   ├── consentimento_controller.py  # Membro 2
│   │   ├── atendimento_controller.py    # Membro 3
│   │   ├── prontuario_controller.py     # Membro 4
│   │   ├── profissional_controller.py   # Membro 4
│   │   ├── abrigo_controller.py         # Membro 5
│   │   ├── vaga_controller.py           # Membro 5
│   │   └── encaminhamento_controller.py # Membro 6
│   │
│   ├── models/                      # Conexão com banco + regras de negócio
│   │   ├── __init__.py
│   │   ├── pessoa_model.py          # Membro 1
│   │   ├── consentimento_model.py   # Membro 2
│   │   ├── atendimento_model.py     # Membro 3
│   │   ├── prontuario_model.py      # Membro 4
│   │   ├── profissional_model.py    # Membro 4
│   │   ├── abrigo_model.py          # Membro 5
│   │   ├── vaga_model.py            # Membro 5
│   │   └── encaminhamento_model.py  # Membro 6
│   │
│   └── database.py                  # Configuração da conexão com o banco
│
├── .env                             # Variáveis de ambiente (não versionar!)
├── .env.example                     # Modelo do .env para a equipe
├── .gitignore
├── requirements.txt
├── run.py                           # Ponto de entrada da aplicação
└── README.md
```

## Swagger / documentação da API

A aplicação agora expõe documentação interativa via Swagger UI:

- UI: `/docs/`
- Spec JSON: `/openapi.json`

A spec cobre os blueprints já registrados em `create_app()` e descreve o contrato esperado dos endpoints.
Enquanto parte da API ainda retorna `501 Endpoint não implementado`, a documentação já serve como referência única para frontend, testes e evolução dos controllers.
