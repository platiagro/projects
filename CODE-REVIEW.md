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

### Padrão para códigos e mensagens de erro
- Use mensagens bastante descritivas. Pode usar várias frases sempre que necessário!
- Para ids inexistentes **INFORMADOS NA URL**:
```json
{"code": "...NotFound", "message": "The specified ... does not exist.", "status_code": 404}
```
- Para ids inexistentes **INFORMADOS NO REQUEST BODY**:
```json
{"code": "Invalid...", "message": "source ... does not exist", "status_code": 400}
```
- Para campos obrigatórios faltantes (não validados pelo pydantic) **INFORMADOS NO REQUEST BODY**:
```json
{"code": "MissingRequired...", "message": "Necessary at least ...", "status_code": 400}
```
- Para campos que violam restruções de valor único **INFORMADOS NO REQUEST BODY**:
```json
{"code": "...Exists", "message": "a ... with that ... already exists", "status_code": 400}
```
- Para erros internos (ex: erro em operações do Kubernetes/Kubeflow):
```json
{"code": "Cannot...", "message": "...", "status_code": 500}
```

## Testes Unitários
- Todo teste deve ter um docstring descrevendo o que é testado:
```python
def test_something_exception(self):
    """
    Should raise an exception when ...
    """
```
- Cada função deve preferencialmente testar 1 única chamada:
```python
 def test_something_success(self):
    """
    Should return ok.
    """
    result = something()
    assert result == "ok"

def test_something_exception(self):
    """
    Should raise an exception.
    """
    with self.assertRaises(Exception):
        something()
```
- Utilize [tests/util.py](./tests/util.py) para códigos de teste reutilizáveis.
```python
import tests.util as util

def setUp(self):
    """
    Sets up the test before running it.
    """
    util.create_mocks()

def test_create_template_given_name_already_exists(self):
    """
    Should return http status 400 and a message 'a template with given name already exists'.
    """
    template_name = util.MOCK_TEMPLATE_NAME_1
    experiment_id = util.MOCK_UUID_1
    rv = TEST_CLIENT.post(
        "/templates",
        json={
            "name": template_name,
            "experimentId": experiment_id,
        },
    )
    ...
```
- Quando criar um mock de uma função, use o [`assert_any_call`](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_any_call) ou [`assert_called_with`](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_with) para testar se a função recebeu os parâmetros adequados.<br>
Caso algum dos parâmetros tenha valor dinâmico, ou possa ser ignorado, utilize [`mock.ANY`](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.ANY).
```python
@mock.patch("projects.kubernetes.kube_config.config.load_incluster_config")
@mock.patch(
    "kubernetes.client.CustomObjectsApi.list_namespaced_custom_object",
    return_value={"items": []},
)
@mock.patch(
    "kfp.Client",
    return_value=util.MOCK_KFP_CLIENT,
)
def test_delete_project_success(
    self, mock_kfp_client, mock_list_namespaced_custom_object, mock_load_kube_config
):
    ...
    mock_load_kube_config.assert_any_call()
    mock_list_namespaced_custom_object.assert_any_call(
        "machinelearning.seldon.io", "v1", "anonymous", "seldondeployments"
    )
    mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
```
