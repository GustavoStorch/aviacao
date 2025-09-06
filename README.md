# ✈️ Dashboard de Análise de Atrasos de Voos no Brasil

Análise de dados e dashboard interativo sobre os padrões de atrasos em voos comerciais no Brasil, utilizando dados abertos da ANAC para o período de 2022 a 2024.

Este projeto foi desenvolvido como parte da atividade N1 - Análise de Dados. O resultado final é um dashboard interativo onde é possível filtrar os dados e explorar visualmente os principais insights sobre a pontualidade da aviação brasileira.

### Acesse o Dashboard Online
**[>> Clique aqui para interagir com o dashboard ao vivo <<](https://aviacao-atrasos-gustavostorch.streamlit.app/)**

---

## 📊 Principais Análises e Perguntas Respondidas

O dashboard foi construído para responder às seguintes perguntas:

-   **Visão Geral:** Qual o volume total de voos, de atrasos e o percentual correspondente no período selecionado?
-   **Ranking de Aeroportos:** Qual o aeroporto com o maior número de decolagens atrasadas no Brasil?
-   **Ranking de Companhias Aéreas:** Qual o desempenho comparativo das principais companhias aéreas em relação a atrasos, ano a ano?
-   **Análise Temporal:** Quais dias da semana e períodos do dia concentram o maior volume de atrasos?
-   **Análise de Tendência (2022-2024):** Quais aeroportos apresentaram uma tendência consistente de aumento ou de redução no número de atrasos?

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

-   **Linguagem:** Python 3
-   **Bibliotecas de Análise:** Pandas
-   **Bibliotecas de Visualização:** Matplotlib e Seaborn
-   **Dashboard Interativo:** Streamlit
-   **Hospedagem:** Streamlit Community Cloud
-   **Versionamento:** Git e GitHub

---

## 📄 Fontes de Dados

Os dados utilizados neste projeto são públicos e foram obtidos das seguintes fontes:

1.  **Histórico de Voos (VRA):** [Agência Nacional de Aviação Civil (ANAC)](https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/voo-regular-ativo-vra)
2.  **Códigos de Aeroportos:** [DataHub.io - Airport Codes](https://datahub.io/core/airport-codes)
3.  **Códigos de Companhias Aéreas:** Dados auxiliares para mapeamento de siglas.

---

## 🚀 Como Executar o Projeto Localmente

Para executar este dashboard em sua máquina local, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [(https://github.com/GustavoStorch/aviacao.git))
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd aviacao
    ```

3.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    ```
    *No Windows:*
    ```bash
    .\venv\Scripts\activate
    ```
    *No Linux/Mac:*
    ```bash
    source venv/bin/activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute o aplicativo Streamlit:**
    ```bash
    streamlit run main.py
    ```

O dashboard deverá abrir automaticamente no seu navegador.

---

### Autor

**Gustavo Storch**

* **LinkedIn:** `https://www.linkedin.com/in/seu-linkedin/`
* **Medium:** `https://medium.com/@seu-usuario`
