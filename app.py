import re
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.doctemplate import LayoutError


def create_client_pdf(record: dict[str, object]) -> bytes:
  pdf_buffer = BytesIO()
  document = SimpleDocTemplate(
    pdf_buffer,
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=18 * mm,
    title="Formulario de vinculacion de clientes",
  )
  styles = getSampleStyleSheet()
  styles["Title"].textColor = colors.HexColor("#18332f")
  styles["Heading2"].textColor = colors.HexColor("#16735e")
  styles["BodyText"].fontSize = 8
  styles["BodyText"].leading = 11

  rows = [[Paragraph("<b>Campo</b>", styles["BodyText"]), Paragraph("<b>Información diligenciada</b>", styles["BodyText"])]]
  for field, value in record.items():
    label = field.replace("_", " ").capitalize()
    display_value = escape(str(value)) if value not in (None, "") else " "
    rows.append(
      [
        Paragraph(escape(label), styles["BodyText"]),
        Paragraph(display_value.replace("\n", "<br/>"), styles["BodyText"]),
      ]
    )

  table = Table(rows, colWidths=[52 * mm, document.width - 52 * mm], repeatRows=1)
  table.setStyle(
    TableStyle(
      [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f1ec")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#18332f")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dce6e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
      ]
    )
  )
  document.build(
    [
      Paragraph("VINCULACIÓN DE CLIENTES", styles["Title"]),
      Paragraph("BODEGAS ASOCIADAS LTDA", styles["Heading2"]),
      Spacer(1, 8 * mm),
      table,
    ]
  )
  return pdf_buffer.getvalue()


st.set_page_config(page_title="Vinculación de clientes | BA LTDA", page_icon="🗂️", layout="wide")

st.markdown(
  """
  <style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

  :root {
    --ink: #18332f;
    --muted: #687975;
    --green: #16735e;
    --green-dark: #105b4a;
    --line: #dce6e1;
    --surface: #ffffff;
    --canvas: #f3f7f4;
  }
  html, body, [class*="css"] {
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
    color: var(--ink);
  }
  .stApp {
    background:
      radial-gradient(ellipse at 95% 0%, rgba(194, 224, 207, .38), transparent 30rem),
      var(--canvas);
  }
  .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
  h1, h2, h3 { font-family: 'Manrope', 'Segoe UI', sans-serif; color: var(--ink); }
  .eyebrow {
    color: var(--green); font-size: .76rem; font-weight: 700;
    letter-spacing: .08em; text-transform: uppercase; margin-bottom: .35rem;
  }
  .subtitle { color: var(--muted); margin-top: -.5rem; margin-bottom: 1.5rem; }
  .panel {
    background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
    padding: 1.35rem 1.45rem; box-shadow: 0 8px 24px rgba(24, 51, 47, .045);
  }
  div.stButton > button[kind="primary"], div.stDownloadButton > button {
    background: var(--green); color: white; border: 0; border-radius: 6px;
    min-height: 2.85rem; font-weight: 700;
  }
  div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover {
    background: var(--green-dark); color: white;
  }
  div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
  div[data-testid="stTextArea"] textarea {
    border-radius: 6px; border-color: var(--line);
  }
  </style>
  """,
  unsafe_allow_html=True,
)


st.markdown('<div class="eyebrow">BA LTDA · Área comercial</div>', unsafe_allow_html=True)
st.title("VINCULACION DE CLIENTES BODEGAS ASOCIADAS")
st.markdown(
  '<p class="subtitle">Formato de identificación y conocimiento de asociado de negocios o cliente.</p>',
  unsafe_allow_html=True,
)

st.subheader("Datos de Control e Identificación de la Solicitud")
date_column, procedure_column = st.columns([1, 2])
with date_column:
  completion_date = st.date_input("Fecha de diligenciamiento", value=date.today())
with procedure_column:
  procedure_type = st.radio(
    "Tipo de trámite",
    ["Vinculación inicial", "Actualización anual"],
    horizontal=True,
  )

client_type = st.radio("Tipo de cliente", ["Empresa", "Persona natural"], horizontal=True)

