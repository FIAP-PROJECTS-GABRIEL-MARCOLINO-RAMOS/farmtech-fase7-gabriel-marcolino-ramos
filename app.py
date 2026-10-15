"""Dashboard integrado FarmTech — Fase 7. Executar: streamlit run app.py."""
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sqlite3
import uuid

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from farmtech import db, manejo, telemetria, alertas, analise
from farmtech.config import ROOT

st.set_page_config(page_title='FarmTech · Operação da fazenda',page_icon='🌱',layout='wide')
st.markdown('''<style>
.block-container {max-width:1440px;padding-top:4rem;padding-bottom:3rem}
h1 {font-size:2rem!important;font-weight:600!important;letter-spacing:-.04em;text-wrap:balance}
h2 {font-size:1.35rem!important;font-weight:600!important}
h3 {font-size:1.05rem!important;font-weight:600!important}
[data-testid="stMetric"] {border-top:1px solid #e5e5e5;padding:18px 0 12px}
[data-testid="stMetricValue"] {font-size:2rem;font-variant-numeric:tabular-nums}
[data-testid="stSidebar"] {border-right:1px solid #e5e5e5;background:#fafafa}
[data-testid="stSidebar"] h1 {color:#07503f}
.stButton button {border-radius:10px}
</style>''',unsafe_allow_html=True)
db.initialize()
with st.sidebar:
    st.title('FarmTech')
    st.caption('OPERAÇÃO DA FAZENDA · FASE 7')
    section=st.radio('Navegação',['Visão geral','Talhões e manejo','Sensores e IoT','Análise e previsão','Visão computacional','Alertas e AWS','Sobre o projeto'],label_visibility='collapsed',key='navigation')
    st.divider()
    st.caption('Gabriel Marcolino Ramos\n\nRM565717 · Grupo 17')
    st.caption('Ambiente acadêmico local')
    if st.button('Atualizar painel',width='stretch'):st.rerun()

plots=db.talhoes();all_alerts=alertas.listing()

def plot_picker(key):
    if not plots:
        st.info('Cadastre um talhão em “Talhões e manejo” para continuar.');return None
    options={p['id']:p['nome'] for p in plots}
    return st.selectbox('Talhão',list(options),format_func=options.get,key=key)

def failure(exc):
    if isinstance(exc,sqlite3.IntegrityError):st.error('Registro não salvo: confira o nome exclusivo e os relacionamentos.')
    else:st.error(str(exc))

def chart(frame,x,y,label,color=None):
    fig=px.line(frame,x=x,y=y,color=color,labels={x:'Data e hora',y:label,'talhao':'Talhão'},markers=False,
                color_discrete_sequence=['#0a0a0a','#07503f','#657285'])
    fig.update_layout(height=285,margin=dict(l=5,r=5,t=12,b=5),plot_bgcolor='white',paper_bgcolor='white',
                      font=dict(size=12,color='#525252'),legend=dict(orientation='h',title=None,y=1.15))
    fig.update_yaxes(gridcolor='#ededed',title=label);fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig,width='stretch')

