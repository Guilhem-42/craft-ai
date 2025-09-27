"""
Test fixtures and sample data for journalist finder tests
"""
import pytest
from datetime import datetime
from typing import Dict, Any, List

# Sample journalist data for testing
SAMPLE_JOURNALIST_DATA = {
    "name": "John Doe",
    "email": "john.doe@techcrunch.com",
    "bio": "Senior AI reporter covering machine learning and artificial intelligence trends",
    "job_title": "Senior Technology Reporter",
    "current_publication": "TechCrunch",
    "twitter_handle": "johndoe_tech",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "website_url": "https://johndoe.tech",
    "country": "United States",
    "city": "San Francisco",
    "timezone": "America/Los_Angeles",
    "specializations": "artificial intelligence,machine learning,programming",
    "source_platform": "newsapi",
    "twitter_followers": 15000,
    "article_count": 150,
    "programming_expertise": True,
    "is_verified": True,
    "reputation_score": 0.85,
    "ai_relevance_score": 0.92
}

SAMPLE_JOURNALIST_DATA_2 = {
    "name": "Jane Smith",
    "email": "jane.smith@wired.com",
    "bio": "Technology journalist specializing in cybersecurity and data privacy",
    "job_title": "Cybersecurity Reporter",
    "current_publication": "Wired",
    "twitter_handle": "janesmith_sec",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "country": "United Kingdom",
    "city": "London",
    "specializations": "cybersecurity,data privacy,technology",
    "source_platform": "twitter",
    "twitter_followers": 8500,
    "article_count": 89,
    "is_verified": False,
    "reputation_score": 0.72,
    "ai_relevance_score": 0.45
}

# Sample API responses for mocking
SAMPLE_NEWSAPI_RESPONSE = {
    "status": "ok",
    "totalResults": 2,
    "articles": [
        {
            "source": {"id": "techcrunch", "name": "TechCrunch"},
            "author": "John Doe",
            "title": "The Future of AI in Healthcare",
            "description": "Exploring how artificial intelligence is transforming healthcare...",
            "url": "https://techcrunch.com/ai-healthcare",
            "urlToImage": "https://example.com/image.jpg",
            "publishedAt": "2024-01-15T10:30:00Z",
            "content": "Artificial intelligence is revolutionizing healthcare..."
        },
        {
            "source": {"id": "wired", "name": "Wired"},
            "author": "Jane Smith",
            "title": "AI Ethics: The New Frontier",
            "description": "As AI becomes more prevalent, ethical considerations...",
            "url": "https://wired.com/ai-ethics",
            "urlToImage": "https://example.com/image2.jpg",
            "publishedAt": "2024-01-14T15:45:00Z",
            "content": "The rapid advancement of AI technology..."
        }
    ]
}

SAMPLE_CLEARBIT_RESPONSE = {
    "person": {
        "id": "12345",
        "name": {
            "fullName": "John Doe",
            "givenName": "John",
            "familyName": "Doe"
        },
        "email": "john.doe@techcrunch.com",
        "bio": "Senior AI reporter covering machine learning trends",
        "twitter": {
            "handle": "johndoe_tech",
            "followers": 15000
        },
        "linkedin": {
            "handle": "johndoe",
            "url": "https://linkedin.com/in/johndoe"
        },
        "location": {
            "country": "United States",
            "state": "California",
            "city": "San Francisco"
        }
    },
    "company": {
        "name": "TechCrunch",
        "domain": "techcrunch.com",
        "category": {
            "industry": "Media"
        }
    }
}

SAMPLE_GOOGLE_SCHOLAR_HTML = """
<html>
<body>
    <div class="gs_r">
        <div class="gs_ri">
            <h3 class="gs_rt">
                <a href="/citations?user=test123">Dr. Alice Johnson</a>
            </h3>
            <div class="gs_a">Professor of Computer Science, MIT</div>
        </div>
    </div>
</body>
</html>
"""

SAMPLE_GOOGLE_SCHOLAR_PROFILE_HTML = """
<html>
<body>
    <div id="gsc_prf_in">Dr. Alice Johnson</div>
    <div class="gsc_prf_il">MIT - Computer Science</div>
    <div id="gsc_prf_int">
        <a class="gsc_prf_inta">Artificial Intelligence</a>
        <a class="gsc_prf_inta">Machine Learning</a>
        <a class="gsc_prf_inta">Neural Networks</a>
    </div>
    <table id="gsc_rsb_st">
        <tr>
            <td class="gsc_rsb_std">1250</td>
            <td class="gsc_rsb_std">850</td>
        </tr>
        <tr>
            <td class="gsc_rsb_std">45</td>
            <td class="gsc_rsb_std">32</td>
        </tr>
    </table>
</body>
</html>
"""

