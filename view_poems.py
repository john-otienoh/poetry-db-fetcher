import argparse
import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

from conn import DatabaseConnection

console = Console()

def _poem_table(title: str, poems: list[dict], *, show_similarity: bool = False):
    table = Table(title=title, show_lines=False)
    table.add_column("ID",     style="cyan",    no_wrap=True, width=6)
    table.add_column("Title",  style="green",   max_width=50)
    table.add_column("Author", style="magenta", max_width=30)
    table.add_column("Lines",  style="blue",    justify="right", width=7)
    if show_similarity:
        table.add_column("Match", style="yellow", justify="right", width=8)

    for p in poems:
        row = [
            str(p["id"]),
            (p["title"][:47] + "…") if len(p["title"]) > 50 else p["title"],
            p["author"],
            str(p["linecount"]),
        ]
        if show_similarity:
            sim = max(p.get("title_sim", 0), p.get("author_sim", 0))
            row.append(f"{sim:.0%}")
        table.add_row(*row)
    return table

def cmd_list(limit: Optional[int]):
    with DatabaseConnection() as db:
        poems = db.get_all_poems()

    if not poems:
        console.print("[yellow]No poems in database.[/yellow]")
        return

    subset = poems[:limit] if limit else poems
    console.print(_poem_table(f"All poems ({len(poems)} total)", subset))


def cmd_export(poem_id: int, format: str = "text"):
    """Export a poem to different formats."""
    with DatabaseConnection() as db:
        poem = db.get_poem_by_id(poem_id)
        
        if not poem:
            console.print(f"✗ [red]No poem found with ID: {poem_id}[/red]")
            return
        
        if format == "json":
            output = {
                'id': poem['id'],
                'title': poem['title'],
                'author': poem['author'],
                'lines': poem['lines'],
                'linecount': poem['linecount'],
                'created_at': str(poem['created_at'])
            }
            console.print_json(data=output)
            
        elif format == "markdown":
            lines = poem['lines']
            if isinstance(lines, str):
                try:
                    lines = json.loads(lines)
                except:
                    lines = [lines]
            
            md = f"# {poem['title']}\n\n"
            md += f"*by {poem['author']}*\n\n"
            for line in lines:
                md += f"{line}\n\n"
            
            console.print(Markdown(md))
            
        else:
            cmd_view(poem_id=poem_id)
            
def cmd_view(poem_id: int):
    with DatabaseConnection() as db:
        poem = db.get_poem_by_id(poem_id)

    if not poem:
        console.print(f"[red]No poem found with id {poem_id}.[/red]")
        return

    console.print(Panel(
        f"[bold cyan]{poem['title']}[/bold cyan]\n[magenta]by {poem['author']}[/magenta]",
        title=f"Poem #{poem['id']}",
        border_style="green",
    ))

    lines = poem["lines"] or []
    if isinstance(lines, str):
        lines = json.loads(lines)

    for i, line in enumerate(lines, 1):
        console.print(f"  [dim]{i:>3}[/dim]  {line}")

    console.print(f"\n[dim]{poem['linecount']} lines · added {poem['created_at'].strftime('%Y-%m-%d')}[/dim]")


def cmd_search(term: str):
    with DatabaseConnection() as db:
        poems = db.search_poems(term)

    if not poems:
        console.print(f"[yellow]No results for '{term}'.[/yellow]")
        return

    console.print(_poem_table(f"Results for '{term}' ({len(poems)} found)", poems, show_similarity=True))


def cmd_author(name: str):
    with DatabaseConnection() as db:
        poems = db.get_poems_by_author(name)

    if not poems:
        console.print(f"[yellow]No poems found by '{name}'.[/yellow]")
        return

    console.print(_poem_table(f"Poems by '{name}' ({len(poems)} total)", poems))


def cmd_stats():
    with DatabaseConnection() as db:
        stats = db.get_statistics()

    table = Table(title="Database Statistics", show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="blue")
    table.add_column("Value",  style="green")

    table.add_row("Total poems",   str(stats.get("total_poems", 0)))
    table.add_row("Total authors", str(stats.get("total_authors", 0)))
    table.add_row("Avg lines/poem", str(stats.get("avg_lines", 0)))
    table.add_row("Total lines",   str(stats.get("total_lines", 0)))

    if stats.get("top_author"):
        table.add_row(
            "Most prolific author",
            f"{stats['top_author']} ({stats['top_author_count']} poems)",
        )

    console.print(table)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browse your local poetry database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python view_poems.py list --limit 20
  python view_poems.py view 3
  python view_poems.py search "raven"
  python view_poems.py author "Emily Dickinson"
  python view_poems.py stats
  python view_poems.py export 1 --format json
        """,
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    lst = sub.add_parser("list",   help="List all poems")
    lst.add_argument("--limit", type=int, metavar="N", help="Show only the first N rows")

    vw = sub.add_parser("view",   help="View a poem by id")
    vw.add_argument("poem_id", type=int)

    sr = sub.add_parser("search", help="Search poems by title or author")
    sr.add_argument("term")

    au = sub.add_parser("author", help="Show poems by a specific author")
    au.add_argument("name")

    export_parser = sub.add_parser("export", help="Export a poem")
    export_parser.add_argument("poem_id", type=int, help="Poem ID")
    export_parser.add_argument("--format", choices=["text", "json", "markdown"], 
                              default="text", help="Export format")
    

    sub.add_parser("stats", help="Show database statistics")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "list":   lambda: cmd_list(args.limit),
        "view":   lambda: cmd_view(args.poem_id),
        "search": lambda: cmd_search(args.term),
        "author": lambda: cmd_author(args.name),
        "export": lambda: cmd_export(args.poem_id, args.format),
        "stats":  cmd_stats,
    }

    action = dispatch.get(args.command)
    if action:
        action()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()