import time
import streamlit as st
import streamlit.components.v1 as components
import base64
from openai import OpenAI
import wikipedia
import re

from dotenv import load_dotenv
import os

wikipedia.set_lang("es")

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:

    api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(

    api_key=api_key

)

# st.title("Háblame Sobre")
# st.write("Historias y conocimiento para escuchar.")

# =========================================================
# SESSION STATE
# =========================================================

if "texto" not in st.session_state:

    st.session_state.texto = None

if "audio_bytes" not in st.session_state:

    st.session_state.audio_bytes = None

if "speech_file_path" not in st.session_state:

    st.session_state.speech_file_path = None

if "texto_file_path" not in st.session_state:

    st.session_state.texto_file_path = None

if "input_version" not in st.session_state:

    st.session_state.input_version = 0

if "generando" not in st.session_state:

    st.session_state.generando = False

col1, col2, col3 = st.columns([1,2,1])

components.html("""

<script>

const isMobile =

window.innerWidth < 768;

window.parent.postMessage(

{
type:"streamlit:setComponentValue",
value:isMobile
},

"*"

);

</script>

""",height=0)

if "mobile" not in st.session_state:

    st.session_state.mobile=False

mobile = st.session_state.mobile

with col2:

    st.image(

        "imagenes/hablameSobre.jpg",

        width=300 if mobile else 600

    )

tema = st.text_input(

    "¿Qué historia quieres descubrir hoy?",

    key=f"tema_widget_{st.session_state.input_version}"

)

tipo_voz = st.selectbox(

"Elige una voz:",
["Hombre Adulto", "Hombre Joven"]
)

modo_narracion = st.selectbox(

"Estilo de narración:",
["Documental Preciso",
"Relato Inmersivo"]
)

tipo_prompt = st.selectbox(

    "Tipo de experiencia:",

    [

        "Fogata",

        "Científico",

        "Educacional"

    ]

)

if tipo_prompt == "Fogata":

    archivo_prompt = "prompts/fogata.txt"


elif tipo_prompt == "Científico":

    archivo_prompt = "prompts/cientifico.txt"


else:

    archivo_prompt = "prompts/educacional.txt"


with open(

    archivo_prompt,

    encoding="utf-8"

) as archivo:

    prompt_base = archivo.read()

# =========================================================
# MOSTRAR CONTENIDO PERSISTENTE
# =========================================================

if (
    st.session_state.texto
    and
    st.session_state.audio_bytes
):

    st.subheader(
        "🎧 Escuchando"
    )

    audio_base64 = base64.b64encode(
        st.session_state.audio_bytes
    ).decode()

    audio_html = f"""
    <audio controls style="width:100%;">

    <source
    src="data:audio/mp3;base64,{audio_base64}"
    type="audio/mp3">

    </audio>

    <script>

    document.querySelector(
        "audio"
    ).playbackRate=1.12;

    </script>

    """

    components.html(
        audio_html,
        height=80
    )

