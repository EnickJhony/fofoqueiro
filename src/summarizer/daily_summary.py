from collections import defaultdict
from datetime import date



def build_daily_summary(rows: list, day: date) -> str:
    if not rows:
        return f"Resumo do dia {day.isoformat()}: sem noticias coletadas."

    grouped: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        grouped[row["source_name"]].append(f"- {row['title']}\n  {row['link']}")

    lines: list[str] = [f"Resumo do dia {day.isoformat()}"]

    for source_name, items in grouped.items():
        lines.append("")
        lines.append(f"Portal: {source_name}")
        lines.extend(items)

    return "\n".join(lines)
