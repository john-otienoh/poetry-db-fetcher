# #!/usr/bin/env python3
# from conn import DatabaseConnection

# def check_data():
#     with DatabaseConnection() as db:
#         # Count poems
#         result = db.execute_query("SELECT COUNT(*) as count FROM poems")
#         count = result[0]['count'] if result else 0
#         print(f"Total poems: {count}")
        
#         if count > 0:
#             # Show all poems
#             poems = db.get_all_poems()
#             print(f"\nPoems:")
#             for poem in poems:
#                 print(f"  ID: {poem['id']} - {poem['title']} by {poem['author']} ({poem['linecount']} lines)")
#         else:
#             print("No poems found in database!")

# if __name__ == "__main__":
#     check_data()
#!/usr/bin/env python3
"""
Command-line utility to view and search poems in the database.
"""
import json
import argparse
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from conn import DatabaseConnection

console = Console()


def list_all_poems(limit: Optional[int] = None):
    """List all poems in the database."""
    with DatabaseConnection() as db:
        poems = db.get_all_poems()
        
        if not poems:
            console.print("[yellow]No poems found in database[/yellow]")
            return
        
        # Create a rich table
        table = Table(title=f"Poems in Database ({len(poems)} total)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Author", style="magenta")
        table.add_column("Lines", justify="right", style="blue")
        table.add_column("Created At", justify="right", style="yellow")
        
        for poem in poems[:limit] if limit else poems:
            table.add_row(
                str(poem['id']),
                poem['title'][:50] + "..." if len(poem['title']) > 50 else poem['title'],
                poem['author'],
                str(poem['linecount']),
                poem['created_at'].strftime("%Y-%m-%d") if poem['created_at'] else "Unknown"
            )
        
        console.print(table)


def view_poem(poem_id: int):
    """View a specific poem by ID."""
    with DatabaseConnection() as db:
        poem = db.get_poem_by_id(poem_id)
        if not poem:
            console.print(f"[red]No poem found with ID: {poem_id}[/red]")
            return
        
        # Header
        console.print(Panel(
            f"[bold cyan]{poem['title']}[/bold cyan]\n[magenta]by {poem['author']}[/magenta]",
            title=f"Poem # {poem['id']}",
            border_style="green"
        ))
        
        # Metadata
        console.print(f"[blue]Lines Count:[/blue] {poem['linecount']}  [yellow]Words:[/yellow]")
        console.print(f"[white]Added:[/white] {poem['created_at'].strftime("%Y-%m-%d") if poem['created_at'] else "Unknown"}")
        console.print()
        
        # Poem lines
        if poem['lines']:
            lines = poem['lines']
            if isinstance(lines, str):
                try:
                    lines = json.loads(lines)
                except:
                    lines = [lines]
            
            for i, line in enumerate(lines, 1):
                console.print(f"  [cyan]{i:3d}[/cyan]  {line}")
        else:
            console.print("  [italic]No lines available[/italic]")


def search_poems(search_term: str):
    """Search for poems by title or author."""
    with DatabaseConnection() as db:
        poems = db.search_poems(search_term)
        
        if not poems:
            console.print(f"[yellow]No poems found matching '{search_term}'[/yellow]")
            return
        
        # Create a rich table
        table = Table(title=f"Search Results for: '{search_term}' ({len(poems)} found)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Author", style="magenta")
        table.add_column("Lines", justify="right", style="blue")
        table.add_column("Similarity", justify="right", style="yellow")
        
        for poem in poems:
            similarity = max(poem.get('title_sim', 0), poem.get('author_sim', 0))
            table.add_row(
                str(poem['id']),
                poem['title'],
                poem['author'],
                str(poem['linecount']),
                f"{similarity:.2%}"
            )
        
        console.print(table)


def poems_by_author(author: str):
    """View all poems by a specific author."""
    with DatabaseConnection() as db:
        poems = db.get_poems_by_author(author)
        
        if not poems:
            console.print(f"📭 [yellow]No poems found by '{author}'[/yellow]")
            return
        
        # Get author statistics
        stats = db.get_statistics()
        
        console.print(Panel(
            f"[bold magenta]{author}[/bold magenta]",
            title=f"Poems by {author} ({len(poems)} total)",
            border_style="blue"
        ))
        
        # Create a rich table
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="green")
        table.add_column("Lines", justify="right", style="blue", width=8)
        table.add_column("Words", justify="right", style="yellow", width=8)
        table.add_column("Added", style="white", width=12)
        
        for poem in poems:
            table.add_row(
                str(poem['id']),
                poem['title'][:60],
                str(poem['linecount']),
                str(poem['word_count']),
                poem['created_at'].strftime("%Y-%m-%d") if poem['created_at'] else "Unknown"
            )
        
        console.print(table)


