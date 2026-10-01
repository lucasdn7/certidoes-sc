

## Comportamento dos portais oficiais

- **SEF-SC:** a API usa o payload atual com `Identificacao.Type/Value` e `CpfSolicitante.Type/Value`, além da resposta `Data.ArquivoCndPdf.Dados`. O sistema já trata esse formato.
- **CNDT:** o portal atual é `https://cndt-certidao.tst.jus.br/gerarCertidao` e apresenta CAPTCHA. A aplicação não tenta contornar CAPTCHA; mostra um link para emissão manual.
- **CRF/FGTS:** a Caixa pode bloquear requisições provenientes de IPs de nuvem com HTTP 403. Nessa situação, a aplicação mostra o portal oficial para emissão manual, em vez de apresentar um erro técnico.
