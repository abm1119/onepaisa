import click
import json
from onepaisa.db import get_conn, get_db_path
from onepaisa import models
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.style import Style
from rich.emoji import Emoji

console = Console()

def print_1paisa_logo():
    logo_text = Text("""
    ██████╗ ███╗   ██╗███████╗██████╗  █████╗ ██╗███████╗ █████╗
    ██╔═══██╗████╗  ██║██╔════╝██╔══██╗██╔══██╗██║██╔════╝██╔══██╗
    ██║   ██║██╔██╗ ██║█████╗  ██████╔╝███████║██║███████╗███████║
    ██║   ██║██║╚██╗██║██╔══╝  ██╔═══╝ ██╔══██║██║╚════██║██╔══██║
    ╚██████╔╝██║ ╚████║███████╗██║     ██║  ██║██║███████║██║  ██║
     ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
    """, style=Style(color="bright_magenta", bold=True))
    subtitle = Text("Personal Finance CLI - Manage Your Money with Style 💰", style=Style(color="cyan", italic=True))
    console.print(Align.center(logo_text))
    console.print(Align.center(subtitle))
    console.print()

def print_footer():
    footer_text = Text("Made by Abdul Basit - ABM", style=Style(color="yellow", bold=True))
    link_text = Text("(www.engrabm.com)", style=Style(color="blue", underline=True))
    combined = Text.assemble(footer_text, " ", link_text)
    console.print(Align.center(combined))
    console.print()


@click.group()
def cli():
    """onepaisa: Personal Finance CLI"""


@cli.command()
def init():
    conn = get_conn()
    db_path = get_db_path()
    conn.close()
    print_1paisa_logo()
    panel = Panel(f"🗄️ Database initialized at [bold bright_green]{str(db_path)}[/bold bright_green]\n\nWelcome to 1Paisa! Start by adding accounts and contacts. 💼", title="🚀 Initialization Complete", border_style="bright_blue")
    console.print(panel)
    print_footer()


@cli.command("account-add")
@click.option("--name", required=True)
def account_add(name):
    conn = get_conn()
    models.ensure_account(conn, name)
    panel = Panel(f"✅ Account [bold bright_yellow]{name}[/bold bright_yellow] added successfully! 💳", title="💰 Account Created", border_style="green")
    console.print(panel)
    print_footer()


@cli.command("contact-add")
@click.option("--name", required=True)
@click.option("--relation", default="other")
@click.option("--tags", multiple=True)
@click.option("--note")
def contact_add(name, relation, tags, note):
    conn = get_conn()
    models.add_contact(conn, name, relation, tags, note)
    tags_str = ", ".join(tags) if tags else "None"
    panel = Panel(f"👥 Contact [bold bright_cyan]{name}[/bold bright_cyan] added!\nRelation: {relation}\nTags: {tags_str}\nNote: {note or 'None'}", title="📱 Contact Added", border_style="magenta")
    console.print(panel)
    print_footer()


@cli.command("contact-list")
def contact_list():
    conn = get_conn()
    rows = models.list_contacts(conn)
    table = Table(title="👥 Your Contacts", header_style="bold bright_white on bright_blue", border_style="bright_blue")
    table.add_column("ID", style="dim cyan", justify="center")
    table.add_column("Name", style="bold bright_yellow", justify="left")
    table.add_column("Relation", style="bright_green", justify="center")
    table.add_column("Tags", style="magenta", justify="left")
    table.add_column("Note", style="dim white", justify="left")
    for r in rows:
        tags = ",".join(json.loads(r["tags"] or "[]")) if r["tags"] else "None"
        table.add_row(
            str(r["id"]),
            r["name"],
            r["relation"],
            tags,
            r["note"] or "None",
        )
    panel = Panel(table, title="📋 Contact List", border_style="bright_cyan")
    console.print(panel)
    print_footer()


@cli.command()
@click.option("--contact", required=True)
@click.option("--account", required=True)
@click.option("--amount", required=True, type=float)
@click.option("--date")
@click.option("--due")
@click.option("--note")
def lend(contact, account, amount, date, due, note):
    conn = get_conn()
    models.create_loan(conn, contact, account, amount, "you_lent", date, due, note)
    panel = Panel(f"💸 Loan recorded: You lent [bold bright_red]{amount:.2f}[/bold bright_red] to [bold bright_yellow]{contact}[/bold bright_yellow] via {account}.\nDue: {due or 'N/A'}\nNote: {note or 'None'}", title="📤 Money Lent", border_style="red")
    console.print(panel)
    print_footer()


@cli.command()
@click.option("--contact", required=True)
@click.option("--account", required=True)
@click.option("--amount", required=True, type=float)
@click.option("--date")
@click.option("--due")
@click.option("--note")
def borrow(contact, account, amount, date, due, note):
    conn = get_conn()
    models.create_loan(conn, contact, account, amount, "you_borrowed", date, due, note)
    panel = Panel(f"💰 Loan recorded: You borrowed [bold bright_green]{amount:.2f}[/bold bright_green] from [bold bright_yellow]{contact}[/bold bright_yellow] via {account}.\nDue: {due or 'N/A'}\nNote: {note or 'None'}", title="📥 Money Borrowed", border_style="green")
    console.print(panel)
    print_footer()


