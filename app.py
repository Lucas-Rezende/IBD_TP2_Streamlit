import streamlit as st
import pandas as pd
import sqlite3
import io

def create_or_connect_database():
    conn = sqlite3.connect('consult.db')
    cursor = conn.cursor()

    return conn

def main():
    st.title('Trabalho Prático 2 | Introdução à Banco de Dados')

    opcao_bloco = st.selectbox('Selecione o Bloco de Código', ['Consulta 1', 'Consulta 2', 'Consulta 3', 'Consulta 4', 'Consulta 5', 'Consulta 6', 'Consulta 7', 'Consulta 8', 'Consulta 9', 'Consulta 10'])

    conn = create_or_connect_database()

    if conn is None:
        st.write("Por favor, verifique o banco de dados e tente novamente.")
        return

    if opcao_bloco == 'Consulta 1':
        # Quantidade de voos por trimestre
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
        st.header("Quantidade de voos de cada Órgão superior.")
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
        st.header("Órgão Superior que mais viajou no primeiro trimestre (Trimestre com menos viagens).")
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
        # companhias aéreas mais utilizadas em ordem decrescente
        st.header("Companhias aéreas mais utilizadas em ordem decrescente")
        query = """
        SELECT
        COMPANHIA_AEREA.NOMECOMPAEREA, COUNT(*) AS quantidade_voos
        FROM
        VIAGEM
        JOIN
        COMPANHIA_AEREA ON VIAGEM.COMPAEREAID = COMPANHIA_AEREA.COMPAEREAID
        GROUP BY
        COMPANHIA_AEREA.NOMECOMPAEREA
        ORDER BY
        quantidade_voos DESC;
        """
        df = pd.read_sql_query(query, conn)
        st.table(df)

    if opcao_bloco == 'Consulta 6':
        # média do desconto relativo entre a VTC e a VTG para cada companhia aérea. (Tributo pagado pela população e governo, respectivamente)
        st.header("Média do desconto relativo entre a VTC e a VTG para cada companhia aérea (Tributo pagado pela população e governo, respectivamente).")
        query = """
        SELECT COMPANHIA_AEREA.NOMECOMPAEREA,
            AVG(TARIFA.VTC) AS media_vtc,
            AVG(TARIFA.VTG) AS media_vtg,
            AVG(TARIFA.VTC - TARIFA.VTG) AS media_diferenca_vtg_vtc
        FROM
        VIAGEM
        JOIN
        COMPANHIA_AEREA ON VIAGEM.COMPAEREAID = COMPANHIA_AEREA.COMPAEREAID
        JOIN
        TARIFA ON VIAGEM.LOCALIZADOR = TARIFA.LOCALIZADOR
        GROUP BY
        COMPANHIA_AEREA.NOMECOMPAEREA;
        """
        df = pd.read_sql_query(query, conn)

        # Criar um gráfico de barras agrupadas para cada companhia aérea
        st.bar_chart(df.set_index('NOMECOMPAEREA'), use_container_width=True)

    if opcao_bloco == 'Consulta 7':
        # numero de cancelamento de viagens em que se pagou multa por orgao superior
        st.header("Número de cancelamento de viagens em que se pagou multa por Órgão superior")
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
        # Contagem de Viagens por Classe Tarifária
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
        st.table(df.set_index('CTB'))

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

        # Ordenar o DataFrame pelo total de cancelamentos em ordem decrescente
        df_sorted = df.sort_values(by='TotalCancelamentos', ascending=False)

        # Exibir apenas os N maiores órgãos solicitantes que mais cancelaram viagens
        _maiores = 10
        chart = st.bar_chart(df_sorted.head(_maiores).set_index('OrgaoSolicitante'), use_container_width=True)
        chart.pyplot().locator_params(axis='x', nbins=10)  # Altere o valor de nbins conforme necessário

if __name__ == '__main__':
    main()