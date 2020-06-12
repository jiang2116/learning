#include<iostream>
using namespace std;
int main() {
	int i;
	cin >> i;
	if (i % 5 == 0)
		cout << "可以被5整除。";
	else
		cout << "不可以被5整除。";
}