import subprocess
import re
import csv
import sys
import os

# --- ΡΥΘΜΙΣΕΙΣ ΠΕΙΡΑΜΑΤΩΝ ---
EXECUTABLE = "./mergesort"
SIZES = [10_000_000, 100_000_000]  # Μεγέθη: 10^7 και 10^8
THREADS = [1, 2, 4, 8, 16, 32]     # Πλήθος νημάτων
RUNS = 4                           # Πόσες φορές να τρέξει το κάθε πείραμα για μέσο όρο
OUTPUT_FILE = "results.csv"

def compile_code():
    """Καλεί το make για μεταγλώττιση."""
    print("--- Compiling Code ---")
    try:
        # Καθαρισμός και compile
        subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, check=False)
        subprocess.run(["make"], check=True)
        print("Compilation successful.\n")
    except subprocess.CalledProcessError:
        print("Error: Compilation failed. Check your C code and Makefile.")
        sys.exit(1)

def parse_time(output):
    """Εξάγει τον χρόνο εκτέλεσης από την έξοδο του προγράμματος C."""
    # Ψάχνουμε τη γραμμή "Execution Time: X.XXXX seconds"
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
    # 1. Έλεγχος αν υπάρχει το makefile και compile
    if not os.path.exists("Makefile"):
        print("Error: Makefile not found.")
        sys.exit(1)
    
    compile_code()

    # 2. Άνοιγμα αρχείου CSV για εγγραφή
    with open(OUTPUT_FILE, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Header του CSV
        writer.writerow(["Size", "Threads", "Mode", "Average_Time_Sec"])
        
        print(f"{'Size':<12} | {'Mode':<10} | {'Threads':<8} | {'Avg Time':<10}")
        print("-" * 50)

        for size in SIZES:
            # --- Σειριακή Εκτέλεση (Mode 0) ---
            # Τρέχουμε μόνο μία φορά το σετ για Threads=1 (τυπικά) καθώς το Mode 0 αγνοεί τα threads
            serial_times = []
            for r in range(RUNS):
                t = run_single_experiment(size, 0, 1) # Mode 0 = Serial
                serial_times.append(t)
            
            avg_serial = sum(serial_times) / RUNS
            writer.writerow([size, 1, "Serial", f"{avg_serial:.6f}"])
            print(f"{size:<12} | {'Serial':<10} | {'1':<8} | {avg_serial:.6f} s")

            # --- Παράλληλη Εκτέλεση (Mode 1) ---
            for th in THREADS:
                parallel_times = []
                for r in range(RUNS):
                    t = run_single_experiment(size, 1, th) # Mode 1 = Parallel
                    parallel_times.append(t)
                
                avg_parallel = sum(parallel_times) / RUNS
                writer.writerow([size, th, "Parallel", f"{avg_parallel:.6f}"])
                print(f"{size:<12} | {'Parallel':<10} | {str(th):<8} | {avg_parallel:.6f} s")
            
            print("-" * 50)

    print(f"\nExperiments completed. Results saved in '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()