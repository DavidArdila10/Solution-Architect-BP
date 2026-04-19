from graphviz import Digraph
from common_c4 import (
    apply_graph_style,
    add_container,
    add_database,
    add_queue,
    add_security,
    connect,
    open_boundary,
    render,
)


def build() -> Digraph:
    g = Digraph("c4_components", engine="dot")
    apply_graph_style(g, "C4 - Diagrama de Componentes | Backend transaccional y de integración")

    boundary = open_boundary(g, "backend", "Contenedor detallado: Servicios backend de canal y negocio")

    entry = open_boundary(boundary, "entry", "Entrada y seguridad")
    add_security(
        entry,
        "jwt_filter",
        "JWT / Token Validation Filter",
        "Componente transversal",
        "Valida issuer, audience, scopes, expiración, nonce, binding de sesión y propaga identidad al resto de componentes.",
    )
    add_security(
        entry,
        "risk_engine",
        "Risk & Step-up Policy",
        "Componente transversal",
        "Evalúa contexto, dispositivo, monto, canal y riesgo para exigir MFA o rechazar operaciones anómalas.",
    )
    add_container(
        entry,
        "api_handlers",
        "API Handlers / Controllers",
        "REST controllers",
        "Endpoints de consulta, transferencias y onboarding; validan contratos y correlacionan requests.",
    )
    boundary.subgraph(entry)

    app = open_boundary(boundary, "app", "Capa de aplicación")
    add_container(
        app,
        "journey_bff",
        "Journey Aggregator / BFF logic",
        "Application service",
        "Orquesta la experiencia del canal, compone respuestas y evita exponer detalles internos al front.",
    )
    add_container(
        app,
        "customer_app",
        "Customer Query Application Service",
        "Application service",
        "Resuelve perfil, cuentas y productos usando cache y adaptadores de integración.",
    )
    add_container(
        app,
        "movements_app",
        "Movements Application Service",
        "Application service",
        "Recupera movimientos con filtros, paginación y políticas de frescura.",
    )
    add_container(
        app,
        "transfer_app",
        "Transfer Application Service",
        "Application service",
        "Orquesta transferencias, controla idempotencia, límites y consistencia del proceso.",
    )
    add_container(
        app,
        "onboarding_app",
        "Onboarding Application Service",
        "Application service",
        "Gestiona alta digital, estados y vinculación de identidad tras biometría exitosa.",
    )
    add_container(
        app,
        "notification_policy",
        "Notification Policy Engine",
        "Application service",
        "Define cuándo, cómo y por qué canal se notifica según tipo de evento y preferencia del cliente.",
    )
    add_container(
        app,
        "audit_publisher",
        "Audit Publisher",
        "Application service",
        "Publica eventos de auditoría con contexto de negocio y seguridad.",
    )
    boundary.subgraph(app)

    domain = open_boundary(boundary, "domain", "Patrones de dominio y resiliencia")
    add_container(
        domain,
        "transfer_saga",
        "Transfer Saga / Process Manager",
        "Saga pattern",
        "Coordina validación, reserva lógica, registro en Core, compensación y cierre de estado.",
    )
    add_container(
        domain,
        "idempotency",
        "Idempotency Guard",
        "Policy component",
        "Evita duplicados por reintentos del cliente, red o timeout del canal.",
    )
    add_container(
        domain,
        "outbox",
        "Outbox Publisher",
        "Transactional outbox",
        "Garantiza publicación fiable de eventos después del commit en base de datos.",
    )
    add_container(
        domain,
        "cache_facade",
        "Cache Facade",
        "Read-through / cache-aside",
        "Encapsula política de cache, TTL, invalidación por evento y fallback al sistema fuente.",
    )
    boundary.subgraph(domain)

    integration = open_boundary(boundary, "integration", "Integración / anticorrupción")
    add_container(
        integration,
        "core_acl",
        "Core Banking ACL",
        "Anti-Corruption Layer",
        "Traduce contratos, normaliza errores legacy y desacopla el dominio de particularidades del Core.",
    )
    add_container(
        integration,
        "customer_acl",
        "Customer Detail ACL",
        "Anti-Corruption Layer",
        "Obtiene atributos ampliados del sistema complementario sin contaminar el modelo de dominio.",
    )
    add_container(
        integration,
        "payments_acl",
        "Payments Rail ACL",
        "Anti-Corruption Layer",
        "Gestiona protocolos con la red interbancaria y normaliza estados transaccionales.",
    )
    add_container(
        integration,
        "notify_acl",
        "Notification Provider ACL",
        "Provider abstraction",
        "Abstrae proveedores de SMS, email y push para failover y sustitución controlada.",
    )
    boundary.subgraph(integration)

    data = open_boundary(boundary, "data", "Persistencia y mensajería")
    add_database(
        data,
        "ops_db",
        "Operational Metadata DB",
        "Aurora PostgreSQL",
        "Estados de proceso, preferencias, outbox, idempotency keys y trazabilidad técnica.",
    )
    add_database(
        data,
        "audit_db",
        "Audit DB",
        "Append-only store",
        "Registro inviolable de acciones del cliente y decisiones del sistema.",
    )
    add_database(
        data,
        "redis",
        "Read Model / Cache",
        "Redis",
        "Optimización de clientes frecuentes y datos de baja criticidad temporal.",
    )
    add_queue(
        data,
        "event_bus",
        "Event Bus",
        "Kafka / EventBridge",
        "Entrega eventos de negocio, auditoría, invalidación de cache y notificaciones.",
    )
    boundary.subgraph(data)

    externals = open_boundary(boundary, "externals", "Dependencias externas")
    add_container(
        externals,
        "idp",
        "IdP corporativo",
        "OIDC / OAuth 2.0",
        "Autenticación, MFA, introspección/JWKS y federación.",
    )
    add_container(
        externals,
        "onboarding_ext",
        "Proveedor biométrico / KYC",
        "API externa segura",
        "Reconocimiento facial, liveness, OCR y validación documental.",
    )
    add_container(
        externals,
        "core",
        "Core bancario",
        "Sistema externo",
        "Datos maestros, productos, movimientos y registro de operaciones.",
    )
    add_container(
        externals,
        "complementario",
        "Sistema complementario",
        "Sistema externo",
        "Detalle ampliado de cliente.",
    )
    add_container(
        externals,
        "interbank",
        "Red interbancaria",
        "Sistema externo",
        "Compensación / autorización de transferencias externas.",
    )
    add_container(
        externals,
        "providers",
        "Canales de notificación",
        "Sistemas externos",
        "Correo, SMS y push.",
    )
    boundary.subgraph(externals)

    g.subgraph(boundary)

    connect(g, "api_handlers", "jwt_filter", "Aplica autenticación y scopes")
    connect(g, "jwt_filter", "idp", "JWKS / introspección / metadata OIDC")
    connect(g, "api_handlers", "risk_engine", "Evalúa step-up y riesgo")
    connect(g, "api_handlers", "journey_bff", "Invoca casos de uso")
    connect(g, "journey_bff", "customer_app", "Consulta perfil")
    connect(g, "journey_bff", "movements_app", "Consulta movimientos")
    connect(g, "journey_bff", "transfer_app", "Inicia transferencia")
    connect(g, "journey_bff", "onboarding_app", "Inicia onboarding")

    connect(g, "customer_app", "cache_facade", "Lee caché / read model")
    connect(g, "movements_app", "cache_facade", "Lee caché corto")
    connect(g, "cache_facade", "redis", "GET / SET / invalidate")
    connect(g, "customer_app", "core_acl", "Consulta datos básicos")
    connect(g, "customer_app", "customer_acl", "Consulta detalle ampliado")
    connect(g, "movements_app", "core_acl", "Consulta movimientos")

    connect(g, "transfer_app", "idempotency", "Valida request idempotente")
    connect(g, "idempotency", "ops_db", "Lee / registra clave")
    connect(g, "transfer_app", "transfer_saga", "Orquesta proceso")
    connect(g, "transfer_saga", "core_acl", "Valida cuentas / registra operación")
    connect(g, "transfer_saga", "payments_acl", "Envía transferencia interbancaria")
    connect(g, "core_acl", "core", "HTTPS/mTLS o MQ segura")
    connect(g, "customer_acl", "complementario", "HTTPS/mTLS")
    connect(g, "payments_acl", "interbank", "Canal seguro / firma / mTLS")

    connect(g, "onboarding_app", "onboarding_ext", "API de biometría y KYC")
    connect(g, "onboarding_app", "ops_db", "Estados del onboarding")

    connect(g, "transfer_app", "ops_db", "Persistencia transaccional")

    connect(g, "customer_app", "audit_publisher", "Evento auditable")
    connect(g, "movements_app", "audit_publisher", "Evento auditable")
    connect(g, "transfer_app", "audit_publisher", "Evento auditable")
    connect(g, "onboarding_app", "audit_publisher", "Evento auditable")
    connect(g, "audit_publisher", "audit_db", "Persistencia append-only")

    connect(g, "transfer_app", "outbox", "Publica evento post-commit")
    connect(g, "customer_app", "outbox", "Publica actualización")
    connect(g, "movements_app", "outbox", "Publica actualización")
    connect(g, "outbox", "ops_db", "Lee outbox pendiente")
    connect(g, "outbox", "event_bus", "Emite evento fiable")

    connect(g, "event_bus", "notification_policy", "Entrega eventos de negocio")
    connect(g, "notification_policy", "notify_acl", "Selecciona canal")
    connect(g, "notify_acl", "providers", "Email / SMS / Push")

    return g


if __name__ == "__main__":
    render(build(), "c4_components")