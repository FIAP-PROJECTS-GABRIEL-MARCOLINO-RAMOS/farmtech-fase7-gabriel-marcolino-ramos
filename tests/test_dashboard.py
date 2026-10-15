from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from farmtech import db,telemetria

@pytest.fixture
def app(monkeypatch,tmp_path):
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'dashboard.db');db.initialize();telemetria.seed_demo()
    return AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()

def test_all_service_pages_render(app):
    for section in ['Visão geral','Talhões e manejo','Sensores e IoT','Análise e previsão','Visão computacional','Alertas e AWS','Sobre o projeto']:
        app.radio(key='navigation').set_value(section).run()
        assert not app.exception, [(e.message) for e in app.exception]
        assert app.title

def test_dashboard_records_reading_and_alert(app):
    app.radio(key='navigation').set_value('Sensores e IoT').run()
    before=len(telemetria.readings())
    app.button(key='FormSubmitter:reading-Registrar leitura e avaliar regras').click().run()
    assert not app.exception
    assert len(telemetria.readings())==before+1
    assert app.success
