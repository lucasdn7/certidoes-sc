# Certidões SC — aplicação web para Vercel

Aplicação web serverless para consultar e tentar baixar, em uma única operação:

- **CND Estadual SC (SEF-SC)** via API REST, salvando o PDF retornado em Base64;
- **CNDT (TST)** via sessão HTTP, procurando o PDF na resposta;
- **CRF/FGTS (Caixa)** via sessão HTTP, procurando o PDF na resposta para CNPJ.

A interface está em `public/` e a API em `api/index.py`. O projeto não grava CPF/CNPJ nem PDFs no GitHub: os PDFs retornados são mantidos na memória da requisição e enviados ao navegador como download.

## Publicar na Vercel sem instalar Git

1. Entre em [vercel.com](https://vercel.com) com sua conta.
2. Clique em **Add New → Project**.
3. Em **Import Git Repository**, escolha o GitHub e autorize o repositório privado `lucasdn7/certidoes-sc`.
4. Selecione `certidoes-sc` e clique em **Import**.
5. Mantenha o framework como **Other** e clique em **Deploy**.
6. Abra o domínio gerado pela Vercel.

Após o deploy, a página já estará acessível pelo navegador do computador da empresa. Nenhum programa local será necessário.

## Uso

1. Informe o CPF/CNPJ.
2. Informe o CPF do solicitante autorizado na SEF-SC para obter a CND Estadual.
3. Selecione os documentos.
4. Clique em **Emitir e baixar certidões**.
5. Baixe os PDFs retornados na seção de resultados.

## Limitações da hospedagem serverless

- A Vercel impõe limite de tempo para funções. O arquivo define `maxDuration: 60`; planos/contas podem aplicar limite inferior.
- Portais externos podem exigir CAPTCHA, login, certificado digital, bloquear datacenters ou alterar o HTML. Nesses casos a aplicação informa o diagnóstico em vez de fabricar um PDF.
- CND Federal, municípios Betha e certidão de falência ainda não estão nesta primeira versão web.
- Antes de uso institucional, proteja o projeto com autenticação e restrição de acesso. Não publique a URL sem controle, pois ela consulta documentos oficiais.

## Desenvolvimento local opcional

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py                  # interface desktop legada
```
