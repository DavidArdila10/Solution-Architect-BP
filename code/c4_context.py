from graphviz import Digraph
from common_c4 import apply_graph_style, add_person, add_system, connect, open_boundary, render


def build() -> Digraph:
    g = Digraph("c4_context", engine="dot")
    apply_graph_style(g, "C4 - Diagrama de Contexto | Plataforma de Banca por Internet")

    add_person(
        g,
        "cliente",
        "Cliente digital",
        "Consulta movimientos, realiza transferencias, gestiona su sesión y recibe notificaciones desde web y móvil.",
    )
    add_person(
        g,
        "operaciones",
        "Operaciones / Soporte / Cumplimiento",
        "Monitorea incidentes, audita eventos y atiende excepciones operativas o regulatorias.",
    )

    platform = open_boundary(g, "internet_banking", "Sistema en alcance")
    add_system(
        platform,
        "internet_bank",
        "Plataforma de Banca por Internet",
        "Canal digital para consulta de productos y movimientos, transferencias propias e interbancarias, onboarding y notificaciones.",
    )
    g.subgraph(platform)

    add_system(
        g,
        "idp",
        "Authorization Server / IdP corporativo",
        "Servicio corporativo compatible con OAuth 2.0 / OpenID Connect para autenticación, MFA, emisión de tokens y federación.",
        external=True,
    )
    add_system(
        g,
        "onboarding",
        "Plataforma de Onboarding y biometría",
        "Valida identidad, documentos, reconocimiento facial y pruebas de vida para altas digitales.",
        external=True,
    )
    add_system(
        g,
        "core",
        "Core bancario",
        "Sistema fuente de verdad para clientes, cuentas, productos, saldos, movimientos y confirmación transaccional.",
        external=True,
    )
    add_system(
        g,
        "complementario",
        "Sistema complementario de cliente",
        "Expone datos ampliados del cliente cuando el detalle no está disponible en el Core.",
        external=True,
    )
    add_system(
        g,
        "interbank",
        "Red / switch interbancario",
        "Procesa transferencias hacia terceros y bancos externos, con respuestas síncronas o diferidas según el rail.",
        external=True,
    )
    add_system(
        g,
        "notifs",
        "Proveedores de notificación",
        "Canales de salida de correo electrónico, SMS y push móvil.",
        external=True,
    )
    add_system(
        g,
        "audit",
        "Plataforma de auditoría y SIEM",
        "Recibe trazas de negocio y eventos de seguridad para investigación, monitoreo y cumplimiento.",
        external=True,
    )

    connect(g, "cliente", "internet_bank", "Usa el canal digital desde SPA web y app móvil")
    connect(g, "operaciones", "internet_bank", "Supervisa operación, consulta auditoría y gestiona incidentes")
    connect(g, "internet_bank", "idp", "Autenticación federada, MFA, emisión y validación de tokens")
    connect(g, "internet_bank", "onboarding", "Onboarding remoto, biometría y validación documental")
    connect(g, "internet_bank", "core", "Consulta datos, movimientos y registra transferencias")
    connect(g, "internet_bank", "complementario", "Consulta detalle ampliado del cliente")
    connect(g, "internet_bank", "interbank", "Envía transferencias interbancarias y recibe estado")
    connect(g, "internet_bank", "notifs", "Envía alertas y notificaciones transaccionales")
    connect(g, "internet_bank", "audit", "Publica auditoría de negocio y eventos de seguridad")

    return g


if __name__ == "__main__":
    render(build(), "c4_context")