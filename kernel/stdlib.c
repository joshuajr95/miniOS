

#include "stdlib.h"



void memcopy(void *dest, void *source, unsigned int num_bytes)
{
    int current = 0;

    char *dst = (char*)dest;
    char *src = (char*)source;

    while(current < num_bytes)
    {
        *dst++ = *src++;
        current++;
    }
}


void memset(void *dest, unsigned char val, unsigned int size)
{
    unsigned int current;

    while(current < size)
    {
        *((char*)dest + current) = val;
        current++;
    }
}