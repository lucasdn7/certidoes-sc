

## Escopo completo do anexo

A interface agora contempla CND Federal RFB/PGFN, CND Estadual SC, CNDT, CRF/FGTS, Dívida Ativa Estadual PGE-SC, CND Municipal Betha com seleção de município, CND Municipal de Florianópolis e certidão de falência/recuperação judicial do TJ-SC.

A CND Estadual SC é o módulo que possui emissão/download automático na API atual. Os demais módulos que dependem de CAPTCHA, certificado digital, bloqueio anti-robô, comarca ou layout municipal específico retornam `ACAO_MANUAL` com link oficial. Isso é intencional: a aplicação não tenta contornar controles dos órgãos e não gera um arquivo sem confirmação oficial.

Para a emissão municipal, selecione o município Betha correspondente ao estabelecimento. Para falência/recuperação, a comarca sede precisa ser escolhida no tribunal competente. A necessidade de PGE-SC deve ser confirmada no edital, pois a CND da SEF-SC normalmente cobre a regularidade tributária estadual.
