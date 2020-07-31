# Routing Tables Helper

Un programme réalisé par un amoureux des nouvelles technologies, pour tous les développeurs réseaux, administrateurs systèmes et autres personnes qui pourrait y trouver une utilitée.
Son objectif est de faciliter la création et le calcul de table de routages lors de travaux sur des réseaux.

## Est-ce fini ?

Non, le programme n'en n'est encore qu'a sa première version stable. J'ai toujours espoir de pouvoir améliorer, créer et inover. Le programme ne sera peut être pas mis à jour pour un bon moment, mais cela ne veut pas pour autant dire que je laisse tomber.

### Informations de contact
Par email: biothewolff [arobase] gmx [point] fr\
Via discord: BioTheWolff#7708\
Vous pouvez aussi me retrouver sur ces deux serveurs (français):
- [Developpeur(euse)s FR](https://discord.gg/8d4ACG5)
- [l4p1n-srv](https://discord.gg/awbUQe4)

## Mais qu'est-ce que donc que ce programme ?

Routing Table Helper ou RTH est un programme qui vous aide créer des tables de routages rapidement et facilement. A la place de les créer à la main, d'utiliser une machine virtuelle (VM), votre propre réseau ou encore un papier et un crayon, cet outil le fait pour vous.


RTH est basé et utiliser un autre de mes programmes: [nettools](https://github.com/BioTheWolff/NetTools), un outil pour géréer et calculer des IPs et réseaux rapidement.

# Documentation

## Classes

La classe principale à utiliser est la classe `Discpatcher`. Vous pouvez l'importer depuis `rth.code.dispatcher`.

Les autres classes, qui font chacunes une part du travail, sont `NetworkCreator`, `Ants` et `RoutingTablesGenerator`.
Normalement, vous ne devriez pas avoir à vous en servir à moins que vous ayez des besoins spécifiques.

## Comment utiliser le programme ?

Le gros du travail consiste à formatter vos données correctements.
Pour générer les tables de routage vous arez besoin de trois choses: les sous-réseaux, les routeurs et les liens. Etant donné que l'rdinateur n'est pas encore conscient (skynet arrive !); Vous devez lui fournir ces données pour qu'il puisse virtuellement reconstruire le réseau et qu'il puisse trouver son chemin dans ce bordel de noms et de chiffres.

### Fonctionnement et utilisation générale du programme

Voici la manière la plus simple et rapide à lire et comprendre.
Vous avez juste besoin d'importer la classe `Dispatcher` puis il n'y à plus qu'a appeller la méthode `execute()` sur votre instance !

```ignorelang
from rth.core.dispatcher import Dispatcher

inst = Dispatcher()
inst.execute(subnetworks, routers, links)
# Et c'est fait !

# Vous pouvez maintenant afficher le résultat dans la console
inst.display_routing_tables()

# Ou l'écrire dans un fichier (nous vous recommandons d'utiliser un .txt pour le moment)
inst.output_routing_tables("D:/Projects/output.txt")
```

### Représentation des sous-réseaux

Les sous-réseaux sont représenté par un dictionnaire. Il doit avoir en clés le nom du réseau en en valeur son [CIDR _[EN]_](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) (`{NAME: CIDR, ...}`).

Exemple: 
```python
sous_reseaux = {
    'A': "10.0.1.0/24",
    'B': "10.0.2.0/24",
    'C': "10.0.3.0/24"
}
```

Note: si vous n'avez ou ne souhaitez donner de nom à un sous réseau, laissez la clé vide (`''`); un nom unique sera automatiquement fournis à votre sous-réseau en suivant la nomenclature suivante: `<Untitled Network#ID:{ID ICI}>` (`{ID ICI}` étant remplacé par l'identifiant unique du réseau).

### Configuration des routers

La configuration des routeurs est aussi un dictionnaire, il prends en clés les noms des routeurs et en valeur si le routeur est connecté à internet (`True` si oui, `None` sinon) (`{NAME: HAS_INTERNET_CONNECTION, ...}`)

Exemple:
```python
routers = {
    0: True, //Ce routeur est conncté à internet
    1: None,
    2: None,
    3: None
}
``` 

**ATTENTION:** Actuellement, seul **UN** routeur doit être connecté à internet. Si aucun ou plus d'un routeur sont connectés à internet, le programme renverra une exception.

Le router avec une connexion internet sera apellé "routeur maitre" ci-après.

### Configuration des Liens

La configuration des liens est la plus importante mais aussi la plus complexe. Le format est le suivant: `{NOM_ROUTEUR: {NOM_SOUSRESEAU: IP, ...}, ...}`. Hum, assez compliqué, voici quelques explications suplémentaires: vous devez faire un dictionnaire listant les sous-réseaux connectés à chaque routeur, pour caque routeur.

La valeur `IP` peut soit être une IPv4 ou `None`, si vous mettez `None`, le programme assignera automatiquement une IP, celle-ci cera la première adresse IP disponible en partant de la fin des possibles pour le sous-réseau.

Exemple:
```python
links = {
    0: {
        "A": "10.0.1.200"
    },
    1: {
        "A": None,
        "C": "10.0.3.254"
    },
    2: {
        "A": "10.0.1.253",
        "B": "10.0.2.253"
    },
    3: {
        "B": "10.0.2.252",
        "C": None
    }
}
```

### Et maintenant tous en coeur !

```python
from rth.core.dispatcher import Dispatcher

subnetworks = {
    'A': "10.0.1.0/24",
    'B': "10.0.2.0/24",
    'C': "10.0.3.0/24"
}

routers = {
    0: True,
    1: None,
    2: None,
    3: None
}

links = {
    0: {
        "A": "10.0.1.200"
    },
    1: {
        "A": None,
        "C": "10.0.3.254"
    },
    2: {
        "A": "10.0.1.253",
        "B": "10.0.2.253"
    },
    3: {
        "B": "10.0.2.252",
        "C": None
    }
}

inst = Dispatcher()
inst.execute(subnetworks, routers, links)
```

## Options cachée et formattage de sortie

### Les options cachée et leurs impacts sur les routes

Ce titre peut paraître un peut bizzarre, mais pas d'inquétude, nous allons vous expliquer.
Le programme, quand il rencontre plusieurs options pour allert d'un sous-réseau à un autre devra faire un choix. De ce fait le chemin suivi par le programme, qui sera biensûr visible sur les tables de routage au final pourra vous étonner.
Donc, afin de vous éviter tout doutes et de vous aider à trouver un chemin plus rapidement, nous avons ajoutés une sections "sauts" dans la sortie

Elle ressemble à ceci
```ignorelang
----- HOPS -----
From subnetwork A to subnetwork B: router 2
From subnetwork A to subnetwork C: router 2 > router 1
From subnetwork A to subnetwork D: router 2 > router 1 > router 3
From subnetwork B to subnetwork A: router 2

...
(Seul un extrait est visible ici)
```

Cela pourra vous aider à visualiser quels chemins ont étés pris

### Formmatage de la sortie

La sortie des tables de routages n'est pas un tableau tel que vous pourriez vous y attendre. Pour le moment, tout du moins.

La sortie ressemble actuellement à ceci
```ignorelang
----- ROUTING TABLES -----
Router MyRouter
  - 192.168.0.0/24      : 192.168.0.254 via 192.168.0.254
  - 192.168.1.0/24      : 192.168.1.254 via 192.168.1.254
  - 0.0.0.0/0           : 192.168.1.253 via 192.168.1.254
  - 10.0.0.0/24         : 192.168.0.253 via 192.168.0.254
  - 10.0.1.0/24         : 192.168.1.253 via 192.168.1.254
```

Comme vous avez pu le deviner, le format est le suivant:  
`REASEAU DE DESTIONATION: PASSERELLE via INTERFACE`  
La route principale (donc la sortie du réseau local) est toujours `0.0.0.0/0` dans la sortie.