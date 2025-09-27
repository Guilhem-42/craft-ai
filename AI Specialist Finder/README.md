# AI Specialist Finder - Journalistes & Chercheurs IA

🔍 **Agent IA intelligent pour identifier et analyser des journalistes spécialistes et chercheurs spécialisés dans l'intelligence artificielle et les technologies émergentes**

## 🎯 Objectif

Ce projet développe un agent IA avancé qui utilise le web scraping multi-plateformes pour identifier, analyser et localiser des **journalistes spécialistes** et **chercheurs spécialisés** dans les domaines de l'IA, du machine learning, de la programmation et des technologies émergentes. L'objectif principal est de faciliter les interviews pour des revues de presse spécialisées et de créer un réseau d'experts qualifiés.

## 🚀 Fonctionnalités Avancées

### 🔍 Scraping Multi-Sources (8 Scrapers Actifs)

#### 🌐 **Sites de Journaux Internationaux**

- **TechCrunch, Wired, Ars Technica, The Verge**
- **VentureBeat, ZDNet, Engadget, Mashable**
- **Sites francophones** : Les Echos, Contexte, Indeed.fr

#### 🐦 **Réseaux Sociaux & APIs**

- **Twitter API** : Recherche de spécialistes tech actifs
- **LinkedIn** : Profils de chercheurs et journalistes spécialisés
- **Serper API** : Recherche Google avancée pour journalistes francophones

#### 🎯 **Sources Académiques & Recherche**

- **Google Scholar** : Chercheurs en IA et machine learning
- **ResearchGate** : Publications scientifiques et profils chercheurs
- **NewsAPI** : Articles d'actualité sur l'IA

### 🧠 Analyse Intelligente & Scoring

#### 📊 **Système de Scoring Avancé**

- **Score de Réputation** (0-1) : Followers, articles, qualité publications
- **Score de Pertinence IA** (0-1) : Expertise en IA, ML, programmation
- **Score de Spécialisation** : Domaines d'expertise précis

#### 🌍 **Géolocalisation Intelligente**

- **Pays multiples** : France, Belgique, Suisse, Canada francophone
- **Détection automatique** : Analyse des URLs et contenus
- **Filtrage géographique** : Recherche par région

### 💾 Base de Données Optimisée

#### 🗄️ **Stockage SQLite Avancé**

- **281+ profils** de journalistes et chercheurs
- **Modèles relationnels** : Journalistes, Articles, Recherches
- **Index optimisés** : Recherche ultra-rapide

#### 📤 **Exports Multi-Formats**

- **CSV** : 200 résultats maximum avec tous les champs
- **Markdown** : Format lisible pour documentation
- **Filtrage intelligent** : Par pays, spécialisation, scores

## 📁 Structure du Projet

```
journalist-finder/
├── src/
│   ├── scrapers/           # Modules de scraping
│   │   ├── newspaper_scraper.py
│   │   ├── twitter_scraper.py
│   │   └── linkedin_scraper.py
│   ├── database/           # Gestion base de données
│   │   ├── models.py
│   │   └── database_manager.py
│   ├── analysis/           # Analyse et scoring
│   │   ├── reputation_analyzer.py
│   │   └── relevance_scorer.py
│   └── main.py            # Application principale
├── config/
│   └── settings.py        # Configuration
├── data/
│   └── journalists.db     # Base de données SQLite
├── logs/                  # Fichiers de logs
├── requirements.txt       # Dépendances Python
└── README.md
```

## 🛠️ Installation

### Prérequis

- Python 3.8+
- pip

### Installation des dépendances

```bash
cd journalist-finder
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` dans le répertoire racine :

```env
# API Twitter (optionnel)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# LinkedIn (optionnel)
LINKEDIN_USERNAME=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
```

2. Les clés API sont optionnelles. Le système fonctionne sans elles avec des fonctionnalités limitées.

## 🚀 Utilisation Avancée

### 💻 Interface CLI Optimisée

#### 🔄 **Recherche Complète Multi-Sources**

```bash
# Recherche complète avec tous les scrapers actifs
python src/main.py --search
```

#### 🎯 **Recherche par Critères Avancés**

```bash
# Recherche par pays multiples (France, Belgique, Suisse, Canada)
python src/main.py --country "France,Belgique,Suisse,Canada" --limit 200

# Recherche par spécialisation avec seuils optimisés
python src/main.py --specialization "artificial intelligence" --min-reputation 0.15 --min-ai-relevance 0.02

# Recherche de chercheurs académiques
python src/main.py --specialization "machine learning researcher" --limit 100
```

#### 📊 **Exports Multi-Formats**

```bash
# Export CSV avec 200 résultats maximum
python src/main.py --export csv --limit 200

# Export Markdown formaté
python src/main.py --export md --limit 200

# Export filtré par pays
python src/main.py --country "France" --export csv --limit 80
```

#### 📈 **Statistiques Détaillées**

```bash
# Statistiques complètes de la base de données
python src/main.py --stats
```

### Utilisation programmatique

```python
from src.main import JournalistFinderAgent

# Initialiser l'agent
agent = JournalistFinderAgent()

# Recherche complète
results = await agent.run_full_search()

# Recherche par critères
journalists = agent.search_by_criteria(
    specialization="artificial intelligence",
    min_reputation=0.6,
    min_ai_relevance=0.7,
    country="France",
    limit=50
)

# Analyser un journaliste spécifique
analysis = agent.analyze_journalist(journalist_id=1)

# Obtenir les statistiques
stats = agent.get_statistics()
```

