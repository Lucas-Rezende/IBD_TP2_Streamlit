import streamlit as st
import pandas as pd
import sqlite3
import io

# Função para criar ou conectar ao banco de dados
def create_or_connect_database():
    conn = sqlite3.connect('/tmp/consult.db')
    cursor = conn.cursor()

    return conn

# Criar o aplicativo Streamlit
def main():
    st.title('Trabalho Prático 2 | Introdução à Banco de Dados :sunglasses:')

    # Adicione uma opção de seleção para o usuário escolher qual bloco de código executar
    opcao_bloco = st.selectbox('Selecione o Bloco de Código', ['Consulta 1', 'Consulta 2', 'Consulta 3', 'Consulta 4', 'Consulta 5', 'Consulta 6', 'Consulta 7', 'Consulta 8', 'Consulta 9', 'Consulta 10'])

    # Conectar ao banco de dados SQLite
    conn = create_or_connect_database()

    # Se a conexão for None, então uma das tabelas não existe
    if conn is None:
        st.write("Por favor, verifique o banco de dados e tente novamente.")
        return

    # Execute as consultas com base na opção do usuário
    if opcao_bloco == 'Consulta 1':
        # Quantidade de voos por semestre
        st.header("Quantidade de voos por trimestre.")
        query = """
        SELECT
            CASE
                WHEN V.DATAEMBARQUE BETWEEN '2023/01/01' AND '2023/03/31' THEN '1º'
                WHEN V.DATAEMBARQUE BETWEEN '2023/04/01' AND '2023/06/30' THEN '2º'
                WHEN V.DATAEMBARQUE BETWEEN '2023/07/01' AND '2023/09/30' THEN '3º'
                WHEN V.DATAEMBARQUE BETWEEN '2023/10/01' AND '2023/12/31' THEN '4º'
                ELSE 'Outros anos'
            END AS Trimestre,
            COUNT(V.LOCALIZADOR) AS NumeroDeViagens
        FROM
            VIAGEM V
        GROUP BY
            Trimestre
        ORDER BY
            Trimestre;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('Trimestre'))  # Use o método bar_chart do Streamlit para exibir os dados em um gráfico de barras

    if opcao_bloco == 'Consulta 2':
        # Calcular o Valor Total Perdido devido a No-Show e Cancelamentos Sem Reembolso (Apenas somando o Valor Liquido)
        st.header("Valor Total Perdido devido a No-Show e Cancelamentos Sem Reembolso (Apenas somando o Valor Liquido).")
        query = """
        SELECT
            SUM(T.VB) AS Valor_Perdido
        FROM
            TARIFA AS T
        JOIN
            REGISTRO AS R ON R.LOCALIZADOR = T.LOCALIZADOR
        WHERE
            R.NOSHOW = 'Sim'  OR (R.CANCELADO = 'Sim' AND R.VALORREEMBOLSO IS '0');
        """
        df = pd.read_sql_query(query, conn)
        st.table(df)  # Use o método dataframe do Streamlit para exibir os dados

    if opcao_bloco == 'Consulta 3':
        # Quantidade de voos de cada orgao superior
        st.header("Quantidade de voos de cada orgao superior.")
        query = """
        SELECT
            OS.NOMEOSUP AS nome_orgao_superior,
            COUNT(DISTINCT V.LOCALIZADOR) AS numero_de_voos
        FROM
            VIAGEM V
        JOIN
            ORGAO_SUPERIOR OS ON V.OSUPID = OS.OSUPID
        GROUP BY
            OS.NOMEOSUP
        ORDER BY numero_de_voos DESC;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('nome_orgao_superior'))

    if opcao_bloco == 'Consulta 4':
        #  identificar o Orgão Superior que mais viajou no primeiro trimestre(Trimestre com menos viagens)
        st.header("Orgão Superior que mais viajou no primeiro trimestre(Trimestre com menos viagens).")
        query = """
        SELECT
            OS.NOMEOSUP AS OrgaoSuperior,
            CASE
                WHEN V.DATAEMBARQUE BETWEEN '2023/01/01' AND '2023/03/31' THEN '1º'
            END AS Trimestre,
            COUNT(V.LOCALIZADOR) AS NumeroDeViagens
        FROM
            ORGAO_SUPERIOR OS
        JOIN
            VIAGEM V ON OS.OSUPID = V.OSUPID
        WHERE
            Trimestre = '1º'
        GROUP BY
            OrgaoSuperior, Trimestre
        ORDER BY
            NumeroDeViagens DESC, Trimestre
        LIMIT 5;
        """
        df = pd.read_sql_query(query, conn)
        st.table(df.set_index('OrgaoSuperior'))

    if opcao_bloco == 'Consulta 5':
        # Orgãos Solicitantes com mais No-Show e Cancelamentos Sem Reembolso (Comparar com os que mais viajam, tem relação?)
        st.header("Orgãos Solicitantes com mais No-Show e Cancelamentos Sem Reembolso (Comparar com os que mais viajam, tem relação?).")
        query = """
        SELECT
            OS.NOMEOSOLICIT AS OrgaoSolicitante,
            COUNT(CASE WHEN R.NOSHOW = 'Sim' THEN 1 END) AS QuantidadeNoShow,
            COUNT(CASE WHEN R.CANCELADO = 'Sim' AND R.VALORREEMBOLSO = 0 THEN 1 END) AS QuantidadeCancelamentosSemReembolso
        FROM
            ORGAO_SOLICITANTE OS
        JOIN
            VIAGEM V ON OS.OSOLICITID = V.OSOLICITID
        JOIN
            REGISTRO R ON V.LOCALIZADOR = R.LOCALIZADOR
        GROUP BY
            OS.NOMEOSOLICIT
        ORDER BY
            QuantidadeNoShow DESC, QuantidadeCancelamentosSemReembolso DESC
        LIMIT 5;
        """
        df = pd.read_sql_query(query, conn)
        st.table(df)  # Use o método dataframe do Streamlit para exibir os dados

    if opcao_bloco == 'Consulta 6':
        # média do desconto relativo entre a VTC e a VTG para cada companhia aérea. (Tributo pagado pela população e governo, respectivamente)
        st.header("Média do desconto relativo entre a VTC e a VTG para cada companhia aérea. (Tributo pagado pela população e governo, respectivamente).")
        query = """
        SELECT
            CA.NOMECOMPAEREA,
            AVG(T.VTC - T.VTG) AS MediaDesconto
        FROM
            COMPANHIA_AEREA CA
        JOIN
            VIAGEM V ON CA.COMPAEREAID = V.COMPAEREAID
        JOIN
            TARIFA T ON V.LOCALIZADOR = T.LOCALIZADOR
        WHERE
            T.VTC > 0 AND T.VTG > 0
        GROUP BY
            CA.NOMECOMPAEREA;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('NOMECOMPAEREA'))

    if opcao_bloco == 'Consulta 7':
        # numero de cancelamento de viagens em que se pagou multa por orgao superior
        st.header("Número de cancelamento de viagens em que se pagou multa por orgao superior")
        query = """
        SELECT
            OS.NOMEOSUP AS nome_orgao_superior,
            COUNT(DISTINCT R.localizador) AS numero_de_cancelamentos
        FROM
            VIAGEM V
        JOIN
            REGISTRO R ON V.LOCALIZADOR = R.LOCALIZADOR
        JOIN
            ORGAO_SUPERIOR OS ON V.OSUPID = OS.OSUPID
        WHERE
            R.CANCELADO = 'Sim'
            AND R.VALORMULTA > 0
        GROUP BY
            OS.NOMEOSUP
        ORDER BY
        numero_de_cancelamentos DESC;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('nome_orgao_superior'))

    if opcao_bloco == 'Consulta 8':
        st.header("Média de gasto na passagem por viagem para cada órgão superior.")
        query = """
        SELECT
            OS.NOMEOSUP AS OrgaoSuperior,
            AVG(T.VB) AS MediaGastoPassagemPorViagem
        FROM
            VIAGEM V
        JOIN
            ORGAO_SUPERIOR OS ON V.OSUPID = OS.OSUPID
        JOIN
            TARIFA T ON V.LOCALIZADOR = T.LOCALIZADOR
        GROUP BY
            OrgaoSuperior
        ORDER BY
            MediaGastoPassagemPorViagem DESC;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('OrgaoSuperior'))

    if opcao_bloco == 'Consulta 9':
        st.header("Contagem de Viagens por Classe Tarifária")
        query = """
        SELECT COMPANHIA_AEREA.NOMECOMPAEREA, CTB, COUNT(*) AS quantidade
        FROM VIAGEM
        JOIN COMPANHIA_AEREA ON VIAGEM.COMPAEREAID = COMPANHIA_AEREA.COMPAEREAID
        WHERE CTB IS NOT NULL
        GROUP BY CTB, COMPANHIA_AEREA.NOMECOMPAEREA
        ORDER BY quantidade DESC
        LIMIT 10;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('ClasseTarifaria'))

    if opcao_bloco == 'Consulta 10':
        st.header("Órgãos solicitantes que mais cancelaram viagens")
        query = """
        SELECT
            OS.NOMEOSOLICIT AS OrgaoSolicitante,
            COUNT(*) AS TotalCancelamentos
        FROM
            ORGAO_SOLICITANTE OS
        JOIN
            VIAGEM V ON OS.OSOLICITID = V.OSOLICITID
        JOIN
            REGISTRO R ON V.LOCALIZADOR = R.LOCALIZADOR
        WHERE
            R.CANCELADO = 'Sim'
        GROUP BY
            OrgaoSolicitante
        ORDER BY
            TotalCancelamentos DESC;
        """
        df = pd.read_sql_query(query, conn)
        st.bar_chart(df.set_index('OrgaoSolicitante'))

    # Fechar a conexão com o banco de dados apenas ao final de todas as operações
    # conn.close()

if __name__ == '__main__':
    main()