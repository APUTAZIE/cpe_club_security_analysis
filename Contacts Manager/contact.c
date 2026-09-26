#include "contact.h"
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

void printsmenu()
{
  puts("Contact Manager");
  puts("(1) Add contact");
  puts("(2) Delete contact file");
  puts("(3) Exit");
}

int addContact(Contact *replace)
{
  char symbol = '\0';
  while(true)
  {
  printf("Enter Name => ");
  fgets(replace->name, sizeof(replace->name), stdin);
  replace->name[strcspn(replace->name, "\n")] = '\0';

  printf("Enter Phone Number => ");
  fgets(replace->phoneNumber, sizeof(replace->phoneNumber), stdin);
  replace->phoneNumber[strcspn(replace->phoneNumber, "\n")] = '\0';

  FILE *add_contact;
  add_contact = fopen("contact.txt", "a");
  if(add_contact == NULL)
  {
    puts("Error opening file");
    return 1;
  }
  fprintf("Name: %s\nPhone Number: %s\n\n", name, phoneNumber);
  fclose(add_contact);
  puts("File saved successfully");
    printf("Would you like to continue? Y[es] or N[o]: ");
    scanf(" %c", &symbol);
    if(!(symbol == 'Y' || symbol == 'y'))
    {
      break;
    }
  }
  return 0;
}


int deletefile(Contact *replace)
{
  if(remove(contact.txt) == 0)
  {
    puts("File removed successfully");
  }

  else
  {
    puts("Error removing file");
  }
  return 0;
}
