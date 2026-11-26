#include<stdio.h>
#include<math.h>

#define N 100
#define NPOINTS 10000

double f(double x, double A, double B) {
	double y=0.0, Apow=A, Bpow=1.0, xx = 2*M_PI*x;
	for(int n=1; n<=N; n++) {
		y += cos(Bpow * xx) / Apow;
		Apow *= A; //Apow(n) = A**n
		Bpow *= B; // Bpow(n) = B**(n-1)
	}
	return y;
}

/////////////////////////////////////////////////////////

int main() {
	double A,B,x,dx;
	A = 1.5;
	B = 2.0;
	// if A<B and B is integer,
	// then for N-->infty f(x,A,B) is fractal in 0<x<1
	dx = 1.0/NPOINTS;
	for(int i=0; i<=NPOINTS; i++) {
		x = 0.0 + i*dx;
		printf("%f %f\n", x,f(x,A,B));
	}
	return 0;
}