def show_statistics():
    """Show database statistics."""
    with DatabaseConnection() as db:
        stats = db.get_statistics()
        diversity = db.get_language_diversity()
        
        # Statistics panel
        console.print(Panel(
            f"[bold cyan]Database Statistics[/bold cyan]",
            border_style="green"
        ))
        
        # Create stats table
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="blue")
        table.add_column("Value", style="green")
        
        table.add_row("Total Poems", str(stats.get('total_poems', 0)))
        table.add_row("Total Authors", str(stats.get('total_authors', 0)))
        table.add_row("Average Lines/Poem", str(stats.get('avg_lines', 0)))
        table.add_row("Total Words", str(stats.get('total_words', 0)))
        
        if stats.get('top_author'):
            table.add_row("Most Prolific Author", 
                         f"{stats['top_author']} ({stats['top_author_count']} poems)")
        
        console.print(table)
        
        # Language diversity
        if diversity:
            console.print("\n[bold cyan] Language Diversity by Year:[/bold cyan]")
            div_table = Table(show_header=True, header_style="bold")
            div_table.add_column("Year", style="cyan")
            div_table.add_column("Unique Languages", style="green", justify="right")
            div_table.add_column("Total Poems", style="blue", justify="right")
            div_table.add_column("Diversity Ratio", style="yellow", justify="right")
            
            for item in diversity:
                div_table.add_row(
                    str(item['year']),
                    str(item['unique_languages']),
                    str(item['total_poems']),
                    f"{item['diversity_ratio']}%"
                )
            
            console.print(div_table)


def export_poem(poem_id: int, format: str = "text"):
    """Export a poem to different formats."""
    with DatabaseConnection() as db:
        poem = db.get_poem_by_id(poem_id)
        
        if not poem:
            console.print(f"✗ [red]No poem found with ID: {poem_id}[/red]")
            return
        
        if format == "json":
            # Export as JSON
            output = {
                'id': poem['id'],
                'title': poem['title'],
                'author': poem['author'],
                'lines': poem['lines'],
                'linecount': poem['linecount'],
                'word_count': poem['word_count'],
                'created_at': str(poem['created_at'])
            }
            console.print_json(data=output)
            
        elif format == "markdown":
            # Export as Markdown
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
            # Default text format
            console.print(f"\n[bold cyan]{poem['title']}[/bold cyan]")
            console.print(f"[magenta]by {poem['author']}[/magenta]\n")
            
            lines = poem['lines']
            if isinstance(lines, str):
                try:
                    lines = json.loads(lines)
                except:
                    lines = [lines]
            
            for line in lines:
                console.print(f"  {line}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Poetry Database Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python view_poems.py list
  python view_poems.py view 1
  python view_poems.py search "dickinson"
  python view_poems.py author "Emily Dickinson"
  python view_poems.py stats
  python view_poems.py export 1 --format json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all poems")
    list_parser.add_argument("--limit", type=int, help="Limit number of poems shown")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View a specific poem")
    view_parser.add_argument("poem_id", type=int, help="Poem ID")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search poems")
    search_parser.add_argument("term", type=str, help="Search term")
    
    # Author command
    author_parser = subparsers.add_parser("author", help="View poems by author")
    author_parser.add_argument("name", type=str, help="Author name")
    
    # Stats command
    # subparsers.add_parser("stats", help="Show database statistics")
    
    # # Export command
    # export_parser = subparsers.add_parser("export", help="Export a poem")
    # export_parser.add_argument("poem_id", type=int, help="Poem ID")
    # export_parser.add_argument("--format", choices=["text", "json", "markdown"], 
    #                           default="text", help="Export format")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_all_poems(args.limit)
    elif args.command == "view":
        view_poem(args.poem_id)
    elif args.command == "search":
        search_poems(args.term)
    # elif args.command == "author":
    #     poems_by_author(args.name)
    # elif args.command == "stats":
    #     show_statistics()
    # elif args.command == "export":
    #     export_poem(args.poem_id, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()