with st.container():
  st.subheader("Información Básica del Cliente")
  if client_type == "Empresa":
    company_name = st.text_input("Razón social *", placeholder="Nombre legal de la empresa")
    nit = st.text_input("NIT *", placeholder="Número de identificación tributaria")
    document_number = ""
    st.subheader("Representantes Legales")
    representative_count = st.number_input(
      "Cantidad de representantes legales",
      min_value=0,
      max_value=50,
      value=1,
      step=1,
    )
    legal_representatives = []
    for representative_index in range(1, int(representative_count) + 1):
      representative_name_column, representative_document_column = st.columns([1.4, 1])
      with representative_name_column:
        representative_name = st.text_input(
          f"Nombre y apellido {representative_index}",
          key=f"legal_representative_name_{representative_index}",
        )
      with representative_document_column:
        representative_document = st.text_input(
          f"Número de documento {representative_index}",
          key=f"legal_representative_document_{representative_index}",
        )
      legal_representatives.append((representative_name, representative_document))
    st.subheader("Accionistas/Socios (participación mayor al 5%)")
    shareholder_count = st.number_input(
      "Cantidad de accionistas/socios",
      min_value=0,
      max_value=19,
      value=1,
      step=1,
    )
    shareholders = []
    for shareholder_index in range(1, int(shareholder_count) + 1):
      st.caption(f"Accionista/Socio {shareholder_index}")
      shareholder_name_column, shareholder_percentage_column, shareholder_document_column = st.columns([1.4, 0.8, 1])
      with shareholder_name_column:
        shareholder_name = st.text_input(
          "Nombres y apellidos *",
          key=f"shareholder_name_{shareholder_index}",
        )
      with shareholder_percentage_column:
        shareholder_percentage = st.number_input(
          "Participación (%) *",
          min_value=5.01,
          max_value=100.0,
          value=5.01,
          step=0.01,
          format="%.2f",
          key=f"shareholder_percentage_{shareholder_index}",
        )
      with shareholder_document_column:
        shareholder_document = st.text_input(
          "Número de documento *",
          key=f"shareholder_document_{shareholder_index}",
        )
      shareholders.append(
        {
          "name": shareholder_name,
          "percentage": shareholder_percentage,
          "document": shareholder_document,
        }
      )
  else:
    company_name = ""
    nit = ""
    document_number = st.text_input("Número de documento *", placeholder="Cédula o documento de identidad")
    legal_representatives = []
    shareholders = []

  st.subheader("Datos de Contacto")
  contact_name = st.text_input("Persona de contacto *", placeholder="Nombre y apellido")
  email_column, phone_column = st.columns(2)
  with email_column:
    email = st.text_input("Correo electrónico *", placeholder="nombre@empresa.com")
  with phone_column:
    phone = st.text_input("Teléfono *", placeholder="+57 300 123 4567")
  city = st.text_input("Ciudad - Departamento", placeholder="Ciudad - Departamento de residencia o sede")
  address = st.text_input("Dirección principal", placeholder="Calle, carrera, número y complemento")

  st.subheader("Información Económica")
  st.caption("Valores expresados en pesos colombianos (COP).")
  activity_column, ciiu_column = st.columns(2)
  with activity_column:
    economic_activity = st.text_input("Actividad económica principal", placeholder="Ej.: comercio, logística, servicios")
  with ciiu_column:
    ciiu_code = st.text_input("Código CIIU principal", placeholder="Ej.: 6201", max_chars=6)
  economic_sector = st.selectbox(
    "Sector económico",
    ["Agropecuario", "Servicios", "Industrial", "Transporte", "Comercio", "Construcción", "Energético", "Otro"],
  )
  iva_regime = st.radio(
    "Régimen",
    ["Responsable de IVA", "No responsable de IVA"],
    horizontal=True,
  )
  large_taxpayer_column, income_tax_exempt_column, self_withholding_column, ica_responsible_column = st.columns(4)
  with large_taxpayer_column:
    large_taxpayer = st.radio("Gran contribuyente *", ["Sí", "No"], index=None, horizontal=True)
  with income_tax_exempt_column:
    income_tax_exempt = st.radio("Exento de impuesto a la renta *", ["Sí", "No"], index=None, horizontal=True)
  with self_withholding_column:
    self_withholding_agent = st.radio("Autorretenedor *", ["Sí", "No"], index=None, horizontal=True)
  with ica_responsible_column:
    ica_responsible = st.radio("Responsable de ICA *", ["Sí", "No"], index=None, horizontal=True)
  if economic_sector == "Otro":
    economic_sector_other = st.text_input(
      "Especifica el sector económico *",
      placeholder="Escribe el sector económico",
    )
  else:
    economic_sector_other = ""
  monthly_income = st.number_input("Ingresos mensuales", min_value=0, value=0, step=100000)
  assets_column, liabilities_column, equity_column = st.columns(3)
  with assets_column:
    total_assets = st.number_input("Activos totales", min_value=0, value=0, step=100000)
  with liabilities_column:
    total_liabilities = st.number_input("Pasivos totales", min_value=0, value=0, step=100000)
  with equity_column:
    equity = st.number_input("Patrimonio", min_value=0, value=0, step=100000)
  registered_capital_column, authorized_capital_column, subscribed_capital_column = st.columns(3)
  with registered_capital_column:
    registered_capital = st.number_input("Capital social registrado", min_value=0, value=0, step=100000)
  with authorized_capital_column:
    authorized_capital = st.number_input("Capital autorizado", min_value=0, value=0, step=100000)
  with subscribed_capital_column:
    subscribed_capital = st.number_input("Capital suscrito", min_value=0, value=0, step=100000)
  st.subheader("Datos Bancarios")
  bank_entity_column, account_number_column = st.columns(2)
  with bank_entity_column:
    financial_entity = st.text_input("Entidad financiera", placeholder="Nombre del banco o entidad")
  with account_number_column:
    account_number = st.text_input("Número de cuenta", placeholder="Número de cuenta bancaria")
  instrument_column, city_bank_column = st.columns(2)
  with instrument_column:
    banking_instrument = st.text_input("Instrumento", placeholder="Ej.: cuenta corriente, ahorros, etc.")
  with city_bank_column:
    banking_city = st.text_input("Ciudad", placeholder="Ciudad de la entidad bancaria")
  account_holder = st.text_input("Titular de la cuenta", placeholder="Nombre del titular")

  st.subheader("Datos para Correspondencia")
  correspondence_office_address = st.text_input(
    "Dirección oficina principal",
    placeholder="Calle, carrera, número, barrio",
  )
  correspondence_city = st.text_input(
    "Ciudad - Departamento",
    placeholder="Ciudad - Departamento",
  )
  correspondence_phone = st.text_input(
    "Teléfono",
    placeholder="+57 300 123 4567",
  )
  correspondence_person = st.text_input(
    "Persona encargada",
    placeholder="Nombre de la persona encargada",
  )

  st.subheader("Datos de Facturación Electrónica")
  billing_email = st.text_input(
    "Correo",
    placeholder="factura@ejemplo.com",
  )
  send_copy_to_another_email = st.radio(
    "¿Solicita copia a otro correo?",
    ["No", "Sí"],
    index=0,
    horizontal=True,
  )
  another_billing_email = ""
  if send_copy_to_another_email == "Sí":
    another_billing_email = st.text_input(
      "Correo adicional",
      placeholder="otrocorreo@ejemplo.com",
    )

  st.subheader("Organización de la empresa")
  employee_column, facilities_column = st.columns([1.2, 1.5])
  with employee_column:
    employee_count = st.number_input("Número de empleados", min_value=0, value=0, step=1)
  with facilities_column:
    facilities_type = st.radio(
      "Sus instalaciones son",
      ["Propia", "Arriendo"],
      index=None,
      horizontal=True,
    )
  goods_description = st.text_area(
    "Descripción resumida de las mercancías objeto de los trámites",
    placeholder="Ejemplo: alimentos secos, textiles, productos químicos, maquinaria, etc.",
    height=100,
  )
  funds_origin = st.text_input(
    "Origen de fondos",
    placeholder="Describa el origen de los fondos",
  )
  pep_status = st.radio(
    "¿Es persona expuesta políticamente (PEP)?",
    ["Sí", "No"],
    index=None,
    horizontal=True,
  )
  pep_related_status = st.radio(
    "¿Es familiar o asociado de una PEP?",
    ["Sí", "No"],
    index=None,
    horizontal=True,
  )
  pep_relationship = ""
  if pep_related_status == "Sí":
    pep_relationship = st.text_input(
      "Relación con la PEP",
      placeholder="Ej.: padre, cónyuge, socio, amigo cercano, etc.",
    )
  gremial_affiliation = st.radio(
    "¿Tiene afiliaciones a entidades gremiales? *",
    ["Sí", "No"],
    index=None,
    horizontal=True,
  )
  certification_options = ["ISO 9001", "ISO 28000", "BASC", "OEA/CTPAT", "Otra", "Ninguna"]
  certifications = st.multiselect(
    "Certificaciones",
    certification_options,
    default=[],
  )
  other_certification = ""
  if "Otra" in certifications:
    other_certification = st.text_input(
      "Especifica otra certificación",
      placeholder="Nombre de la certificación",
    )
  elif "Otra" not in certifications:
    other_certification = ""

  st.subheader("Personas para firmar documentos")
  signer_count = st.number_input(
    "Cantidad de personas",
    min_value=1,
    max_value=10,
    value=1,
    step=1,
  )
  signers = []
  for signer_index in range(1, int(signer_count) + 1):
    signer_name_column, signer_document_column, signer_position_column = st.columns([1.5, 1.2, 1.3])
    with signer_name_column:
      signer_name = st.text_input(
        f"Nombre completo {signer_index}",
        key=f"signer_name_{signer_index}",
      )
    with signer_document_column:
      signer_document = st.text_input(
        f"Identificación {signer_index}",
        key=f"signer_document_{signer_index}",
      )
    with signer_position_column:
      signer_position = st.text_input(
        f"Cargo {signer_index}",
        key=f"signer_position_{signer_index}",
      )
    signers.append(
      {
        "name": signer_name,
        "document": signer_document,
        "position": signer_position,
      }
    )

  st.subheader("Referencias Comerciales")
  references = []
  for reference_index in range(1, 3):
    st.caption(f"Referencia {reference_index}")
    reference_name = st.text_input(
      "Nombre o razón social",
      key=f"reference_name_{reference_index}",
    )
    ref_address, ref_city, ref_phone = st.columns([1.5, 1.3, 1])
    with ref_address:
      reference_address = st.text_input(
        "Dirección",
        key=f"reference_address_{reference_index}",
      )
    with ref_city:
      reference_city = st.text_input(
        "Ciudad - Departamento",
        key=f"reference_city_{reference_index}",
      )
    with ref_phone:
      reference_phone = st.text_input(
        "Teléfono",
        key=f"reference_phone_{reference_index}",
      )
    reference_email = st.text_input(
      "Correo",
      key=f"reference_email_{reference_index}",
      placeholder="correo@ejemplo.com",
    )
    references.append(
      {
        "name": reference_name,
        "address": reference_address,
        "city": reference_city,
        "phone": reference_phone,
        "email": reference_email,
      }
    )

  st.markdown(
    """
    <div class="panel">
      <h3 style="margin-top:0; margin-bottom: .7rem;">Documentos a anexar</h3>
      <ul style="margin: 0; padding-left: 1.2rem; line-height: 1.8;">
        <li>Certificado original de cámara de comercio no mayor a 30 días.</li>
        <li>RUT (Registro Único Tributario) completo y actualizado.</li>
        <li>Certificación bancaria con vigencia máxima de tres meses.</li>
        <li>Fotocopia cédula de ciudadanía del personal autorizado para firmas.</li>
        <li>Fotocopia cédula de ciudadanía del representante legal.</li>
        <li>2 referencias comerciales.</li>
        <li>RUB – Registro Único de Beneficiarios Finales.</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
  )

  st.markdown(
    """
    <div class="panel">
      <h3 style="margin-top:0; margin-bottom: .7rem;">Autorización</h3>
      <p style="margin: 0; text-align: justify; line-height: 1.8;">
        Obrando en nombre propio, de manera voluntaria y dando certeza de que todo lo aquí consignado es cierto,
        realizo la siguiente declaración de origen de fondos a BODEGAS ASOCIADAS LTDA con NIT 837.000.606-1,
        con el propósito de que se pueda dar cumplimiento a lo señalado circular externa 170 de 2002 expedida por la dirección
        de impuestos y aduanas nacionales y la ley 526 de 1999, ley 599 de 2000 y ley 190 de 1.995 (estatuto anticorrupción)
        y demás normas legales concordantes para el desarrollo de operaciones de Comercio exterior.
      </p>
      <p style="margin: 1rem 0 0; text-align: justify; line-height: 1.8;">
        Así mismo, declaro que lo escrito en la casilla "origen de fondos" de este formulario, sobre los recursos no provienen de ninguna
        actividad ilícita de las contempladas en el código penal colombiano o en cualquier norma que lo modifique o adicione, ni efectuare
        transacciones destinadas a tales actividades o a favor de personas relacionadas con las mismas; en caso de infracción de cualquiera
        de los numerales contenidos en este documento, eximo a BODEGAS ASOCIADAS LTDA con NIT 837.000.606-1, de toda responsabilidad que se
        derive por información errónea, falsa o inexacta que yo hubiere proporcionado en este documento o de la violación del mismo.
      </p>
      <p style="margin: 1rem 0 0; text-align: justify; line-height: 1.8;">
        Declaro que como asociado de negocio de BODEGAS ASOCIADAS LTDA con NIT 837.000.606-1, me acojo a la Resolución 017 de 2016 proferida
        por el director general de la UIAF, la cual establece que se debe dar cumplimiento al Sistema Integral Prevención y control del Lavado de
        activos, la Financiación del Terrorismo y financiamiento de la Proliferación de Armas de Destrucción Masiva para la – SIPLAFT/PADM, por lo que
        estoy dando fe, que al interior de mi organización no se tienen, ni se llevan a cabo actividades ilícitas. Compromiso SIPLAFT/SARLAFT sistema
        informático para la prevención del lavado de activos y financiación terrorista. Según el reporte en (UIAF) unidad de información de análisis financiero,
        en la sección de (GAFI) grupo de acción financiera internacional.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
  )

  consent = st.checkbox("Autorizo a BA LTDA a contactarme para gestionar esta solicitud. *")
  submitted = st.button("Registrar cliente", type="primary", use_container_width=True)

