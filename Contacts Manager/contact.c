#include "contact.h"
#include <stdio.h>
#include <string.h>

int addContact(Contact *replace)
{
  printf("Enter Name => ");
  fgets(replace->name, sizeof(replace->name), stdin);
  replace->name[strcspn(replace->name, "\n")] = '\0';

  printf("Enter Phone Number => ");
  fgets(replace->phoneNumber, sizeof(replace->phoneNumber), stdin);
  replace->phoneNumber[strcspn(replace->phoneNumber, "\n")] = '\0';

}
int deletefile(Contact *replace)
{
}
