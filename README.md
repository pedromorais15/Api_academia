# 🏋️ API Academia

API REST para gerenciamento de alunos e controle de acesso (catraca) de academia.

## 📋 Sobre o Projeto

Esta é uma aplicação backend desenvolvida com **Flask** que fornece endpoints para:
- 👤 Gerenciamento de alunos
- 🔐 Autenticação e autorização com JWT
- 📊 Integração com Firebase Firestore
- 🔄 Controle de catraca (acesso)
- 📖 Documentação interativa com Swagger

**Autores:** Joaquim e Pedro

---

## 🚀 Tecnologias Utilizadas

- **Flask** 3.1.0 - Framework web Python
- **Firebase Admin** 6.8.0 - Integração com Firestore
- **PyJWT** 2.10.1 - Autenticação com tokens JWT
- **Flask-CORS** 5.0.1 - Controle de requisições cross-origin
- **Flasgger** 0.9.7.1 - Documentação automática com Swagger
- **python-dotenv** 1.0.1 - Variáveis de ambiente
- **Gunicorn** 23.0.0 - Servidor WSGI para produção

---

## 📦 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Arquivo `firebase.json` com credenciais do Firebase (ou variável de ambiente `FIREBASE_CREDENTIALS`)

---

## ⚙️ Instalação

### 1. Clone ou baixe o projeto
```bash
cd Api_academia
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta_aqui
ADM_USUARIO=admin
ADM_SENHA=senha_admin
VERCEL=false
```

**Variáveis obrigatórias:**
- `SECRET_KEY`: Chave para assinar tokens JWT
- `ADM_USUARIO`: Usuário do administrador
- `ADM_SENHA`: Senha do administrador
- `VERCEL`: Define se está rodando no Vercel (true/false)
- `FIREBASE_CREDENTIALS` (opcional): JSON com credenciais do Firebase (necessário se `VERCEL=true`)

---

## 🏃 Como Executar

### Desenvolvimento Local
```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

### Produção
```bash
gunicorn app:app
```

---

## 📡 Endpoints Principais

### 🔐 Autenticação

**Login**
```
POST /login
```
Corpo da requisição:
```json
{
  "usuario": "admin",
  "senha": "senha_admin"
}
```

Resposta:
```json
{
  "message": "Login realizado com sucesso!",
  "token": "JWT_TOKEN_AQUI"
}
```

### 👥 Alunos

**Listar todos os alunos**
```
GET /alunos
```

**Criar novo aluno**
```
POST /alunos
Authorization: Bearer TOKEN
```

**Buscar aluno por ID**
```
GET /alunos/{id}
```

**Atualizar aluno**
```
PUT /alunos/{id}
Authorization: Bearer TOKEN
```

**Deletar aluno**
```
DELETE /alunos/{id}
Authorization: Bearer TOKEN
```

---

## 🔒 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação de rotas protegidas.

### Como usar:

1. **Faça login** em `/login` para obter um token
2. **Inclua o token** nas requisições subsequentes no header:
   ```
   Authorization: Bearer seu_token_aqui
   ```

Os tokens expiram em **1 hora**.

---

## 📖 Documentação Interativa

Acesse a documentação completa e teste os endpoints em:

```
http://localhost:5000/apidocs
```

Powered by Swagger/Flasgger

---

## 🗄️ Banco de Dados

O projeto utiliza **Firebase Firestore** como banco de dados.

### Coleções:
- **alunos** - Armazena dados dos alunos da academia
- **catraca** - Registro de acessos (opcional)

---

## 📁 Estrutura do Projeto

```
Api_academia/
├── app.py              # Aplicação principal
├── auth.py             # Autenticação JWT
├── openapi.yaml        # Documentação OpenAPI/Swagger
├── firebase.json       # Credenciais Firebase (não versionado)
├── requirements.txt    # Dependências Python
├── vercel.json         # Configuração Vercel
├── .env                # Variáveis de ambiente (não versionado)
└── README.md           # Este arquivo
```

---

## 🌐 Deploy

### Vercel

O projeto está pronto para fazer deploy no Vercel.

1. Configure as variáveis de ambiente no painel do Vercel:
   - `SECRET_KEY`
   - `ADM_USUARIO`
   - `ADM_SENHA`
   - `FIREBASE_CREDENTIALS`
   - `VERCEL=true`

2. Faça push do código para o repositório Git
3. Conecte o repositório no Vercel
4. Deploy automático será acionado

---

## ✅ Exemplo de Uso

```bash
# 1. Fazer login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d "{\"usuario\": \"admin\", \"senha\": \"senha_admin\"}"

# 2. Listar alunos (sem autenticação)
curl http://localhost:5000/alunos

# 3. Criar novo aluno (com autenticação)
curl -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_AQUI" \
  -d "{\"nome\": \"João Silva\", \"matricula\": \"12345\"}"
```

---

## 🐛 Troubleshooting

**Erro: "FIREBASE_CREDENTIALS não encontrada"**
- Certifique-se de ter o arquivo `firebase.json` na raiz do projeto OU configurar a variável `FIREBASE_CREDENTIALS` com o JSON das credenciais

**Erro: "Token ausente"**
- Verifique se você incluiu o header `Authorization: Bearer TOKEN` nas requisições protegidas

**CORS bloqueando requisições**
- A API está configurada para aceitar requisições de qualquer origem (`*`)
- Se precisar restringir, edite a configuração no `app.py`

---

## 📝 Licença

Projeto desenvolvido para fins educacionais no SENAI.

---

## 👨‍💼 Suporte

Para dúvidas ou bugs, entre em contato com os autores do projeto.