if submitted:
  required_identity = [contact_name.strip()]
  if client_type == "Empresa":
    required_identity.extend([company_name.strip(), nit.strip()])
  else:
    required_identity.append(document_number.strip())

  email_valid = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))
  billing_email_valid = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", billing_email.strip()))
  reference_emails_valid = all(
    bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", reference["email"].strip()))
    for reference in references
  )
  signer_data_valid = all(
    signer["name"].strip() and signer["document"].strip() and signer["position"].strip()
    for signer in signers
  )
  reference_data_valid = all(
    reference["name"].strip()
    and reference["address"].strip()
    and reference["city"].strip()
    and reference["phone"].strip()
    and reference["email"].strip()
    for reference in references
  )
  shareholder_data_valid = all(
    shareholder["name"].strip() and shareholder["document"].strip()
    for shareholder in shareholders
  ) and sum(shareholder["percentage"] for shareholder in shareholders) <= 100
  another_billing_email_valid = True
  if send_copy_to_another_email == "Sí":
    another_billing_email_valid = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", another_billing_email.strip()))

  if (
    not all(required_identity)
    or not phone.strip()
    or not email_valid
    or not billing_email_valid
    or not reference_emails_valid
    or not signer_data_valid
    or not reference_data_valid
    or not consent
    or facilities_type is None
    or not funds_origin.strip()
    or pep_status is None
    or pep_related_status is None
    or (pep_related_status == "Sí" and not pep_relationship.strip())
    or gremial_affiliation is None
    or (economic_sector == "Otro" and not economic_sector_other.strip())
    or any(
      status is None
      for status in (large_taxpayer, self_withholding_agent, income_tax_exempt, ica_responsible)
    )
    or not shareholder_data_valid
    or not another_billing_email_valid
  ):
    st.error("Revisa los campos obligatorios, los datos de accionistas/socios, las referencias, las firmas, la relación con la PEP, el correo y la autorización de contacto.")
  else:
    record = {
      "fecha_diligenciamiento": completion_date.isoformat(),
      "tipo_tramite": procedure_type,
      "tipo_cliente": client_type,
      "razon_social": company_name.strip(),
      "nit": nit.strip(),
      "numero_documento": document_number.strip(),
      "nombre_contacto": contact_name.strip(),
      "correo": email.strip(),
      "telefono": phone.strip(),
      "ciudad": city.strip(),
      "direccion_principal": address.strip(),
      "numero_empleados": employee_count,
      "sus_instalaciones_son": facilities_type,
      "descripcion_mercancias": goods_description.strip(),
      "origen_de_fondos": funds_origin.strip(),
      "persona_expuesta_politicamente": pep_status,
      "familiar_o_asociado_pep": pep_related_status,
      "relacion_con_pep": pep_relationship.strip(),
      "afiliacion_entidades_gremiales": gremial_affiliation,
      "certificaciones": "; ".join(certifications),
      "otra_certificacion": other_certification.strip(),
      "actividad_economica": economic_activity.strip(),
      "codigo_ciiu_principal": ciiu_code.strip(),
      "sector_economico": economic_sector,
      "sector_economico_otro": economic_sector_other.strip(),
      "regimen_iva": iva_regime,
      "gran_contribuyente": large_taxpayer,
      "autorretenedor": self_withholding_agent,
      "exento_impuesto_renta": income_tax_exempt,
      "responsable_ica": ica_responsible,
      "ingresos_mensuales_cop": monthly_income,
      "activos_totales_cop": total_assets,
      "pasivos_totales_cop": total_liabilities,
      "patrimonio_cop": equity,
      "capital_social_registrado_cop": registered_capital,
      "capital_autorizado_cop": authorized_capital,
      "capital_suscrito_cop": subscribed_capital,
      "entidad_financiera": financial_entity.strip(),
      "numero_cuenta": account_number.strip(),
      "instrumento_bancario": banking_instrument.strip(),
      "ciudad_entidad_financiera": banking_city.strip(),
      "titular_cuenta": account_holder.strip(),
      "direccion_oficina_principal": correspondence_office_address.strip(),
      "ciudad_departamento_correspondencia": correspondence_city.strip(),
      "telefono_correspondencia": correspondence_phone.strip(),
      "persona_encargada_correspondencia": correspondence_person.strip(),
      "correo_facturacion": billing_email.strip(),
      "solicita_copia_otro_correo": send_copy_to_another_email,
      "correo_facturacion_copia": another_billing_email.strip(),
      "autorizacion_contacto": "Sí",
    }
    for signer_index, signer in enumerate(signers, start=1):
      record[f"firma_persona_{signer_index}_nombre"] = signer["name"].strip()
      record[f"firma_persona_{signer_index}_identificacion"] = signer["document"].strip()
      record[f"firma_persona_{signer_index}_cargo"] = signer["position"].strip()
    for reference_index, reference in enumerate(references, start=1):
      record[f"referencia_comercial_{reference_index}_nombre_razon_social"] = reference["name"].strip()
      record[f"referencia_comercial_{reference_index}_direccion"] = reference["address"].strip()
      record[f"referencia_comercial_{reference_index}_ciudad_departamento"] = reference["city"].strip()
      record[f"referencia_comercial_{reference_index}_telefono"] = reference["phone"].strip()
      record[f"referencia_comercial_{reference_index}_correo"] = reference["email"].strip()
    for representative_index, (representative_name, representative_document) in enumerate(
      legal_representatives,
      start=1,
    ):
      record[f"representante_legal_{representative_index}_nombre"] = representative_name.strip()
      record[f"representante_legal_{representative_index}_documento"] = representative_document.strip()
    for shareholder_index, shareholder in enumerate(shareholders, start=1):
      record[f"accionista_socio_{shareholder_index}_nombre"] = shareholder["name"].strip()
      record[f"accionista_socio_{shareholder_index}_participacion_porcentaje"] = shareholder["percentage"]
      record[f"accionista_socio_{shareholder_index}_documento"] = shareholder["document"].strip()
    try:
      pdf_data = create_client_pdf(record)
      client_filename = re.sub(r"[^A-Za-z0-9_-]+", "_", contact_name.strip()).strip("_")
      if not client_filename:
        client_filename = "cliente"
      st.success("Formulario completado. Descarga tu copia en PDF.")
      st.download_button(
        label="Descargar formulario en PDF",
        data=pdf_data,
        file_name=f"formulario_vinculacion_{client_filename}.pdf",
        mime="application/pdf",
        type="primary",
        on_click="ignore",
      )
    except (LayoutError, UnicodeEncodeError, ValueError) as error:
      st.error(f"No se pudo generar el PDF: {error}")

st.caption("El formulario no almacena ni publica la información enviada; cada persona descarga únicamente su propio PDF.")