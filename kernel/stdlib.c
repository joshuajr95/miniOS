

#include "misc.h"



void memcpy(void *dest, void *source, unsigned int num_bytes)
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