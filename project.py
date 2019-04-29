import numpy as np

OVERHEADS = 100000


def model(horizon, avg_working_time, avg_repair_time, machines, tool_packages, setup):
    # setup - układ liniowy "L" lub gniazdowy "G"
    total_cost = 0
    horizon = horizon * 24 * 60  # horyzont działania w minutach
    events = list(np.random.exponential(avg_working_time, machines))  # wektor zdarzeń, który zmienia stan symulacji
    status = ["W"] * machines  # status - określa aktualny stan maszyny
    t_start = [0] * machines  # t_start - określa początek bezczynności maszyny
    t_cum = [0] * machines  # t_cum - skumulowany czas bezczynności maszyny
    tools_loc = [-1] * tool_packages  # tools_loc lokalizacja narzedzi - albo numer maszyny albo -1 czyli warsztat
    tools_occupied = [0] * tool_packages  # tools_occupied czas zajecia zestawu przez naprawianą maszynę
    t = min(events)  # zegar symulacji- najblizsze zadanie, które ma być wykonane

    # rozpoczynamy symulacje "skacząc" po kolejnych zdarzeniach
    while t <= horizon:

        # jeżeli zestawy nie są aktualnie zajęte to przenosimy je z powrotem do warsztatu
        for i in range(tool_packages):
            if tools_occupied[i] <= t:  # jezeli czas zajecia narzedzi jest mniejszy niz czas symulacji, to
                tools_loc[i] = -1  # wtedy dane narzedzia sa na warsztacie

        # wybieramy maszynę, której dotyczy zdarzenie
        machine = events.index(t)

        """
        Gdy maszyna, której dotyczy zdarzenie ma status "W(orking) - pracuje":
            - to najpierw zaktualizuj wektor t_start dla tej maszyny jako początek jej bezczynności = t.
            - następnie sprawdź czy dostępny jest jakiś zestaw naprawczy. Jezeli nie:
                - to ustaw status maszyny na "Q(queue) - czeka na narzędzia" 
                - zaktualizuj wektor events podajac mu najkrótszy czas oczekiwania na wolny zestaw.
              Jeżeli tak:
                - ustaw status maszyny na "R(eady) - jest naprawiona"
                - wyznacz czas  potrzebny na naprawę maszyny w zależności od ukladu taśmociągu 
                (czas transportu + czas naprawy)
                - ustaw koniec naprawy jako zdarzenie dla danej maszyny
                - zaktualizuj wektor tools_loc dla odpowiedniego zestawu podając numer maszyny, którą on obsługuje
                - zaktualizuj wektor tools_occupied czasem jaki mu to zajmie (2* transport + naprawa)
        """
        if status[machine] == "W":  # maszyna pracuje
            t_start[machine] = t
            tools = - 1  # przypisujemy wartość -1, ponieważ symulujemy, że maszyna się zepsuła
            total_cost += 1
            for i in range(machine):  # iterujemy przez wszystkie maszyny i przypisujemy
                if tools_loc[i] == -1:  # danej maszynie odpowiadający jej zestaw narzędzi
                    tools = i
                    break  # wychodzimy z petli po przypisaniu narzedzi do danej maszyny
            if tools == -1:  # szukamy maszyny, ktora ma przestoj
                status[machine] = "Q"  # zmieniamy status maszyny na Q - czeka na narzedzia
                events[machine] = min(tools_occupied)  # najkrotszy czas oczekiwania
            else:
                status[machine] = "R"  # jezeli maszyna pracuje to wybierz typ maszyny i okresl czas transportu
                if setup == "L":
                    transport_time = 2 * (1 + machine)
                elif setup == "G":
                    transport_time = 3
                else:
                    print("Niepoprawny układ! Należy wybrać układ 'L' lub 'G'!")
                    break
                repair_time = np.random.gamma(3, avg_repair_time / 3)  # probkuj czas naprawy
                events[machine] += repair_time + transport_time  # dodaj czas naprawy i czas transportu per maszyna
                tools_loc[tools] = machine  # zapisz lokalizacje narzedzi (przy ktorej sa maszynie)
                tools_occupied[tools] += repair_time + 2 * transport_time  # okresl ile dane narzedzia beda zajete

                """
                Gdy maszyna ma status "Q":
                    - wybierz dostępny zestaw naprawczy
                    - ustal status maszyny na "R"
                    - zaktualizuj wektor tools_loc lokalizacją narzedzi i tools_occupied 
                    czasem jaki zajmie ich transport (w dwie strony) i naprawa maszyny
                    -zaktualizuj wektor zdarzeń czasem potrzebnym na naprawę maszyny i transport narzedzi
                """

        elif status[machine] == "Q":
            for i in range(tool_packages):
                if tools_loc[i] == -1:
                    tools = i
                    break
            status[machine] = "R"
            if setup == "L":
                transport_time = 2 * (1 + machine)
            elif setup == "G":
                transport_time = 3
            else:
                print("zly uklad - moze byc L lub G!")
                break
            repair_time = np.random.gamma(3, avg_repair_time / 3)
            events[machine] += repair_time + transport_time
            tools_loc[tools] = machine
            tools_occupied[tools] += repair_time + 2 * transport_time
            """
            Gdy maszyna ma status "R":
                - ustal jej status na "W"
                - wyznacz czas kolejnej awarii i zaktualizuj wektor events
                - wylicz czas bezczynnosci i uzupelnij o niego liste t_cum
            """

        else:
            status[machine] = "W"
            events[machine] += np.random.exponential(avg_working_time)
            t_cum[machine] += t - t_start[machine]

        # ustalamy nowe t
        t = min(events)  # wartosci w zmiennej "t" to inaczej czasy

    # wynik - liste skumulowanych bezczynnosci dla kazdej z maszyn
    return t_cum, total_cost


def run_simulation(iterations, horizon, avg_working_time, avg_repair_time, tool_packages, machines, setup):
    avg_t_cum = []
    total_cost = []
    for i in range(iterations):
        run, tot_cost = model(horizon, avg_working_time, avg_repair_time, tool_packages, machines, setup)
        avg_t_cum.append(run)
        total_cost.append(tot_cost)
    return list(map(np.mean, np.transpose(avg_t_cum))), list(map(np.sum, total_cost))


avg_t_time, total_cost = run_simulation(iterations=3,
                                        horizon=50,
                                        avg_working_time=75,
                                        avg_repair_time=15,
                                        tool_packages=6,
                                        machines=6,
                                        setup="L")
print(avg_t_time)
print(total_cost)  # wyliczyc koszt calkowity jaki generuje zarowno maszyna typu liniowego oraz gwiazdowego
