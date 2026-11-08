import streamlit as st

from agente import perguntar
from dados import carregar_dados

st.set_page_config(page_title="Agente BMS", page_icon="🔋")
st.title("🔋 Agente BMS")
st.caption(
    "Pergunte em português sobre um ensaio de descarga de um conjunto 3S1P "
    "de baterias de íon-lítio. O agente busca os números nos dados e explica."
)


@st.cache_data
def tensoes_por_minuto():
    df = carregar_dados()
    df["tempo_min"] = df["tempo_s"] / 60
    return df.set_index("tempo_min")[["v_celula1", "v_celula2", "v_celula3"]]


def mostrar_ferramentas(ferramentas):
    if not ferramentas:
        return
    with st.expander(f"Ferramentas usadas ({len(ferramentas)})"):
        for f in ferramentas:
            st.markdown(f"**{f['nome']}** {f['argumentos'] or ''}")
            st.json(f["resultado"], expanded=False)


with st.expander("Tensão das células durante o ensaio", expanded=True):
    st.line_chart(tensoes_por_minuto(), x_label="Tempo (min)", y_label="Tensão (V)")

# A conversa fica guardada na sessão para não sumir quando a página atualiza
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        mostrar_ferramentas(msg.get("ferramentas"))

pergunta = st.chat_input("Ex.: qual célula está mais gasta?")

if pergunta:
    with st.chat_message("user"):
        st.markdown(pergunta)

    historico = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.mensagens
    ]

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analisando os dados..."):
                resultado = perguntar(pergunta, historico)
        except Exception as erro:
            st.error(f"Não consegui falar com o modelo agora. Detalhe: {erro}")
            st.stop()
        st.markdown(resultado["resposta"])
        mostrar_ferramentas(resultado["ferramentas"])

    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    st.session_state.mensagens.append({
        "role": "assistant",
        "content": resultado["resposta"],
        "ferramentas": resultado["ferramentas"],
    })