"""MedGemma x CompText — Interactive CLI Demo.

Run with:
    python demo_cli.py
"""

import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from src.agents.doctor_agent import DoctorAgent
from src.agents.nurse_agent import NurseAgent

console = Console()


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (≈ 1 token per 4 characters)."""
    return max(1, len(text) // 4)


def main() -> None:
    console.print(
        Panel(
            "[bold cyan]MedGemma x CompText[/bold cyan]\n"
            "[dim]Privacy-First Multi-Agent Healthcare System[/dim]",
            expand=False,
        )
    )

    raw_text = console.input(
        "\n[bold green]Enter patient symptoms:[/bold green] "
    )

    if not raw_text.strip():
        console.print("[red]No input provided. Exiting.[/red]")
        return

    # Step 1 — Nurse agent compresses the input
    nurse = NurseAgent()

    with Progress(console=console, transient=True) as progress:
        task = progress.add_task(
            "[cyan]Compressing with CompText...", total=100
        )
        for _ in range(100):
            time.sleep(0.01)
            progress.advance(task)

    patient_state = nurse.intake(raw_text)
    compressed_json = json.dumps(patient_state, indent=2)

    # Step 2 — Token comparison table
    raw_tokens = _estimate_tokens(raw_text)
    compressed_tokens = _estimate_tokens(compressed_json)

    table = Table(title="Token Usage Comparison", show_lines=True)
    table.add_column("Format", style="bold")
    table.add_column("Tokens", justify="right")
    table.add_column("Status")

    table.add_row("Raw Text", str(raw_tokens), "[red]❌ Bloated[/red]")
    table.add_row(
        "CompText JSON", str(compressed_tokens), "[green]✅ Optimized[/green]"
    )
    console.print(table)

    # Step 3 — Show compressed output
    console.print(
        Panel(compressed_json, title="Compressed Patient State", border_style="green")
    )

    # Step 4 — Doctor agent diagnosis
    doctor = DoctorAgent()
    recommendation = doctor.diagnose(patient_state)
    console.print(
        Panel(recommendation, title="Doctor Agent Response", border_style="blue")
    )


if __name__ == "__main__":
    main()
