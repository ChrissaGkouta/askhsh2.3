#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include <time.h>

#define TASK_THRESHOLD 10000

// συνάρτηση συγχώνευσης (Merge) 
void merge(int *arr, int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    // Δημιουργία προσωρινών πινάκων
    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));

    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    i = 0; j = 0; k = l;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = L[i];
        i++; k++;
    }
    while (j < n2) {
        arr[k] = R[j];
        j++; k++;
    }

    free(L);
    free(R);
}

// Σειριακή έκδοση 
void mergesort_serial(int *arr, int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        mergesort_serial(arr, l, m);
        mergesort_serial(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

// Παράλληλη έκδοση
void mergesort_parallel_tasks(int *arr, int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        int size = r - l + 1;
        
        #pragma omp task shared(arr) if(size > TASK_THRESHOLD)
        mergesort_parallel_tasks(arr, l, m);

        #pragma omp task shared(arr) if(size > TASK_THRESHOLD)
        mergesort_parallel_tasks(arr, m + 1, r);

        #pragma omp taskwait
        
        merge(arr, l, m, r);
    }
}

// Συνάρτηση ελέγχου ορθότητας
void check_sorted(int *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            printf("Error: Array is NOT sorted at index %d (%d > %d)\n", i, arr[i], arr[i+1]);
            return;
        }
    }
    printf("Verification: Array is sorted.\n");
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <size> <mode: 0=serial, 1=parallel> <threads>\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    int mode = atoi(argv[2]);
    int threads = atoi(argv[3]);

    omp_set_num_threads(threads);

    int *arr = (int *)malloc(n * sizeof(int));
    
    srand(42); 
    for (int i = 0; i < n; i++) {
        arr[i] = rand();
    }

    printf("Sorting array of size %d using %d threads (%s)...\n", 
           n, threads, mode == 1 ? "Parallel" : "Serial");

    double start_time = omp_get_wtime();

    if (mode == 0) {
        mergesort_serial(arr, 0, n - 1);
    } else {
        #pragma omp parallel
        {
            #pragma omp single
            {
                mergesort_parallel_tasks(arr, 0, n - 1);
            }
        }
    }

    double end_time = omp_get_wtime();

    check_sorted(arr, n);
    printf("Execution Time: %f seconds\n", end_time - start_time);

    free(arr);
    return 0;
}
