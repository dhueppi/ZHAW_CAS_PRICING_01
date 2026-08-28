#!/usr/bin/env python3
import argparse
import csv
import json
import math
import random
import re
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path


def parse_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        if not inner.strip():
            return []
        pieces = [p.strip().strip('"\'') for p in inner.split(",")]
        return [p for p in pieces if p]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"\'')


def parse_markdown_spec(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()

    attributes = []
    config = {}
    current_attr = None
    section = None

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        heading_match = re.match(r"^#+\s*(.+)$", stripped)
        if heading_match:
            heading = heading_match.group(1).strip().lower()
            if heading == "attributes":
                section = "attributes"
            elif heading == "config":
                section = "config"
            else:
                section = None
            continue

        if stripped.lower() == "attributes":
            section = "attributes"
            continue
        if stripped.lower() == "config":
            section = "config"
            continue

        if section == "config":
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                config[key.strip().lower()] = parse_scalar(value)
            continue

        if section == "attributes":
            match_name = re.match(r"^-\s*name:\s*(.+)$", stripped)
            if match_name:
                if current_attr is not None:
                    attributes.append(current_attr)
                current_attr = {"name": match_name.group(1).strip(), "levels": []}
                continue

            if current_attr is not None and stripped.lower() == "levels:":
                continue

            if current_attr is not None and stripped.startswith("- "):
                current_attr["levels"].append(stripped[2:].strip())
                continue

    if current_attr is not None:
        attributes.append(current_attr)

    if not attributes:
        raise ValueError(f"No attributes found in {path}. Expected an 'Attributes' section with name and levels.")

    tasks = int(config.get("tasks", 10))
    alts_per_task = int(config.get("alts_per_task", 3))
    return attributes, tasks, alts_per_task


def shuffle_list(items):
    items = list(items)
    random.shuffle(items)
    return items


def generate_design(attributes, num_tasks, alts_per_task):
    total_slots = num_tasks * alts_per_task
    columns = {}
    for attr in attributes:
        levels = attr["levels"]
        if not levels:
            raise ValueError(f"Attribute '{attr['name']}' has no levels.")
        pool = []
        while len(pool) < total_slots:
            pool.extend(shuffle_list(levels))
        columns[attr["name"]] = pool[:total_slots]

    profiles = []
    for slot in range(total_slots):
        profile = {}
        for attr in attributes:
            profile[attr["name"]] = columns[attr["name"]][slot]
        profiles.append(profile)

    tasks = []
    for t in range(num_tasks):
        task_profiles = profiles[t * alts_per_task:(t + 1) * alts_per_task]

        for i in range(len(task_profiles)):
            for j in range(i + 1, len(task_profiles)):
                same = all(task_profiles[i][attr["name"]] == task_profiles[j][attr["name"]] for attr in attributes)
                if same:
                    swap_idx = (t * alts_per_task + j + alts_per_task) % len(profiles)
                    swap_attr = attributes[random.randrange(len(attributes))]
                    swap_name = swap_attr["name"]
                    tmp = profiles[swap_idx][swap_name]
                    profiles[swap_idx][swap_name] = task_profiles[j][swap_name]
                    task_profiles[j][swap_name] = tmp

        alternatives = [
            {"altId": f"A{i + 1}", "isNone": False, **profile} for i, profile in enumerate(task_profiles)
        ]
        tasks.append({"taskId": t + 1, "alternatives": alternatives})

    return tasks


def design_to_csv(tasks, attributes, out_path):
    header = ["TaskID", "AltID", *[attr["name"] for attr in attributes]]
    rows = [header]
    for task in tasks:
        for alt in task["alternatives"]:
            rows.append([task["taskId"], alt["altId"], *[alt[attr["name"]] for attr in attributes]])

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)

    return out_path


