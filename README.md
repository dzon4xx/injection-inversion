Wyobraź sobie, że dostajesz zadanie.

Napisz aplikację, która zautomatyzuje proces wdrażania do firmy nowych pracowników.

Wymagania:
* Interfejs aplikacji to CLI
* Aplikacja na wejściu otrzymuje: 
  * imię i nazwisko pracownika
  * Odpowiednie dane dostępowe do systemów zewnętrznych
  * Domeny firmy.
* Aplikacja zakłada konta dla pracownika w serwisach:
  * Gmail w formacie: <imię.nazwisko@domena> wszystko lowercase
  * Jira w formacie użytkownik <imie.n> z mailem
  * Slack w formacie użytkownik: <imie.nazwisko> z mailem z kroku poprzedniego
* Aplikacja przerywa swoje działanie, jeśli nie udało się założyć maila. Jest on wymagany w kolejnych krokach
* Aplikacja kontynuuje swoje działanie, jeśli nie udało się założyć konta w pozostałych serwisach.
* Aplikacja raportuje efekt swojego działania wyświetlając komunikat o pomyślnym wdrożeniu pracownika, lub raport o błędach wdrożenia (niepomyślne kroki i niewykonane kroki)