if section=='Visão geral':
    st.caption('MONITORAMENTO · CULTIVO · AÇÕES')
    st.title('A fazenda, em uma visão.')
    st.write('Acompanhe os talhões e confira as ocorrências que precisam de atenção.')
    if not plots:
        st.info('Comece cadastrando seus talhões ou abra o cenário demonstrativo.')
        if st.button('Carregar cenário demonstrativo',type='primary'):
            telemetria.seed_demo();st.rerun()
    else:
        readings=pd.DataFrame(telemetria.readings())
        open_alerts=[a for a in all_alerts if a['estado']=='aberto']
        k1,k2,k3,k4=st.columns(4)
        k1.metric('Área cadastrada',f"{sum(p['area_m2'] for p in plots)/10000:.1f} ha")
        k2.metric('Talhões ativos',len(plots))
        k3.metric('Leituras registradas',len(readings))
        k4.metric('Ocorrências abertas',len(open_alerts))
        st.caption('Cenário demonstrativo: as leituras marcadas como “simulado” não vieram de sensores físicos.')
        left,right=st.columns([2,1],gap='large')
        with left:
            st.subheader('Umidade do solo')
            if not readings.empty:
                readings['observado_em']=pd.to_datetime(readings['observado_em'],utc=True)
                chart(readings,'observado_em','umidade_solo','Umidade do solo (%)','talhao')
                st.caption('Indicador de solo separado da umidade do ar. Faixa de alerta demonstrativa: abaixo de 30%.')
            else:st.info('Ainda não há leituras. Registre uma medição em “Sensores e IoT”.')
        with right:
            st.subheader('Próximas ações')
            if not open_alerts:st.success('Nenhuma ocorrência aberta.')
            for a in open_alerts[:3]:
                with st.container(border=True):
                    st.caption(a['talhao'] or 'Monitoramento visual')
                    st.markdown('**'+a['titulo']+'**');st.write(a['acao'])
                    st.caption('Notificação: '+a['notificacao'])
        st.subheader('Talhões em acompanhamento')
        if not readings.empty:
            latest=readings.sort_values(['observado_em','id']).groupby('talhao_id').tail(1)
            summary=pd.DataFrame(plots).merge(latest[['talhao_id','umidade_solo','umidade_ar','origem','observado_em']],left_on='id',right_on='talhao_id',how='left')
            st.dataframe(summary[['nome','cultura','area_m2','umidade_solo','umidade_ar','origem','observado_em']],hide_index=True,width='stretch')
        else:st.dataframe(pd.DataFrame(plots)[['nome','cultura','area_m2']],hide_index=True,width='stretch')

