import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def show_proof_result(is_proof_correct: bool):
    if is_proof_correct:
        st.success("A prova está correta!")
    else:
        st.error("A prova está incorreta!")
        st.subheader("Explicação:")
        st.text("\n".join(result.splitlines()[1:]))

st.header("Verificador de Provas por Dedução Natural")
st.html("<p>Este verificador utiliza o serviço online do <a href=\"https://proofs.openlogicproject.org/\">Open Logic Project</a> para validar provas em dedução natural usando o estilo Fitch. O benefício deste verificador é que você pode enviar as provas em formato de texto ou arquivo, evitando a reescrita sempre que precisar verificar a mesma prova mais de uma vez. Além disso, aqui você pode baixar uma captura de tela das prova verificada.</p>")

submit_file = st.toggle("Submeter Arquivo", value=False)

if submit_file:
    uploaded_file = st.file_uploader("Selecione o arquivo contendo a prova", )
else:
    proof_text = st.text_area("Insira a prova no formato de texto abaixo", height=200)

if st.button("Verificar Prova"):
    if True:
        if submit_file and uploaded_file is None:
            st.warning("Por favor, envie um arquivo primeiro.")
            st.stop()
        elif not submit_file and proof_text == "":
            st.warning("Por favor, insira a prova no campo de texto.")
            st.stop()

        if submit_file:
            lines = uploaded_file.getvalue().decode("utf-8").splitlines()
        else:
            lines = proof_text.splitlines()
        
        premises = lines[0].strip().split(";") if lines[0].strip() != "" else []
        conclusion = lines[1].strip()
        proof = [line.strip().split(";") if len(line.strip().split(";")) == 3 else [*line.strip().split(";"), ""] for line in lines[2:] if line.strip() != ""]

        print("Premises:", premises)
        print("Conclusion:", conclusion)
        print("Proof:", proof)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        with open("automation-script.js", "r") as file:
            script = file.read()

        driver.get("https://proofs.openlogicproject.org/")

        driver.execute_script(script, premises, conclusion, proof)

        results_locator = (By.CLASS_NAME, "resultsdiv")

        WebDriverWait(driver, 30).until(
            lambda d: d.find_element(*results_locator).text != "Checking …"
        )

        result = driver.find_element(By.CLASS_NAME, "resultsdiv").text
        proof = driver.find_element(By.ID, "theproof")
        is_proof_correct = result == "☺ Congratulations! This proof is correct."

        if is_proof_correct:
            print("\033[32mProof is correct!\033[0m")
            additional_height = 0
        else:   
            print("\033[31mProof is incorrect!\033[0m")
            print("Explanation:", "\n".join(result.splitlines()[1:]), sep="\n")
            additional_height = 400

        full_page_height = proof.get_property('scrollHeight')
        full_page_width = proof.get_property('scrollWidth')
        driver.set_window_size(full_page_width, full_page_height + additional_height)

        driver.execute_script("arguments[0].scrollIntoView();", proof)

        proof_screenshot = driver.get_screenshot_as_png()

        driver.quit()

        show_proof_result(is_proof_correct)

        if proof_screenshot:
            st.download_button(
                label="Baixar Imagem da Prova",
                data=proof_screenshot,
                file_name="proof_screenshot.png",
                mime="image/png",
                icon=":material/download:",
            )

        if not submit_file and proof_text:
            st.download_button(
                label="Baixar Arquivo da Prova",
                data=proof_text,
                file_name="proof.txt",
                mime="text/plain",
                icon=":material/download:",
            )

st.subheader("Formato do Arquivo de Prova")
st.text("1. A primeira linha deve conter as premissas separadas por ponto e vírgula (;). Se não houver premissas, deixe a linha em branco e vá para a segunda")
st.text("2. A segunda linha deve conter a conclusão")
st.text("3. As linhas subsequentes devem conter cada passo da prova")
st.text("4. Cada passo deve estar no formato: Comando;Fórmula;Justificativa")
st.text("5. Comando: NL (Nova linha), NS (Nova subprova), FL (Finaliza subprova atual e adiciona nova linha), FS (Finaliza subprova atual e inicia nova subprova)")
st.text("6. Fórmula: Nova fórmula introduzida naquela linha, escrita como no site original")
st.text("7. Justificativa: Justificativa para a fórmula introduzida, escrita como no site original")
st.subheader("Exemplo de Arquivo de Prova")
st.code("""A>B;B>C\nA>C\nNS;A\nNL;B;>E1,3\nNL;C;>E2,4\nFL;A>C;>I3-5""", language="plaintext")