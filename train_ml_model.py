"""
Treinar Modelo de Machine Learning (Random Forest)
Train/Test Split: 80/20
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
from collections import Counter

print("=" * 80)
print("TREINAMENTO DO MODELO DE MACHINE LEARNING")
print("=" * 80)

# Carregar dataset
print("\n📂 Carregando dataset...")
df = pd.read_csv('/home/ubuntu/analise-copa-2026/ml_dataset.csv')
print(f"✅ {len(df)} jogos carregados")

# Selecionar features
feature_columns = [
    'home_strength', 'away_strength', 'strength_diff',
    'home_attack', 'away_attack', 'attack_diff',
    'home_defense', 'away_defense', 'defense_diff',
    'home_fifa', 'away_fifa', 'fifa_diff'
]

X = df[feature_columns]
y_score = df['score']  # Target: placar completo
y_result = df['result']  # Target auxiliar: resultado (H/D/A)

print(f"\n📊 Features: {len(feature_columns)}")
print(f"📊 Classes (placares únicos): {y_score.nunique()}")

# Train/Test Split (80/20)
print("\n🔀 Fazendo train/test split (80/20)...")
X_train, X_test, y_train_score, y_test_score, y_train_result, y_test_result = train_test_split(
    X, y_score, y_result, test_size=0.2, random_state=42, stratify=y_result
)

print(f"✅ Train: {len(X_train)} jogos ({len(X_train)/len(df)*100:.1f}%)")
print(f"✅ Test: {len(X_test)} jogos ({len(X_test)/len(df)*100:.1f}%)")

# Treinar modelo para PLACAR
print("\n🤖 Treinando Random Forest para PLACAR...")
rf_score = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

rf_score.fit(X_train, y_train_score)
print("✅ Modelo de PLACAR treinado!")

# Treinar modelo para RESULTADO (auxiliar)
print("\n🤖 Treinando Random Forest para RESULTADO...")
rf_result = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

rf_result.fit(X_train, y_train_result)
print("✅ Modelo de RESULTADO treinado!")

# Avaliar no conjunto de TREINO
print("\n" + "=" * 80)
print("📊 PERFORMANCE NO CONJUNTO DE TREINO")
print("=" * 80)

y_pred_train_score = rf_score.predict(X_train)
train_accuracy_score = accuracy_score(y_train_score, y_pred_train_score)

print(f"\n🎯 Acurácia de PLACAR (treino): {train_accuracy_score*100:.2f}%")

# Distribuição de placares previstos (treino)
train_pred_dist = Counter(y_pred_train_score)
print(f"\n📊 Top 10 placares previstos (treino):")
for score, count in train_pred_dist.most_common(10):
    pct = count / len(y_pred_train_score) * 100
    print(f"   {score}: {count:4d} ({pct:5.2f}%)")

# Avaliar no conjunto de TESTE
print("\n" + "=" * 80)
print("📊 PERFORMANCE NO CONJUNTO DE TESTE")
print("=" * 80)

y_pred_test_score = rf_score.predict(X_test)
y_pred_test_result = rf_result.predict(X_test)

test_accuracy_score = accuracy_score(y_test_score, y_pred_test_score)
test_accuracy_result = accuracy_score(y_test_result, y_pred_test_result)

print(f"\n🎯 Acurácia de PLACAR (teste): {test_accuracy_score*100:.2f}%")
print(f"🎯 Acurácia de RESULTADO (teste): {test_accuracy_result*100:.2f}%")

# Distribuição de placares previstos (teste)
test_pred_dist = Counter(y_pred_test_score)
print(f"\n📊 Top 10 placares previstos (teste):")
for score, count in test_pred_dist.most_common(10):
    pct = count / len(y_pred_test_score) * 100
    print(f"   {score}: {count:4d} ({pct:5.2f}%)")

# Distribuição de placares reais (teste)
test_real_dist = Counter(y_test_score)
print(f"\n📊 Top 10 placares reais (teste):")
for score, count in test_real_dist.most_common(10):
    pct = count / len(y_test_score) * 100
    print(f"   {score}: {count:4d} ({pct:5.2f}%)")

# Calcular pontuação
print("\n📊 Calculando pontuação no conjunto de TESTE...")
total_points = 0
for i in range(len(y_test_score)):
    real = y_test_score.iloc[i]
    pred = y_pred_test_score[i]
    
    real_h, real_a = map(int, real.split('x'))
    pred_h, pred_a = map(int, pred.split('x'))
    
    if pred == real:
        total_points += 10  # Placar exato
    elif (pred_h - pred_a) == (real_h - real_a):
        total_points += 5  # Saldo correto
    elif (pred_h > pred_a and real_h > real_a) or \
         (pred_h < pred_a and real_h < real_a) or \
         (pred_h == pred_a and real_h == real_a):
        total_points += 3  # Resultado correto

avg_points = total_points / len(y_test_score)
print(f"✅ Pontuação média (teste): {avg_points:.2f} pts/jogo")

# Feature importance
print("\n📊 Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_score.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['feature']:20s}: {row['importance']:.4f}")

# Comparação com modelos anteriores
print("\n" + "=" * 80)
print("📊 COMPARAÇÃO COM MODELOS ANTERIORES")
print("=" * 80)

print(f"\nModelo Poisson (V1):")
print(f"   Placar Exato: 11.36% | Pontos/jogo: 2.53 | 1x1: 51.81%")

print(f"\nModelo Machine Learning (Random Forest):")
print(f"   Placar Exato: {test_accuracy_score*100:.2f}% | Pontos/jogo: {avg_points:.2f} | {test_pred_dist.most_common(1)[0][0]}: {test_pred_dist.most_common(1)[0][1]/len(y_pred_test_score)*100:.2f}%")

if test_accuracy_score > 0.1136:
    print(f"\n✅ MELHORIA: +{(test_accuracy_score - 0.1136)*100:.2f}% em placar exato")
else:
    print(f"\n❌ PIORA: {(test_accuracy_score - 0.1136)*100:.2f}% em placar exato")

# Salvar modelos
print("\n💾 Salvando modelos...")
with open('/home/ubuntu/analise-copa-2026/rf_score_model.pkl', 'wb') as f:
    pickle.dump(rf_score, f)

with open('/home/ubuntu/analise-copa-2026/rf_result_model.pkl', 'wb') as f:
    pickle.dump(rf_result, f)

print("✅ Modelos salvos!")

# Salvar resultados
results = {
    'train_accuracy': float(train_accuracy_score),
    'test_accuracy_score': float(test_accuracy_score),
    'test_accuracy_result': float(test_accuracy_result),
    'avg_points': float(avg_points),
    'feature_importance': feature_importance.to_dict('records'),
    'test_pred_distribution': dict(test_pred_dist.most_common(20)),
    'test_real_distribution': dict(test_real_dist.most_common(20))
}

import json
with open('/home/ubuntu/analise-copa-2026/ml_training_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
print("=" * 80)
