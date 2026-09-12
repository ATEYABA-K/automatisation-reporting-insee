# Automatisation d'un pipeline de reporting (Insee → dashboard)

Automatisation de bout en bout de la collecte, du nettoyage et de la mise à jour d'un jeu de données et de ses graphiques — un exercice type "Chargé de Projet Data" : remplacer une tâche manuelle récurrente (retélécharger un fichier, refaire le nettoyage, régénérer les graphiques) par un pipeline qui tourne seul.

Ce projet réutilise les données et l'analyse du projet [adoption-ia-pme-france](https://github.com/ATEYABA-K/adoption-ia-pme-france), mais l'angle ici est différent : pas le résultat de l'analyse, mais **la fiabilité et l'automatisation de la chaîne qui le produit**.

## Ce que fait le pipeline

`scripts/refresh_pipeline.py` exécute, sans intervention manuelle :

1. **Téléchargement** du fichier source Insee (`IP2120.xlsx`) depuis l'URL officielle
2. **Nettoyage** : extraction de l'onglet pertinent, séparation des blocs, passage au format tidy
3. **Contrôle de cohérence** : le script vérifie que le nombre de lignes obtenu après nettoyage est bien celui attendu (13 catégories × 6 combinaisons zone/année) — s'il y a un écart (l'Insee a changé la structure du fichier, une ligne manque), le pipeline **échoue explicitement** plutôt que de produire silencieusement des données fausses
4. **Génération des graphiques** (mêmes visuels que le projet d'analyse)

## Automatisation (GitHub Actions)

Le fichier [`.github/workflows/refresh.yml`](.github/workflows/refresh.yml) exécute ce pipeline automatiquement :
- **Tous les mois** (le 1er, 6h UTC) — voir "Limite honnête" ci-dessous sur ce que ça surveille réellement
- **À la demande**, via l'onglet "Actions" du repo (bouton "Run workflow")

S'il y a un changement dans les données ou les graphiques générés, le workflow les commit et les pousse automatiquement sur `main`. Sinon, il ne fait rien (pas de commit vide).

## Limite honnête sur la fréquence

L'enquête Insee TIC entreprises est publiée **une fois par an**, pas en continu. Une exécution mensuelle ne "découvre" donc pas de nouvelles données chaque mois dans l'immédiat — elle sert à détecter automatiquement :
- une correction ou mise à jour du fichier existant par l'Insee,
- la publication de la prochaine édition annuelle, sans avoir à surveiller la page manuellement.

Sur un vrai projet en entreprise avec une source de données à cadence quotidienne/hebdomadaire (CRM, ERP, API interne), le même pattern s'applique simplement avec un cron plus fréquent.

## Pourquoi un contrôle de cohérence dans le script (et pas juste un `try/except` générique)

Un pipeline automatisé qui échoue silencieusement ou qui produit des données subtilement fausses (parce que la source a changé de structure) est pire qu'un pipeline qui ne tourne pas du tout — l'erreur peut passer inaperçue pendant des mois. Le contrôle explicite du nombre de lignes (`ValueError` si ≠ 78) fait échouer le job GitHub Actions de façon visible (statut rouge, notification) plutôt que de pousser un CSV corrompu.

## Fichiers

- `scripts/refresh_pipeline.py` — le pipeline complet
- `.github/workflows/refresh.yml` — l'automatisation (planification + déclenchement manuel)
- `requirements.txt` — dépendances Python
- `data/` — sortie du pipeline (régénérée à chaque exécution)
- `chart_ia_par_taille_2025.png`, `chart_evolution_ia_2023_2025.png` — graphiques régénérés

## Pistes pour aller plus loin

- Notifier une équipe (Slack/email) uniquement quand le pipeline échoue, plutôt que de devoir consulter l'onglet Actions
- Ajouter une étape de test automatisé (`pytest`) sur la fonction de nettoyage, indépendante de l'appel réseau
- Historiser chaque version du CSV (au lieu d'écraser) pour pouvoir comparer les éditions Insee dans le temps

## Auteur

Alvin Kouadio
