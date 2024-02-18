

#ifndef MISC_H
#define MISC_H


void memcpy(void *dest, void *source, unsigned int num_bytes);
void memset(void *dest, unsigned char val, unsigned int num_bytes);

int strlen(char *string);
int strnlen(char *string, int maxlen);
void strcpy(char *dest_string, char *source_string);
int strncpy(char *dest_string, char *source_string, int maxlen);




#endif