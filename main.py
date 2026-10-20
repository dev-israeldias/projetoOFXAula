from ofxparse import OfxParser

ARQUIVO = "extrato.ofx"


def ler_transacoes(caminho):
    with open(caminho, "rb") as arquivo:
        ofx = OfxParser.parse(arquivo)
    return ofx.account.statement.transactions


def descricao(t):
    # Alguns bancos preenchem apenas "payee" ou deixam o memo vazio
    return (t.memo or t.payee or "SEM DESCRIÇÃO").strip()


# Ordem importa: a primeira categoria com palavra-chave encontrada vence
CATEGORIAS = {
    "Veículos": ["VEICULO", "ESTACIONAMENTO", "COMBUSTIVEL"],
    "Aluguel": ["ALUGUEL"],
    "Utilidades": ["ENERGIA", "INTERNET", "AGUA", "TELEFONE"],
    "Folha de pagamento": ["FOLHA"],
    "Material de consumo": ["MATERIAL"],
    "Equipamentos e TI": ["EQUIPAMENTOS", "CLOUD", "ASSINATURA"],
    "Receita de clientes": ["CLIENTE", "RECEBIMENTO", "PIX"],
}


def classificar(texto):
    texto = texto.upper()
    for categoria, palavras in CATEGORIAS.items():
        if any(p in texto for p in palavras):
            return categoria
    return "Outros"


def main():
    transacoes = ler_transacoes(ARQUIVO)
    por_categoria = {}

    print("EXTRATO BANCÁRIO")
    print("=" * 40)

    entradas = 0
    saidas = 0

    for t in transacoes:
        print(f"Data      : {t.date.strftime('%d/%m/%Y')}")
        print(f"Valor     : R$ {t.amount:.2f}")
        desc = descricao(t)
        categoria = classificar(desc)
        por_categoria[categoria] = por_categoria.get(categoria, 0) + t.amount
        print(f"Descrição : {desc}")
        print(f"Categoria : {categoria}")
        print("-" * 40)

        if t.amount > 0:
            entradas += t.amount
        else:
            saidas += t.amount

    saldo = entradas + saidas

    print(f"Total de movimentações: {len(transacoes)}")
    print(f"Entradas: R$ {entradas:.2f}")
    print(f"Saídas  : R$ {saidas:.2f}")
    print(f"Saldo   : R$ {saldo:.2f}")

    print()
    print("TOTAL POR CATEGORIA")
    print("=" * 40)
    for categoria, total in sorted(por_categoria.items(), key=lambda i: i[1]):
        print(f"{categoria:<22}: R$ {total:>10.2f}")


if __name__ == "__main__":
    main()
