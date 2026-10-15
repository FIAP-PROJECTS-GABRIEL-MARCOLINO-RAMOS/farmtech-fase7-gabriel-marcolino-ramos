import csv
import os

ARQUIVO_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_farmtech.csv")

# Vetores (listas) para armazenar os dados
culturas = []


def carregar_dados():
    """Carrega dados do CSV para o vetor, se o arquivo existir."""
    if not os.path.exists(ARQUIVO_CSV):
        return
    with open(ARQUIVO_CSV, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            registro = {"tipo": linha["tipo"]}
            if linha["tipo"] == "cafe":
                registro["base_maior"] = float(linha["base_maior"])
                registro["base_menor"] = float(linha["base_menor"])
                registro["altura"] = float(linha["altura"])
                registro["dosagem_ml_por_metro"] = float(linha["dosagem_ml_por_metro"])
                registro["comprimento_rua"] = float(linha["comprimento_rua"])
                registro["num_ruas"] = int(linha["num_ruas"])
            else:
                registro["comprimento"] = float(linha["comprimento"])
                registro["largura"] = float(linha["largura"])
                registro["dosagem_l_por_ha"] = float(linha["dosagem_l_por_ha"])
            registro["area"] = float(linha["area"])
            registro["insumo_total"] = float(linha["insumo_total"])
            culturas.append(registro)


def salvar_dados():
    """Salva o vetor de culturas no CSV."""
    campos = [
        "tipo", "base_maior", "base_menor", "altura",
        "dosagem_ml_por_metro", "comprimento_rua", "num_ruas",
        "comprimento", "largura", "dosagem_l_por_ha",
        "area", "insumo_total"
    ]
    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        for reg in culturas:
            escritor.writerow(reg)


def ler_float(msg):
    while True:
        try:
            return float(input(msg))
        except ValueError:
            print("Valor inválido. Digite um número.")


def ler_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")


def cadastrar_cultura():
    """Entrada de dados — cadastra uma nova cultura no vetor."""
    print("\n--- Cadastrar Cultura ---")
    print("1. Café")
    print("2. Cana-de-açúcar")
    opcao = input("Escolha a cultura: ").strip()

    if opcao == "1":
        registro = {"tipo": "cafe"}
        print("\nÁrea de plantio (trapézio):")
        registro["base_maior"] = ler_float("  Base maior (m): ")
        registro["base_menor"] = ler_float("  Base menor (m): ")
        registro["altura"] = ler_float("  Altura (m): ")
        registro["area"] = (registro["base_maior"] + registro["base_menor"]) * registro["altura"] / 2

        print(f"\n  Área calculada: {registro['area']:.2f} m²")

        print("\nManejo de insumo — Fosfato:")
        registro["dosagem_ml_por_metro"] = ler_float("  Dosagem de fosfato (mL/metro): ")
        registro["comprimento_rua"] = ler_float("  Comprimento de cada rua (m): ")
        registro["num_ruas"] = ler_int("  Número de ruas na lavoura: ")
        registro["insumo_total"] = (
            registro["dosagem_ml_por_metro"] * registro["comprimento_rua"] * registro["num_ruas"] / 1000
        )
        print(f"  Total de fosfato necessário: {registro['insumo_total']:.2f} litros")

    elif opcao == "2":
        registro = {"tipo": "cana"}
        print("\nÁrea de plantio (retângulo):")
        registro["comprimento"] = ler_float("  Comprimento (m): ")
        registro["largura"] = ler_float("  Largura (m): ")
        registro["area"] = registro["comprimento"] * registro["largura"]

        print(f"\n  Área calculada: {registro['area']:.2f} m²")

        area_ha = registro["area"] / 10000
        print(f"  Área em hectares: {area_ha:.4f} ha")

        print("\nManejo de insumo — Herbicida:")
        registro["dosagem_l_por_ha"] = ler_float("  Dosagem de herbicida (L/ha): ")
        registro["insumo_total"] = registro["dosagem_l_por_ha"] * area_ha
        print(f"  Total de herbicida necessário: {registro['insumo_total']:.2f} litros")

    else:
        print("Opção inválida.")
        return

    culturas.append(registro)
    print("\nCultura cadastrada com sucesso!")


def exibir_dados():
    """Saída de dados — exibe todos os registros do vetor."""
    print("\n--- Dados Cadastrados ---")
    if not culturas:
        print("Nenhum registro encontrado.")
        return

    for i, reg in enumerate(culturas):
        print(f"\n[{i}] Tipo: {reg['tipo'].upper()}")
        if reg["tipo"] == "cafe":
            print(f"    Base maior: {reg['base_maior']:.2f} m | Base menor: {reg['base_menor']:.2f} m | Altura: {reg['altura']:.2f} m")
            print(f"    Área (trapézio): {reg['area']:.2f} m²")
            print(f"    Fosfato: {reg['dosagem_ml_por_metro']:.1f} mL/m × {reg['comprimento_rua']:.1f} m × {reg['num_ruas']} ruas = {reg['insumo_total']:.2f} L")
        else:
            print(f"    Comprimento: {reg['comprimento']:.2f} m | Largura: {reg['largura']:.2f} m")
            print(f"    Área (retângulo): {reg['area']:.2f} m²")
            print(f"    Herbicida: {reg['dosagem_l_por_ha']:.1f} L/ha → {reg['insumo_total']:.2f} L total")


def atualizar_dados():
    """Atualização de dados — modifica um registro em posição qualquer do vetor."""
    exibir_dados()
    if not culturas:
        return

    idx = ler_int("\nDigite o índice do registro a atualizar: ")
    if idx < 0 or idx >= len(culturas):
        print("Índice inválido.")
        return

    print(f"Atualizando registro [{idx}] — {culturas[idx]['tipo'].upper()}")
    # Remove o registro antigo e cadastra um novo na mesma posição
    tipo_antigo = culturas[idx]["tipo"]
    culturas.pop(idx)

    print(f"Recadastrando dados para {tipo_antigo}:")
    # Força o mesmo tipo de cultura
    if tipo_antigo == "cafe":
        registro = {"tipo": "cafe"}
        print("\nÁrea de plantio (trapézio):")
        registro["base_maior"] = ler_float("  Base maior (m): ")
        registro["base_menor"] = ler_float("  Base menor (m): ")
        registro["altura"] = ler_float("  Altura (m): ")
        registro["area"] = (registro["base_maior"] + registro["base_menor"]) * registro["altura"] / 2
        print(f"  Área calculada: {registro['area']:.2f} m²")

        print("\nManejo de insumo — Fosfato:")
        registro["dosagem_ml_por_metro"] = ler_float("  Dosagem de fosfato (mL/metro): ")
        registro["comprimento_rua"] = ler_float("  Comprimento de cada rua (m): ")
        registro["num_ruas"] = ler_int("  Número de ruas na lavoura: ")
        registro["insumo_total"] = (
            registro["dosagem_ml_por_metro"] * registro["comprimento_rua"] * registro["num_ruas"] / 1000
        )
        print(f"  Total de fosfato necessário: {registro['insumo_total']:.2f} litros")
    else:
        registro = {"tipo": "cana"}
        print("\nÁrea de plantio (retângulo):")
        registro["comprimento"] = ler_float("  Comprimento (m): ")
        registro["largura"] = ler_float("  Largura (m): ")
        registro["area"] = registro["comprimento"] * registro["largura"]
        print(f"  Área calculada: {registro['area']:.2f} m²")

        area_ha = registro["area"] / 10000
        print("\nManejo de insumo — Herbicida:")
        registro["dosagem_l_por_ha"] = ler_float("  Dosagem de herbicida (L/ha): ")
        registro["insumo_total"] = registro["dosagem_l_por_ha"] * area_ha
        print(f"  Total de herbicida necessário: {registro['insumo_total']:.2f} litros")

    culturas.insert(idx, registro)
    print("Registro atualizado com sucesso!")


def deletar_dados():
    """Deleção de dados — remove um registro do vetor."""
    exibir_dados()
    if not culturas:
        return

    idx = ler_int("\nDigite o índice do registro a deletar: ")
    if idx < 0 or idx >= len(culturas):
        print("Índice inválido.")
        return

    removido = culturas.pop(idx)
    print(f"Registro [{idx}] ({removido['tipo'].upper()}) removido com sucesso!")


def menu():
    """Menu principal com loop e decisão."""
    carregar_dados()
    if culturas:
        print(f"({len(culturas)} registro(s) carregado(s) do arquivo)")

    while True:
        print("\n=============================")
        print("   FarmTech Solutions")
        print("=============================")
        print("1. Entrada de dados")
        print("2. Saída de dados")
        print("3. Atualizar dados")
        print("4. Deletar dados")
        print("5. Sair")
        print("=============================")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_cultura()
        elif opcao == "2":
            exibir_dados()
        elif opcao == "3":
            atualizar_dados()
        elif opcao == "4":
            deletar_dados()
        elif opcao == "5":
            salvar_dados()
            print("Dados salvos. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