elif section=='Talhões e manejo':
    st.caption('FASES 1 E 2 · CADASTRO E PERSISTÊNCIA')
    st.title('Talhões e manejo')
    st.write('Calcule a área de plantio, organize culturas e registre as operações realizadas.')
    calc,manage,ops,weather=st.tabs(['Calcular e cadastrar','Gerenciar talhões','Operações','Meteorologia'])
    with calc:
        with st.form('plot_create'):
            name=st.text_input('Nome do talhão',max_chars=80)
            culture=st.selectbox('Cultura',[1,2],format_func=lambda v:{1:'Café',2:'Cana-de-açúcar'}[v])
            shape=st.selectbox('Formato',['retangulo','trapezio'],format_func=lambda v:{'retangulo':'Retângulo','trapezio':'Trapézio'}[v])
            c1,c2,c3=st.columns(3)
            base=c1.number_input('Comprimento ou base maior (m)',min_value=.1,value=400.)
            height=c2.number_input('Largura ou altura (m)',min_value=.1,value=200.)
            small=c3.number_input('Base menor, para trapézio (m)',min_value=.1,value=300.)
            dose=st.number_input('Dose de referência informada (L/ha)',min_value=0.,value=2.)
            st.caption('A dose é definida pelo operador. O sistema calcula o volume e não prescreve o produto.')
            submit=st.form_submit_button('Calcular e salvar talhão',type='primary')
        if submit:
            try:
                result=manejo.calculate(shape,base,height,small,dose)
                manejo.save_plot(name,culture,result['area_m2'],dose)
                st.success(f"Talhão salvo: {result['area_ha']:.2f} ha · volume de referência {result['insumo_l']:.2f} L.")
            except (ValueError,sqlite3.IntegrityError) as exc:failure(exc)
        with st.expander('Cálculo por ruas de café, da Fase 1'):
            a,b,c=st.columns(3);ml=a.number_input('Dose (mL/m)',min_value=0.,value=10.);length=b.number_input('Comprimento da rua (m)',min_value=.1,value=100.);rows=c.number_input('Número de ruas',min_value=1,value=20)
            st.metric('Volume calculado',f'{manejo.coffee_input(ml,length,rows):.2f} L')
    with manage:
        table=pd.DataFrame(db.talhoes(active=False))
        if not table.empty:st.dataframe(table[['id','nome','cultura','area_m2','dose_l_ha','ativo']],hide_index=True,width='stretch')
        selected=plot_picker('edit_plot')
        if selected:
            current=next(p for p in plots if p['id']==selected)
            with st.form('edit_form'):
                new_name=st.text_input('Nome atualizado',value=current['nome'])
                new_area=st.number_input('Área atualizada (m²)',min_value=.1,value=float(current['area_m2']))
                new_dose=st.number_input('Dose atualizada (L/ha)',min_value=0.,value=float(current['dose_l_ha']))
                saved=st.form_submit_button('Salvar alterações')
            if saved:
                try:manejo.save_plot(new_name,current['cultura_id'],new_area,new_dose,selected);st.success('Talhão atualizado.');st.rerun()
                except (ValueError,sqlite3.IntegrityError) as exc:failure(exc)
            if st.button('Arquivar talhão',key='archive_plot'):
                manejo.archive_plot(selected);st.rerun()
            st.caption('Arquivar preserva o histórico e impede novas leituras nesse talhão.')
    with ops:
        selected=plot_picker('operation_plot')
        if selected:
            with st.form('operation'):
                kind=st.selectbox('Operação',['irrigacao','insumo'])
                liters=st.number_input('Volume realizado (L)',min_value=0.,value=100.)
                note=st.text_input('Descrição da operação',max_chars=300)
                record=st.form_submit_button('Registrar operação')
            if record:
                try:manejo.register_operation(selected,kind,liters,note);st.success('Operação registrada.')
                except ValueError as exc:failure(exc)
            st.dataframe(pd.DataFrame(db.query('SELECT * FROM operacao WHERE talhao_id=? ORDER BY id DESC',(selected,))),hide_index=True,width='stretch')
    with weather:
        st.subheader('Previsão de 7 dias · Open-Meteo')
        st.caption('Local demonstrativo: Ribeirão Preto. Previsão modelada, separada das medições locais.')
        a,b=st.columns(2);lat=a.number_input('Latitude',min_value=-90.,max_value=90.,value=-21.17);lon=b.number_input('Longitude',min_value=-180.,max_value=180.,value=-47.81)
        if st.button('Consultar previsão'):
            from farmtech.clima import forecast
            try:
                with st.spinner('Consultando Open-Meteo…'):result=forecast(lat,lon)
                st.session_state['weather']=result
            except (requests.RequestException,ValueError,KeyError):st.error('A previsão não está disponível agora. Tente novamente; nenhuma medição local foi alterada.')
        if 'weather' in st.session_state:
            result=st.session_state['weather'];st.dataframe(pd.DataFrame(result['daily']),hide_index=True,width='stretch');st.caption('Consulta: '+result['_proveniencia']['consultado_em'])
        st.link_button('Fonte e unidades · Open-Meteo','https://open-meteo.com/en/docs')

