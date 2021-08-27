## Dicas para revisão de código

### Commits
- Título (1a linha do commit): apresentar resumo do que foi alterado/adicionado/removido.
ex: adiciona action que salva parametros no backend; exibe rótulo no componente de selecao de dataset;
- Descrição (outras linhas): dar mais detalhes de cada alteração:
- motivos das alterações
    ex: havia um bug que causava...; nova funcionalidade que faz isso...; código foi movido para...;
- bibliotecas adicionadas e versões (requirements.txt)
    ex: atualiza para SQLAlchemy 1.3.20;
- testes unitários criados/alterados
    ex: adiciona testes para a API PATCH /projects/{projectId}/experiments/{experimentId};
- alterações do `swagger.yaml`
    ex: adiciona documentação para `GET /projects/{projectId}`
- Mensagens auto-explicativas! Quem revisa o código deve entender o que foi feito (e porque foi feito) **sem perguntar para quem fez o commit**.
- Não devem ter conflitos. Solicitar que sejam resolvidas as ocorrências de "This branch has conflicts that must be resolved".

### SonarCloud Quality Gate
- Coverage > 80.0%, e sempre que possível = 100%
- 0 Bugs, 0 Code Smells, 0 Vulnerabilities

### Build Github actions COM SUCESSO

### Python
- Usar Python>=3.8
- Remover `print`.
- Não deixar código-fonte comentado.
- f-string `f'text-{variable}'` é melhor que `'text-{}'.format(variable)` e `'text-' + variable`
- Métodos que são chamados de outros arquivos `.py` **DEVEM TER Docstring**.
- Usar NumPy Style Python Docstring: https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html
- Usar sempre import absoluto.
ex: from projects.database import Base (BOM), from .database import Base (RUIM)

### Padrão de URLs para API REST
- Usar REST resource naming guide: https://restfulapi.net/resource-naming/
- USE SUBSTANTIVOS! **NÃO USE VERBOS NA URL!**
ex: `/projects/:projectId/executions` (BOM), `/project/execute` (RUIM)
- **SUBSTANTIVOS SEMPRE NO PLURAL!**
ex: `/deployments/:deploymentId` (BOM), `/deployment/:deploymentId` (RUIM)
- **SUBSTANTIVOS SÃO SEMPRE SEPARADOS POR UM ID. NÃO USE DOIS SUBSTANTIVOS SEGUIDOS**
ex: `/experiments/:experimentId/results` (BOM), `/experiments/results/:experimentId` (RUIM)
- Para consultar uma lista de resources (paginada ou não):
ex: `GET /resources?page=1&size=10&filter=...`
- Para criar um resource (e gerar um resourceId aleatório):
ex: `POST /resources`
- Para acessar um resource por resourceId:
ex: `GET /resources/{resourceId}`
- Para substituir/criar (ou atualizar TODOS OS CAMPOS) de um resource com resourceId específico:
ex: `PUT /resources/{resourceId}`
- Para excluir um resource:
ex: `DELETE /resources/{resourceId}`
- Para atualizar alguns campos de um resource:
ex: `PATCH /resources/{resourceId}`
- Em dúvidas? Mantenha uma consistência com as URLs já existem.