## 📊 Résultats Actuels & Métriques

### 🎯 **Base de Données Active**

- **281+ profils** de journalistes et chercheurs spécialisés
- **8 scrapers opérationnels** : Newspaper, NewsAPI, Google Scholar, ResearchGate, Serper français, etc.
- **Couverture géographique** : France, Belgique, Suisse, Canada francophone + monde entier

### 🏆 **Top Experts Identifiés**

1. **Martin Shepperd** (0.71 rep, 0.40 IA) - Professeur Brunel University London
2. **Haitao Wu** (0.66 rep, 0.37 IA) - Associate Professor Zhongnan University
3. **Yoshua Bengio** (0.72 rep, 0.33 IA) - Professeur Mila IVADO CIFAR
4. **Lars Johannsmeier** (0.65 rep, 0.33 IA) - Research Scientist NVIDIA
5. **Andrew McCallum** (0.72 rep, 0.31 IA) - Distinguished Professor UMass Amherst

### 🌍 **Spécialistes Francophones**

- **Sam Altman** (Trends-Tendances) - Score IA: 0.30
- **Jérôme Colombain** (YouTube) - Score IA: 0.22
- **Christophe Charlot** (Trends-Tendances) - Score IA: 0.20
- **Luc Chagnon** (LinkedIn France) - Score IA: 0.02

## 📊 Critères d'Évaluation Avancés

### 🏅 Score de Réputation (0-1)

- **Articles publiés** (30%) : Quantité et qualité des publications
- **Followers sociaux** (25%) : Twitter, LinkedIn, influence digitale
- **Qualité publications** (25%) : Réputation du média/revue
- **Expertise technique** (20%) : Pertinence IA/tech démontrée

### 🎯 Score de Pertinence IA (0-1)

- **Mots-clés spécialisés** : IA, ML, deep learning, neural networks
- **Domaines d'expertise** : Computer vision, NLP, robotics, etc.
- **Publications académiques** : Papers, conférences, citations
- **Expérience pratique** : Projets, entreprises tech, contributions open-source

## 🔍 Sources de Données

### Sites de Journaux Supportés

- TechCrunch, Wired, Ars Technica
- The Verge, VentureBeat, ZDNet
- Engadget, Mashable, Recode
- Axios, et plus...

### Critères de Sélection

- **Spécialisation** : IA, programmation, technologies émergentes
- **Réputation** : Followers, articles, vérification
- **Géolocalisation** : Pays et ville d'origine

## 📈 Exemples de Résultats

```json
{
  "name": "John Doe",
  "email": "john.doe@techcrunch.com",
  "current_publication": "TechCrunch",
  "reputation_score": 0.85,
  "ai_relevance_score": 0.92,
  "specializations": ["artificial intelligence", "machine learning"],
  "twitter_handle": "johndoe_tech",
  "country": "United States",
  "twitter_followers": 15000
}
```

## 🔧 Configuration Avancée

### Personnalisation des Sources

Modifiez `config/settings.py` pour ajouter de nouvelles sources :

```python
NEWS_SOURCES = [
    "votre-site.com",
    "autre-source.fr"
]

AI_KEYWORDS = [
    "intelligence artificielle",
    "apprentissage automatique",
    "vos-mots-clés"
]
```

### Ajustement des Poids

```python
REPUTATION_WEIGHTS = {
    "article_count": 0.4,      # Augmenter pour privilégier la productivité
    "social_followers": 0.3,   # Réduire si moins important
    "engagement_rate": 0.2,
    "publication_quality": 0.1,
    "expertise_relevance": 0.0
}
```

## 📝 Logs et Monitoring

Les logs sont automatiquement générés dans `logs/journalist_finder.log` avec :

- Progression du scraping
- Erreurs et avertissements
- Statistiques de performance
- Détails des journalistes trouvés

## ⚠️ Considérations Légales

### Respect des Conditions d'Utilisation

- **Délais entre requêtes** : Configurés pour éviter la surcharge
- **User-Agent approprié** : Identification correcte du bot
- **Respect robots.txt** : Vérification recommandée

### APIs Officielles Recommandées

- Utilisez l'API Twitter officielle quand possible
- LinkedIn API pour un accès professionnel
- Respectez les limites de taux

## 🤝 Contribution

### Ajouter de Nouveaux Scrapers

1. Créez un nouveau fichier dans `src/scrapers/`
2. Implémentez la classe avec les méthodes requises
3. Ajoutez les tests appropriés

### Améliorer l'Analyse

1. Modifiez `reputation_analyzer.py` ou `relevance_scorer.py`
2. Ajustez les poids et critères
3. Testez avec des données réelles

## 📞 Support

Pour des questions ou problèmes :

1. Vérifiez les logs dans `logs/`
2. Consultez la documentation des APIs
3. Ouvrez une issue avec les détails d'erreur

## 🔮 Roadmap

### Fonctionnalités Futures

- [ ] Interface web avec dashboard
- [ ] Analyse de sentiment des articles
- [ ] Détection automatique de nouveaux journalistes
- [ ] Intégration avec CRM
- [ ] Notifications en temps réel
- [ ] Support multilingue
- [ ] API REST pour intégrations

### Améliorations Techniques

- [ ] Cache Redis pour les performances
- [ ] Scraping distribué avec Celery
- [ ] Machine learning pour le scoring
- [ ] Détection de doublons avancée

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Développé pour faciliter la recherche de journalistes spécialisés en IA et programmation** 🤖📰
