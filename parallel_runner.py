import subprocess
import concurrent.futures
import json
import os
import time
from datetime import datetime
import argparse
import re


def extract_stats_and_config(stdout_text):
    """
    Извлекает статистику и конфигурацию бота из вывода скрипта
    """
    stats = {
        "wins": None,
        "loses": None, 
        "draw": None,
        "wins_percent": None,
        "loses_percent": None,
        "draw_percent": None,
        "total_games": None
    }
    
    config_info = {
        "bot_matchup": None,
        "bot_config_name": None
    }
    
    # Ищем строки с результатами
    win_match = re.search(r'wins:\s*(\d+)\s*/\s*(\d+)\s*=\s*([\d.]+)%', stdout_text)
    lose_match = re.search(r'loses:\s*(\d+)\s*/\s*(\d+)\s*=\s*([\d.]+)%', stdout_text)
    draw_match = re.search(r'draw:\s*(\d+)\s*/\s*(\d+)\s*=\s*([\d.]+)%', stdout_text)
    
    # Ищем информацию о противостоянии ботов
    matchup_match = re.search(r'(const_\d+_lvl_bot VS .+|.+ VS const_\d+_lvl_bot)', stdout_text)
    
    if win_match:
        stats["wins"] = int(win_match.group(1))
        stats["total_games"] = int(win_match.group(2))
        stats["wins_percent"] = float(win_match.group(3))
    
    if lose_match:
        stats["loses"] = int(lose_match.group(1))
        stats["loses_percent"] = float(lose_match.group(3))
    
    if draw_match:
        stats["draw"] = int(draw_match.group(1))
        stats["draw_percent"] = float(draw_match.group(3))
    
    if matchup_match:
        config_info["bot_matchup"] = matchup_match.group(1)
    
    return stats, config_info


def get_bot_config_details(script_path):
    """
    Извлекает детали конфигурации бота из скрипта
    """
    try:
        import sys
        import os
        
        # Добавляем путь к скрипту в sys.path
        script_dir = os.path.dirname(os.path.abspath(script_path))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Импортируем модули из скрипта
        from constants import Bot_3_lvl, Bot_4_lvl
        from explore_scrypts import hz
        
        config_details = {
            "hz_second_bot": hz.second_bot,
            "hz_bot_difficult": hz.bot_difficult,
            "hz_play_vs_bot": hz.play_vs_bot,
            "hz_gravity": hz.GRAVITY,
            "hz_shape": hz.SHAPE,
            "bot_config": None
        }
        
        # Получаем конфигурацию основного бота (hz.bot_difficult)
        if hz.bot_difficult == 3:
            bot_configs = Bot_3_lvl()
            config_details["main_bot_config"] = {
                "type": "Bot_3_lvl",
                "level": hz.bot_difficult,
                "own_weights": getattr(bot_configs, 'own_weights', None),
                "enemy_weights": getattr(bot_configs, 'enemy_weights', None)
            }
        elif hz.bot_difficult == 4:
            bot_configs = Bot_4_lvl()
            config_details["main_bot_config"] = {
                "type": "Bot_4_lvl", 
                "level": hz.bot_difficult,
                "win_points": getattr(bot_configs, 'win_points', None),
                "win_points_force": getattr(bot_configs, 'win_points_force', None),
                "force_weight": getattr(bot_configs, 'force_weight', None),
                "fork_weights": getattr(bot_configs, 'fork_weights', None),
                "own_weights": getattr(bot_configs, 'own_weights', None),
                "enemy_weights": getattr(bot_configs, 'enemy_weights', None),
                "odd_dead_points": getattr(bot_configs, 'odd_dead_points', None),
                "common_3rd_dead_point": getattr(bot_configs, 'common_3rd_dead_point', None),
                "own_3rd_dead_point": getattr(bot_configs, 'own_3rd_dead_point', None),
                "line_weights": getattr(bot_configs, 'line_weights', None),
                "third_points_lines": getattr(bot_configs, 'third_points_lines', None)
            }
        
        # Также получаем конфигурацию второго бота (hz.second_bot) для полноты
        if hz.second_bot == 3:
            second_bot_configs = Bot_3_lvl()
            config_details["second_bot_config"] = {
                "type": "Bot_3_lvl",
                "level": hz.second_bot,
                "name": getattr(second_bot_configs, 'name', 'main_3_lvl_bot'),
                "own_weights": getattr(second_bot_configs, 'own_weights', None),
                "enemy_weights": getattr(second_bot_configs, 'enemy_weights', None)
            }
        elif hz.second_bot == 4:
            second_bot_configs = Bot_4_lvl()
            config_details["second_bot_config"] = {
                "type": "Bot_4_lvl", 
                "level": hz.second_bot,
                "name": getattr(second_bot_configs, 'name', 'test_4_lvl_bot_0_no_force_moves'),
                "win_points": getattr(second_bot_configs, 'win_points', None),
                "win_points_force": getattr(second_bot_configs, 'win_points_force', None),
                "force_weight": getattr(second_bot_configs, 'force_weight', None),
                "fork_weights": getattr(second_bot_configs, 'fork_weights', None),
                "own_weights": getattr(second_bot_configs, 'own_weights', None),
                "enemy_weights": getattr(second_bot_configs, 'enemy_weights', None),
                "odd_dead_points": getattr(second_bot_configs, 'odd_dead_points', None),
                "common_3rd_dead_point": getattr(second_bot_configs, 'common_3rd_dead_point', None),
                "own_3rd_dead_point": getattr(second_bot_configs, 'own_3rd_dead_point', None),
                "line_weights": getattr(second_bot_configs, 'line_weights', None),
                "third_points_lines": getattr(second_bot_configs, 'third_points_lines', None)
            }
        
        return config_details
        
    except Exception as e:
        return {"error": str(e)}


