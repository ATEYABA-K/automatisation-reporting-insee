# Arrêter de refaire la même tâche à la main

## En bref
Après avoir nettoyé les données Insee à la main sur [adoption-ia-pme-france](https://github.com/ATEYABA-K/adoption-ia-pme-france), je me suis demandé : et si je dois refaire ça dans 6 mois avec une nouvelle édition du fichier ? J'ai automatisé les mêmes étapes plutôt que de les refaire manuellement.

## Comment ça marche
`scripts/refresh_pipeline.py` fait 3 choses, sans intervention :
1. Télécharge le fichier Insee source
2. Le nettoie (même logique que le projet précédent)
3. Régénère les graphiques

Un robot (GitHub Actions) déclenche ce script une fois par mois, ou à la demande. S'il y a un vrai changement dans les données, il enregistre automatiquement le résultat. Sinon, rien ne se passe.

## Reproduire
```bash
pip install -r requirements.txt
python3 scripts/refresh_pipeline.py
```

## Le point sur lequel j'ai fait attention
Un script qui échoue en silence, ou qui produit un résultat faux sans prévenir, est plus dangereux qu'un script qui ne marche pas du tout — personne ne s'en rendrait compte. J'ai donc fait en sorte que le script vérifie le nombre de lignes attendu (78) avant d'enregistrer le résultat. Si ce nombre ne correspond pas, le script s'arrête tout seul plutôt que de laisser passer un fichier faux.

## Ce que je ferais en plus
Une notification (email) en cas d'échec, pour ne pas avoir à vérifier moi-même que tout s'est bien passé.

Alvin Kouadio
