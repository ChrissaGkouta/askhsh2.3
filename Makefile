CC = gcc
CFLAGS = -O3 -fopenmp -Wall
TARGET = mergesort

all: $(TARGET)

$(TARGET): mergesort_omp.c
	$(CC) $(CFLAGS) -o $(TARGET) mergesort_omp.c

clean:
	rm -f $(TARGET)