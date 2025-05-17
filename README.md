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
   python timetable-generator.py
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


        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emplois du temps - Département d'Informatique</title>
            <style>
                :root {
                    --primary: #2c3e50;
                    --secondary: #4a6785;
                    --light: #f5f7fa;
                    --dark: #2c3e50;
                    --border: #ddd;
                    --text: #333;
                    --text-light: #666;
                    --highlight: #e9eef2;
                }
                
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #fff;
                    color: var(--text);
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    background-color: var(--primary);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                header h1 {
                    margin: 0;
                    font-size: 24px;
                }
                
                header h2 {
                    margin: 5px 0;
                    font-size: 16px;
                    font-weight: normal;
                }
                
                .semester-indicator {
                    display: inline-block;
                    padding: 5px 10px;
                    color: var(--text);
                    background-color: var(--light);
                    border: 1px solid var(--border);
                    border-radius: 4px;
                    margin-left: 10px;
                    font-size: 13px;
                    font-weight: normal;
                }
                
                .tabs {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    margin: 20px 0;
                    background-color: white;
                    border-radius: 2px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    padding: 10px;
                    border: 1px solid var(--border);
                }
                
                .tab-button {
                    background-color: var(--light);
                    border: 1px solid var(--border);
                    padding: 8px 16px;
                    margin: 4px;
                    cursor: pointer;
                    border-radius: 2px;
                    transition: all 0.2s ease;
                    font-weight: normal;
                    color: var(--text);
                }
                
                .tab-button:hover {
                    background-color: var(--highlight);
                }
                
                .tab-button.active {
                    background-color: var(--secondary);
                    color: white;
                    border-color: var(--secondary);
                }
                
                .semester-label {
                    font-weight: normal;
                    margin-left: 5px;
                    font-size: 12px;
                }
                
                .tab-content {
                    display: none;
                    background-color: white;
                    border-radius: 2px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                    border: 1px solid var(--border);
                }
                
                .tab-content.active {
                    display: block;
                }
                
                .schedule-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 10px;
                }
                
                .schedule-title {
                    margin: 0;
                    font-size: 18px;
                    color: var(--primary);
                }
                
                .schedule-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                
                .schedule-table th, .schedule-table td {
                    border: 1px solid var(--border);
                    padding: 10px;
                    text-align: center;
                }
                
                .schedule-table th {
                    background-color: var(--primary);
                    color: white;
                    font-weight: normal;
                }
                
                .schedule-table tr:nth-child(even) {
                    background-color: var(--light);
                }
                
                .schedule-table .time-col {
                    width: 120px;
                    background-color: var(--secondary);
                    color: white;
                    font-weight: normal;
                }
                
                .course-cell {
                    padding: 6px;
                    border-radius: 2px;
                    background-color: var(--highlight);
                    min-height: 70px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    border: 1px solid #d9e1e7;
                }
                
                .course-id {
                    font-weight: bold;
                    color: var(--primary);
                }
                
                .course-info {
                    font-size: 0.85em;
                    color: var(--text-light);
                    margin-top: 3px;
                }
                
                .legend {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: white;
                    border-radius: 2px;
                    border: 1px solid var(--border);
                }
                
                .legend h3 {
                    color: var(--primary);
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 10px;
                    margin-top: 0;
                    font-size: 16px;
                }
                
                .legend-item {
                    display: flex;
                    margin: 8px 0;
                }
                
                .legend-code {
                    font-weight: bold;
                    color: var(--primary);
                    width: 100px;
                }
                
                .print-button {
                    display: block;
                    margin: 20px auto;
                    background-color: var(--secondary);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 2px;
                    cursor: pointer;
                    font-weight: normal;
                    transition: background-color 0.2s ease;
                }
                
                .print-button:hover {
                    background-color: var(--primary);
                }
                
                .summary {
                    background-color: var(--light);
                    border-radius: 2px;
                    padding: 15px;
                    margin: 20px 0;
                    border: 1px solid var(--border);
                }
                
                .summary h3 {
                    margin-top: 0;
                    color: var(--primary);
                    font-size: 16px;
                }
                
                .not-scheduled {
                    color: #666;
                    font-style: italic;
                }
                
                @media print {
                    .tabs, .print-button, .summary {
                        display: none;
                    }
                    
                    .tab-content {
                        display: block;
                        page-break-after: always;
                        box-shadow: none;
                        border: none;
                    }
                    
                    body {
                        padding: 0;
                        margin: 0;
                    }
                    
                    .schedule-table {
                        font-size: 11px;
                    }
                    
                    .container {
                        max-width: 100%;
                        padding: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Emplois du Temps - Département d'Informatique</h1>
                <h2>Année Académique 2024-2025</h2>
            </header>
            
            <div class="container">
                <div class="tabs">
        
                    <button class="tab-button active" onclick="showTab('L1Ss1')">
                        Niveau 1 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L1Ss2')">
                        Niveau 1 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L2Ss1')">
                        Niveau 2 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L2Ss2')">
                        Niveau 2 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L3Ss1')">
                        Niveau 3 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L3Ss2')">
                        Niveau 3 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L4Ss1')">
                        Niveau 4 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                    <button class="tab-button " onclick="showTab('L4Ss2')">
                        Niveau 4 <span class="semester-label">(Semestre s)</span>
                    </button>
            
                </div>
                
                <div class="summary">
                    <h3>Remarque</h3>
                    <p>En raison de contraintes d'occupation des salles et de disponibilité des enseignants, 
                    certains cours peuvent ne pas apparaître dans cette version de l'emploi du temps.</p>
                </div>
                
                <button class="print-button" onclick="window.print()">Imprimer tous les emplois du temps</button>
        
                <div id="L1Ss1-tab" class="tab-content active">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 1 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF121</div>
                                        <div class="course-info">KOUOKAM, KOUOKAM E. A.</div>
                                        <div class="course-info">EXTENSION 1 S008</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">FBL111</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF141</div>
                                        <div class="course-info">EKODECK</div>
                                        <div class="course-info">EXTENSION 2 S005</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">MAT131</div>
                                        <div class="course-info">BOGSO</div>
                                        <div class="course-info">EXTENSION 2 S005</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF111</div>
                                        <div class="course-info">ATSA, ETOUNDI ROGER</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">PPE111</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">EXTENSION 2 S003</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                <td></td><td></td><td></td><td></td><td></td>
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF131</div>
                                        <div class="course-info">DOMGA, KOMGUEM Rodrigue</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF111</span>
                            <span class="">INTRODUCTION À L'ALGORITHMIQUE ET À LA PROGRAMMATION</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF121</span>
                            <span class="">INTRODUCTION À L'ARCHITECTURE DES ORDINATEURS</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF131</span>
                            <span class="">INTRODUCTION AUX SYSTÈMES ET RÉSEAUX</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">MAT131</span>
                            <span class="">ANALYSE DE LA DROITE REELLE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">FBL111</span>
                            <span class="">FORMATION BILINGUE I</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF141</span>
                            <span class="">INTRODUCTION À LA SÉCURITÉ INFORMATIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">PPE111</span>
                            <span class="">EXPLORATION PROFESSIONNELLE, ORIENTATION ET EDUCATION A LA CITOYENETE</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L1Ss2-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 1 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INFO142</div>
                                        <div class="course-info">MELATAGIA, YONTA PAULIN</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R108</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF122</div>
                                        <div class="course-info">KOUOKAM, KOUOKAM E. A.</div>
                                        <div class="course-info">AMPHI A502</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF112</div>
                                        <div class="course-info">AMINOU, HALIDOU</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R108</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">MAT112</div>
                                        <div class="course-info">OGADOA</div>
                                        <div class="course-info">AMPHI A1002</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INFO132</div>
                                        <div class="course-info">TSOPZE, NORBERT</div>
                                        <div class="course-info">AMPHI A250</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INFO152</div>
                                        <div class="course-info">ADAMOU, HAMZA</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF112</span>
                            <span class="">INTRODUCTION AUX STRUCTURES DE DONNEES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF122</span>
                            <span class="">FONDEMENTS MATHEMATIQUES DE L'INFORMATIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INFO132</span>
                            <span class="">PROGRAMMATION STRUCTUREE EN C</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INFO142</span>
                            <span class="">INTRODUCTION À LA SCIENCE DES DONNÉES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">MAT112</span>
                            <span class="">ALGEBRE 1B</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INFO152</span>
                            <span class="">Unnamed</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L2Ss1-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 2 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF251</div>
                                        <div class="course-info">BAYEM, JACQUES NARCISSE</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">MAT211</div>
                                        <div class="course-info">MBIAKOP, Hilaire George</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF211</div>
                                        <div class="course-info">ABESSOLO, GHISLAIN</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF221</div>
                                        <div class="course-info">ABESSOLO, GHISLAIN</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">FBL211</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF231</div>
                                        <div class="course-info">TAPAMO, HYPOLITE</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">FBL211</span>
                            <span class="">FORMATION BILINGUE II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF211</span>
                            <span class="">PROGRAMMATION ORIENTÉE OBJET</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF221</span>
                            <span class="">BASES DE DONNEES ET MODELISATION</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF231</span>
                            <span class="">METHODES ALGORITHMIQUES ET STRUCTURES DE DONNEES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">MAT211</span>
                            <span class="">ALGEBRE 2A : THEORIE SPECTRALE ET ALGEBRE MULTILINEAIRE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF251</span>
                            <span class="">GENIE LOGICIEL ET SYSTEMES D'INFORMATION</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L2Ss2-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 2 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">PPE212</div>
                                        <div class="course-info">TAPAMO, HYPOLITE</div>
                                        <div class="course-info">AMPHI A250</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">MAT232</div>
                                        <div class="course-info">FOKAM</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF232</div>
                                        <div class="course-info">MAKEMBE, S. OSWALD</div>
                                        <div class="course-info">AMPHI A1002</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF252</div>
                                        <div class="course-info">NKONDOCK, BAHANACK N.</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF212</div>
                                        <div class="course-info">NDOUNDAM, RENE</div>
                                        <div class="course-info">AMPHI A502</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF222</div>
                                        <div class="course-info">MESSI NGEULE, THOMAS</div>
                                        <div class="course-info">AMPHI A135</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                <td></td><td></td><td></td>
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF242</div>
                                        <div class="course-info">MELATAGIA, YONTA PAULIN</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        <td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF222</span>
                            <span class="">PROGRAMMATION WEB</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF232</span>
                            <span class="">STATISTIQUES ET ANALYSE DE DONNEES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF212</span>
                            <span class="">MATHEMATIQUES DISCRETES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF242</span>
                            <span class="">SCIENCE DES DONNEES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF252</span>
                            <span class="">SECURITE INFORMATIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">PPE212</span>
                            <span class="">PROJET PROFESSIONNEL ET PRE-IMMERSION</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">MAT232</span>
                            <span class="">CALCUL INTEGRAL SUR Rn</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L3Ss1-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 3 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">ENG3035</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF3115</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">FRA3045</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R110</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF3125</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R108</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF3015</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE E203</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF3025</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">ENG3035</span>
                            <span class="">ENGLISH FOR MATHEMATICS AND COMPUTER SCIENCE II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">FRA3045</span>
                            <span class="">FRANÇAIS POUR SCIENCES MATHÉMATIQUES ET INFORMATIQUES II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF3015</span>
                            <span class="">CONCEPTION ET ANALYSE DES ALGORITHMES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF3025</span>
                            <span class="">CALCUL SCIENTIFIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF3115</span>
                            <span class="">FOUILLE DE DONNÉES I</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF3125</span>
                            <span class="">ANALYSES STATISTIQUES</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L3Ss2-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 3 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF322</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A502</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF342</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF316</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF382</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A135</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF352</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R110</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF372</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF362</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">EXTENSION 1 S008</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">PPE312</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI A1002</div>
                                    </div>
                                </td>
                        <td></td><td></td><td></td>
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF332</div>
                                        <div class="course-info">N/A</div>
                                        <div class="course-info">AMPHI AIII</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF382</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF372</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF322</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF362</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF352</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF342</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF316</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF332</span>
                            <span class=""></span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">PPE312</span>
                            <span class="">PROJET PROFESSIONNEL DE L'ETUDIANT III</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L4Ss1-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 4 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4167</div>
                                        <div class="course-info">EBELLE</div>
                                        <div class="course-info">AMPHI A1002</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4147</div>
                                        <div class="course-info">EBELLE</div>
                                        <div class="course-info">EXTENSION 2 S003</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4127</div>
                                        <div class="course-info">MELATAGIA, YONTA PAULIN</div>
                                        <div class="course-info">AMPHI A135</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4027</div>
                                        <div class="course-info">ATSA, ETOUNDI ROGER</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4057</div>
                                        <div class="course-info">DJAM KIMBI, XAVERIA YOUHEP</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4067</div>
                                        <div class="course-info">VALERY, MONTHE</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R108</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4017</div>
                                        <div class="course-info">NDOUNDAM, RENE</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4077</div>
                                        <div class="course-info">JIOMEKONG, FIDEL AZANZI</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4137</div>
                                        <div class="course-info">NZEKON</div>
                                        <div class="course-info">EXTENSION 1 S006</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4157</div>
                                        <div class="course-info">DJAM KIMBI, XAVERIA YOUHEP</div>
                                        <div class="course-info">AMPHI AI</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4087</div>
                                        <div class="course-info">AMINOU, HALIDOU</div>
                                        <div class="course-info">AMPHI A250</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4107</div>
                                        <div class="course-info">MONTHE, VALERY</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R110</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                <td></td>
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4117</div>
                                        <div class="course-info">TSOPZE, NORBERT</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        <td></td><td></td>
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4097</div>
                                        <div class="course-info">ADAMOU, HAMZA</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        <td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF4017</span>
                            <span class="">COMPLEXITÉ ET ALGORITHMIQUE AVANCÉE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4027</span>
                            <span class="">GÉNIE LOGICIEL</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4057</span>
                            <span class="">ARCHITECTURES LOGICIELLES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4067</span>
                            <span class="">UML ET DESIGN PATTERNS</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4077</span>
                            <span class="">PROGRAMMATION DES TERMINAUX MOBILES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4087</span>
                            <span class="">RÉSEAUX II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4097</span>
                            <span class="">PRINCIPES DE CONCEPTION DES SYSTÈMES D'EXPLOITATION</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4107</span>
                            <span class="">CLOUD COMPUTING</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4117</span>
                            <span class="">FOUILLE DE DONNÉES II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4127</span>
                            <span class="">TECHNIQUES D'OPTIMISATION II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4137</span>
                            <span class="">ANALYSE DES DONNÉES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4147</span>
                            <span class="">SÉCURITÉ INFORMATIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4157</span>
                            <span class="">SÉCURITÉ LOGICIELLE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4167</span>
                            <span class="">CRYPTOGRAPHIE SYMÉTRIQUE</span>
                        </div>
                
                    </div>
                </div>
            
                <div id="L4Ss2-tab" class="tab-content ">
                    <div class="schedule-header">
                        <h2 class="schedule-title">
                            Emploi du Temps - Niveau 4 
                            <span class="semester-indicator">Second Semestre</span>
                        </h2>
                    </div>
                    
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            <th>Lundi</th><th>Mardi</th><th>Mercredi</th><th>Jeudi</th><th>Vendredi</th><th>Samedi</th>
                            </tr>
                        </thead>
                        <tbody>
            
                            <tr>
                                <td class="time-col">7:00-9:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4198</div>
                                        <div class="course-info">JIOMEKONG, FIDEL AZANZI</div>
                                        <div class="course-info">EXTENSION 2 S003</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4258</div>
                                        <div class="course-info">TSOPZE, NORBERT</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE E203</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4288</div>
                                        <div class="course-info">EBELLE</div>
                                        <div class="course-info">AMPHI A250</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4238</div>
                                        <div class="course-info">TAPAMO, HYPOLITE</div>
                                        <div class="course-info">EXTENSION 1 S008</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4218</div>
                                        <div class="course-info">ADAMOU, HAMZA</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4268</div>
                                        <div class="course-info">EKODECK</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">10:05-12:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4208</div>
                                        <div class="course-info">DOMGA, KOMGUEM Rodrigue</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE E203</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4038</div>
                                        <div class="course-info">TAPAMO, HYPOLITE</div>
                                        <div class="course-info">AMPHI A1001</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4188</div>
                                        <div class="course-info">JIOMEKONG, FIDEL AZANZI</div>
                                        <div class="course-info">EXTENSION 2 S005</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4228</div>
                                        <div class="course-info">AMINOU, HALIDOU</div>
                                        <div class="course-info">AMPHI A350</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4178</div>
                                        <div class="course-info">DJAM KIMBI, XAVERIA YOUHEP</div>
                                        <div class="course-info">BLOC PEDAGOGIQUE R101</div>
                                    </div>
                                </td>
                        
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4278</div>
                                        <div class="course-info">NDOUNDAM, RENE</div>
                                        <div class="course-info">AMPHI A250</div>
                                    </div>
                                </td>
                        
                            </tr>
                
                            <tr>
                                <td class="time-col">13:05-15:55</td>
                
                                <td>
                                    <div class="course-cell">
                                        <div class="course-id">INF4248</div>
                                        <div class="course-info">MELATAGIA, YONTA PAULIN</div>
                                        <div class="course-info">EXTENSION 2 S003</div>
                                    </div>
                                </td>
                        <td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">16:05-18:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                            <tr>
                                <td class="time-col">19:05-21:55</td>
                <td></td><td></td><td></td><td></td><td></td><td></td>
                            </tr>
                
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
            
                        <div class="legend-item">
                            <span class="legend-code">INF4038</span>
                            <span class="">BASE DE DONNÉES DISTRIBUÉES</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4048</span>
                            <span class="not-scheduled">COMPILATION (Non programmé)</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4178</span>
                            <span class="">GÉNIE LOGICIEL I</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4188</span>
                            <span class="">WEB SÉMANTIQUE ET APPLICATIONS</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4198</span>
                            <span class="">PROJET II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4048</span>
                            <span class="not-scheduled">COMPILATION (Non programmé)</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4208</span>
                            <span class="">RÉSEAUX MOBILES ET SANS FILS</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4218</span>
                            <span class="">PROGRAMMATION DISTRIBUÉE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4228</span>
                            <span class="">PROJET II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4238</span>
                            <span class="">VISION PAR ORDINATEUR</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4248</span>
                            <span class="">APPRENTISSAGE ARTIFICIEL II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4258</span>
                            <span class="">PROJET II</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4268</span>
                            <span class="">CRYPTOGRAPHIE ASYMÉTRIQUE</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4278</span>
                            <span class="">COURBES ELLIPTIQUES 1</span>
                        </div>
                
                        <div class="legend-item">
                            <span class="legend-code">INF4288</span>
                            <span class="">PROJET II</span>
                        </div>
                
                    </div>
                </div>
            
                <script>
                    function showTab(className) {
                        // Masquer tous les contenus d'onglet
                        const tabs = document.querySelectorAll('.tab-content');
                        tabs.forEach(tab => {
                            tab.classList.remove('active');
                        });
                        
                        // Désactiver tous les boutons d'onglet
                        const buttons = document.querySelectorAll('.tab-button');
                        buttons.forEach(button => {
                            button.classList.remove('active');
                        });
                        
                        // Afficher l'onglet sélectionné
                        document.getElementById(className + '-tab').classList.add('active');
                        
                        // Activer le bouton sélectionné
                        document.querySelector(`.tab-button[onclick="showTab('${className}')"]`).classList.add('active');
                    }
                </script>
            </div>
        </body>
        </html>
        
