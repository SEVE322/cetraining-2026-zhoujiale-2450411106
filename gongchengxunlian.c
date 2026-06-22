#include <stdio.h>

int main() {
    float num1, num2, result;
    char op;

    printf("====简易加减计算器====\n");
    printf("请输入计算式（格式：数字+符号+数字，例：5+3  9-2）：");
    // 读取数字、运算符、第二个数字
    scanf("%f%c%f", &num1, &op, &num2);

    // 判断运算符并计算
    if (op == '+') {
        result = num1 + num2;
        printf("计算结果：%.2f + %.2f = %.2f\n", num1, num2, result);
    } else if (op == '-') {
        result = num1 - num2;
        printf("计算结果：%.2f - %.2f = %.2f\n", num1, num2, result);
    } else {
        printf("错误！仅支持 + 、- 两种运算\n");
    }

    return 0;
}