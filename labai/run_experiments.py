#!/usr/bin/env python3
"""
Batch experiments for the 2x2 rotation puzzle.

Generates puzzles with a prescribed optimal depth and runs search algorithms.
Results are saved to CSV (detailed) and a summary CSV with averages.
"""
import argparse
import csv
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support
import multiprocessing as mp
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from algoritms import Stats, astar_h1, astar_h2, bfs, dfs, iddfs
from game_logic import State, generate_puzzle, tiles_to_string

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - tqdm may be absent
    tqdm = None


ResultRow = Dict[str, object]
AlgorithmFn = Callable[[State, Tuple[int, ...]], Stats]


def parse_depths(raw: str) -> List[int]:
    depths = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        val = int(part)
        if val <= 0:
            raise argparse.ArgumentTypeError("Depth values must be positive integers.")
        depths.append(val)
    if not depths:
        raise argparse.ArgumentTypeError("Provide at least one depth.")
    return depths


def build_algorithm_names(include_dfs: bool) -> List[str]:
    names = ["BFS"]
    if include_dfs:
        names.append("DFS")
    names.extend(["IDDFS", "A*(h1)", "A*(h2)"])
    return names


def solver_for_name(name: str, iddfs_limit: int) -> AlgorithmFn:
    if name == "BFS":
        return bfs
    if name == "DFS":
        return dfs
    if name == "IDDFS":
        return lambda s, g: iddfs(s, g, limit=iddfs_limit)
    if name == "A*(h1)":
        return astar_h1
    if name == "A*(h2)":
        return astar_h2
    raise ValueError(f"Unknown algorithm: {name}")


def timed_run(solver: AlgorithmFn, start_state: State,
              goal: Tuple[int, ...]) -> Tuple[Stats, float, Optional[int]]:
    t0 = time.perf_counter()
    stats = solver(start_state, goal)
    elapsed = time.perf_counter() - t0
    path_len = len(stats.path) - 1 if stats.path else None
    return stats, elapsed, path_len


def write_csv(path: Path, rows: List[ResultRow], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def average(nums: List[float]) -> float:
    return sum(nums) / len(nums) if nums else 0.0


def format_eta(seconds: float) -> str:
    secs = int(round(seconds))
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def make_row(task_id: int, rows: int, cols: int, depth_target: int, depth_opt: Optional[int],
             alg_name: str, stats: Stats, elapsed: float, path_len: Optional[int],
             seed: int, start_tiles: Tuple[int, ...], goal_tiles: Tuple[int, ...]) -> ResultRow:
    return {
        "task_id": task_id,
        "rows": rows,
        "cols": cols,
        "depth_target": depth_target,
        "depth_opt": depth_opt if depth_opt is not None else "",
        "algorithm": stats.heuristic_name if stats.heuristic_name else alg_name,
        "solved": stats.path is not None,
        "path_length": path_len if path_len is not None else "",
        "iterations": stats.iterations,
        "max_open": stats.max_open,
        "open_end": stats.open_end,
        "max_memory": stats.max_memory,
        "elapsed_time_sec": elapsed,
        "seed": seed,
        "start_state": tiles_to_string(start_tiles, rows, cols),
        "goal_state": tiles_to_string(goal_tiles, rows, cols),
    }


def _run_solver_process(queue, alg_name: str, iddfs_limit: int,
                        start_tiles: Tuple[int, ...], rows: int, cols: int,
                        goal_tiles: Tuple[int, ...]):
    solver = solver_for_name(alg_name, iddfs_limit)
    start_state = State(start_tiles, rows, cols)
    stats, elapsed, path_len = timed_run(solver, start_state, goal_tiles)
    stats.path = None  # убираем тяжёлый путь перед передачей через очередь
    queue.put((stats, elapsed, path_len))


def run_with_timeout(alg_name: str, iddfs_limit: int, start_tiles: Tuple[int, ...],
                     rows: int, cols: int, goal_tiles: Tuple[int, ...],
                     timeout_s: float) -> Tuple[Optional[Stats], Optional[float], Optional[int], bool]:
    """
    Запуск алгоритма в отдельном процессе с таймаутом.
    Возвращает (stats, elapsed, path_len, timed_out).
    """
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_run_solver_process,
                    args=(q, alg_name, iddfs_limit, start_tiles, rows, cols, goal_tiles))
    p.start()
    p.join(timeout_s)
    if p.is_alive():
        p.terminate()
        p.join()
        return None, None, None, True
    if q.empty():
        return None, None, None, True
    stats, elapsed, path_len = q.get()
    return stats, elapsed, path_len, False


