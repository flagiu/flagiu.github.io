#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>

#define NMAX 1e+08
#define PRINTMAX 1e+05

double dRan(double min, double max) {
	return drand48()*(max-min) + min;
}

double isInEllipse(double x, double y, double ax, double ay, double theta) {
	return ( (x*x)/(ax*ax) + (y*y)/(ay*ay) <= 1.0 );
}

unsigned int askNp() {
	int res=0, n=0;
	while(n<=0 || n>NMAX || res!=1){
		fprintf(stderr, "Inserisci il numero di punti Hit and Miss:\n");
		res=scanf("%d",&n);
		while('\n'!=getchar());
		if(n<=0 || n>NMAX) fprintf(stderr, "Errore: deve essere positivo e minore di %d.\n",(int)NMAX);
		if(res!=1) fprintf(stderr, "Errore durante la lettura dell'input (scanf returned %d).\n", res);
	}
	return (unsigned int)n;
}

/////////////////////////////////////////////////////////

int main() {
	int i,hit;
	unsigned int Np, Nh=0;
	double a,b, A, Atrue, x,y;
	char inFile[]="ellissi.in";
	char outFile[]="ellissi.punti.out";
	srand48(time(NULL));
	FILE *fp;

	// read number of points from terminal
	Np = askNp();
	// read ellipses' semiaxes from file
	fp = fopen("ellissi.in","r");
	i = fscanf(fp,"%lf %lf", &a, &b);
	if(i!=2) {
		fprintf(stderr,"Error in reading input file %s. Abort.",inFile);
		exit(1);
	}
	fclose(fp);
	if(a<b){ // take a>=b: switch values otherwise
		x=a; // temporary variable
		a=b;
		b=x;
	}
	// algorithm
	fp = fopen(outFile,"w");
	for(i=0; i<Np; i++) {
		x = dRan(-a, a);
		y = dRan(-a, a);
		hit =  isInEllipse(x,y,a,b,0.0) && isInEllipse(x,y,b,a,0.0);
		if(hit) Nh++;
		if(i<PRINTMAX) fprintf(fp, "%f %f %d\n", x,y, hit);
	}
	fclose(fp);
	// results
	A = (2*a)*(2*a)*Nh/(double)Np;
	fprintf(stdout,"%u %f\n",Np,A);
	Atrue = 4*a*b*atan(b/a);
	fprintf(stderr,"Area vera:\t%f\n",Atrue);
	return 0;
}
