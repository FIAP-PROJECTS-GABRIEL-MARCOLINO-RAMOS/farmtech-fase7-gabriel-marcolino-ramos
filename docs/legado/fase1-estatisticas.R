# FarmTech Solutions - Estatísticas Básicas
# Lê os dados gerados pelo Python e calcula média e desvio padrão

arquivo <- file.path(dirname(sys.frame(1)$ofile), "dados_farmtech.csv")

if (!file.exists(arquivo)) {
  cat("Arquivo dados_farmtech.csv não encontrado.\n")
  cat("Execute o programa Python primeiro para gerar os dados.\n")
  quit(status = 1)
}

dados <- read.csv(arquivo, stringsAsFactors = FALSE)

if (nrow(dados) == 0) {
  cat("Nenhum registro encontrado no arquivo.\n")
  quit(status = 1)
}

cat("==========================================\n")
cat("   FarmTech Solutions - Estatísticas\n")
cat("==========================================\n\n")

tipos <- unique(dados$tipo)

for (tipo in tipos) {
  subset_dados <- dados[dados$tipo == tipo, ]
  n <- nrow(subset_dados)

  nome <- ifelse(tipo == "cafe", "CAFÉ", "CANA-DE-AÇÚCAR")
  cat(paste0("--- ", nome, " (", n, " registro(s)) ---\n"))

  cat(paste0("  Área (m²):\n"))
  cat(paste0("    Média:        ", round(mean(subset_dados$area), 2), "\n"))
  cat(paste0("    Desvio padrão: ", round(sd(subset_dados$area), 2), "\n"))

  cat(paste0("  Insumo total (L):\n"))
  cat(paste0("    Média:        ", round(mean(subset_dados$insumo_total), 2), "\n"))
  cat(paste0("    Desvio padrão: ", round(sd(subset_dados$insumo_total), 2), "\n"))

  cat("\n")
}

cat("==========================================\n")
