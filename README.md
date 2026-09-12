# Arrêter de refaire la même tâche à la main

Après avoir fait le nettoyage des données Insee à la main sur [adoption-ia-pme-france](https://github.com/ATEYABA-K/adoption-ia-pme-france), la question logique suivante : et si je dois refaire ça dans 6 mois avec une nouvelle édition du fichier ? Refaire manuellement les mêmes 10 étapes à chaque fois, c'est le genre de tâche qu'on doit pouvoir déléguer à une machine plutôt qu'à sa propre mémoire.

## Comment ça marche

`scripts/refresh_pipeline.py` fait 3 choses, sans intervention :

1. Télécharge le fichier Insee source
2. Le nettoie (même logique que le projet précédent, mais en fonctions réutilisables)
3. Régénère les graphiques

Le fichier [`.github/workflows/refresh.yml`](.github/workflows/refresh.yml) déclenche ce script tout seul, une fois par mois, ou à la demande via le bouton "Run workflow" dans l'onglet Actions du repo. S'il y a un vrai changement dans les données, il commit et pousse automatiquement. Sinon, rien ne se passe — pas de commit vide juste pour dire qu'il a tourné.

## Reproduire

```bash
pip install -r requirements.txt
python3 scripts/refresh_pipeline.py
```

## Le point qui m'a pris le plus de temps à bien faire

Un pipeline qui échoue en silence, ou pire, qui produit des données subtilement fausses sans que personne s'en rende compte, c'est plus dangereux qu'un pipeline qui ne tourne pas du tout — l'erreur peut vivre plusieurs mois avant d'être remarquée. Donc le script vérifie explicitement que le nettoyage sort bien 78 lignes (13 catégories × 6 combinaisons). Si l'Insee change un jour la structure du fichier et que ce nombre ne correspond plus, le script plante volontairement (`ValueError`) plutôt que de pousser un CSV cassé sans le dire.

**Sur la fréquence** : l'enquête Insee ne sort qu'une fois par an, donc un cron mensuel ne "trouve" pas de nouvelle donnée chaque mois — il sert à détecter une correction du fichier existant, ou la sortie de la prochaine édition, sans avoir à surveiller la page à la main. Sur une vraie source à cadence quotidienne (API interne, CRM), le même code s'applique avec un cron plus serré, rien d'autre ne change.

Ce que je ferais en plus si c'était un vrai projet d'équipe : une notification (Slack/email) uniquement en cas d'échec plutôt que d'avoir à consulter l'onglet Actions, et garder un historique des versions du CSV au lieu d'écraser à chaque run — utile pour comparer les éditions dans le temps.

Alvin Kouadio
