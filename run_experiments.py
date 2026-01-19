import subprocess
import re
import sys
import os

EXECUTABLE = "./mergesort"
SIZES = [10_000, 100_000, 10_000_000, 100_000_000] 
THREADS = [1, 2, 4, 8, 16]     
RUNS = 4                         

def compile_code():
    print("--- Compiling Code ---")
    try:
        
        subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, check=False)
        subprocess.run(["make"], check=True)
        print("Compilation successful.\n")
    except subprocess.CalledProcessError:
        print("Error: Compilation failed.")
        sys.exit(1)

def parse_time(output):
    """Εξάγει τον χρόνο εκτέλεσης από την έξοδο του προγράμματος C."""
    match = re.search(r"Execution Time:\s*([0-9\.]+)", output)
    if match:
        return float(match.group(1))
    else:
        return None

def run_single_experiment(size, mode, num_threads):
    """Τρέχει το εκτελέσιμο μία φορά και επιστρέφει τον χρόνο."""
    cmd = [EXECUTABLE, str(size), str(mode), str(num_threads)]
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        time_taken = parse_time(result.stdout)
        if time_taken is None:
            print(f"Warning: Could not parse time from output:\n{result.stdout}")
            return 0.0
        return time_taken
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(e.stderr)
        return 0.0

def main():
    if not os.path.exists("Makefile"):
        print("Error: Makefile not found.")
        sys.exit(1)
    
    compile_code()

    print(f"{'Size (N)':<12} | {'Thr':<4} | {'Avg Serial(s)':<15} | {'Avg Parallel(s)':<15} | {'Speedup':<8}")
    print("-" * 75)

    for size in SIZES:
        t_serial_total = 0
        for _ in range(RUNS):
            t_serial_total += run_single_experiment(size, 0, 1)
        avg_serial = t_serial_total / RUNS
        
        print(f"{size:<12} | {'1':<4} | {avg_serial:.6f}        | {avg_serial:.6f}        | 1.00")

        for th in THREADS:
            if th == 1: continue 
            
            t_parallel_total = 0
            for _ in range(RUNS):
                t_parallel_total += run_single_experiment(size, 1, th)
            avg_parallel = t_parallel_total / RUNS
            
            # Υπολογισμός Speedup
            if avg_parallel > 0:
                speedup = avg_serial / avg_parallel
            else:
                speedup = 0.0
            
            print(f"{size:<12} | {str(th):<4} | {avg_serial:.6f}        | {avg_parallel:.6f}        | {speedup:.2f}")
        
        print("-" * 75) 

if __name__ == "__main__":
    main()