def solve_task(task: Dict[str, object], algorithm_names: Iterable[str], iddfs_limit: int,
               timeout_s: float) -> List[ResultRow]:
    rows = int(task["rows"])
    cols = int(task["cols"])
    depth_target = int(task["depth_target"])
    task_id = int(task["task_id"])
    seed = int(task["seed"])
    start_tiles: Tuple[int, ...] = task["start_tiles"]  # type: ignore
    goal_tiles: Tuple[int, ...] = task["goal_tiles"]  # type: ignore

    depth_opt: Optional[int] = None
    rows_out: List[ResultRow] = []
    for alg_name in algorithm_names:
        stats, elapsed, path_len, timed_out = run_with_timeout(
            alg_name, iddfs_limit, start_tiles, rows, cols, goal_tiles, timeout_s)
        if not timed_out and alg_name == "BFS":
            depth_opt = path_len
        if timed_out or stats is None:
            rows_out.append({
                "task_id": task_id,
                "rows": rows,
                "cols": cols,
                "depth_target": depth_target,
                "depth_opt": depth_opt if depth_opt is not None else "-",
                "algorithm": alg_name,
                "solved": False,
                "path_length": "-",
                "iterations": "-",
                "max_open": "-",
                "open_end": "-",
                "max_memory": "-",
                "elapsed_time_sec": timeout_s,
                "seed": seed,
                "start_state": tiles_to_string(start_tiles, rows, cols),
                "goal_state": tiles_to_string(goal_tiles, rows, cols),
            })
        else:
            rows_out.append(make_row(task_id, rows, cols, depth_target, depth_opt,
                                     alg_name, stats, elapsed, path_len, seed,
                                     start_tiles, goal_tiles))
    # Не валим весь прогон, если BFS за таймаут не дал глубину:
    # в таком случае depth_opt может остаться None или "-".
    if depth_opt is None:
        depth_opt = "-"
    return rows_out
    return rows_out


def build_summary(rows: List[ResultRow]) -> List[ResultRow]:
    grouped: Dict[Tuple[int, str], Dict[str, List[float]]] = {}
    for row in rows:
        key = (int(row["depth_target"]), str(row["algorithm"]))
        grp = grouped.setdefault(key, {
            "iterations": [],
            "max_open": [],
            "open_end": [],
            "max_memory": [],
            "elapsed_time_sec": [],
            "path_length": [],
            "runs": 0,
            "solved": 0,
        })
        grp["runs"] += 1
        def add_if_number(lst: List[float], val):
            try:
                lst.append(float(val))
            except (TypeError, ValueError):
                pass
        add_if_number(grp["iterations"], row["iterations"])
        add_if_number(grp["max_open"], row["max_open"])
        add_if_number(grp["open_end"], row["open_end"])
        add_if_number(grp["max_memory"], row["max_memory"])
        add_if_number(grp["elapsed_time_sec"], row["elapsed_time_sec"])
        if row["path_length"] not in ("", None, "-"):
            try:
                grp["path_length"].append(float(row["path_length"]))
                grp["solved"] += 1
            except (TypeError, ValueError):
                pass

    summary_rows: List[ResultRow] = []
    for (depth, alg), grp in sorted(grouped.items()):
        summary_rows.append({
            "depth_target": depth,
            "algorithm": alg,
            "runs": grp["runs"],
            "solved": grp["solved"],
            "avg_iterations": average(grp["iterations"]),
            "avg_max_open": average(grp["max_open"]),
            "avg_open_end": average(grp["open_end"]),
            "avg_max_memory": average(grp["max_memory"]),
            "avg_elapsed_time": average(grp["elapsed_time_sec"]),
            "avg_path_length": average(grp["path_length"]) if grp["path_length"] else "",
        })
    return summary_rows


