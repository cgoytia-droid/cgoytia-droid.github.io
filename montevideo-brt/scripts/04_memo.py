"""Genera la nota técnica en Word (Calibri 11, títulos en negrita, tablas sin relleno)."""
import sys, pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
R = sys.argv[1]  # carpeta montevideo-brt
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11); st.font.color.rgb = RGBColor(0, 0, 0)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
for s in doc.sections: s.left_margin = s.right_margin = Cm(2.3)

def H(t, lvl=1):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(14 if lvl == 0 else 12 if lvl == 1 else 11)
    p.paragraph_format.space_before = Pt(12 if lvl < 2 else 6); p.paragraph_format.keep_with_next = True
def P(t, b=None):
    p = doc.add_paragraph(style='List Bullet' if b else None)
    # negrita con **...**
    parts = t.split('**')
    for i, x in enumerate(parts):
        r = p.add_run(x); r.bold = i % 2 == 1
    p.paragraph_format.space_after = Pt(6); return p
def borders(tbl):
    tblPr = tbl._tbl.tblPr; b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{e}'); el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), '4'); el.set(qn('w:color'), '000000'); b.append(el)
    tblPr.append(b)
def T(rows, header, widths=None, size=9):
    t = doc.add_table(rows=1, cols=len(header)); borders(t)
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size)
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ''; r = cs[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph()
def F(img, w=16):
    doc.add_picture(f'{R}/figuras/{img}', width=Cm(w))
def fmt(x, d=1): return f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

t1 = pd.read_csv(f'{R}/tablas/t1_depto_banda.csv')
t2 = pd.read_csv(f'{R}/tablas/t2_tramo.csv')
t5 = pd.read_csv(f'{R}/tablas/t5_anv_banda.csv')
t7 = pd.read_csv(f'{R}/tablas/t7_participaciones_mvd.csv')

H('BRT Área Metropolitana de Montevideo. Material DINOT del 30/09/2026: uso propuesto, mapas de vacancia y análisis de instrumentos de retorno de valorizaciones', 0)
P('Nota técnica de trabajo. Borrador para discusión interna, 01/10/2026.')

H('1. Síntesis')
P('**Qué llegó.** Cuatro insumos nuevos: (i) una capa de ocupación de la vivienda por segmento censal 2023 (1.734 segmentos urbanos de Montevideo, Canelones y San José) con desocupación desagregada por motivo; (ii) un documento metodológico con gráficos y tablas por localidad; (iii) la capa de vivienda promovida de ANV con corte al 31/08/2026 (1.632 proyectos, 45.773 unidades); (iv) una matriz normativa de retorno de valorizaciones (RV) y mayores aprovechamientos (MA) en los instrumentos de ordenamiento territorial departamentales aprobados entre 2008 y 2025, con su nota de método.')
P('**Hallazgo de vacancia.** En Montevideo, la desocupación no estacional dentro de 400 m de una estación BRT es 10,1 % del stock, contra 7,7 % a más de 800 m. La diferencia entre el entorno de 800 m y el resto es 1,8 puntos porcentuales (IC 95 % por remuestreo de segmentos: 1,2 a 2,5). Casi toda la diferencia proviene de viviendas en alquiler o venta (4,4 % contra 2,9 %) y se concentra en el tramo troncal (18 de Julio). La vacancia estructural (vacante más ruinosa o tapiada) no difiere: 0,1 puntos (IC 95 %: -0,1 a 0,4).')
P('**Magnitud.** Dentro de 800 m de las estaciones de Montevideo hay 165.875 viviendas, 15.844 desocupadas no estacionales y 4.336 vacantes o degradadas. Ese último número es el universo relevante para instrumentos de activación, no los casi 16.000.')
P('**Hallazgo de instrumentos.** Canelones tiene RV y MA operativos en 12 de sus 19 instrumentos relevados, con una fórmula homogeneizada por el decreto general 002/022 (verificar año y número completo). Montevideo no incluye RV ni MA en ninguno de sus siete planes 2009-2015 relevados y opera con una reglamentación general (Res. 1709/2024). San José los prevé solo en Kiyú. El diseño montevideano cobra cuando un proyecto supera la norma vigente; el canario cobra sobre todo lo que excede un aprovechamiento básico fijo. Para capturar parte de la valorización asociada al BRT, esa diferencia de diseño pesa más que las alícuotas.')
P('**Vivienda promovida.** El 49 % de las unidades promovidas por ANV en Montevideo está a menos de 400 m de una estación BRT, donde se ubica el 14 % del stock de vivienda. El régimen de exoneraciones ya opera como instrumento de densificación del corredor, en especial del tramo central.')

H('2. Qué es cada insumo y cómo usarlo')
T([
    ['Ocupación de la vivienda 2023 (shp, DINOT)', '1.734 segmentos censales urbanos. Viviendas totales, desocupadas no temporada, temporada, degradadas, y desocupadas por motivo (alquiler o venta, construcción o reparación, vacante, ignorado).',
     'Línea de base ex ante de vacancia por banda de distancia al BRT. Separar vacancia friccional de estructural. Seleccionar sectores piloto para instrumentos de activación.'],
    ['Gráficos y tablas Viviendas 2023 (docx)', 'Método de agregación a localidad, departamento y AMET; totales de control (Montevideo 576.477 viviendas en localidades; AMET 914.343).',
     'Cuadro de control de totales. Citar como fuente metodológica de la capa.'],
    ['Vivienda promovida ANV, corte 31/08/2026 (shp)', '1.632 proyectos con padrón, tipo (obra nueva, reciclaje), unidades, fecha de promoción, barrio, zona y coordenadas.',
     'Medir dónde se concentra la inversión residencial subsidiada respecto del corredor. Base para estimar costo fiscal por unidad si ANV o DGI aportan montos exonerados.'],
    ['Matriz RV y MA (xlsx y nota, docx)', 'Artículo por artículo de los IOT departamentales 2008-2025 de Canelones, Montevideo y San José, con texto transcripto.',
     'Tipología de instrumentos, comparación de bases de cálculo y disparadores, y detección de vacíos sobre el corredor (sección 4).'],
    ['DINOT 2 + 3009 (docx)', 'Guion de pedidos a DINOT y a otras direcciones del MVOT.', 'Agenda de la próxima reunión; se complementa con los pedidos de la sección 5.'],
], ['Insumo', 'Contenido', 'Uso propuesto'], [4, 6.5, 6])

P('**Control de calidad realizado.** La capa de ocupación se leyó registro a registro. Se verificó que, en los 1.734 segmentos, las desocupadas no temporada igualan exactamente la suma de alquiler o venta, construcción o reparación, vacante, ignorado y degradada. Los totales por departamento coinciden con los del documento metodológico para Montevideo (576.477) y Canelones (253.981); San José difiere en 20 viviendas (45.830 contra 45.810), lo que debería aclararse con DINOT. Contra la base censal usada antes en el proyecto (vacancia_centro_segmentos_1509.csv), las categorías coinciden y los totales difieren entre 0,1 % y 2 % por segmento; conviene preguntar a DINOT qué universo de viviendas usa TotViv.')

H('3. Vacancia en el entorno del BRT')
H('3.1 Definiciones', 2)
P('**Desocupación no estacional:** viviendas desocupadas que no son de temporada, sobre el total de viviendas del segmento. **Vacancia friccional:** desocupadas para alquiler o venta; refleja rotación de mercado y aumenta, en parte, con la liquidez del submercado. **Vacancia estructural:** vacantes más ruinosas o tapiadas; es el stock que no circula y el blanco natural de instrumentos de activación (impuesto progresivo al baldío y a la edificación inapropiada, declaración de inmueble abandonado, cartera de tierras). Las bandas de 0-400 m, 400-800 m y más de 800 m se miden desde el centroide de cada segmento a la estación más cercana de la red corregida 2025 (83 estaciones, líneas A y B).')

H('3.2 Resultados', 2)
rows = []
for _, r in t1.iterrows():
    rows.append([r.NOMDEPTO.title(), r.banda, f"{int(r.Viviendas):,}".replace(',', '.'), fmt(r['% desocupadas']), fmt(r['% no temporada']), fmt(r['% Alquiler o venta']), fmt(r['% estructural']), fmt(r['% Temporada'])])
T(rows, ['Depto.', 'Banda', 'Viviendas', '% desocup. total', '% no temporada', '% alquiler o venta', '% estructural', '% temporada'], [2.3, 2, 2, 2, 2, 2, 2, 2], 8.5)
P('Fuente: elaboración propia con DINOT-MVOT, ocupación de la vivienda por segmento censal 2023. Tasas ponderadas por viviendas (suma de desocupadas sobre suma de viviendas). San José no se incluye por falta de centroides de segmento en la base del proyecto.').runs[0].font.size = Pt(9)
F('G1_composicion_banda_MVD.png')
P('La lectura descriptiva tiene tres partes. Primero, en Montevideo la desocupación crece hacia las estaciones, pero el gradiente es friccional: alquiler o venta pasa de 2,9 % a 4,4 % entre la banda exterior y la interior, mientras vacante y degradada se mantienen cerca de 2,5 %. Segundo, el exceso está en el tramo troncal: allí la desocupación no estacional es 11,3 %, contra 8,5 % en los entornos de las líneas fuera del troncal y 8,4 % fuera de los entornos (tabla de tramos en tablas/t2_tramo.csv). Tercero, en Canelones el patrón se invierte: el corredor (Giannattasio) tiene menos desocupación que el resto del departamento porque la vivienda de temporada se concentra en la Costa de Oro, fuera de los entornos (mapa 5).')
P('**Qué sostiene y qué no sostiene esto.** Son diferencias descriptivas sobre un BRT que todavía no existe; no miden efecto alguno del BRT. La objeción más fuerte es que la distancia a las estaciones es un indicador de centralidad: el troncal recorre el área central, con más vivienda pequeña, más alquiler y más rotación. Los datos son consistentes con esa lectura, porque el exceso desaparece casi por completo fuera del troncal (8,5 % contra 7,7 %). La implicancia práctica no depende de la interpretación causal: el stock friccional del centro no requiere instrumentos de activación sino fluidez de mercado, y el stock estructural del corredor es acotado (4.336 unidades en Montevideo).')
P('El intervalo de confianza se obtuvo remuestreando segmentos con reposición (2.000 réplicas). El censo es un conteo completo, así que el intervalo describe la variabilidad entre segmentos, no un error muestral. Entre segmentos de más de 50 viviendas, la desocupación no estacional en la banda de 0-400 m de Montevideo tiene mediana 9,3 % y rango intercuartil 7,2 % a 12,3 %, con lo cual un promedio de banda oculta mucha heterogeneidad local.')

H('3.3 Mapas', 2)
for f, w in [('M1_desocupacion_no_temporada_AMM.png', 16), ('M2_vacancia_estructural_corredor.png', 16), ('M3_vacancia_friccional_corredor.png', 16), ('M5_temporada_costa.png', 16)]:
    F(f, w)
P('Lectura de los mapas. El mapa 2 es el que sirve para seleccionar sectores: muestra conteos, no tasas, y ubica los segmentos con más de 40 viviendas vacantes o degradadas en Ciudad Vieja, Centro, Cordón y el primer tramo de 8 de Octubre. El mapa 3 muestra que la vacancia friccional se concentra en el área central y en la costa sur, fuera de las líneas periféricas. Los mapas usan centroides de segmento porque el entorno de procesamiento no pudo leer la geometría poligonal del shapefile; en QGIS la misma tabla se une a los polígonos por CODSEG (los scripts quedan en la carpeta montevideo-brt/scripts).')

H('3.4 Vivienda promovida (ANV)', 2)
rows = [[r.NOMDEPTO.title(), r.banda, int(r.proyectos), f"{int(r.viviendas):,}".replace(',', '.')] for _, r in t5.iterrows()]
T(rows, ['Depto.', 'Banda', 'Proyectos', 'Unidades promovidas'], [3, 3, 3, 4])
rows = [[r.banda, fmt(r['% stock viviendas 2023']), fmt(r['% vacancia estructural']), fmt(r['% vivienda promovida ANV'])] for _, r in t7.iterrows()]
T(rows, ['Banda (Montevideo)', '% del stock 2023', '% de la vacancia estructural', '% de unidades promovidas'], [4, 4, 4, 4])
F('M4_vivienda_promovida_ANV.png')
P('Tres de cada cuatro unidades promovidas en Montevideo (76 %) están a menos de 800 m de una estación, contra 29 % del stock. La proporción es estable entre 2011-2020 (73 %) y 2021-2026 (74 %), considerando ambos departamentos. La vivienda promovida no se dirige especialmente a la vacancia estructural, que se distribuye como el stock. El régimen (Ley 18.795, verificar cita) ya densifica el corredor central con una transferencia fiscal; el cobro de MA sobre esos mismos proyectos, si corresponde, compensaría parte de esa transferencia. Falta conocer el monto exonerado por proyecto para cuantificarlo, y falta el significado de los códigos de zona (C01 a C04, INT), que deben confirmarse con ANV.')

H('4. Análisis de los instrumentos de retorno de valorizaciones y mayor aprovechamiento')
H('4.1 Universo relevado', 2)
T([
    ['Canelones', '19 instrumentos + decreto general 002/022', '12 (Microrregiones 6-8 y 7, Costaplan y su revisión, Costa de Oro, Ruta 5, Nicolich, PAI Huertos, ACRES, Olivos, SERE, Zona Franca Parque de las Ciencias)', '7 (Jaureguiberry, Ruralidades, Directrices departamentales, La Paz-Las Piedras-Progreso, Parque Roosevelt, revisión Ruta 5, áreas de protección ambiental)'],
    ['Montevideo', '7 planes + PAI Melilla Oeste + Res. 1709/2024', 'Res. 1709/2024 (reglamentación general); Melilla Oeste solo con equidistribución de cargas y beneficios', '7 planes 2009-2015 (Bella Vista-Capurro-La Teja, Carrasco-Punta Gorda, Directrices, Goes, UAM, Casavalle, Prado-Capurro)'],
    ['San José', '4', '1 (Kiyú: 5 % de la edificabilidad en suelo potencialmente transformable)', '3 (San José de Mayo, Directrices, Ciudad del Plata)'],
], ['Depto.', 'Instrumentos', 'Con RV o MA', 'Sin RV ni MA'], [2.3, 3.5, 6, 5])
P('Fuente: elaboración propia sobre la matriz RV y MA entregada (SIT-MVOT, IOT 2008-2025). Los conteos son de instrumentos con articulado propio; los decretos modificativos se cuentan con el instrumento que modifican.').runs[0].font.size = Pt(9)

H('4.2 Cómo funciona cada régimen', 2)
T([
    ['Hecho generador', 'Cambio de categoría, cambio de uso, reparcelamiento (RV); edificación por encima de un básico fijo de 8,50 m y FOT 120 % (MA)', 'Transformación de suelo y cambio de categoría (RV); superación del aprovechamiento de la normativa vigente, con o sin mayor edificabilidad, y mayor intensidad de uso en rural y suburbano (MA)'],
    ['Base y alícuota RV', 'Hasta 2020 (Costaplan 2010): 20 % de la valorización neta (valor después menos valor antes menos inversión en infraestructura). Desde la revisión 001/2020 y el decreto 002/022: 5 % × área × FOT básico × valor venal del suelo transformado', '5 % del valor final del suelo transformado neto'],
    ['Base y alícuota MA', 'm² sobre la altura básica ÷ FOT básico × valor del m² de suelo, con tope de 15 % del precio de venta del m² construido; mitad si no supera el FOT básico ("mejor aprovechamiento")', '15 % de la mayor edificabilidad valuada a precio de comercialización de la obra; 10 % si supera parámetros sin mayor edificabilidad; 5 % del valor del suelo por mayor intensidad de uso'],
    ['Valuación', 'Valor venal declarado por el proponente y verificado por la Intendencia; en controversia, tasación de Catastro', 'Tasación de la Intendencia según manuales; la Comisión Permanente del Plan Montevideo fija el precio cuando interviene'],
    ['Pago y destino', 'Dinero al Fondo de Gestión Urbana o especie (inmuebles, obras); registro de padrones con pago pendiente, exigible ante compraventa, permiso u otras gestiones', '10 % inicial y saldo en cuatro cuotas semestrales al FEGUR; especie solo excepcional; la Comisión recomienda destino al FEGUR o a obras del área'],
    ['Reducciones', 'No aplica MA en áreas urbanas consolidadas con FOT mayor al básico, si no se supera la altura máxima', 'Hasta 70 % de reducción por cumplimiento del Modelo SuAmVi (10 % a 400 puntos, +10 % cada 100 puntos)'],
], ['Componente', 'Canelones (Costaplan y decreto 002/022)', 'Montevideo (Res. 1709/2024)'], [3, 7, 7], 8.5)
P('Fuente: textos transcriptos en la matriz RV y MA. La Res. 1709/2024 reglamenta el Decreto 37.567 según el texto citado en la matriz (verificar cita del decreto). El artículo 46 de la Ley 18.308 fija un mínimo de 5 % de la edificabilidad total en suelo con atributo potencialmente transformable, según la transcripción incluida en el PAI Zona Franca Parque de las Ciencias.').runs[0].font.size = Pt(9)

H('4.3 Mecanismos y consecuencias para el BRT', 2)
P('**(a) El BRT no dispara ninguno de los dos regímenes por sí mismo.** Ambos cobran por decisiones normativas (recategorizar, cambiar uso, reparcelar, autorizar más edificabilidad), no por inversión pública en accesibilidad. Sobre suelo urbano consolidado (18 de Julio, 8 de Octubre, Av. Italia) no hay cambio de categoría que gravar. La única vía para recuperar parte de la valorización del corredor con los instrumentos vigentes es asociar el BRT a un cambio de edificabilidad y cobrar MA sobre él. Recuperar valorización sin cambio normativo requeriría contribución por mejoras o un ajuste del valor catastral del corredor, que no figuran en la matriz.')
P('**(b) La diferencia decisiva es el aprovechamiento de referencia.** Canelones define un básico fijo (8,50 m, FOT 120 %) distinto del máximo permitido, de modo que todo lo construido por encima del básico paga aunque el plan lo habilite. Montevideo, según el texto de la Res. 1709/2024, cobra cuando un proyecto supera el aprovechamiento de la normativa vigente. Si un plan del corredor sube las alturas, lo que pasa a ser norma deja de ser "mayor aprovechamiento" y la valorización generada por el cambio normativo queda en manos del propietario. Esta lectura se basa en el texto transcripto y debe confirmarse con la Unidad Gestión Territorial: es la pregunta más importante para el diseño del componente de financiamiento.')
P('**(c) Las bases de cálculo responden distinto al valor del suelo.** En Canelones el MA cobra el suelo equivalente a la superficie adicional (m² adicionales ÷ 1,2 × valor del suelo), así que el cargo sube con la incidencia del suelo y es bajo donde el suelo es barato. En Montevideo se cobra 15 % del valor de venta de la superficie adicional, independiente del valor del suelo. Con valores ilustrativos (no observados) de 2.000 USD/m² de venta: en Montevideo el cargo es 300 USD por m² adicional en cualquier localización; en Canelones es 250 USD si el suelo vale 300 USD/m² y 83 USD si vale 100 USD/m². El tope canario de 15 % solo se activa si el suelo supera 18 % del precio de venta. Implicancia: la regla montevideana puede exceder la valorización efectiva en tramos periféricos de baja incidencia del suelo (Camino Maldonado, Ruta 8), justo donde el BRT busca atraer densidad, y quedar por debajo en el área central.')
P('**(d) El cambio de fórmula de RV en Canelones redujo la captura cuando la valorización es grande.** La fórmula vigente (5 % × FOT 1,2 × valor final × área) equivale a 6 % del valor final del suelo. La anterior (20 % de la valorización neta) equivale a 6 % solo si la valorización neta es 30 % del valor final. En una recategorización rural a suburbana donde el suelo pasa a valer cinco veces más y la infraestructura cuesta 20 % del valor final (supuestos ilustrativos), la regla anterior cobraba 12 % del valor final y la actual 6 %. A cambio, la regla actual no requiere tasar el valor previo, que es el paso más litigioso. Es un intercambio explícito entre recaudación y costo administrativo.')
P('**(e) Las reducciones pueden vaciar el cobro.** La rebaja de hasta 70 % por sustentabilidad en Montevideo y la exclusión de las áreas urbanas consolidadas en Canelones operan, en el corredor, sobre la mayor parte de los proyectos potenciales. Sin datos de expedientes no es posible saber cuánto se aplican.')
P('**(f) La norma no informa la recaudación.** La matriz muestra qué está previsto, no qué se cobró. Para cualquier estimación de potencial de financiamiento se necesitan los ingresos efectivos del Fondo de Gestión Urbana (Canelones) y del FEGUR (Montevideo) por concepto y año, y una muestra de expedientes con precio compensatorio fijado.')

H('5. Próximos pasos propuestos')
for s in [
    '**Unir la capa de ocupación a polígonos en QGIS** (clave CODSEG) y rehacer los mapas 2 y 3 como coropletas; agregar centroides o polígonos de San José.',
    '**Seleccionar 3 a 5 sectores piloto** con alta vacancia estructural en conteo dentro de 800 m (mapa 2) y cruzarlos con las capas municipales de impuesto al baldío y edificación inapropiada ya descargadas (ic_v_sca_impuesto_baldio, ic_v_sca_edif_inap) para pasar de segmento a padrón.',
    '**Preguntar a la Intendencia de Montevideo** si el "aprovechamiento definido en la normativa vigente" de la Res. 1709/2024 admite un básico distinto del máximo en un plan de corredor, y pedir recaudación del FEGUR por concepto 2020-2026.',
    '**Pedir a Canelones** recaudación del Fondo de Gestión Urbana por RV y MA desde 2022 y el registro de padrones con pago pendiente, para medir aplicación efectiva del decreto 002/022.',
    '**Pedir a ANV** montos exonerados o costo fiscal por proyecto y el diccionario del campo ZONA, para comparar la transferencia fiscal del régimen promovido con lo que el MA recaudaría en los mismos padrones.',
    '**Simular el MA en un plan de corredor** con básico fijo, usando valores de suelo DGR 2025 (dgr_compraventas2025 ya está en la carpeta) y la edificabilidad propuesta en dos o tres tramos tipo, con un rango de supuestos sobre absorción.',
    '**Aclarar con DINOT** la diferencia de 20 viviendas en San José y el universo de TotViv frente a la base censal usada antes.',
]: P(s, b=True)

H('6. Limitaciones', 2)
P('Los centroides de segmento ubican cada segmento en un punto: segmentos grandes que cruzan el límite de 800 m se asignan enteros a una banda. Las tasas por banda usan segmentos con cualquier número de viviendas, y los mapas excluyen segmentos con menos de 30. La red de estaciones es la corregida por el proyecto en 2025 y no está validada contractualmente por MTOP-DNT. Todos los valores monetarios de la sección 4.3 son ilustrativos y están marcados como tales.')
doc.save(f'{R}/Nota_material_DINOT_3009_vacancia_e_instrumentos.docx')
print('ok')