elif section=='Sensores e IoT':
    st.caption('FASE 3 · COLETA, VALIDAÇÃO E REGRAS')
    st.title('Sensores e IoT')
    selected=plot_picker('sensor_plot')
    if selected:
        history,manual,import_tab=st.tabs(['Histórico','Nova leitura','Importar lote'])
        with history:
            frame=pd.DataFrame(telemetria.readings(plot_id=selected))
            if frame.empty:st.info('Sem leituras para este talhão.')
            else:
                frame['observado_em']=pd.to_datetime(frame['observado_em'],utc=True)
                a,b=st.columns(2)
                with a:st.subheader('Umidade do solo');chart(frame,'observado_em','umidade_solo','Umidade do solo (%)')
                with b:st.subheader('Umidade do ar');chart(frame,'observado_em','umidade_ar','Umidade do ar (%)')
                st.dataframe(frame,hide_index=True,width='stretch')
                st.download_button('Exportar leituras CSV',frame.to_csv(index=False).encode(),'leituras.csv','text/csv')
        with manual:
            with st.form('reading'):
                sensor=st.text_input('Identificação do sensor',value='manual-01')
                a,b,c=st.columns(3)
                soil=a.number_input('Umidade do solo (%)',min_value=0.,max_value=100.,value=24.5)
                air=b.number_input('Umidade do ar (%)',min_value=0.,max_value=100.,value=65.)
                temp=c.number_input('Temperatura (°C)',min_value=-40.,max_value=85.,value=29.)
                ph=st.number_input('pH simulado',min_value=0.,max_value=14.,value=6.3)
                p=st.checkbox('Indicador de fósforo presente',value=True);k=st.checkbox('Indicador de potássio presente',value=True)
                st.caption('Leitura manual de demonstração. O LDR não mede pH; a interface conserva essa distinção.')
                save=st.form_submit_button('Registrar leitura e avaliar regras',type='primary')
            if save:
                try:
                    result=telemetria.ingest_many([{'sensor_id':sensor,'evento_id':uuid.uuid4().hex,'observado_em':db.now(),'umidade_solo':soil,'umidade_ar':air,'temperatura':temp,'ph':ph,'ph_simulado':True,'fosforo':int(p),'potassio':int(k),'origem':'manual'}],selected)
                    st.success(f"Leitura salva · {result['alertas']} alerta(s) na fila. Nenhuma mensagem externa foi enviada.")
                except (ValueError,sqlite3.IntegrityError) as exc:failure(exc)
        with import_tab:
            st.write('Importe JSON, JSON Lines ou CSV. O lote é validado integralmente antes de ser gravado.')
            upload=st.file_uploader('Arquivo de leituras',type=['json','jsonl','csv'])
            if st.button('Validar e importar',disabled=upload is None):
                try:
                    raw=upload.getvalue().decode('utf-8-sig')
                    if upload.name.endswith('.csv'):
                        table=pd.read_csv(io.StringIO(raw));payload=table.astype(object).where(pd.notna(table),None).to_dict('records')
                    elif upload.name.endswith('.jsonl'):payload=[json.loads(s) for s in raw.splitlines() if s.strip()]
                    else:
                        payload=json.loads(raw);payload=payload if isinstance(payload,list) else [payload]
                    result=telemetria.ingest_many(payload,selected);st.success(f"Importação concluída: {result}")
                except (ValueError,UnicodeError,sqlite3.IntegrityError,TypeError) as exc:failure(exc)
            with st.expander('Conectar ESP32 por USB'):
                st.code('python scripts/serial_bridge.py --port /dev/ttyUSB0 --talhao 1',language='bash')
                st.write('Firmware em iot/. O DHT22 fornece umidade do ar e temperatura; o pH do LDR é simulado. A umidade do solo permanece ausente até existir sensor próprio calibrado.')

elif section=='Análise e previsão':
    st.caption('FASES 4 E 5 · MODELOS E AVALIAÇÃO')
    st.title('Análise e previsão')
    st.write('Compare modelos de rendimento e explore os cenários climáticos da base da Fase 5.')
    if not analise.REPORT_FILE.exists():
        st.info('O treinamento ainda não foi executado nesta cópia.')
        if st.button('Treinar modelos',type='primary'):
            with st.spinner('Treinando e validando por cenário climático…'):analise.train()
            st.rerun()
    else:
        report=json.loads(analise.REPORT_FILE.read_text());selected=next(x for x in report['metrics'] if x['modelo']==report['selected_model'])
        a,b,c=st.columns(3);a.metric('Modelo selecionado',report['selected_model']);b.metric('MAE no teste',f"{selected['teste_mae']:.1f}");c.metric('R² no teste',f"{selected['teste_r2']:.3f}")
        st.caption('Seleção por validação cruzada apenas no treino. Teste separado por cenário climático, sem grupos em comum.')
        prediction,metrics,profiles=st.tabs(['Simular rendimento','Métricas e correlações','Perfis climáticos'])
        df=analise.dataset()
        with prediction:
            st.warning('Yield e precipitação conservam a escala original do CSV, com unidades ainda não confirmadas. Não converter o resultado em toneladas, doses ou decisões de irrigação.')
            with st.form('predict'):
                crop=st.selectbox('Cultura da base',sorted(df['Crop'].unique()))
                inputs=[]
                for name in analise.NUMERIC:
                    inputs.append(st.number_input(name,value=float(df[name].median()),format='%.2f'))
                run=st.form_submit_button('Estimar rendimento',type='primary')
            if run:
                try:
                    result=analise.predict(crop,inputs);st.metric('Estimativa · escala original de Yield',f"{result['estimativa']:.1f}")
                    if result['fora_da_faixa']:st.warning('Extrapolação: '+', '.join(result['fora_da_faixa']))
                except ValueError as exc:failure(exc)
        with metrics:
            st.dataframe(pd.DataFrame(report['metrics']),hide_index=True,width='stretch')
            corr=df[analise.NUMERIC+['Yield']].corr()
            fig=px.imshow(corr,text_auto='.2f',zmin=-1,zmax=1,color_continuous_scale='RdBu_r',aspect='auto')
            fig.update_layout(height=480,margin=dict(l=0,r=0,t=10,b=0));st.plotly_chart(fig,width='stretch')
            st.caption('Correlação não implica causalidade. O R² agregado também reflete as diferentes escalas entre culturas. O teste tem '+str(report['test_rows'])+' linhas; confira o erro por cultura e a baseline de média por cultura.')
            st.dataframe(pd.DataFrame(report.get('test_metrics_by_crop',[])),hide_index=True,width='stretch')
        with profiles:
            frame=pd.read_csv(ROOT/'results/perfis_climaticos.csv');st.dataframe(frame,hide_index=True,width='stretch')
            st.caption('K-Means com 3 perfis e Isolation Forest nos 39 cenários únicos. Perfis descritivos; outlier não é erro confirmado.')

