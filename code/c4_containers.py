from graphviz import Digraph
from common_c4 import (
    apply_graph_style,
    add_container,
    add_database,
    add_person,
    add_queue,
    add_security,
    add_system,
    connect,
    open_boundary,
    render,
)


def build() -> Digraph:
    g = Digraph("c4_containers", engine="dot")
    apply_graph_style(g, "C4 - Diagrama de Contenedores | Plataforma de Banca por Internet")

    add_person(
        g,
        "cliente",
        "Cliente digital",
        "Utiliza la banca por internet desde navegador o aplicación móvil.",
    )

    add_system(
        g,
        "idp",
        "Authorization Server / IdP corporativo",
        "Autenticación OIDC/OAuth 2.0, MFA, gestión de sesiones y tokens.",
        external=True,
    )
    add_system(
        g,
        "onboarding_ext",
        "Plataforma de Onboarding y biometría",
        "Prueba de vida, OCR, comparación facial y validación documental.",
        external=True,
    )
    add_system(
        g,
        "core",
        "Core bancario",
        "Fuente de verdad de clientes, productos, saldos y movimientos.",
        external=True,
    )
    add_system(
        g,
        "complementario",
        "Sistema complementario de cliente",
        "Detalle ampliado del cliente y atributos no disponibles en Core.",
        external=True,
    )
    add_system(
        g,
        "interbank",
        "Red / switch interbancario",
        "Procesamiento de transferencias a terceros y otros bancos.",
        external=True,
    )
    add_system(
        g,
        "notif_providers",
        "Proveedores Email / SMS / Push",
        "Entrega de notificaciones transaccionales.",
        external=True,
    )
    add_system(
        g,
        "siem",
        "Auditoría / SIEM corporativo",
        "Correlación de eventos, monitoreo y cumplimiento.",
        external=True,
    )

    system = open_boundary(g, "internet_banking", "Sistema en alcance: Plataforma de Banca por Internet")

    edge = open_boundary(system, "edge", "Capa de acceso y canales")
    add_container(
        edge,
        "spa",
        "SPA Web",
        "Angular/TypeScript",
        "Canal web para clientes. Consume BFF web y delega autenticación al IdP corporativo.",
    )
    add_container(
        edge,
        "mobile",
        "App móvil",
        "Flutter/Dart",
        "Canal móvil multiplataforma con soporte para biometría del dispositivo, cámara y push.",
    )
    add_security(
        edge,
        "edge_security",
        "CloudFront + WAF + Shield",
        "CDN / protección perimetral",
        "Entrega estática, terminación TLS, mitigación DDoS, reglas antifraude básico y rate limiting.",
    )
    add_container(
        edge,
        "apigw",
        "API Gateway",
        "AWS API Gateway",
        "Expone APIs públicas, aplica throttling, JWT authorizer, versionado y routing hacia BFFs.",
    )
    system.subgraph(edge)

    channel = open_boundary(system, "channel", "Capa de canal / experiencia")
    add_container(
        channel,
        "web_bff",
        "Web BFF",
        "Python / FastAPI en ECS",
        "Backend for Frontend para SPA. Agrega respuestas, reduce exposición de servicios internos y aplica políticas de canal.",
    )
    add_container(
        channel,
        "mobile_bff",
        "Mobile BFF",
        "Python / FastAPI en ECS",
        "Backend for Frontend para móvil. Maneja jornadas móviles, device context y contratos optimizados para red celular.",
    )
    add_container(
        channel,
        "onboarding_orch",
        "Onboarding Orchestrator",
        "Servicio de aplicación",
        "Orquesta alta digital, invoca biometría/KYC y crea el vínculo inicial con identidad digital del cliente.",
    )
    system.subgraph(channel)

    domain = open_boundary(system, "domain", "Capa de negocio")
    add_container(
        domain,
        "customer_service",
        "Customer & Products Service",
        "Microservicio",
        "Consulta datos básicos de cliente, cuentas y productos; compone información del Core y del sistema complementario.",
    )
    add_container(
        domain,
        "movements_service",
        "Transaction History Service",
        "Microservicio",
        "Consulta movimientos, aplica paginación, filtros y políticas de frescura de datos.",
    )
    add_container(
        domain,
        "transfer_service",
        "Transfer Orchestrator Service",
        "Microservicio",
        "Gestiona transferencias propias e interbancarias, idempotencia, validaciones, límites y estados transaccionales.",
    )
    add_container(
        domain,
        "notification_service",
        "Notification Orchestrator",
        "Microservicio",
        "Aplica preferencias, plantillas, enrutamiento y reintentos para email, SMS y push.",
    )
    add_container(
        domain,
        "audit_service",
        "Audit & Trace Service",
        "Microservicio",
        "Consolida auditoría de negocio, eventos de seguridad y correlación transaccional.",
    )
    add_queue(
        domain,
        "event_bus",
        "Event Bus",
        "Kafka / EventBridge",
        "Backbone de eventos para auditoría, notificaciones, actualizaciones de cache y desacoplamiento entre servicios.",
    )
    system.subgraph(domain)

    integration = open_boundary(system, "integration", "Capa de integración y anticorrupción")
    add_container(
        integration,
        "core_adapter",
        "Core Banking Adapter",
        "Adapter Service",
        "Aísla contratos legacy, transforma mensajes y protege al dominio de acoplamiento con el Core.",
    )
    add_container(
        integration,
        "customer_adapter",
        "Customer Detail Adapter",
        "Adapter Service",
        "Consulta el sistema complementario cuando se requiere información ampliada del cliente.",
    )
    add_container(
        integration,
        "payments_adapter",
        "Payments Rail Adapter",
        "Adapter Service",
        "Conecta con redes interbancarias y normaliza respuestas síncronas o diferidas.",
    )
    add_container(
        integration,
        "notifications_adapter",
        "Notification Provider Adapter",
        "Adapter Service",
        "Abstrae proveedores de correo, SMS y push para evitar lock-in y facilitar failover.",
    )
    system.subgraph(integration)

    data = open_boundary(system, "data", "Datos y persistencia")
    add_database(
        data,
        "operational_db",
        "Operational Metadata DB",
        "Aurora PostgreSQL",
        "Metadatos de canal, preferencias, idempotency keys, estado de procesos, outbox y configuración.",
    )
    add_database(
        data,
        "audit_db",
        "Audit DB",
        "Aurora PostgreSQL / esquema append-only",
        "Bitácora de acciones del cliente con sellado temporal, correlación y evidencia de cumplimiento.",
    )
    add_database(
        data,
        "cache",
        "Customer Cache / Read Model",
        "Redis",
        "Optimiza lectura de clientes frecuentes y dashboards, sin reemplazar al Core como fuente de verdad.",
    )
    add_database(
        data,
        "object_store",
        "Evidence Store",
        "Amazon S3",
        "Resguarda comprobantes, evidencias de onboarding y exportaciones con cifrado y retención.",
    )
    system.subgraph(data)

    g.subgraph(system)

    connect(g, "cliente", "spa", "Usa navegador web")
    connect(g, "cliente", "mobile", "Usa aplicación móvil")
    connect(g, "spa", "idp", "Authorization Code + PKCE (redirección OIDC)")
    connect(g, "mobile", "idp", "Authorization Code + PKCE (browser tab / system browser)")
    connect(g, "spa", "edge_security", "HTTPS/TLS")
    connect(g, "mobile", "edge_security", "HTTPS/TLS")
    connect(g, "edge_security", "apigw", "Filtra y enruta tráfico")
    connect(g, "apigw", "web_bff", "REST/JSON + JWT")
    connect(g, "apigw", "mobile_bff", "REST/JSON + JWT")

    connect(g, "web_bff", "customer_service", "Consulta perfil y productos")
    connect(g, "web_bff", "movements_service", "Consulta movimientos")
    connect(g, "web_bff", "transfer_service", "Inicia transferencias")

    connect(g, "mobile_bff", "customer_service", "Consulta perfil y productos")
    connect(g, "mobile_bff", "movements_service", "Consulta movimientos")
    connect(g, "mobile_bff", "transfer_service", "Inicia transferencias")
    connect(g, "mobile_bff", "onboarding_orch", "Alta digital y enrolamiento")

    connect(g, "onboarding_orch", "onboarding_ext", "API segura de biometría/KYC")

    connect(g, "customer_service", "cache", "Read-through cache")
    connect(g, "movements_service", "cache", "Cache corto / read model")
    connect(g, "transfer_service", "operational_db", "Persistencia transaccional e idempotencia")

    connect(g, "customer_service", "core_adapter", "Consulta datos básicos")
    connect(g, "customer_service", "customer_adapter", "Consulta detalle ampliado")
    connect(g, "movements_service", "core_adapter", "Consulta movimientos")
    connect(g, "transfer_service", "core_adapter", "Valida cuentas y registra transferencia")
    connect(g, "transfer_service", "payments_adapter", "Transferencias interbancarias")

    connect(g, "transfer_service", "event_bus", "Publica evento de transferencia")
    connect(g, "customer_service", "event_bus", "Publica eventos de actualización")
    connect(g, "movements_service", "event_bus", "Publica eventos de consulta relevante")

    connect(g, "event_bus", "notification_service", "Eventos de negocio")
    connect(g, "event_bus", "audit_service", "Eventos auditables")

    connect(g, "notification_service", "notifications_adapter", "Solicita entrega por canal")
    connect(g, "notifications_adapter", "notif_providers", "Email / SMS / Push")

    connect(g, "audit_service", "audit_db", "Persistencia append-only")
    connect(g, "audit_service", "siem", "Eventos de seguridad y monitoreo")

    connect(g, "core_adapter", "core", "APIs / MQ / servicios legacy")
    connect(g, "customer_adapter", "complementario", "API segura")
    connect(g, "payments_adapter", "interbank", "Canal interbancario")

    connect(g, "onboarding_orch", "operational_db", "Estados del onboarding")
    connect(g, "onboarding_orch", "object_store", "Evidencias y documentos")

    return g


if __name__ == "__main__":
    render(build(), "c4_containers")