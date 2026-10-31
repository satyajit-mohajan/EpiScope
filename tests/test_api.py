from fastapi.testclient import TestClient
from sentinel.api import app

client=TestClient(app)

def test_frontend_and_health():
    r=client.get('/')
    assert r.status_code==200 and 'EpiScope Sentinel' in r.text
    assert client.get('/api/health').json()['simulation_only']
    assert client.get('/static/app.js').status_code==200

def test_endpoints_and_csv():
    assert client.get('/api/meta').json()['project']=='EpiScope Sentinel'
    overview=client.get('/api/overview?syndrome=dengue')
    assert overview.status_code==200
    assert len(overview.json()['districts'])==8
    fore=client.get('/api/forecast?syndrome=ili&district=Sylhet&weeks=4')
    assert fore.status_code==200
    assert len(fore.json()['forecast'])==4
    scen=client.get('/api/scenario?syndrome=dengue&district=Dhaka&reduction_pct=35')
    assert scen.status_code==200 and scen.json()['difference_total']>0
    dl=client.get('/api/export?syndrome=dengue')
    assert dl.status_code==200 and 'SIMULATED_SENTINEL' in dl.text

def test_validation():
    assert client.get('/api/forecast?weeks=13').status_code==422
    assert client.get('/api/forecast?district=Unknown').status_code==422
    assert client.get('/api/overview?syndrome=unknown').status_code==422
    assert client.get('/api/scenario?reduction_pct=100').status_code==422
