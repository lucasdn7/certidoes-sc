# Certidões SC — protótipo desktop

Protótipo local em Python/Tkinter para consultar e tentar baixar:

- **CND Estadual SC (SEF-SC)** via API REST, salvando o PDF retornado em Base64;
- **CNDT (TST)** via sessão HTTP, procurando o PDF na resposta;
- **CRF/FGTS (Caixa)** via sessão HTTP, procurando o PDF na resposta para CNPJ.

Os arquivos são organizados em `output/<documento>/<AAAA-MM-DD>/`. Cada consulta também cria `log.json`. Quando o portal não entrega um PDF ou muda o layout, o HTML/JSON de resposta é salvo na mesma pasta para diagnóstico.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e informe o CPF solicitante da SEF-SC
python main.py
```

O campo de CPF solicitante também pode ser preenchido diretamente na interface; nesta versão ele não é lido automaticamente do `.env` para evitar expor dados no formulário.

## Uso

1. Informe um CPF ou CNPJ válido em quantidade de dígitos.
2. Para CND Estadual SC, informe o CPF do solicitante autorizado.
3. Selecione as certidões desejadas.
4. Clique em **Emitir e baixar certidões**.
5. Consulte os PDFs e o `log.json` em `output`.

## Validação rápida sem emitir documentos

```bash
python -m compileall -q .
python - <<'PY'
from certidoes.utils import validar_documento
assert validar_documento('12.345.678/0001-95')[0]
assert validar_documento('123.456.789-01')[0]
print('Validação local OK')
PY
```

## Limitações importantes

- A disponibilidade e o fluxo dos portais são externos ao aplicativo. Não há garantia de que os formulários mantenham os mesmos campos ou endpoints.
- A emissão de certidões reais requer documentos autorizados e pode depender de validações do próprio órgão.
- A CND Federal, municípios Betha e certidão de falência não fazem parte deste protótipo inicial.
- Esta versão não tenta contornar CAPTCHA, login, certificado digital ou bloqueios do portal. Se um portal exigir isso, o resultado será diagnóstico/manual, não um PDF inventado.
- O CRF/FGTS não é aplicável a CPF comum; a interface permite a seleção, mas retorna `NAO_APLICAVEL` para CPF.
