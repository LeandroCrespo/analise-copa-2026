# Adicionar ao final do backtesting.py
if results:
    performance = 'performando bem' if resultado_rate >= 0.5 else 'precisa de mais dados'
    recommendation = 'Recomendado para uso no Bolão' if resultado_rate >= 0.5 else 'Coletar mais dados antes de usar'
    summary = f"""
✅ Backtesting Concluído!

📊 Resumo:
  - Jogos testados: {len(results)}
  - Taxa de acerto de resultado: {resultado_rate:.1%}
  - Pontuação média: {avg_points:.1f} pts/jogo

💡 Interpretação:
  - O modelo está {performance}
  - {recommendation}
  
🚀 Próximos Passos:
  1. Revisar previsões incorretas
  2. Ajustar parâmetros se necessário
  3. Coletar mais dados históricos
  4. Usar sistema adaptativo durante a Copa
"""
    print(summary)
else:
    print("⚠️ Nenhum resultado disponível")
