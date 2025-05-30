# -*- coding: utf-8 -*-
"""k-means y reglas de asociación

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gKuBPcTToWmITbQWNqY3I8GGv45vpQBh
"""

#librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

#cargar conjunto de datos aisles
df1 = pd.read_csv("aisles.csv")
df1

#cargar conjunto de datos departments
df2 = pd.read_csv("departments.csv")
df2

#cargar conjunto de datos order_products__train
df3 = pd.read_csv("order_products__train.csv")
df3

df3['product_id'].value_counts()

#cargar conjunto de datos orders
df4 = pd.read_csv("orders.csv")
df4

df4.info()

df4['order_dow'].value_counts()

df4['order_hour_of_day'].value_counts()

#cargar conjunto de datos products
df5 = pd.read_csv("products.csv")
df5

#Juntando los conjuntos de datos
merged_df = pd.merge(df4, df3, on='order_id')
merged_df

merged_df = pd.merge(merged_df, df5, on='product_id')
merged_df

#Contando el numero de ordenes por hora
hourly_orders = merged_df.groupby('order_hour_of_day')['order_id'].count().reset_index()
hourly_orders

#Renombrar la columna del total
hourly_orders.columns = ['order_hour_of_day', 'total_orders']
hourly_orders

#Seleccionando las columnas que se usaran
X = hourly_orders[['order_hour_of_day', 'total_orders']]
X

#Metodo el codo
inertia = []
for k in range(1, min(11, len(X) + 1)):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertia.append(kmeans.inertia_)

# Grafico
plt.plot(range(1, min(11, len(X) + 1)), inertia, marker='o')
plt.title('Método del Codo')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inertia')
plt.show()

#Kmeans
selected_k = 4 #Seleccionamos 4 cluster basandonos en el metodo del codo
#Ya que de 4 en adelante no se nota mucha diferencia
kmeans = KMeans(n_clusters=selected_k, random_state=42)
hourly_orders['cluster'] = kmeans.fit_predict(X)

# Visualiza los resultados del algoritmo k-means
plt.scatter(hourly_orders['order_hour_of_day'], hourly_orders['total_orders'], c=hourly_orders['cluster'], cmap='viridis', s=50, alpha=0.8)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=200, marker='X', c='red', label='Centroides')
plt.title('Resultado del algoritmo K-Means')
plt.xlabel('Hora del día')
plt.ylabel('Total de compras en esa hora')
plt.legend()
plt.show()

#Al dataframe se le agregaron los clusters para identificarlos mejor
hourly_orders

#Contando el numero de puntos que tiene cada cluster
hourly_orders['cluster'].value_counts()

hourly_orders.info()

"""Características comunes
- El conjunto tiene arriba de 93 mil compras
- Mas del 50% de las compras del dia se hacen en estan periodo (del conjunto)
- Las compras de este conjunto se realizan entre las 9am y las 5pm
- Los 3 productos que mas se compran en este conjunto son:
  - Banana
  - Bag of Organic Bananas
  - Organic Strawberries

- Los 2 pasillos donde mas se compra en este conjunto son (Teniendo en cunenta que estos 2 superan por el doble al tercer puesto):
  - 83 = Fresh vegetables
  - 24 = Fresh fruits

- Los departamentos donde mas se compra son:
  - 4 = Produce
  - 16 = Dairy eggs
  - 19 = Snacks

Reglas de asociacion con el grupo seleccionado

Cluster #1
"""

#Preparando los datos para las reglas de asociación
merged_df1 = pd.merge(df4, df3, on='order_id')
merged_df1

merged_df1 = pd.merge(merged_df1, df5, on='product_id')
merged_df1

#Como seleccionamos el cluster #1 solo tomaremos los datos de que contiene este grupo
#En este caso las horas (de 9 a 17)
filtered_orders = merged_df[(merged_df['order_hour_of_day'] >= 9) & (merged_df['order_hour_of_day'] <= 17)]
filtered_orders

#Comprobando que solo existan los datos que nececitamos
filtered_orders['order_hour_of_day'].value_counts()

#Seleccionamos las columnas que nececitemos
selected_columns = ['order_id','user_id', 'product_id', 'product_name', 'order_hour_of_day']
result_df = filtered_orders[selected_columns]
result_df

#La columna de la hora no es estrictamente necesaria, asi que hacemos otro dataframe sin ella
selected_columns2 = ['order_id','user_id', 'product_id', 'product_name']
result_df2 = filtered_orders[selected_columns2]
result_df2

#Total de productos comprados dentro del rango de horas
result_df2['product_name'].value_counts()

#Cuantas ordenes hizo cada usuario dentro del rango de horas
result_df2['user_id'].value_counts()

#Reemplazamos el index por el user_id
result_df2.set_index('user_id', inplace = True)
result_df2

#Instalando apyori
pip install apyori

from apyori import apriori

#Haciendo una lista de listas segun los productos que compro cada usuario
transactions1 = result_df2.groupby('user_id')['product_name'].apply(list).tolist()
transactions1

#Aplicando apriori
res = list(apriori(transactions1, min_support = 0.001, min_confidence = 0.1, lift = 1.0))
res

#Creando un dataframe con columnas especificas para darle mas formato a las reglas de asociación
result_df = pd.DataFrame(columns=['Antecedente', 'Consecuente', 'Soporte', 'Confianza', 'Lift'])

#Pasando cada resultado de las reglas al dataframe
for result in res:
    antecedente = tuple(result.items)[0] if result.items else None
    consecuente = tuple(result.items)[1] if len(result.items) > 1 else None
    soporte = result.support
    confianza = result.ordered_statistics[0].confidence
    levantamiento = result.ordered_statistics[0].lift

    result_df = result_df.append({
        'Antecedente': antecedente,
        'Consecuente': consecuente,
        'Soporte': soporte,
        'Confianza': confianza,
        'Lift': levantamiento
    }, ignore_index=True)

#Data frame de las reglas
result_df

# Eliminar filas con "None" en la columna "Consecuente"
result_df = result_df.dropna(subset=['Consecuente'])

#Dataframe final
result_df

"""Basandonos en el "lift" y a partir de las reglas de asociación podemos ver que:

 - Si compramos **"Strawberry Rhubarb Yoghurt"** es **88.47 veces** probable que compremos **"Blueberry Yoghurt"**

 - Si compramos **"Non Fat Acai & Mixed Berries Yogurt"** es **82.79 veces** probable que compremos **"Icelandic Style Skyr Blueberry Non-fat Yogurt"**

 - Si compramos **"Non Fat Raspberry Yogurt"** es **81.35 veces** probable que compremos **"Nonfat Icelandic Style Strawberry Yogurt"**

 - Si compramos **"Icelandic Style Skyr Blueberry Non-fat Yogurt"** es **79.12 veces** probable que compremos **"Nonfat Icelandic Style Strawberry Yogurt"**

 - Si compramos **"Kiwi Sandia Sparkling Water"** es **76 veces** probable que compremos **"Blackberry Cucumber Sparkling Water"**
"""