def run() -> None:
    parser = argparse.ArgumentParser(description="Batch runner for puzzle search experiments.")
    parser.add_argument("--rows", type=int, default=4, help="Number of rows in the board.")
    parser.add_argument("--cols", type=int, default=4, help="Number of columns in the board.")
    parser.add_argument("--depths", default="2,4,6,8,10",
                        help="Comma separated optimal depths to generate (e.g., 2,4,6,8,10).")
    parser.add_argument("--tasks-per-depth", type=int, default=5,
                        help="How many tasks to generate for each depth.")
    parser.add_argument("--seed", type=int, default=123, help="Master seed for reproducibility.")
    parser.add_argument("--output", required=True,
                        help="Path to the detailed CSV results file.")
    parser.add_argument("--summary", help="Optional path for the summary CSV "
                                          "(defaults to <output> with _summary suffix).")
    parser.add_argument("--include-dfs", action="store_true",
                        help="Also run DFS in addition to the required algorithms.")
    parser.add_argument("--iddfs-limit", type=int, default=20,
                        help="Depth limit for each IDDFS iteration.")
    parser.add_argument("--max-tries", type=int, default=5000,
                        help="Maximum generation attempts per puzzle to achieve the exact depth.")
    parser.add_argument("--jobs", type=int, default=1,
                        help="Number of worker processes to use for running algorithms (generation stays sequential).")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout in seconds for each algorithm run; on timeout results are marked with '-'.")
    args = parser.parse_args()

    depths = parse_depths(str(args.depths))
    if args.rows < 2 or args.cols < 2:
        raise SystemExit("Rows and cols must be at least 2.")

    output_path = Path(args.output)
    summary_path = Path(args.summary) if args.summary else output_path.with_name(
        f"{output_path.stem}_summary{output_path.suffix}")

    master_rng = random.Random(args.seed)
    tasks = []
    total_to_generate = len(depths) * args.tasks_per_depth
    print(f"Генерация задач: всего {total_to_generate} (depths={depths})...")
    gen_start = time.perf_counter()
    gen_bar = tqdm(total=total_to_generate, unit="task", desc="Генерация") if tqdm else None
    for depth in depths:
        generated = 0
        seed_attempts = 0
        while generated < args.tasks_per_depth:
            puzzle_seed = master_rng.randint(0, 2**31 - 1)
            rng = random.Random(puzzle_seed)
            try:
                start_state, goal_state, _ = generate_puzzle(
                    args.rows, args.cols, depth, rng, max_tries=args.max_tries)
            except RuntimeError:
                seed_attempts += 1
                # Try more seeds before giving up entirely.
                if seed_attempts > 50:
                    raise RuntimeError(f"Could not generate task for depth={depth} "
                                       f"after {seed_attempts} seeds. Try raising --max-tries.")
                continue
            tasks.append({
                "task_id": len(tasks) + 1,
                "depth_target": depth,
                "seed": puzzle_seed,
                "start_tiles": start_state.tiles,
                "goal_tiles": goal_state.tiles,
                "rows": start_state.rows,
                "cols": start_state.cols,
            })
            generated += 1
            if gen_bar:
                gen_bar.update(1)
                gen_bar.set_postfix_str(f"d={depth} seed={puzzle_seed}")
            else:
                print(f"[генерация] {len(tasks)}/{total_to_generate} d={depth} seed={puzzle_seed}",
                      end="\r", flush=True)
    if gen_bar:
        gen_bar.close()
    else:
        print()
    print(f"Генерация завершена за {time.perf_counter() - gen_start:.2f}s. Старт решения...")
    algorithm_names = build_algorithm_names(include_dfs=args.include_dfs)
    total_runs = len(tasks) * len(algorithm_names)

    results: List[ResultRow] = []

    # Progress tracking
    start_wall = time.perf_counter()
    done_runs = 0
    use_tqdm = tqdm is not None
    bar = tqdm(total=total_runs, unit="run", desc="Решение") if use_tqdm else None

    def update_progress(status: str):
        nonlocal done_runs
        done_runs += 1
        elapsed = time.perf_counter() - start_wall
        avg = elapsed / done_runs
        eta = avg * (total_runs - done_runs)
        if bar:
            bar.update(1)
            bar.set_postfix_str(f"{status} | avg={avg:.2f}s eta={format_eta(eta)}")
        else:
            print(f"[{done_runs}/{total_runs} ({done_runs/total_runs*100:.1f}%)] "
                  f"{status} avg={avg:.2f}s eta={format_eta(eta)}", end="\r", flush=True)

    if args.jobs <= 1:
        for task in tasks:
            rows_out = solve_task(task, algorithm_names, args.iddfs_limit, args.timeout)
            for row in rows_out:
                results.append(row)
                status = f"d={row['depth_target']} task={row['task_id']} alg={row['algorithm']}"
                update_progress(status)
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            future_to_task = {
                ex.submit(solve_task, task, algorithm_names, args.iddfs_limit, args.timeout): task
                for task in tasks
            }
            for fut in as_completed(future_to_task):
                try:
                    rows_out = fut.result()
                except Exception as exc:  # pragma: no cover - error path
                    if bar:
                        bar.close()
                    print(f"\nОшибка в задаче {future_to_task[fut].get('task_id')}: {exc}")
                    raise
                for row in rows_out:
                    results.append(row)
                    status = f"d={row['depth_target']} task={row['task_id']} alg={row['algorithm']}"
                    update_progress(status)

    if bar:
        bar.close()
    else:
        print()  # finish progress line

    write_csv(output_path, results, [
        "task_id", "rows", "cols", "depth_target", "depth_opt", "algorithm",
        "solved", "path_length", "iterations", "max_open", "open_end", "max_memory",
        "elapsed_time_sec", "seed", "start_state", "goal_state",
    ])

    summary_rows = build_summary(results)
    write_csv(summary_path, summary_rows, [
        "depth_target", "algorithm", "runs", "solved",
        "avg_iterations", "avg_max_open", "avg_open_end",
        "avg_max_memory", "avg_elapsed_time", "avg_path_length",
    ])

    print(f"Saved detailed results to: {output_path}")
    print(f"Saved summary results to:  {summary_path}")


if __name__ == "__main__":
    freeze_support()
    run()
