"""
Treinar Modelo V2 com Features Categóricas
Train/Test Split: 80/20
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import pickle
from collections import Counter

print("=" * 80)
print("TREINAMENTO DO MODELO V2 (COM FEATURES CATEGÓRICAS)")
print("=" * 80)

# Carregar dataset V2
print("\n📂 Carregando dataset V2...")
df = pd.read_csv('/home/ubuntu/analise-copa-2026/ml_dataset_v2.csv')
print(f"✅ {len(df)} jogos carregados")

# Encode features categóricas
print("\n🔧 Encoding features categóricas...")
le_home_cat = LabelEncoder()
le_away_cat = LabelEncoder()
le_matchup = LabelEncoder()

df['home_category_encoded'] = le_home_cat.fit_transform(df['home_category'])
df['away_category_encoded'] = le_away_cat.fit_transform(df['away_category'])
df['matchup_type_encoded'] = le_matchup.fit_transform(df['matchup_type'])

print(f"✅ Categorias encoded!")

# Selecionar features
feature_columns = [
    # Numéricas
    'home_strength', 'away_strength', 'strength_diff',
    'home_attack', 'away_attack', 'attack_diff',
    'home_defense', 'away_defense', 'defense_diff',
    'home_fifa', 'away_fifa', 'fifa_diff',
    # Categóricas (encoded) ✨ NOVO
    'home_category_encoded', 'away_category_encoded', 'matchup_type_encoded'
]

X = df[feature_columns]
y_score = df['score']
y_result = df['result']

print(f"\n📊 Features: {len(feature_columns)} (12 numéricas + 3 categóricas)")
print(f"📊 Classes (placares únicos): {y_score.nunique()}")

# Train/Test Split (80/20)
print("\n🔀 Fazendo train/test split (80/20)...")
X_train, X_test, y_train_score, y_test_score, y_train_result, y_test_result = train_test_split(
    X, y_score, y_result, test_size=0.2, random_state=42, stratify=y_result
)

print(f"✅ Train: {len(X_train)} jogos ({len(X_train)/len(df)*100:.1f}%)")
print(f"✅ Test: {len(X_test)} jogos ({len(X_test)/len(df)*100:.1f}%)")

# Treinar modelo V2
print("\n🤖 Treinando Random Forest V2...")
rf_v2 = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

rf_v2.fit(X_train, y_train_score)
print("✅ Modelo V2 treinado!")

# Avaliar no conjunto de TESTE
print("\n" + "=" * 80)
print("📊 PERFORMANCE NO CONJUNTO DE TESTE")
print("=" * 80)

y_pred_test = rf_v2.predict(X_test)
test_accuracy = accuracy_score(y_test_score, y_pred_test)

print(f"\n🎯 Acurácia de PLACAR (teste): {test_accuracy*100:.2f}%")

# Distribuição de placares previstos
test_pred_dist = Counter(y_pred_test)
print(f"\n📊 Top 15 placares previstos (teste):")
for score, count in test_pred_dist.most_common(15):
    pct = count / len(y_pred_test) * 100
    print(f"   {score}: {count:4d} ({pct:5.2f}%)")

# Distribuição de placares reais
test_real_dist = Counter(y_test_score)
print(f"\n📊 Top 15 placares reais (teste):")
for score, count in test_real_dist.most_common(15):
    pct = count / len(y_test_score) * 100
    print(f"   {score}: {count:4d} ({pct:5.2f}%)")

# Calcular pontuação
print("\n📊 Calculando pontuação...")
total_points = 0
for i in range(len(y_test_score)):
    real = y_test_score.iloc[i]
    pred = y_pred_test[i]
    
    real_h, real_a = map(int, real.split('x'))
    pred_h, pred_a = map(int, pred.split('x'))
    
    if pred == real:
        total_points += 10
    elif (pred_h - pred_a) == (real_h - real_a):
        total_points += 5
    elif (pred_h > pred_a and real_h > real_a) or \
         (pred_h < pred_a and real_h < real_a) or \
         (pred_h == pred_a and real_h == real_a):
        total_points += 3

avg_points = total_points / len(y_test_score)
print(f"✅ Pontuação média (teste): {avg_points:.2f} pts/jogo")

# Resultado (V/E/D)
y_pred_result = []
for pred in y_pred_test:
    pred_h, pred_a = map(int, pred.split('x'))
    if pred_h > pred_a:
        y_pred_result.append('H')
    elif pred_h < pred_a:
        y_pred_result.append('A')
    else:
        y_pred_result.append('D')

result_accuracy = accuracy_score(y_test_result, y_pred_result)
print(f"🎯 Acurácia de RESULTADO (teste): {result_accuracy*100:.2f}%")

# Feature importance
print("\n📊 Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_v2.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['feature']:30s}: {row['importance']:.4f}")

# Comparação
print("\n" + "=" * 80)
print("📊 COMPARAÇÃO DE MODELOS")
print("=" * 80)

print(f"\nModelo Poisson (V1):")
print(f"   Placar: 11.36% | Resultado: 39.13% | Pontos: 2.53 | 1x1: 51.81%")

print(f"\nModelo ML V1 (sem categorias):")
print(f"   Placar: 13.65% | Resultado: 52.81% | Pontos: 2.72 | 1x0: 52.69%")

print(f"\nModelo ML V2 (COM categorias):")
most_common = test_pred_dist.most_common(1)[0]
print(f"   Placar: {test_accuracy*100:.2f}% | Resultado: {result_accuracy*100:.2f}% | Pontos: {avg_points:.2f} | {most_common[0]}: {most_common[1]/len(y_pred_test)*100:.2f}%")

# Melhoria
if test_accuracy > 0.1365:
    print(f"\n✅ MELHORIA vs ML V1: +{(test_accuracy - 0.1365)*100:.2f}% em placar exato")
else:
    print(f"\n❌ PIORA vs ML V1: {(test_accuracy - 0.1365)*100:.2f}% em placar exato")

# Número de placares diferentes
num_different = len(test_pred_dist)
print(f"\n📊 Placares diferentes previstos: {num_different}")

# Salvar modelo
print("\n💾 Salvando modelo V2...")
with open('/home/ubuntu/analise-copa-2026/rf_v2_model.pkl', 'wb') as f:
    pickle.dump(rf_v2, f)

# Salvar encoders
with open('/home/ubuntu/analise-copa-2026/label_encoders.pkl', 'wb') as f:
    pickle.dump({
        'home_category': le_home_cat,
        'away_category': le_away_cat,
        'matchup_type': le_matchup
    }, f)

print("✅ Modelo V2 e encoders salvos!")

# Salvar resultados
results = {
    'test_accuracy_score': float(test_accuracy),
    'test_accuracy_result': float(result_accuracy),
    'avg_points': float(avg_points),
    'num_different_scores': num_different,
    'feature_importance': feature_importance.to_dict('records'),
    'test_pred_distribution': dict(test_pred_dist.most_common(20)),
    'test_real_distribution': dict(test_real_dist.most_common(20))
}

import json
with open('/home/ubuntu/analise-copa-2026/ml_v2_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("✅ TREINAMENTO V2 CONCLUÍDO!")
print("=" * 80)
