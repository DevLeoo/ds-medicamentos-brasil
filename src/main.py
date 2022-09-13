# import packages
import streamlit as st
import pandas as pd
from constants import states, price_correlation

pd.options.plotting.backend = "plotly"

unwanted = '(*)'
FILE_PATH = './raw/TA_PRECO_MEDICAMENTO.csv'

# Set page title and favicon
st.set_page_config(page_title='Medicamentos - Brasil', page_icon="💊", layout='centered', initial_sidebar_state='auto')

# Set web page title
st.title("Preço dos medicamentos - Brasil 🇧🇷")

# Set content description

st.markdown(
    "Os dados representam a **lista de preços de Medicamentos**, contemplando o "
    "preço Fábrica, ou preço fabricante (PF), que é o preço máximo que pode ser "
    "praticado pelas empresas produtoras ou importadoras do produto e pelas empresas "
    "distribuidoras. O PF indica o preço máximo permitido para venda a farmácias e "
    "drogarias e o Preço Máximo ao Consumidor (PMC) indica o preço teto de venda ao consumidor."
)

st.subheader("Dicionário de variáveis")
st.markdown(
    """* **substância**: É o nome comercial dado ao medicamento
* **cnpj**: Código de identificação da pessoa jurídica.
* **laboratório**: É o nome da empresa detentora do registro sanitário
* **produto**: É o nome da empresa detentora do registro sanitário
* **apresentação**: É a descrição de como o medicamento é apresentado, quanto a sua forma farmacêutica, dosagem e quantidade
* **classe terapêutica**: É a Classificação Anatômica de Produtos Farmacêuticos
* **tipo de produto** (status do produto): Tipo é a categorização do medicamento
por tipo de produto em Biológicos, Biológico Novo, Similar, Genérico, Novo, Específico,
Radiofármaco.
* **regime de preço**: Indica se o preço do medicamento é regulado ou não 
* **restrição hospitalar**: Indica se tem ou não restrição hospitalar
* **icms 0%**: ndica se o medicamento tem ou não o imposto sobre Circulação de
Mercadorias e Prestação de Serviços (ICMS), onde o imposto de cada Estado deve ser
considerado.
* **tarja**: Indica qual se a venda do medicamento necessita de recita.
**Observação**: 
* PF: Preço de Fábrica - Refere-se ao preço pelo qual um laboratório ou
distribuidor de medicamentos pode comercializar no mercado brasileiro um medicamento
* PMC: Preço Máximo ao Consumidor - É o preço a ser praticado pelo
comércio varejista de medicamentos, ou seja, farmácias e drogarias.
**Alíquotas**
As seguintes alíquotas referem-se às seguintes unidades federativas indicadas pelas respectivas siglas:
* **20%**: RJ
* **18%**: AM, AP, BA, CE, MA, MG, PB, PE, PI, PR, RN, RS, SE, SP, TO.
* **17,5%**: RO.
* **17%**: AC, AL, ES, GO, MT, MS, PA, RR, SC, DF.
* **12%**": SP, MG.
* **ALC**: Refere-se as seguintes zonas de livre comércio dos seus respectivos estados: 
Manaus/Tabatinga (AM), Boa Vista/Bonfim (RR), Macapá/Santana (AP), Guajará-Mirim (RO),
Brasiléia/Eitacolândia/Cruzeiro do Sul (AC)
"""
)


def clean_tarja_values(val: str):
    if 'vermelha' in val:
        val = "Tarja Vermelha"
    elif 'preta' in val:
        val = 'Tarja Preta'
    elif 'livre' in val:
        val = 'Venda Livre / Sem Tarja'
    else:
        val = None
    return val


def get_key(example):
    for key, val in price_correlation.items():
        if val == example or example in val:
            return key


def get_filter(type: str, tax: int):
    return f'{type} {tax}%'


@st.cache()
def set_state():
    st.session_state.vars = {
        "tarja": "", "medicine": "", "state": "", "type": "", "value": ""
    }


@st.cache()
def get_data_frame() -> pd.DataFrame:
    df = pd.read_csv(FILE_PATH, encoding="ISO-8859-1", sep=";")
    return clean_data_frame(df)


def clean_data_frame(df):
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis='columns', inplace=True)
    df = df.drop(columns=['ean 1', 'ean 2', 'ean 3', 'código ggrem', 'comercialização 2020', 'registro',
                     'análise recursal', 'lista de concessão de crédito tributário (pis/cofins)', 'cap', 'confaz 87'])
    df = df.dropna()
    df["tarja"] = (
        df["tarja"].apply(lambda x: clean_tarja_values(str(x)
                                                       .replace(unwanted, "")
                                                       .replace('-', '')
                                                       .strip().lower()))
    )

    for col in df.loc[:, 'pf sem impostos': 'pmc 20%'].columns:
        df[col] = df[col].apply(lambda x: str(x).replace(',', '.'))

    df = df.astype({"pf sem impostos": "float64", "pf 0%": "float64", "pf 12%": "float64", "pf 17%": "float64",
                    "pf 17% alc": "float64", "pf 17,5%": "float64", "pf 17,5% alc": "float64", "pf 18%": "float64",
                    "pf 18% alc": "float64", "pf 20%": "float64", "pmc 0%": "float64", "pmc 12%": "float64",
                    "pmc 17%": "float64", "pmc 17% alc": "float64", "pmc 17,5%": "float64", "pmc 17,5% alc": "float64",
                    "pmc 18%": "float64", "pmc 18% alc": "float64", "pmc 20%": "float64"})
    return df


def get_descriptions(**filters):
    df = get_data_frame()
    filter = get_filter(filters.get('type'), get_key(filters.get('state')))
    filtered_col = [col for col in df.columns if filter in col]
    df = df[(0 < df.get(filtered_col[0])) & (df.get(filtered_col[0]) < filters.get('value'))]
    return df.describe()


def get_results(**filters):
    df = get_data_frame()
    new_df = df

    if st.session_state.vars["tarja"] != filters.get('tarja'):
        st.session_state.vars["tarja"] = filters.get('tarja')
        new_df = df.loc[(df.tarja == filters.get('tarja'))]

    if st.session_state.vars["medicine"] != filters.get('medicine'):
        new_df = df.loc[df.substância == filters.get('medicine')]
        st.session_state.vars["medicine"] = filters.get('medicine')

    return new_df


with st.sidebar:
    add_subheader = st.subheader("Filtros")
    tarja = st.radio(
        "Escolha o tipo de tarja",
        get_data_frame()["tarja"].dropna().unique()
    )

    medicine = st.selectbox("Selecione o medicamento",  get_data_frame()["substância"].dropna().unique())
    st.info("Para os dados estatisticos")
    state = st.selectbox("Selecione o estado", states)
    price_type = st.selectbox("Selecione o tipo de preço", ("Fábrica", "Consumidor Final"))
    value = st.slider("Selecione os valores", min_value=0, max_value=1000, value=100)

# Set state auxiliar variables
set_state()
type = "pf" if price_type == "Fábrica" else "pmc"
result = get_results(tarja=tarja, medicine=medicine)

if st.checkbox("Mostrar tabela"):
    st.dataframe(result)
    st.text(f"Foram carregadas {float(result.shape[0])} linhas")

st.markdown("---")
st.subheader("Descrição estatística dos valores")
descriptions = get_descriptions(state=state, type=type, value=value)
st.dataframe(descriptions)

# Remove hamburguer button and footer from app
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
chart = descriptions.plot.bar()
st.plotly_chart(chart, )
