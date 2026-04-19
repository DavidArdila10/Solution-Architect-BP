from __future__ import annotations

from html import escape
from pathlib import Path
from graphviz import Digraph

FONT = "Helvetica"
PALETTE = {
    "person": "#FFF2CC",
    "system": "#D9EAD3",
    "external": "#D0E0FF",
    "container": "#EAD1DC",
    "database": "#FCE5CD",
    "queue": "#D9D2E9",
    "security": "#F4CCCC",
    "boundary": "#F8F9FA",
    "edge": "#4B5563",
    "title": "#111827",
    "muted": "#4B5563",
}


def _fmt(text: str) -> str:
    return escape(text).replace("\n", "<BR ALIGN=\"LEFT\"/>")


def card_label(title: str, stereotype: str, description: str, fill: str) -> str:
    return f'''<
<TABLE BORDER="1" COLOR="#6B7280" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8">
    <TR><TD BGCOLOR="{fill}" ALIGN="LEFT"><FONT FACE="{FONT}" POINT-SIZE="14"><B>{_fmt(title)}</B></FONT></TD></TR>
    <TR><TD BGCOLOR="{fill}" ALIGN="LEFT"><FONT FACE="{FONT}" POINT-SIZE="10" COLOR="#374151">{_fmt(stereotype)}</FONT></TD></TR>
    <TR><TD BGCOLOR="white" ALIGN="LEFT"><FONT FACE="{FONT}" POINT-SIZE="10" COLOR="#111827">{_fmt(description)}</FONT></TD></TR>
</TABLE>
>'''


def add_person(g: Digraph, node_id: str, title: str, description: str) -> None:
    g.node(
        node_id,
        label=card_label(title, "Persona", description, PALETTE["person"]),
        shape="plain",
    )


def add_system(g: Digraph, node_id: str, title: str, description: str, external: bool = False) -> None:
    fill = PALETTE["external"] if external else PALETTE["system"]
    stereotype = "Sistema externo" if external else "Sistema"
    g.node(node_id, label=card_label(title, stereotype, description, fill), shape="plain")


def add_container(g: Digraph, node_id: str, title: str, technology: str, description: str) -> None:
    g.node(node_id, label=card_label(title, technology, description, PALETTE["container"]), shape="plain")


def add_database(g: Digraph, node_id: str, title: str, technology: str, description: str) -> None:
    g.node(node_id, label=card_label(title, technology, description, PALETTE["database"]), shape="plain")


def add_queue(g: Digraph, node_id: str, title: str, technology: str, description: str) -> None:
    g.node(node_id, label=card_label(title, technology, description, PALETTE["queue"]), shape="plain")


def add_security(g: Digraph, node_id: str, title: str, technology: str, description: str) -> None:
    g.node(node_id, label=card_label(title, technology, description, PALETTE["security"]), shape="plain")


def apply_graph_style(g: Digraph, title: str) -> None:
    g.attr(
        rankdir="LR",
        splines="spline",
        nodesep="0.55",
        ranksep="1.05",
        bgcolor="white",
        labelloc="t",
        labeljust="l",
        label=title,
        fontsize="22",
        fontname=FONT,
        pad="0.25",
    )
    g.attr("node", fontname=FONT)
    g.attr(
        "edge",
        fontname=FONT,
        fontsize="10",
        color=PALETTE["edge"],
        arrowsize="0.8",
        penwidth="1.2",
    )


def open_boundary(parent: Digraph, name: str, label: str) -> Digraph:
    # Graphviz interpreta como cluster a los subgrafos cuyo nombre inicia con "cluster_"
    cluster = Digraph(name=f"cluster_{name}")
    cluster.attr(
        label=label,
        labelloc="t",
        labeljust="l",
        fontsize="16",
        fontname=FONT,
        color="#9CA3AF",
        style="rounded,filled",
        fillcolor=PALETTE["boundary"],
        margin="18",
    )
    return cluster


def connect(g: Digraph, src: str, dst: str, label: str, style: str = "solid", color: str | None = None) -> None:
    kwargs = {"label": label, "style": style}
    if color:
        kwargs["color"] = color
        kwargs["fontcolor"] = color
    g.edge(src, dst, **kwargs)


def render(graph: Digraph, filename: str) -> None:
    # Guarda el .dot y luego renderiza a PNG en la carpeta out/
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    dot_path = out_dir / f"{filename}.dot"
    graph.save(str(dot_path))

    graph.render(
        filename=filename,
        directory=str(out_dir),
        format="png",
        cleanup=False,
    )

    print(f"Generado: {out_dir / (filename + '.png')}")
    print(f"Fuente DOT: {dot_path}")