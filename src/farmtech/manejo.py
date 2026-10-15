import math
from .db import connection, now

def number(value, name, minimum=0, maximum=None, strictly_positive=False):
    if isinstance(value, bool):
        raise ValueError(f'{name}: informe um número.')
    try:
        value=float(value)
    except (ValueError, TypeError):
        raise ValueError(f'{name}: informe um número válido.') from None
    if not math.isfinite(value) or value < minimum or (maximum is not None and value > maximum) or (strictly_positive and value <= 0):
        raise ValueError(f'{name}: valor fora do intervalo permitido.')
    return value

def calculate(shape, base, height, smaller_base=None, dose_l_ha=0):
    base=number(base,'Base',strictly_positive=True)
    height=number(height,'Altura',strictly_positive=True)
    dose=number(dose_l_ha,'Dose')
    if shape=='retangulo':
        area=base*height
    elif shape=='trapezio':
        small=number(smaller_base,'Base menor',strictly_positive=True)
        if small>base:raise ValueError('A base menor não pode superar a base maior.')
        area=(base+small)*height/2
    else:
        raise ValueError('Formato desconhecido.')
    return {'area_m2':area,'area_ha':area/10000,'insumo_l':area/10000*dose}

def coffee_input(ml_per_meter, row_length, rows):
    dose=number(ml_per_meter,'Dose em mL/m');length=number(row_length,'Comprimento',strictly_positive=True)
    rows=number(rows,'Número de ruas',strictly_positive=True)
    if not rows.is_integer():raise ValueError('Número de ruas deve ser inteiro.')
    return dose*length*rows/1000

def save_plot(name, culture_id, area_m2, dose_l_ha, plot_id=None, path=None):
    name=str(name).strip()
    if not name or len(name)>80:raise ValueError('Nome deve ter de 1 a 80 caracteres.')
    area=number(area_m2,'Área',strictly_positive=True);dose=number(dose_l_ha,'Dose')
    with connection(path) as conn:
        if plot_id is None:
            cur=conn.execute('INSERT INTO talhao(nome,cultura_id,area_m2,dose_l_ha,criado_em) VALUES (?,?,?,?,?)',
                             (name,culture_id,area,dose,now()))
            return cur.lastrowid
        cur=conn.execute('UPDATE talhao SET nome=?, cultura_id=?, area_m2=?, dose_l_ha=? WHERE id=? AND ativo=1',
                         (name,culture_id,area,dose,plot_id))
        if not cur.rowcount:raise ValueError('Talhão não encontrado ou arquivado.')
        return plot_id

def archive_plot(plot_id,path=None):
    with connection(path) as conn:
        if not conn.execute('UPDATE talhao SET ativo=0 WHERE id=? AND ativo=1',(plot_id,)).rowcount:
            raise ValueError('Talhão não encontrado ou já arquivado.')

def register_operation(plot_id, kind, liters, note, path=None):
    if kind not in ('irrigacao','insumo'):raise ValueError('Operação desconhecida.')
    volume=number(liters,'Volume');note=str(note).strip()
    if not note:raise ValueError('Descreva a operação.')
    with connection(path) as conn:
        if not conn.execute('SELECT 1 FROM talhao WHERE id=? AND ativo=1',(plot_id,)).fetchone():
            raise ValueError('Talhão indisponível.')
        return conn.execute('INSERT INTO operacao(talhao_id,criado_em,tipo,volume_l,observacao) VALUES (?,?,?,?,?)',
                            (plot_id,now(),kind,volume,note)).lastrowid
