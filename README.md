# RAPPORT DE CONCEPTION
# GÉNÉRATEUR D'EMPLOI DU TEMPS UNIVERSITAIRE

<div style="text-align: center; margin-top: 50px; margin-bottom: 100px;">
<img src="https://upload.wikimedia.org/wikipedia/commons/f/f8/Logo_Universit%C3%A9_de_Yaound%C3%A9_I.jpg" alt="Logo Université" style="width: 200px;"/>

# DÉPARTEMENT D'INFORMATIQUE
## CONCEPTION ET IMPLÉMENTATION D'UN GÉNÉRATEUR D'EMPLOI DU TEMPS UNIVERSITAIRE
### Présenté par : SPRING_SHOGUN🍃🍃
### Matricule : 21T2580
### Niveau : Master 1
### Date : Mai 2025
</div>

<div style="page-break-after: always;"></div>

## TABLE DES MATIÈRES

1. [INTRODUCTION](#introduction)
2. [ÉNONCÉ DU PROBLÈME](#énoncé-du-problème)
3. [ANALYSE DES BESOINS](#analyse-des-besoins)
4. [CONCEPTION DE LA SOLUTION](#conception-de-la-solution)
   1. [Architecture générale](#architecture-générale)
   2. [Modèle de contraintes](#modèle-de-contraintes)
   3. [Technologies utilisées](#technologies-utilisées)
5. [IMPLÉMENTATION](#implémentation)
   1. [Prérequis d'installation](#prérequis-dinstallation)
   2. [Structure du code](#structure-du-code)
   3. [Format des fichiers d'entrée](#format-des-fichiers-dentrée)
6. [UTILISATION DU PROGRAMME](#utilisation-du-programme)
   1. [Comment lancer le programme](#comment-lancer-le-programme)
   2. [Configuration](#configuration)
   3. [Visualisation des résultats](#visualisation-des-résultats)
7. [RÉSULTATS OBTENUS](#résultats-obtenus)
8. [DIFFICULTÉS RENCONTRÉES ET SOLUTIONS](#difficultés-rencontrées-et-solutions)
9. [PERSPECTIVES D'AMÉLIORATION](#perspectives-damélioration)
10. [CONCLUSION](#conclusion)
11. [RÉFÉRENCES](#références)

<div style="page-break-after: always;"></div>

## INTRODUCTION

La planification des emplois du temps universitaires est un défi logistique complexe qui nécessite la prise en compte de nombreuses contraintes : disponibilité des salles, des enseignants, répartition équilibrée des cours, etc. La création manuelle de ces emplois du temps est non seulement chronophage mais aussi susceptible d'erreurs.

Ce rapport présente la conception et l'implémentation d'un générateur automatique d'emploi du temps destiné au Département d'Informatique. Cet outil utilise des techniques avancées d'optimisation par contraintes pour générer des emplois du temps qui respectent l'ensemble des contraintes spécifiées tout en optimisant l'utilisation des ressources disponibles.

Le générateur développé vise à résoudre ce problème en automatisant entièrement le processus de création d'emplois du temps, permettant ainsi aux administrateurs de gagner un temps considérable tout en garantissant la qualité et la cohérence des planifications.

## ÉNONCÉ DU PROBLÈME

Le Département d'Informatique de l'Université fait face à un problème récurrent de planification des emplois du temps. Avec un nombre croissant d'étudiants, de cours et de contraintes diverses, la création manuelle des emplois du temps devient de plus en plus complexe et chronophage.

Le problème qui nous a été soumis peut être résumé comme suit :

"*Concevoir et implémenter un générateur automatique d'emploi du temps qui puisse planifier tous les cours du département d'informatique sur une semaine type, en respectant diverses contraintes liées aux salles, aux enseignants et aux préférences horaires.*"

Les principales difficultés à surmonter sont :
- La gestion des conflits d'occupation des salles
- La gestion des disponibilités des enseignants 
- L'optimisation de l'utilisation des ressources
- La satisfaction de diverses contraintes pédagogiques et logistiques
- La génération d'emplois du temps lisibles et faciles à consulter

## ANALYSE DES BESOINS

L'analyse du problème a permis d'identifier les besoins fonctionnels et non fonctionnels suivants :

### Besoins fonctionnels :

1. **Planification complète** : Le système doit être capable de programmer tous les cours du département pour une semaine type.
2. **Respect des contraintes** : Le système doit respecter l'ensemble des contraintes spécifiées.
3. **Optimisation** : Le système doit optimiser l'utilisation des ressources, notamment en privilégiant les périodes du matin.
4. **Visualisation** : Le système doit générer des emplois du temps dans un format facile à consulter.
5. **Exportation** : Le système doit permettre l'exportation des emplois du temps dans différents formats.

### Besoins non fonctionnels :

1. **Performance** : Le système doit générer une solution dans un temps raisonnable (quelques minutes maximum).
2. **Facilité d'utilisation** : Le système doit être facile à configurer et à utiliser.
3. **Maintenabilité** : Le code doit être bien structuré et documenté pour faciliter les modifications futures.
4. **Portabilité** : Le système doit fonctionner sur différentes plateformes.

<div style="page-break-after: always;"></div>

## CONCEPTION DE LA SOLUTION

### Architecture générale

L'architecture du générateur d'emploi du temps est organisée en plusieurs composants interconnectés :

1. **Module de chargement des données** : Responsable de la lecture des fichiers de configuration JSON et de la transformation des données en structures internes.

2. **Module de construction du modèle** : Crée le modèle mathématique de contraintes qui représente le problème d'emploi du temps.

3. **Module de résolution** : Utilise un solveur de satisfaction de contraintes pour trouver une solution optimale au modèle.

4. **Module de génération de sortie** : Transforme la solution trouvée en emplois du temps lisibles au format HTML et Markdown.

Le diagramme ci-dessous illustre cette architecture :

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Chargement    │     │  Construction   │     │    Résolution   │     │   Génération    │
│   des données   │──►  │   du modèle     │──►  │    du modèle    │──►  │   des sorties   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                                                                        │
        │                                                                        │
        └───────────────────────────────────────────────────────────────────────┘
                                    Retour d'information
```

### Modèle de contraintes

Le cœur du système repose sur un modèle mathématique de satisfaction de contraintes. Pour chaque combinaison possible (classe, cours, salle, jour, période), une variable binaire est créée. Cette variable vaut 1 si le cours est programmé à ce moment et dans cette salle, et 0 sinon.

Les principales contraintes implémentées sont :

1. **Contrainte d'unicité des salles** : Une salle ne peut accueillir qu'un seul cours à la fois.
2. **Contrainte de programmation unique** : Chaque cours doit être programmé exactement une fois par semaine.
3. **Contrainte de respect du programme** : Une classe ne peut suivre que les cours qui sont dans son programme.
4. **Contrainte de disponibilité des enseignants** : Un enseignant ne peut donner qu'un seul cours à la fois.
5. **Contrainte de préférence horaire** : Les périodes du matin sont privilégiées par rapport aux périodes de l'après-midi et du soir.

La fonction objectif vise à minimiser la somme pondérée des périodes utilisées, avec un poids plus faible pour les périodes du matin afin de les favoriser.

### Technologies utilisées

Le générateur d'emploi du temps a été développé en utilisant les technologies suivantes :

- **Python** : Langage de programmation principal
- **Google OR-Tools** : Bibliothèque d'optimisation et de résolution de contraintes
- **pandas** : Bibliothèque de manipulation de données
- **numpy** : Bibliothèque de calcul scientifique
- **JSON** : Format de fichier pour les données d'entrée
- **HTML/CSS/JavaScript** : Technologies web pour la visualisation des résultats

<div style="page-break-after: always;"></div>

## IMPLÉMENTATION

### Prérequis d'installation

Pour utiliser le générateur d'emploi du temps, les prérequis suivants sont nécessaires :

1. **Python 3.6 ou supérieur** :
   ```bash
   # Vérifier la version de Python
   python --version
   ```

2. **Google OR-Tools** :
   ```bash
   pip install ortools>=9.4.1874
   ```

3. **pandas** :
   ```bash
   pip install pandas>=1.3.0
   ```

4. **numpy** :
   ```bash
   pip install numpy>=1.20.0
   ```

#### Script d'installation automatique

Le script suivant peut être utilisé pour installer automatiquement toutes les dépendances requises :

```bash
#!/bin/bash
# Script d'installation pour le Générateur d'Emploi du Temps

# Vérifier si Python est installé
python_version=$(python --version 2>&1)
if [[ $python_version != *"Python 3"* ]]; then
  echo "Python 3 n'est pas installé ou n'est pas la version par défaut."
  echo "Veuillez installer Python 3 depuis https://www.python.org/downloads/"
  exit 1
fi

# Installer les dépendances
echo "Installation des dépendances..."
pip install ortools pandas numpy

# Vérifier l'installation
echo "Vérification de l'installation..."
python -c "import ortools, pandas, numpy; print('Installation réussie')"

if [ $? -eq 0 ]; then
  echo "Toutes les dépendances sont correctement installées."
  echo "Vous pouvez maintenant exécuter le générateur d'emploi du temps."
else
  echo "Erreur lors de l'installation des dépendances."
  exit 1
fi
```

### Structure du code

Le code du générateur est organisé autour d'une classe principale `TimeTableGenerator` qui encapsule toute la logique de l'application. Voici les principales méthodes de cette classe :

- `__init__(rooms_file, courses_file)` : Initialise le générateur avec les fichiers de configuration
- `load_data(rooms_file, courses_file)` : Charge les données des fichiers JSON
- `build_model()` : Construit le modèle de contraintes
- `solve_model()` : Résout le modèle pour trouver une solution optimale
- `process_solution(solver)` : Traite la solution trouvée
- `generate_combined_html_timetable()` : Génère l'emploi du temps au format HTML
- `generate_markdown_timetable(class_id)` : Génère l'emploi du temps d'une classe au format Markdown

### Format des fichiers d'entrée

Le générateur utilise deux fichiers JSON comme entrée :

1. **data_salles.json** : Contient les informations sur les salles disponibles
   ```json
   {
     "Informatique": [
       {
         "num": "101",
         "capacite": "50",
         "batiment": "Bloc A",
         "filier": "Informatique"
       },
       ...
     ]
   }
   ```

2. **data_cours.json** : Contient les informations sur les cours et les enseignants
   ```json
   {
     "niveau": {
       "1": {
         "semestre1": {
           "subjects": [
             {
               "name": "Algorithmique 1",
               "code": "INFO101",
               "Course Lecturer": ["Dr. Dupont"],
               "credit": 4
             },
             ...
           ]
         }
       }
     }
   }
   ```

<div style="page-break-after: always;"></div>

## UTILISATION DU PROGRAMME

### Comment lancer le programme

Pour exécuter le générateur d'emploi du temps, suivez ces étapes :

1. Assurez-vous que tous les prérequis sont installés
2. Placez les fichiers de configuration `data_salles.json` et `data_cours.json` dans le même répertoire que le script
3. Exécutez la commande suivante :
   ```bash
   python timetable-generator-V3.py
   ```
4. Attendez que le programme termine l'exécution (cela peut prendre quelques minutes en fonction de la complexité du problème)
5. Ouvrez le fichier `all_timetables.html` généré dans votre navigateur web

### Configuration

Le comportement du générateur peut être personnalisé en modifiant certains paramètres dans le code :

1. **Périodes** - Vous pouvez modifier les horaires et poids des périodes :
   ```python
   self.periods = ['7:00am - 9:55am', '10:05am - 12:55pm', '1:05pm - 3:55pm', 
                  '4:05pm - 6:55pm', '7:05pm - 9:55pm']
   self.period_weights = [1, 2, 3, 4, 5]  # Lower weights have higher priority
   ```

2. **Limite de temps** - Vous pouvez augmenter le temps alloué au solveur :
   ```python
   solver.parameters.max_time_in_seconds = 300  # Augmenter au besoin
   ```

3. **Style HTML** - Vous pouvez personnaliser l'apparence de l'emploi du temps en modifiant les styles CSS dans la méthode `generate_combined_html_timetable()`.

### Visualisation des résultats

Le générateur produit les fichiers de sortie suivants :

1. **all_timetables.html** : Un fichier HTML interactif contenant tous les emplois du temps avec navigation entre les différents niveaux/semestres

2. **timetable_Level_X_SemestreY.md** : Des fichiers Markdown individuels pour chaque niveau/semestre

L'interface HTML offre plusieurs fonctionnalités :
- Navigation entre les différents niveaux et semestres
- Affichage détaillé des cours avec codes, enseignants et salles
- Légende explicative pour chaque cours
- Possibilité d'impression des emplois du temps

<div style="page-break-after: always;"></div>

## RÉSULTATS OBTENUS

Le générateur d'emploi du temps produit plusieurs types de résultats :

### 1. Emploi du temps HTML interactif

L'interface HTML générée permet de naviguer facilement entre les différents niveaux et semestres. Voici un aperçu de cette interface :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Emplois du Temps                                 │
│                        Département d'Informatique                           │
│                        Année académique 2024-2025                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Niveau 1 - Semestre 1]  [Niveau 1 - Semestre 2]  [Niveau 2 - Semestre 3] │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                   ┌────────┬────────┬────────┬────────┬────────┬────────┐  │
│                   │ Lundi  │ Mardi  │ Mercr. │ Jeudi  │ Vendr. │ Samedi │  │
│  ┌───────────────┼────────┼────────┼────────┼────────┼────────┼────────┤  │
│  │ 7:00-9:55     │ INFO101│        │ INFO103│        │ INFO102│        │  │
│  ├───────────────┼────────┼────────┼────────┼────────┼────────┼────────┤  │
│  │ 10:05-12:55   │        │ INFO102│        │ INFO101│        │ INFO104│  │
│  ├───────────────┼────────┼────────┼────────┼────────┼────────┼────────┤  │
│  │ 13:05-15:55   │ INFO104│        │        │ INFO105│        │        │  │
│  ├───────────────┼────────┼────────┼────────┼────────┼────────┼────────┤  │
│  │ 16:05-18:55   │        │ INFO105│        │        │        │        │  │
│  ├───────────────┼────────┼────────┼────────┼────────┼────────┼────────┤  │
│  │ 19:05-21:55   │        │        │        │        │        │        │  │
│  └───────────────┴────────┴────────┴────────┴────────┴────────┴────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Statistiques d'utilisation

Le générateur calcule également diverses statistiques sur l'emploi du temps généré :
- Nombre total de cours programmés
- Pourcentage de cours programmés en matinée
- Taux d'occupation des salles
- Nombre de salles utilisées

Ces statistiques permettent d'évaluer la qualité de la solution trouvée et d'identifier d'éventuelles améliorations possibles.

### 3. Respect des contraintes

Toutes les contraintes spécifiées ont été respectées dans la solution générée :
- Aucune salle n'est utilisée pour deux cours différents au même moment
- Tous les cours sont programmés exactement une fois par semaine
- Aucun enseignant n'est programmé pour donner deux cours en même temps
- Les périodes du matin sont privilégiées lorsque c'est possible

### 4. Performance

Le temps de génération varie en fonction de la complexité du problème (nombre de cours, salles, etc.). Pour le jeu de données de test, comportant environ 30 cours répartis sur 3 niveaux, la génération a pris environ 2 minutes sur un ordinateur standard.

<div style="page-break-after: always;"></div>

## DIFFICULTÉS RENCONTRÉES ET SOLUTIONS

### 1. Complexité du problème d'optimisation

**Difficulté** : La principale difficulté a été la résolution efficace du problème d'optimisation sous contraintes, qui est NP-difficile.

**Solution** : Utilisation de la bibliothèque Google OR-Tools, qui implémente des algorithmes performants pour ce type de problème. De plus, une limite de temps de 5 minutes a été fixée pour éviter des temps de résolution trop longs.

### 2. Structure des données d'entrée

**Difficulté** : La structure des fichiers JSON d'entrée devait être à la fois flexible et facile à générer manuellement.

**Solution** : Conception d'une structure de fichiers JSON intuitive, avec validation des données lors du chargement pour détecter rapidement les erreurs de format.

### 3. Interface utilisateur

**Difficulté** : Création d'une interface utilisateur intuitive pour la consultation des emplois du temps générés.

**Solution** : Développement d'une interface HTML interactive avec navigation par onglets et filtres, permettant une visualisation claire et organisée des emplois du temps.

### 4. Gestion des contraintes conflictuelles

**Difficulté** : Dans certains cas, l'ensemble des contraintes pouvait être trop restrictif, ne permettant pas de trouver une solution.

**Solution** : Implémentation d'un système de contraintes avec priorités, où certaines contraintes (comme la programmation de tous les cours) sont considérées comme des contraintes dures, tandis que d'autres (comme la préférence pour les périodes du matin) sont des contraintes souples avec une fonction objectif à optimiser.

## PERSPECTIVES D'AMÉLIORATION

Plusieurs améliorations pourraient être apportées au générateur d'emploi du temps :

1. **Interface graphique** : Développer une interface graphique complète pour la configuration et la visualisation des emplois du temps.

2. **Contraintes supplémentaires** : Ajouter la prise en compte de contraintes supplémentaires, comme les préférences individuelles des enseignants, les contraintes de salle spécifiques, etc.

3. **Optimisation multi-objectif** : Implémenter une optimisation prenant en compte plusieurs objectifs, comme l'équilibre de la charge de travail des enseignants, la minimisation des déplacements, etc.

4. **Intégration de données externes** : Permettre l'importation de données depuis des systèmes de gestion académique existants.

5. **Édition manuelle** : Ajouter des fonctionnalités d'édition manuelle des emplois du temps générés.

6. **Export avancé** : Développer des options d'exportation vers d'autres formats (PDF, Excel, iCalendar, etc.).

7. **Gestion des exceptions** : Ajouter la possibilité de gérer des exceptions ponctuelles à l'emploi du temps type.

<div style="page-break-after: always;"></div>

## CONCLUSION

Ce projet a permis de développer un générateur d'emploi du temps efficace et flexible pour le département d'informatique. En utilisant des techniques avancées d'optimisation par contraintes, le système est capable de produire des emplois du temps qui respectent l'ensemble des contraintes spécifiées tout en optimisant l'utilisation des ressources.

Les principales contributions de ce travail sont :
- La formalisation mathématique du problème d'emploi du temps comme un problème de satisfaction de contraintes
- L'implémentation d'un solveur efficace utilisant Google OR-Tools
- Le développement d'une interface de visualisation interactive pour les emplois du temps
- L'automatisation complète du processus de génération d'emploi du temps

Le générateur développé répond aux besoins exprimés et offre une solution pratique et efficace au problème de planification des emplois du temps universitaires. Il permet de réduire considérablement le temps et l'effort nécessaires pour créer des emplois du temps de qualité, tout en garantissant le respect de toutes les contraintes essentielles.

Les perspectives d'amélioration identifiées ouvrent la voie à de futurs développements qui pourront rendre cet outil encore plus performant et flexible.

## RÉFÉRENCES
@@SPRING_SHOGUN🍃🍃