SAMPLE_RESEARCHGATE_HTML = """
<html>
<body>
    <div class="profile-header">
        <h1 class="profile-name">Dr. Bob Wilson</h1>
        <div class="institution">Stanford University</div>
    </div>
    <div class="research-interests">
        <span class="interest-item">Deep Learning</span>
        <span class="interest-item">Computer Vision</span>
    </div>
    <div class="stats">
        <div class="publication-count">75</div>
        <div class="citation-count">2100</div>
        <div class="h-index">28</div>
    </div>
</body>
</html>
"""

# Test database configuration
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def sample_journalist():
    """Return sample journalist data"""
    return SAMPLE_JOURNALIST_DATA.copy()

@pytest.fixture
def sample_journalist_2():
    """Return second sample journalist data"""
    return SAMPLE_JOURNALIST_DATA_2.copy()

@pytest.fixture
def sample_journalists_list():
    """Return list of sample journalists"""
    return [SAMPLE_JOURNALIST_DATA.copy(), SAMPLE_JOURNALIST_DATA_2.copy()]

@pytest.fixture
def sample_newsapi_response():
    """Return sample NewsAPI response"""
    return SAMPLE_NEWSAPI_RESPONSE.copy()

@pytest.fixture
def sample_clearbit_response():
    """Return sample Clearbit response"""
    return SAMPLE_CLEARBIT_RESPONSE.copy()

@pytest.fixture
def sample_google_scholar_html():
    """Return sample Google Scholar HTML"""
    return SAMPLE_GOOGLE_SCHOLAR_HTML

@pytest.fixture
def sample_google_scholar_profile_html():
    """Return sample Google Scholar profile HTML"""
    return SAMPLE_GOOGLE_SCHOLAR_PROFILE_HTML

@pytest.fixture
def sample_researchgate_html():
    """Return sample ResearchGate HTML"""
    return SAMPLE_RESEARCHGATE_HTML

@pytest.fixture
def test_database_url():
    """Return test database URL"""
    return TEST_DATABASE_URL

# Mock environment variables for testing
@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("NEWSAPI_KEY", "test_newsapi_key")
    monkeypatch.setenv("CLEARBIT_KEY", "test_clearbit_key")
    monkeypatch.setenv("TWITTER_API_KEY", "test_twitter_key")
    monkeypatch.setenv("TWITTER_API_SECRET", "test_twitter_secret")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "test_access_token")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET", "test_access_secret")
    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "test_linkedin_id")
    monkeypatch.setenv("LINKEDIN_CLIENT_SECRET", "test_linkedin_secret")

# Common test utilities
class MockResponse:
    """Mock HTTP response for testing"""
    
    def __init__(self, json_data=None, text_data=None, status_code=200):
        self.json_data = json_data
        self.text_data = text_data
        self.status_code = status_code
        self.text = text_data or ""
    
    def json(self):
        if self.json_data is None:
            raise ValueError("No JSON data")
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} Error")

def create_mock_response(json_data=None, text_data=None, status_code=200):
    """Create a mock HTTP response"""
    return MockResponse(json_data, text_data, status_code)

# Test data generators
def generate_journalist_data(count: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple journalist data entries for testing"""
    journalists = []
    for i in range(count):
        journalist = SAMPLE_JOURNALIST_DATA.copy()
        journalist["name"] = f"Test Journalist {i+1}"
        journalist["email"] = f"journalist{i+1}@example.com"
        journalist["twitter_handle"] = f"journalist{i+1}"
        journalist["reputation_score"] = 0.5 + (i * 0.1)
        journalist["ai_relevance_score"] = 0.4 + (i * 0.15)
        journalists.append(journalist)
    return journalists

def generate_articles_data(count: int = 3) -> List[Dict[str, Any]]:
    """Generate multiple article data entries for testing"""
    articles = []
    for i in range(count):
        article = {
            "source": {"name": f"Publication {i+1}"},
            "author": f"Author {i+1}",
            "title": f"AI Article {i+1}",
            "description": f"Description for article {i+1}",
            "url": f"https://example{i+1}.com/article",
            "publishedAt": "2024-01-15T10:30:00Z"
        }
        articles.append(article)
    return articles
