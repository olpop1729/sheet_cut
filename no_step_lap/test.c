#include <stdio.h>
int main(){
	int a[4];
	for(int i=0;i<sizeof(a);i++) {
		printf("%d\n",a[i]);
	}
	}
}