elif section=='Visão computacional':
    st.caption('FASE 6 · DETECÇÃO COM YOLO')
    st.title('Visão computacional')
    st.write('Processe uma fotografia com o modelo treinado na Fase 6 e registre o resultado no histórico.')
    st.info('O modelo reconhece gatos e carros. Não detecta pragas, doenças ou qualidade da lavoura.')
    model_key=st.selectbox('Modelo',['yolo60','yolo30','yolo_padrao','cnn'],format_func=lambda k:{'yolo60':'YOLO customizado · 60 épocas','yolo30':'YOLO customizado · 30 épocas','yolo_padrao':'YOLO padrão · COCO','cnn':'CNN · classificação da imagem inteira'}[k])
    file=st.file_uploader('Fotografia JPG ou PNG',type=['jpg','jpeg','png'])
    samples=sorted((ROOT/'data/imagens').glob('*.jpg'))
    choice=st.selectbox('Ou use uma imagem de demonstração',[None]+samples,format_func=lambda p:'Selecionar imagem' if p is None else p.name)
    if st.button('Processar imagem',type='primary',disabled=file is None and choice is None):
        from farmtech.visao import detect
        try:
            with st.spinner('Executando YOLOv5n…'):
                result,rendered=detect(file.getvalue() if file else choice.read_bytes(),file.name if file else choice.name,model_key=model_key)
            st.session_state['vision_result']=(result,rendered)
        except (ValueError,ImportError,RuntimeError,OSError) as exc:failure(exc)
    if 'vision_result' in st.session_state:
        result,rendered=st.session_state['vision_result']
        if 'classificacao' in result:
            st.image(rendered,caption='Imagem classificada integralmente pela CNN',width='stretch')
            st.metric('Classe estimada',result['classificacao']['classe'])
            st.caption(result['classificacao']['nota'])
        else:
            st.image(rendered,caption='Caixas geradas nesta execução',width='stretch')
            st.caption(f"{len(result['deteccoes'])} detecção(ões) · {result['tempo_ms']:.0f} ms · registro {result['execucao_id']}")
            if result['deteccoes']:st.dataframe(pd.DataFrame(result['deteccoes']),hide_index=True,width='stretch')
            else:st.write('Nenhum objeto das classes conhecidas superou o limiar de confiança de 0,25.')
    with st.expander('Comparação registrada na Fase 6'):
        st.dataframe(pd.read_csv(ROOT/'results/comparacao_fase6.csv'),hide_index=True,width='stretch')
        st.caption('Resultados do protocolo original da Fase 6, com 8 imagens de teste e execução em GPU. Os tempos desta tela usam CPU e não são diretamente comparáveis. O teste pequeno não comprova superioridade robusta.')
    with st.expander('Histórico de inferências'):
        st.dataframe(pd.DataFrame(db.query('SELECT id,criado_em,arquivo,modelo,tempo_ms FROM visao ORDER BY id DESC LIMIT 30')),hide_index=True,width='stretch')

