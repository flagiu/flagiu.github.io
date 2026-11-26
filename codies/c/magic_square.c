#include<stdio.h>
#include<stdlib.h>
#include<time.h>

#define NDIM 3
#define NMAT 1.00e+08

unsigned int uRandom(unsigned int n) {
	return lrand48()%n;
}

void fillRandom(unsigned int m[NDIM][NDIM]) {
	unsigned int i,j, n=NDIM*NDIM;
	for(i=0; i<NDIM; i++) {
		for(j=0; j<NDIM; j++) {
			m[i][j] = 1 + uRandom(n);
		}
	}
	return;
}

void sort(unsigned int *a, unsigned int *b, unsigned int n) {
	// Bubblesort a and b according to a
	unsigned int i,j, tmp;
	for(i=0;i<n;i++) {
		for(j=i+1;j<n;j++) {
			if (a[i]>a[j]) {
				tmp = a[j];
				a[j] = a[i];
				a[i] = tmp;

				tmp = b[j];
				b[j] = b[i];
				b[i] = tmp;
			}
		}
	}
	return;
}

void fillRight(unsigned int m[NDIM][NDIM]) {
	unsigned int i,j, n=NDIM*NDIM;
	unsigned int a[n],b[n];
	for(i=0;i<n;i++) {
		a[i] = lrand48(); //random numbers
		b[i] = i+1; //numbers 1...n
	}
	sort(a,b,n); //equivalent to randomly shuffle b
	for(i=0;i<n;i++) {
		m[i/NDIM][i%NDIM] = b[i]; //assign shuffled numbers to m
	}
	return;
}

void printMatrix(unsigned int m[NDIM][NDIM]) {
	unsigned int i,j;
	for(i=0; i<NDIM; i++) {
		for(j=0; j<NDIM; j++) {
			printf("\t%u", m[i][j]);
		}
		printf("\n");
	}
	printf("\n");
	return;
}

int isMagic(unsigned int m[NDIM][NDIM]) {
	int false=0, true=1;
	unsigned int i,j, rows[NDIM]={0}, cols[NDIM]={0};
	for(i=0;i<NDIM;i++) {
		for(j=0;j<NDIM;j++) {
			rows[i] += m[i][j];
			cols[j] += m[i][j];
		}
	}
	// check if all rows' and cols' sums are equal
	for(i=0;i<NDIM;i++) {
		if(rows[i]!=cols[i]) return false;
		for(j=i+1;j<NDIM;j++) {
			if( rows[i]!=rows[j] || cols[i]!=cols[j]) return false;
		}
	}
	return true;
}

/////////////////////////////////////////////////////////

int main() {
	unsigned int square[NDIM][NDIM];
	double freq=0.0;
	srand48(time(NULL));

	for(int i=0; i<NMAT; i++) {
//		fillRandom(square);
		fillRight(square);
		if( isMagic(square) ) {
//			printf("iterazione = \t%d\tMAGIC!!!\n",i+1);
//			printMatrix(square);
			freq += 1.0;
		}
	}
	freq /= NMAT;
	printf("%f %f\n",NMAT, freq);
	return 0;
}