@cli.command()
@click.option("--contact", required=True)
@click.option("--amount", required=True, type=float)
@click.option("--loan_id", type=int)
@click.option("--date")
@click.option("--note")
def repay(contact, amount, loan_id, date, note):
    conn = get_conn()
    if loan_id:
        cur = conn.cursor()
        cur.execute("SELECT * FROM loans WHERE id=?", (loan_id,))
        loan = cur.fetchone()
        if not loan:
            panel = Panel("❌ Loan not found! Please check the loan ID.", title="🚨 Error", border_style="red")
            console.print(panel)
            print_footer()
            return
        applied = models.apply_repayment_to_loan(conn, loan, amount, date, note)
        panel = Panel(f"✅ Applied [bold bright_green]{applied:.2f}[/bold bright_green] to loan ID {loan_id}.\nContact: {contact}", title="💳 Repayment Applied", border_style="green")
        console.print(panel)
    else:
        res = models.repay_contact_oldest_first(conn, contact, amount, date, note)
        panel = Panel(f"💸 Repayment processed for [bold bright_yellow]{contact}[/bold bright_yellow]:\nApplied: [bold bright_green]{res['applied']:.2f}[/bold bright_green]\nUnapplied: [bold bright_red]{res['unapplied']:.2f}[/bold bright_red]", title="🔄 Auto-Repayment", border_style="blue")
        console.print(panel)
    print_footer()


@cli.command("contact-summary")
@click.option("--contact", required=True)
def contact_summary(contact):
    conn = get_conn()
    s = models.compute_contact_summary(conn, contact)
    table = Table(title=f"👤 Contact Summary: {contact}", header_style="bold bright_white on bright_magenta", border_style="bright_magenta")
    table.add_column("Metric", style="bold cyan", justify="left")
    table.add_column("Value", style="bold yellow", justify="right")
    table.add_row("They owe you (open)", f"💰 {s['lent_open']:.2f}")
    table.add_row("You owe them (open)", f"💸 {s['borrowed_open']:.2f}")
    table.add_row("Net", f"⚖️ {s['net']:.2f}")
    panel = Panel(table, title="📊 Summary", border_style="bright_yellow")
    console.print(panel)
    print_footer()


@cli.command("contacts-report")
def contacts_report_cmd():
    conn = get_conn()
    rep = models.contacts_report(conn)
    table = Table(title="📋 Global Contacts Report", header_style="bold bright_white on bright_green", border_style="bright_green")
    table.add_column("Name", style="bold bright_yellow", justify="left")
    table.add_column("They owe you", style="green", justify="right")
    table.add_column("You owe them", style="red", justify="right")
    table.add_column("Net", style="cyan", justify="right")
    for c in rep['contacts']:
        table.add_row(
            c['name'],
            f"💰 {c['they_owe_you']:.2f}",
            f"💸 {c['you_owe_them']:.2f}",
            f"⚖️ {c['net']:.2f}",
        )
    table.add_row(
        "[bold]GRAND TOTAL[/bold]",
        f"[bold green]💰 {rep['grand_they_owe']:.2f}[/bold green]",
        f"[bold red]💸 {rep['grand_you_owe']:.2f}[/bold red]",
        f"[bold cyan]⚖️ {rep['net']:.2f}[/bold cyan]",
    )
    panel = Panel(table, title="🌍 Report", border_style="bright_cyan")
    console.print(panel)
    print_footer()


@cli.command("aging")
def aging_cmd():
    conn = get_conn()
    b = models.aging_buckets(conn)
    table = Table(title="⏰ Aging Buckets", header_style="bold bright_white on bright_red", border_style="bright_red")
    table.add_column("Bucket", style="bold bright_yellow", justify="center")
    table.add_column("Amount", style="bold green", justify="right")
    for k, v in b.items():
        table.add_row(k, f"💰 {v:.2f}")
    panel = Panel(table, title="📅 Loan Aging Analysis", border_style="bright_magenta")
    console.print(panel)
    print_footer()


@cli.command("summary")
@click.option("--period", default="month", type=click.Choice(["day", "week", "month"]))
@click.option("--month")
def summary_cmd(period, month):
    conn = get_conn()
    panel = Panel("🚧 Summary command is under development. Use [bold]contacts-report[/bold] or [bold]aging[/bold] for now! 📈", title="⚠️ Coming Soon", border_style="yellow")
    console.print(panel)
    print_footer()


@cli.command("ask")
@click.argument("query", nargs=-1)
def ask_cmd(query):
    q = " ".join(query)
    conn = get_conn()
    ans = models.ask_agent(conn, q)
    panel = Panel(f"""🤖 Answer: [bold bright_cyan]{ans['answer']}[/bold bright_cyan]

📝 Explanation: {ans['explanation']}""", title="🧠 AI Assistant Response", border_style="bright_blue")
    console.print(panel)
    print_footer()


if __name__ == "__main__":
    cli()