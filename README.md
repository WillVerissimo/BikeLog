# 🚴 BikeLog

Sistema web acadêmico para gerenciar bicicletas e registrar pedaladas.

## Tecnologias
Python 3, Flask, SQLite, HTML, CSS e JavaScript.

## Funcionalidades
- Cadastro de usuário, login e logout por sessão.
- CRUD de bicicletas do usuário autenticado.
- CRUD de pedaladas, com validação e isolamento por usuário.
- Velocidade média calculada no servidor.
- Histórico e indicadores de distância, duração e velocidade média geral.

## Executar localmente
1. Clone o repositório e crie um ambiente virtual Python.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Certifique-se de que o banco SQLite está criado em `backend/database/bikelog.db`, conforme os scripts de inicialização do projeto.
4. Entre na pasta `backend` e execute `python app.py`.
5. Sirva a pasta `frontend` em `http://127.0.0.1:5500` (por exemplo, com Live Server no VS Code).
6. Acesse `login.html`, faça login e entre no dashboard.

**Atenção:** a API usa `http://127.0.0.1:5000` e o frontend espera a origem `http://127.0.0.1:5500`. Ajuste as configurações caso use outras portas. O modo debug é apenas para desenvolvimento.

## Verificação da AC3
- [ ] Login e logout
- [ ] Cadastro e listagem de bicicletas
- [ ] Cadastro de pedalada
- [ ] Edição de pedalada
- [ ] Exclusão de pedalada
- [ ] Estatísticas após cadastrar, editar e excluir
- [ ] Bloqueio de acesso sem login
- [ ] Isolamento dos registros entre usuários
- [ ] Responsividade e demonstração em vídeo

## Projeto acadêmico
Disciplina de Projeto de Software. As implementações da AC3 estão na branch `ac3-pedaladas` até a revisão final.