elif section=='Alertas e AWS':
    st.caption('FASE 5 · MENSAGERIA DA FASE 7')
    st.title('Alertas e ações')
    st.write('Confira a ocorrência, a ação sugerida e o estado real de cada notificação.')
    arn=os.getenv('FARMTECH_SNS_TOPIC_ARN','')
    st.caption('Canal AWS SNS configurado.' if arn else 'Canal AWS ainda não configurado. As ocorrências ficam na fila local.')
    if not all_alerts:st.success('Nenhum alerta registrado.')
    else:
        status=st.selectbox('Exibir ocorrências',['Abertas','Todas'])
        filtered=[a for a in all_alerts if status=='Todas' or a['estado']=='aberto']
        if not filtered:st.info('Nenhuma ocorrência corresponde ao filtro.')
        else:
            labels={a['id']:f"#{a['id']} · {a['titulo']} · {a['talhao'] or 'Imagem'}" for a in filtered}
            selected_id=st.selectbox('Ocorrência',list(labels),format_func=labels.get)
            item=next(a for a in filtered if a['id']==selected_id)
            with st.container(border=True):
                st.subheader(item['titulo']);st.write(item['acao'])
                st.caption(f"Origem: {item['origem'] or 'inferência visual'} · estado: {item['estado']} · notificação: {item['notificacao']}")
                if item['message_id']:st.code('SNS MessageId: '+item['message_id'])
                if item['erro']:st.error('Última tentativa: '+item['erro'])
                st.caption('As faixas são demonstrativas. Confirme a leitura antes de intervir no cultivo.')
                a,b=st.columns(2)
                if a.button('Enviar notificação pela AWS',type='primary',disabled=not arn or item['estado']!='aberto' or item['notificacao'] not in ('pendente','falha')):
                    try:alertas.dispatch(item['notificacao_id']);st.success('Mensagem aceita pelo SNS. A chegada ao e-mail depende da assinatura confirmada.');st.rerun()
                    except (ValueError,RuntimeError) as exc:failure(exc)
                if b.button('Marcar ocorrência como resolvida',disabled=item['estado']=='resolvido'):
                    alertas.resolve(item['id']);st.rerun()
            st.dataframe(pd.DataFrame(filtered)[['id','titulo','talhao','origem','estado','notificacao','tentativas','criado_em']],hide_index=True,width='stretch')
        st.caption('“Aceito pelo SNS” registra o retorno da AWS; não comprova recebimento ou leitura do e-mail. Envio com resultado incerto fica retido para evitar duplicação automática.')

else:
    st.title('Um projeto, seis fases integradas.')
    st.write('Gabriel Marcolino Ramos · RM565717 · rm565717@fiap.com.br · Grupo 17')
    st.write('Fase 7 — A consolidação de um sistema. Prazo: 10/11/2026 às 23h59.')
    st.dataframe(pd.DataFrame([
        ['1','Áreas, insumos e meteorologia','Talhões e manejo'],['2','Banco relacional e integridade','Cadastro e histórico'],
        ['3','Leituras, importação e ponte ESP32','Sensores e IoT'],['4','Painel, correlações e estimativas','Análise e previsão'],
        ['5','Modelagem e serviço de mensagens AWS','Análise e alertas'],['6','Checkpoint YOLO e inferência','Visão computacional']
    ],columns=['Fase','Serviço','Onde encontrar']),hide_index=True,width='stretch')
    st.markdown('**Limites atuais:** dados de sensores demonstrativos; hardware físico não validado nesta integração; classes visuais restritas a gatos e carros; unidade de rendimento não confirmada. A implantação AWS e a comprovação de e-mail serão registradas após validação real.')
    with st.expander('Modelo do banco e execução por terminal'):
        st.code((ROOT/'sql/schema.sql').read_text(),language='sql')
        st.code('python -m farmtech demo\npython -m farmtech talhoes\npython -m farmtech treinar\npython -m farmtech alertas',language='bash')
