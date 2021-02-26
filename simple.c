#include <stdio.h>

int findMin(int *arr,int n);
void resetDistances(int *arr, int pl, int index);
void showCut( int n);


int main(int argc, char **argv) {

	//************************************** Input block ***************************************

	//number of holes
	int nh = 4;
	// hole positions
	int h[nh];
	h[0] = 100;
	h[1] = 300;
	h[2] = 500;
	h[3] = 700;

	//number of v's
	int nv = 2;
	//v positions
	int v[2];
	v[0] = 200;
	v[1] = 600;

	//number of +45's
	int np45=1;
	//position of +45's
	int p45[1];
	p45[0] = 0;

	//number of -45's
	int nm45=1;
	//postion of -45's
	int m45[1];
	m45[0] = 400;

	//distance between 45 and V cutters
	int dav = 4335;
	//distance between hole and V cutters
	int dhv = 1250;

	//coil start distance with respec to V
	int coil_start_pos = 0;

	//pattern length
	int pl = 800;

	//************************************** Input block end ************************************


	//******************************* Intialize distance vector *********************************
	int ld = nh+nv+np45+nm45;
	int dist[ld];

	//cut to index mapping
	char map[ld];

	for(int i=0;i<ld;i++){
		// 0 to nv-1 are V
		if(i < nv && i >= 0) {
			dist[i] = coil_start_pos + v[i];
			map[i] = 'v';
		}
		//nv to nv+nh-1 are H
		else if ( i-nv >= 0 && i < nv+nh){
			dist[i] = coil_start_pos + dhv + h[i-nv];
			map[i] = 'h';
		}
		//nv+nh+np45 are p45(+45)
		else if (i-nv-nh >= 0 && i < nv+nh+np45) {
			dist[i] = coil_start_pos + dav + p45[i-nv-nh];
			map[i] = 'p';
		}
		// remainin are m45(-45)
		else {
			dist[i] = coil_start_pos + dav + m45[i-nv-nh-np45];
			map[i] = 'm';
		}

	}

	// for ( int i=0; i<ld;i++) {
	// 	printf("%d\n", dist[i]);
	// }

	//********************************************************************************************




	//*********************************** Main block *********************************************

	int sheet_length = 10000;
	int start = 0;
	int min=0;


	while (start < sheet_length) {
		min = findMin(dist, ld);
		printf("Feed - %d\n", min);
		for (int i=0;i<ld;i++) {
			if (dist[i] == min) {
				if (i >= 0 && i < nv) {
					showCut(0);
				}
				else if(i-nv >= 0 && i < nv+nh) {
					showCut(1);
				}
				else if(i-nv-nh >= 0 && i < nv+nh+np45){
					showCut(2);
				}
				else {
					showCut(3);
				}
				resetDistances(dist,pl,i);
			} else {
				dist[i] = dist[i] - min;
			}
		}
		for(int i=0;i<ld;i++){
			printf("%c\t",map[i]);
		}
		printf("\n");
		for(int i=0;i<ld;i++){
			printf("%d\t",dist[i]);
		}
		char str[20];
		scanf("%s",str );
		start = start + min;

	}


}


int findMin(int *arr,int n) {
	int min = arr[0];
	for(int i=0;i<n;i++){
		if (arr[i] < min){
			min = arr[i];
		}
	}
	return min;
}

void resetDistances(int *arr, int pl, int index) {
	arr[index] = pl;
}

void showCut(int n){
	switch(n) {
		case 0:
			printf("Cut V \n");
			break;
		case 1:
			printf("Cut H\n");
			break;
		case 2:
			printf("Cut +45\n");
			break;
		case 3:
			printf("Cut -45\n");
			break;

	}
}
