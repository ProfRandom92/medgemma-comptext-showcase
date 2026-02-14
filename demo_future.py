"""Future EHR Demo — AI-Native Patient Record showcase.

Simulates a cross-facility scenario:
  - Oct 2023: Patient visits Clinic A (history generated & saved).
  - Feb 2026: Patient rushes to ER at Clinic B (instant context load).

Run with:
    python demo_future.py
"""

import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.future_ehr import AINativeRecord

console = Console()

SAMPLE_RECORD = (
    "Chief complaint: chest pain radiating to left arm. "
    "History: Patient is a 58-year-old male with a history of hypertension, "
    "type 2 diabetes, and hyperlipidemia. Previous MI in 2019, stent placed "
    "in LAD. Family history of CAD (father, age 62). Allergies: Penicillin. "
    "Current medications: Metoprolol 50mg BID, Lisinopril 20mg daily, "
    "Atorvastatin 40mg daily, Aspirin 81mg daily, Metformin 1000mg BID. "
    "Social history: Former smoker (quit 2020), occasional alcohol use. "
    "HR 105, BP 148/92, Temp 37.1C. "
    "ECG shows ST-segment depression in leads V3-V5. "
    "Troponin pending. Patient appears diaphoretic and anxious."
)

PATIENT_ID = "PT-2023-88421"


def main() -> None:
    ehr = AINativeRecord()

    console.print(
        Panel(
            "[bold cyan]Future EHR Demo[/bold cyan]\n"
            "[dim]AI-Native Patient Record — Cross-Facility Showcase[/dim]",
            expand=False,
        )
    )

    # ── Scene 1: Clinic A saves the record ──────────────────────────
    console.print("\n[bold yellow]📅 Oct 2023 — Clinic A[/bold yellow]")
    console.print("[dim]Patient visits for cardiac evaluation. "
                  "Record compressed & saved.[/dim]\n")

    result = ehr.save_record(PATIENT_ID, SAMPLE_RECORD)
    console.print(
        Panel(
            json.dumps(json.loads(result["compressed_json"]), indent=2),
            title=f"Saved CompText Record ({PATIENT_ID})",
            border_style="green",
        )
    )

    # ── Scene 2: Clinic B loads the record ──────────────────────────
    console.print("\n[bold red]🚨 Feb 2026 — Clinic B (ER)[/bold red]")
    console.print("[dim]Patient arrives with acute symptoms. "
                  "ER needs context NOW.[/dim]\n")

    # Simulate raw PDF load (slow)
    console.print("[yellow]⏳ Loading raw PDF record...[/yellow]")
    t0 = time.perf_counter()
    time.sleep(2)  # simulated latency for legacy PDF parsing
    pdf_time = time.perf_counter() - t0
    console.print(f"[yellow]   Raw PDF ready in {pdf_time:.2f}s[/yellow]\n")

    # Simulate CompText load (instant)
    console.print("[green]⚡ Loading CompText record...[/green]")
    t0 = time.perf_counter()
    loaded = ehr.load_record(PATIENT_ID)
    comptext_time = time.perf_counter() - t0
    console.print(f"[green]   CompText ready in {comptext_time:.4f}s[/green]\n")

    assert loaded is not None

    # ── Results table ───────────────────────────────────────────────
    stats = ehr.get_stats(PATIENT_ID, SAMPLE_RECORD)

    table = Table(title="⚡ Time-to-First-Token Comparison", show_lines=True)
    table.add_column("Method", style="bold")
    table.add_column("Load Time", justify="right")
    table.add_column("Status")
    table.add_row("Raw PDF (legacy)", f"{pdf_time:.2f}s", "[red]❌ Slow[/red]")
    table.add_row(
        "CompText Record", f"{comptext_time:.4f}s", "[green]✅ Instant[/green]"
    )
    console.print(table)

    table2 = Table(title="💾 Storage Footprint Comparison", show_lines=True)
    table2.add_column("Metric", style="bold")
    table2.add_column("Raw", justify="right")
    table2.add_column("CompText", justify="right")
    table2.add_column("Saved", justify="right", style="green")
    table2.add_row(
        "Characters",
        str(stats["raw_chars"]),
        str(stats["compressed_chars"]),
        f"{stats['storage_saved_pct']}%",
    )
    table2.add_row(
        "Tokens (est.)",
        str(stats["raw_tokens"]),
        str(stats["compressed_tokens"]),
        f"{stats['tokens_saved_pct']}%",
    )
    console.print(table2)

    console.print(
        "\n[bold green]✅ Demo complete — CompText enables instant, "
        "cross-facility context sharing.[/bold green]\n"
    )


if __name__ == "__main__":
    main()
