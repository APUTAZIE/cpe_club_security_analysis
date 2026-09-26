#ifndef CONTACT_H
#define CONTACT_H

typedef struct
{
 char name[40];
 char phoneNumber[16];
} Contact;

int addContact(Contact *replace);
int deletefile(Contact *replace);

#endif