OLLAMA_SPEED_PRESETS = {
    "fast": {"temperature": 0.0, "top_p": 0.8, "num_predict": 32, "num_ctx": 1024, "repeat_penalty": 1.1},
    "balanced": {"temperature": 0.2, "top_p": 0.9, "num_predict": 48, "num_ctx": 1536, "repeat_penalty": 1.1},
    "quality": {"temperature": 0.3, "top_p": 0.95, "num_predict": 64, "num_ctx": 2048, "repeat_penalty": 1.1},
}


def call_ollama_generate(prompt, model="gemma4:e2b", profile="fast"):
    settings = OLLAMA_SPEED_PRESETS.get(profile, OLLAMA_SPEED_PRESETS["fast"])
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": settings["temperature"],
            "top_p": settings["top_p"],
            "num_predict": settings["num_predict"],
            "num_ctx": settings["num_ctx"],
            "repeat_penalty": settings["repeat_penalty"],
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama server nicht erreichbar unter http://localhost:11434: {exc}") from exc

    return result.get("response", "")


def parse_ollama_choice_payload(response_text):
    cleaned = str(response_text or "").strip()
    if not cleaned:
        raise ValueError("Leere Antwort von Ollama.")

    match = re.search(r"```json\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if match:
        cleaned = match.group(1)
    elif cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return parsed[0]
    except json.JSONDecodeError:
        pass

    raise ValueError(f"Ollama-Antwort konnte nicht als JSON geparst werden: {cleaned[:200]}")


def design_from_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError(f"No design rows found in {path}.")

    header = rows[0]
    task_idx = header.index("TaskID") if "TaskID" in header else None
    alt_idx = header.index("AltID") if "AltID" in header else None
    if task_idx is None or alt_idx is None:
        raise ValueError(f"Design CSV {path} must contain TaskID and AltID columns.")

    attributes = []
    for col in header[2:]:
        attributes.append({"name": col, "levels": []})

    task_map = defaultdict(list)
    for row in rows[1:]:
        if len(row) < len(header):
            continue
        task_id = row[task_idx]
        task_map[int(task_id)].append(row)

    tasks = []
    for task_id in sorted(task_map.keys()):
        alts = []
        for row in task_map[task_id]:
            alt_id = row[alt_idx]
            payload = {"altId": alt_id}
            for attr_idx, attr in enumerate(attributes):
                payload[attr["name"]] = row[2 + attr_idx]
            alts.append(payload)
        tasks.append({"taskId": task_id, "alternatives": alts})

    return tasks, attributes


def generate_llm_choice_csv(attributes, design, model="gemma4:e2b", profile="fast", respondent_id="OLLAMA_R1"):
    rows = [["RespondentID", "TaskID", "AltID", *[attr["name"] for attr in attributes], "Chosen"]]
    total_tasks = len(design)

    print(f"Generating {total_tasks} LLM choice tasks with model={model} profile={profile}...", flush=True)

    for index, task in enumerate(design, start=1):
        alternatives = task["alternatives"]
        alternative_text = " | ".join(
            [
                f"{alt['altId']}: " + "; ".join(f"{attr['name']}: {alt[attr['name']]}" for attr in attributes)
                for alt in alternatives
            ]
        )

        print(f"[Task {index}/{total_tasks}] asking Ollama for Task {task['taskId']}...", flush=True)

        prompt = (
            "Du bist ein typischer Konsument in einem realistischen Choice-Experiment. "
            "Wähle immer die Alternative mit dem höchsten erwarteten Nutzen.\n"
            "Wichtige Regeln:\n"
            "- Preis: niedrigere Preise sind besser.\n"
            "- Verbrauch / Effizienz: besserer Verbrauch ist besser.\n"
            "- Antriebsart: Elektro und Hybrid sind oft bevorzugt, aber nur innerhalb eines realistischen Trade-offs.\n"
            "- Fahrzeugklasse: größere Klassen sind nur dann besser, wenn sie nicht mit zu hohem Preis oder unnötiger Überdimensionierung einhergehen.\n"
            "- Marke: verwende nur die angegebenen Labels und keine semantischen Assoziationen.\n"
            "- Ignoriere implizite Produktstorys und nutze nur die explizit genannten Attribute.\n"
            "- Wenn die Varianten gegeneinander abgewogen werden, wähle die Alternative mit dem höchsten erwarteten Nutzen.\n"
            "Return only valid JSON in the format {\"taskId\": 1, \"chosenAltId\": \"A1\"}.\n\n"
            f"Task {task['taskId']}: {alternative_text}"
        )

        response = call_ollama_generate(prompt, model=model, profile=profile)
        decision = parse_ollama_choice_payload(response)
        chosen_alt_id = decision.get("chosenAltId") or decision.get("altId") or decision.get("choice")
        if not chosen_alt_id:
            raise ValueError(f"Ollama hat keine gültige Auswahl für Task {task['taskId']} zurückgegeben: {response[:200]}")

        print(f"[Task {index}/{total_tasks}] selection received: {chosen_alt_id}", flush=True)

        for alt in alternatives:
            rows.append([
                respondent_id,
                task["taskId"],
                alt["altId"],
                *[alt[attr["name"]] for attr in attributes],
                "1" if alt["altId"] == chosen_alt_id else "0",
            ])

    print(f"Completed LLM choice generation for {total_tasks} tasks.", flush=True)
    return rows


def write_csv_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return path


def parse_choice_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No data found in {path}.")

    headers = reader.fieldnames or []
    lower_headers = {h.lower(): h for h in headers}

    respondent_col = lower_headers.get("respondentid") or lower_headers.get("respondent")
    task_col = lower_headers.get("taskid") or lower_headers.get("task")
    alt_col = lower_headers.get("altid") or lower_headers.get("alt")
    chosen_col = lower_headers.get("chosen")

    if not respondent_col:
        raise ValueError('Missing column "RespondentID" (or "Respondent").')
    if not task_col:
        raise ValueError('Missing column "TaskID" (or "Task").')
    if not alt_col:
        raise ValueError('Missing column "AltID" (or "Alt").')
    if not chosen_col:
        raise ValueError('Missing column "Chosen".')

    attr_cols = [h for h in headers if h.lower() not in {"respondentid", "respondent", "taskid", "task", "altid", "alt", "chosen"}]
    if not attr_cols:
        raise ValueError("No attribute columns found. Expected columns for each attribute level.")

    groups = defaultdict(list)
    for row in rows:
        key = f"{row[respondent_col]}__{row[task_col]}"
        groups[key].append(row)

    choice_sets = []
    for group_rows in groups.values():
        chosen = [r for r in group_rows if str(r[chosen_col]).strip() in {"1", "true", "True", "TRUE"}]
        if len(chosen) != 1:
            continue
        choice_sets.append(group_rows)

    if not choice_sets:
        raise ValueError("No valid choice sets found. Each task must have exactly one chosen alternative.")

    return attr_cols, choice_sets


def build_feature_names(attr_cols, choice_sets):
    levels_by_attr = {}
    for attr in attr_cols:
        levels = {str(row[attr]).strip() for row in [item for group in choice_sets for item in group]}
        levels_by_attr[attr] = sorted(levels)

    feature_names = []
    reference_levels = {}
    for attr in attr_cols:
        levels = levels_by_attr[attr]
        if not levels:
            continue
        reference_levels[attr] = levels[0]
        for level in levels[1:]:
            feature_names.append(f"{attr}::{level}")
    return feature_names, reference_levels


def fit_mnl(choice_sets, feature_names, iterations=400, lr=0.15, l2=0.002):
    k = len(feature_names)
    beta = [0.0] * k
    n = len(choice_sets)

    for _ in range(iterations):
        grad = [0.0] * k

        for choice_set in choice_sets:
            utilities = []
            for alt in choice_set:
                features = []
                for idx, fn in enumerate(feature_names):
                    attr, level = fn.split("::", 1)
                    features.append(1 if str(alt[attr]).strip() == level else 0)
                util = sum(f * beta[idx] for idx, f in enumerate(features))
                utilities.append(util)

            max_u = max(utilities)
            exps = [math.exp(u - max_u) for u in utilities]
            denom = sum(exps)
            probs = [e / denom for e in exps]

            for idx, alt in enumerate(choice_set):
                chosen = str(alt["Chosen"]).strip() in {"1", "true", "True", "TRUE"}
                diff = (1 if chosen else 0) - probs[idx]
                for j, fn in enumerate(feature_names):
                    attr, level = fn.split("::", 1)
                    feature_val = 1 if str(alt[attr]).strip() == level else 0
                    grad[j] += diff * feature_val

        for j in range(k):
            beta[j] += lr * (grad[j] / n - l2 * beta[j])

    return beta


def build_part_worths(attr_cols, reference_levels, feature_names, beta):
    part_worths = {}
    for attr in attr_cols:
        part_worths[attr] = {reference_levels[attr]: 0.0}

    for fn, b in zip(feature_names, beta):
        attr, level = fn.split("::", 1)
        part_worths[attr][level] = b

    return part_worths


def compute_importance(part_worths):
    ranges = {}
    for attr, levels in part_worths.items():
        vals = list(levels.values())
        ranges[attr] = max(vals) - min(vals)
    total = sum(ranges.values()) or 1
    importance = {attr: (rng / total) * 100 for attr, rng in ranges.items()}
    return importance


def analyze_choice_file(choice_csv_path, design_csv_path=None):
    with open(choice_csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows in {choice_csv_path}.")

    headers = reader.fieldnames or []
    lower_headers = {h.lower(): h for h in headers}

    respondent_col = lower_headers.get("respondentid") or lower_headers.get("respondent")
    task_col = lower_headers.get("taskid") or lower_headers.get("task")
    chosen_col = lower_headers.get("chosen") or lower_headers.get("choice")

    if not task_col:
        raise ValueError('Missing column "TaskID" (or "Task").')
    if not chosen_col:
        raise ValueError('Missing column "Chosen" (or "Choice").')

    for row in rows:
        if respondent_col is None:
            row["RespondentID"] = "R1"
        else:
            row.setdefault("RespondentID", "R1")

    if respondent_col is None:
        respondent_col = "RespondentID"

    attr_cols = [h for h in headers if h.lower() not in {"respondentid", "respondent", "taskid", "task", "altid", "alt", "chosen", "choice"}]
    if not attr_cols:
        raise ValueError("No attribute columns found in the response CSV.")

    levels_by_attr = {}
    for attr in attr_cols:
        unique = {str(row.get(attr, "")).strip() for row in rows}
        levels_by_attr[attr] = sorted(unique)

    feature_names = []
    reference_levels = {}
    for attr in attr_cols:
        levels = levels_by_attr[attr]
        if not levels:
            continue
        reference_levels[attr] = levels[0]
        for level in levels[1:]:
            feature_names.append(f"{attr}::{level}")

    groups = defaultdict(list)
    for row in rows:
        task_id = row.get(task_col)
        respondent_id = row.get(respondent_col) or "R1"
        if not task_id or not respondent_id:
            continue
        groups[(respondent_id, task_id)].append(row)

    valid_sets = []
    for alt_rows in groups.values():
        chosen = [r for r in alt_rows if str(r.get(chosen_col) or "").strip() in {"1", "true", "True", "TRUE"}]
        if len(chosen) == 1:
            valid_sets.append(alt_rows)

    if not valid_sets:
        raise ValueError("No valid choice sets detected. Make sure each task has exactly one chosen alternative (1/true).")

    beta = fit_mnl(valid_sets, feature_names)
    part_worths = build_part_worths(attr_cols, reference_levels, feature_names, beta)
    importance = compute_importance(part_worths)
    return part_worths, importance


def render_markdown_summary(part_worths, importance):
    lines = ["# Conjoint-Auswertung", "", "## Teilnutzenwerte", ""]
    for attr, levels in part_worths.items():
        lines.append(f"### {attr}")
        for level, value in sorted(levels.items(), key=lambda kv: str(kv[0])):
            lines.append(f"- {level}: {value:.3f}")
        lines.append("")

    lines.append("## Wichtigkeit (Importance)")
    for attr, value in sorted(importance.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {attr}: {value:.1f}%")
    lines.append("")
    return "\n".join(lines)


def generate_example_input(path):
    example = '''# Conjoint Input

## Attributes
- name: Preis
  levels:
    - 299 CHF
    - 499 CHF
    - 699 CHF

- name: Speicher
  levels:
    - 64 GB
    - 128 GB
    - 256 GB

- name: Akkulaufzeit
  levels:
    - 8h
    - 12h
    - 16h

- name: Marke
  levels:
    - Marke A
    - Marke B
    - Marke C

## Config
tasks: 10
alts_per_task: 3
'''
    Path(path).write_text(example, encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="CLI for conjoint design generation and analysis.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a conjoint design from a markdown input file.")
    generate_parser.add_argument("input", help="Markdown input file (e.g. example_input.md)")
    generate_parser.add_argument("--out", default="generated_design.csv", help="Output CSV path")

    llm_parser = subparsers.add_parser("llm", help="Generate a choice CSV by asking a local Ollama model to choose the preferred alternative per task.")
    llm_parser.add_argument("input", nargs="?", help="Markdown input file describing the attributes and levels")
    llm_parser.add_argument("--design", help="Optional existing design CSV generated by the 'generate' command. If provided, this is used instead of markdown input.")
    llm_parser.add_argument("--out", default="llm_choices.csv", help="Output CSV path")
    llm_parser.add_argument("--design-out", help="Optional path to save the design CSV before LLM choices are generated")
    llm_parser.add_argument("--model", default="gemma4:e2b", help="Ollama model name")
    llm_parser.add_argument("--profile", choices=["fast", "balanced", "quality"], default="fast", help="Ollama generation profile")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a choice CSV and write a markdown summary.")
    analyze_parser.add_argument("input", help="CSV file containing choices")
    analyze_parser.add_argument("--design", help="Optional design CSV for validation")
    analyze_parser.add_argument("--out", default="conjoint_summary.md", help="Output markdown summary path")

    example_parser = subparsers.add_parser("example", help="Create an example markdown input file.")
    example_parser.add_argument("--out", default="example_input.md", help="Write example input markdown to this path")

    args = parser.parse_args()

    if args.command == "generate":
        attributes, tasks, alts_per_task = parse_markdown_spec(args.input)
        design = generate_design(attributes, tasks, alts_per_task)
        out_path = Path(args.out)
        design_to_csv(design, attributes, out_path)
        print(f"Generated design with {tasks} tasks and {alts_per_task} alternatives per task -> {out_path}")
        return

    if args.command == "llm":
        if args.design:
            design, attributes = design_from_csv(args.design)
        else:
            if not args.input:
                raise ValueError("Provide either a markdown input file or --design path.")
            attributes, tasks, alts_per_task = parse_markdown_spec(args.input)
            design = generate_design(attributes, tasks, alts_per_task)
            if args.design_out:
                design_to_csv(design, attributes, args.design_out)
                print(f"Design saved to {args.design_out}")

        rows = generate_llm_choice_csv(attributes, design, model=args.model, profile=args.profile)
        out_path = Path(args.out)
        write_csv_rows(out_path, rows)
        print(f"LLM-generated choice data saved to {out_path}")
        return

    if args.command == "analyze":
        part_worths, importance = analyze_choice_file(args.input, args.design)
        summary = render_markdown_summary(part_worths, importance)
        out_path = Path(args.out)
        out_path.write_text(summary, encoding="utf-8")
        print(f"Analysis saved to {out_path}")
        print(summary)
        return

    if args.command == "example":
        generated_path = generate_example_input(args.out)
        print(f"Example markdown created at {generated_path}")


if __name__ == "__main__":
    main()
