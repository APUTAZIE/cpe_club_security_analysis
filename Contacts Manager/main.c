#include "contact.h"
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>

int main(void)
{
  Contact credel; //Contact is the data type, credel means create and delete
  int option = 0;
  char symbol2 = '\0';
  while(true)
    {
    puts("");
    printsmenu();
    puts("");
    printf("Enter the number of your choice: ");
    scanf("%d", &option);
    (void)getchar();

    switch(option)
      {
        case 1:
          puts("");
          addContact(&credel);
        break;
        
        case 2:
          puts("");
          puts("Deleting....");
          sleep(2);
          deletefile(&credel);
        break;
        
        case 3:
          puts("");
        return 1;
        
        default:
          puts("");
          puts("Invalid option");
      }
       puts("");
       printf("would you like back to menu? Y[es] or N[o]: ");
       scanf(" %c", &symbol2);
       if(!(symbol2 == 'Y' || symbol2 == 'y'))
       {
         break;
       }
  }

  return 0;
}
