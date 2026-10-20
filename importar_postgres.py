import os

import psycopg2
from ofxparse import OfxParser

ARQUIVO = "extrato.ofx"

# Ajuste os dados ou defina variáveis de ambiente (evita senha no GitHub)
CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB", "postgres"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "edu2708"),
}

SQL_CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);
"""

SQL_EXISTE = """
SELECT 1 FROM movimentacoes
WHERE data_movimentacao = %s AND valor = %s AND descricao = %s
LIMIT 1;
"""

SQL_INSERIR = """
INSERT INTO movimentacoes (data_movimentacao, valor, descricao)
VALUES (%s, %s, %s);
"""


def ler_transacoes(caminho):
    with open(caminho, "rb") as arquivo:
        ofx = OfxParser.parse(arquivo)
    return ofx.account.statement.transactions


def main():
    transacoes = ler_transacoes(ARQUIVO)
    inseridas = 0
    duplicadas = 0

    conexao = psycopg2.connect(**CONFIG)
    try:
        with conexao, conexao.cursor() as cur:  # commit/rollback automático
            cur.execute(SQL_CRIAR_TABELA)

            for t in transacoes:
                data = t.date.date()
                valor = t.amount
                desc = (t.memo or t.payee or "SEM DESCRIÇÃO").strip()[:255]

                # Bônus: evita gravar a mesma transação duas vezes
                cur.execute(SQL_EXISTE, (data, valor, desc))
                if cur.fetchone():
                    duplicadas += 1
                    continue

                cur.execute(SQL_INSERIR, (data, valor, desc))
                inseridas += 1
    finally:
        conexao.close()

    print(f"Lidas     : {len(transacoes)}")
    print(f"Inseridas : {inseridas}")
    print(f"Duplicadas (ignoradas): {duplicadas}")


if __name__ == "__main__":
    main()