def run_script(script_path, run_id, output_dir="parallel_results"):
    """
    Запускает скрипт и возвращает результат
    """
    try:
        # Создаем директорию для результатов если не существует
        os.makedirs(output_dir, exist_ok=True)
        
        # Запускаем скрипт
        start_time = time.time()
        
        # Используем sys.executable чтобы запустить тот же Python что и текущий процесс
        import sys
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(script_path))
        )
        end_time = time.time()
        
        # Извлекаем статистику из вывода
        stats, config_info = extract_stats_and_config(result.stdout)
        
        # Сохраняем результат каждого запуска
        run_result = {
            "run_id": run_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "stats": stats,
            "config_info": config_info
        }
        
        # Сохраняем результат в отдельный файл
        result_file = os.path.join(output_dir, f"run_{run_id}.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(run_result, f, indent=2, ensure_ascii=False)
        
        status = "SUCCESS" if result.returncode == 0 else "FAILED"
        win_info = f"Wins: {stats['wins_percent']:.1f}%" if stats['wins_percent'] is not None else "No stats"
        print(f"Run {run_id}: {status} ({win_info}, Duration: {end_time - start_time:.2f}s)")
        
        return run_result
        
    except Exception as e:
        error_result = {
            "run_id": run_id,
            "error": str(e),
            "success": False,
            "stats": {}
        }
        print(f"Run {run_id}: ERROR - {str(e)}")
        return error_result


def combine_results(output_dir="parallel_results", final_output="combined_results.json"):
    """
    Объединяет все результаты в один файл и суммирует статистику
    """
    combined_results = {
        "timestamp": datetime.now().isoformat(),
        "total_runs": 0,
        "successful_runs": 0,
        "failed_runs": 0,
        "total_duration": 0,
        "aggregated_stats": {
            "total_games": 0,
            "total_wins": 0,
            "total_loses": 0,
            "total_draws": 0,
            "average_win_rate": 0.0,
            "average_lose_rate": 0.0,
            "average_draw_rate": 0.0
        },
        "results": []
    }
    
    # Читаем все файлы результатов
    valid_runs = []
    for filename in os.listdir(output_dir):
        if filename.startswith("run_") and filename.endswith(".json"):
            filepath = os.path.join(output_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    combined_results["results"].append(result)
                    combined_results["total_runs"] += 1
                    
                    if result.get("success", False):
                        combined_results["successful_runs"] += 1
                        combined_results["total_duration"] += result.get("duration", 0)
                        
                        # Собираем статистику для агрегации
                        stats = result.get("stats", {})
                        if stats.get("total_games") is not None:
                            valid_runs.append(stats)
                    else:
                        combined_results["failed_runs"] += 1
                        
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    
    # Сортируем результаты по run_id
    combined_results["results"].sort(key=lambda x: x.get("run_id", 0))
    
    # Агрегируем статистику
    if valid_runs:
        total_games = sum(run["total_games"] for run in valid_runs)
        total_wins = sum(run.get("wins", 0) for run in valid_runs)
        total_loses = sum(run.get("loses", 0) for run in valid_runs)
        total_draws = sum(run.get("draw", 0) for run in valid_runs)
        
        combined_results["aggregated_stats"].update({
            "total_games": total_games,
            "total_wins": total_wins,
            "total_loses": total_loses,
            "total_draws": total_draws,
            "average_win_rate": (total_wins / total_games * 100) if total_games > 0 else 0,
            "average_lose_rate": (total_loses / total_games * 100) if total_games > 0 else 0,
            "average_draw_rate": (total_draws / total_games * 100) if total_games > 0 else 0
        })
    
    # Сохраняем объединенный результат
    with open(final_output, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nCombined results saved to: {final_output}")
    print(f"Total runs: {combined_results['total_runs']}")
    print(f"Successful: {combined_results['successful_runs']}")
    print(f"Failed: {combined_results['failed_runs']}")
    print(f"Total duration: {combined_results['total_duration']:.2f}s")
    
    # Выводим агрегированную статистику
    agg = combined_results["aggregated_stats"]
    if agg["total_games"] > 0:
        print(f"\nAggregated Statistics:")
        print(f"Total games played: {agg['total_games']}")
        print(f"Total wins: {agg['total_wins']} ({agg['average_win_rate']:.1f}%)")
        print(f"Total loses: {agg['total_loses']} ({agg['average_lose_rate']:.1f}%)")
        print(f"Total draws: {agg['total_draws']} ({agg['average_draw_rate']:.1f}%)")
    
    return combined_results


def save_to_history(combined_results, script_path, history_file="bot_performance_history.json"):
    """
    Сохраняет результаты в историческую базу данных
    """
    # Получаем детали конфигурации бота
    bot_config_details = get_bot_config_details(script_path)
    
    # Создаем запись для истории
    history_entry = {
        "timestamp": combined_results["timestamp"],
        "total_runs": combined_results["total_runs"],
        "successful_runs": combined_results["successful_runs"],
        "failed_runs": combined_results["failed_runs"],
        "total_duration": combined_results["total_duration"],
        "aggregated_stats": combined_results["aggregated_stats"],
        "bot_configuration": bot_config_details,
        "bot_matchup": combined_results["results"][0].get("config_info", {}).get("bot_matchup") if combined_results["results"] else None
    }
    
    # Читаем существующую историю
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read history file {history_file}: {e}")
            history = []
    
    # Добавляем новую запись
    history.append(history_entry)
    
    # Сохраняем обновленную историю
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"Results saved to history: {history_file}")
        print(f"Total historical entries: {len(history)}")
    except Exception as e:
        print(f"Error saving to history: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run script in parallel multiple times")
    parser.add_argument("script", help="Path to the script to run")
    parser.add_argument("-n", "--num-runs", type=int, default=5, help="Number of parallel runs")
    parser.add_argument("-w", "--workers", type=int, default=None, help="Number of worker threads")
    parser.add_argument("-o", "--output", default="combined_results.json", help="Output file for combined results")
    parser.add_argument("--output-dir", default="parallel_results", help="Directory for individual run results")
    parser.add_argument("--history", default="bot_performance_history.json", help="History file for all results")
    parser.add_argument("--no-history", action="store_true", help="Don't save to history file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.script):
        print(f"Error: Script {args.script} not found")
        return
    
    print(f"Running {args.script} {args.num_runs} times in parallel...")
    print(f"Workers: {args.workers or 'auto'}")
    print(f"Output directory: {args.output_dir}")
    print(f"Final output: {args.output}")
    print("-" * 50)
    
    # Очищаем предыдущие результаты
    if os.path.exists(args.output_dir):
        for filename in os.listdir(args.output_dir):
            if filename.startswith("run_") and filename.endswith(".json"):
                os.remove(os.path.join(args.output_dir, filename))
    
    # Запускаем параллельно
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_script, args.script, i, args.output_dir)
            for i in range(args.num_runs)
        ]
        
        # Ждем завершения всех задач
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error in parallel execution: {e}")
    
    end_time = time.time()
    
    print("-" * 50)
    print(f"All runs completed in {end_time - start_time:.2f}s")
    
    # Объединяем результаты
    combined_results = combine_results(args.output_dir, args.output)
    
    # Сохраняем в историю если нужно
    if not args.no_history:
        save_to_history(combined_results, args.script, args.history)
    
    return combined_results


if __name__ == "__main__":
    main()