if st.button(

    "Generar historia",

    use_container_width=True,

    disabled=st.session_state.generando

):

    st.session_state.generando = True

    with st.spinner(
        "🔎 Buscando información y creando historia..."
    ):

        try:

            informacion = wikipedia.summary(

                tema,

                sentences=5

            )

        except:
    
            informacion = f"No encontré información clara sobre {tema}"

        try:
        
            prompt = f"""
            Eres el narrador principal de una aplicación llamada “Háblame Sobre”.
            Tu misión es transformar cualquier tema solicitado en una narración fascinante, cálida, entretenida y fácil de escuchar en formato audio, como si estuvieras contando una gran historia junto a una fogata o en un podcast documental envolvente.
            Pero esta narración debe basarse en información real, históricamente válida y científicamente confiable en una narración fascinante, cálida y entretenida para escuchar en audio.
            La narración debe sentirse humana, cercana y curiosa, nunca académica, fría ni como una enciclopedia.
            El objetivo es despertar asombro, imaginación y ganas de seguir aprendiendo.
            La audiencia incluye adultos curiosos, familias y niños interesados en descubrir el mundo.
            
            REGLAS IMPORTANTES:

                {prompt_base}

                CONTEXTO VERIFICADO:

                    {informacion}

            IMPORTANTE:
            La información anterior debe considerarse factual y verificable.
            No modifiques fechas, nombres, lugares, acontecimientos históricos o datos específicos presentes en el contexto. 
            Nunca reemplaces datos específicos por aproximaciones vagas si el contexto contiene información precisa.
            Si no estás seguro de un dato, debes reconocer explícitamente la incertidumbre en vez de inventar información.
            Basa siempre la narración en hechos reales, información científica aceptada y contexto histórico válido.
            •	No inventes datos falsos.
            •	Si existen teorías, leyendas o versiones no comprobadas, debes aclararlo.
            •	Diferencia claramente entre hechos históricos y tradiciones populares.
            •	Explica temas complejos de forma simple pero inteligente.
            •	Mantén un tono humano, cercano y lleno de curiosidad.
            •	Usa ejemplos visuales y comparaciones fáciles de imaginar.
            •	Genera sensación de descubrimiento y asombro.
            •	Prioriza claridad y profundidad antes que espectacularidad exagerada.
            •	Cuando puedas usa una información precisa, úsala en vez de decir "fundado hace varias décadas", usar el dato exacto de fundación
            •	Usa un tono cálido, natural y conversacional.
            •	Explica temas complejos de forma simple pero inteligente.
            •	Mantén un ritmo dinámico y agradable para escuchar mientras alguien maneja o descansa.
            •	Evita listas excesivas o lenguaje técnico innecesario.
            •	Usa ejemplos visuales y comparaciones fáciles de imaginar.
            •	Genera sensación de descubrimiento y aventura.
            •	Incluye curiosidades sorprendentes cuando sea apropiado.
            •	Nunca suenes como una clase escolar o un artículo de Wikipedia.
            •	Mantén siempre una narrativa fluida y entretenida.
            Evita introducir conceptos modernos, palabras en otro idioma diferente al que se está utilizando, marcas, expresiones contemporáneas o referencias fuera del contexto histórico o cultural del tema.
            Mantén coherencia temporal, cultural y narrativa durante toda la narración.
            No agregues elementos decorativos que no estén respaldados por el contexto verificado.

            ESTRUCTURA:
            1.	Comienza con una frase o idea que genere curiosidad inmediata.
            2.	Introduce el tema como una historia o viaje.
            3.	Explica progresivamente las ideas más importantes.
            4.	Agrega momentos sorprendentes o curiosos.
            5.	Termina con una reflexión, pregunta interesante o sensación de maravilla.
            6.  Cierra con la frase "Esto fue Háblame Sobre, hasta la próxima historia"
            El contenido debe estar optimizado para ser escuchado en voz alta.
        

            Tema:
            {tema}

            Duración:
            2 minutos.
            """

            respuesta = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                    ]
                    )

            texto = respuesta.choices[0].message.content

            st.session_state.texto = texto

            # =========================================================
            # GUARDAR TEXTO GENERADO
            # =========================================================

            tema_limpio = re.sub(

                r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]',

                '_',

                tema

            )

            tema_limpio = tema_limpio[:50]

            if tema_limpio == "":

                tema_limpio = "historia"
                
            texto_file_path = f"{tema_limpio}.txt"

            with open(
            
                texto_file_path,

                "w",
                
                encoding="utf-8"
            
            ) as archivo:

                archivo.write(texto)

            speech_file_path = f"{tema_limpio}.mp3"

            with client.audio.speech.with_streaming_response.create(
            
                model="gpt-4o-mini-tts",
                voice="onyx" if tipo_voz == "Hombre Adulto" else "alloy",
                speed=1.1,
                input=texto
            
            ) as response:

                response.stream_to_file(speech_file_path)

            audio_file = open(
            
                speech_file_path,
                "rb"
            )
                
            audio_bytes = audio_file.read()
        
            audio_file.close()

            if not audio_bytes:

                st.error(
                    "No fue posible generar audio."
                )

                st.stop()

            st.session_state.audio_bytes = audio_bytes

            st.session_state.speech_file_path = speech_file_path

            st.session_state.texto_file_path = texto_file_path
            
            st.subheader(
                f"🎧 Escuchando: {tema}"
            )

            # =========================================================
            # REPRODUCTOR PERSONALIZADO CON VELOCIDAD 1.12
            # =========================================================

            audio_base64 = base64.b64encode(
                st.session_state.audio_bytes
            ).decode()

            audio_html = f"""
            <audio
                id="player"
                controls
                style="width:100%;"
            >

            <source
                src="data:audio/mp3;base64,{audio_base64}"
                type="audio/mp3"
            >

            </audio>

            <script>

                var audio = document.getElementById("player");

                audio.playbackRate = 1.12;

            </script>

            """

            components.html(
                audio_html,
                height=80
            )
        
        except Exception as e:

            st.error(

                f"Error generando contenido: {e}"

            )

        finally:

            st.session_state.generando = False

# =========================================================
# BOTONES CENTRADOS BAJO REPRODUCTOR
# =========================================================

if (
    st.session_state.texto
    and
    st.session_state.audio_bytes
):

    esp1, centro, esp2 = st.columns(
        [1,4,1]
    )

    with centro:

        c1, c2, c3, c4 = st.columns(
            [1,1,1,1]
        )

        with c1:

            st.download_button(

                label="⬇️ Descargar Audio",

                data=st.session_state.audio_bytes,

                file_name=st.session_state.speech_file_path,

                mime="audio/mp3",

                use_container_width=True

            )


        with c2:

            st.download_button(

                label="📄 Descargar Texto",

                data=st.session_state.texto,

                file_name=st.session_state.texto_file_path,

                mime="text/plain",

                use_container_width=True

            )


        with c3:

            if st.button(

                "🔄 Nueva Historia",

                use_container_width=True

            ):

                st.session_state.texto = None

                st.session_state.audio_bytes = None

                st.session_state.speech_file_path = None

                st.session_state.texto_file_path = None

                st.session_state.input_version += 1

                st.rerun()


        with c4:

            st.link_button(

                "📝 Dar Opinión",

                "https://forms.office.com/r/XJdSkdBnbj",

                use_container_width=True

            )