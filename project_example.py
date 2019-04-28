import numpy as np

# liczba maszyn
n = 6
# średni czas pracy bez usterki
avg_working_time = 75  # minut
# średni czas naprawy
avg_repair_time = 15  # minut
# ilość zestawów narzędzi
m = 6
# horyzont analizy
horizon = 30  # dni
# liczba uruchomień symulacji
iterations = 10


def model(horizon, avg_working_time, avg_repair_time, n, m, setup):
    # setup - układ liniowy "L" lub gniazdowy "G"

    # horyzont działania w minutach
    horizon = horizon * 24 * 60

    # wektor zdarzeń, który zmienia stan symulacji
    events = list(np.random.exponential(avg_working_time, n))

    # status - określa aktualny stan maszyny
    status = ["W"] * n

    # t_start - określa początek bezczynności maszyny
    t_start = [0] * n

    # t_cum - skumulowany czas bezczynności maszyny
    t_cum = [0] * n

    # tools_loc lokalizacja narzedzi - albo numer maszyny albo -1 czyli warsztat
    tools_loc = [-1] * m

    # tools_occupied czas zajecia zestawu przez naprawianą maszynę
    tools_occupied = [0] * m

    # zegar symulacji- najblizsze zadanie, które ma być wykonane
    t = min(events)

    # rozpoczynamy symulacje "skacząc" po kolejnych zdarzeniach
    while t <= horizon:

        # jeżeli zestawy nie są aktualnie zajęte to przenosimy je z powrotem do warsztatu
        for i in range(m):
            if tools_occupied[i] <= t:
                tools_loc[i] = -1

        # wybieramy maszynę, której dotyczy zdarzenie
        machine = events.index(t)

        """
        Gdy maszyna, której dotyczy zdarzenie ma status "W":
            - to najpierw zaktualizuj wektor t_start dla tej maszyny jako początek jej bezczynności = t.
            - następnie sprawdź czy dostępny jest jakiś zestaw naprawczy. Jezeli nie:
                - to ustaw status maszyny na "Q" 
                - zaktualizuj wektor events podajac mu najkrótszy czas oczekiwania na wolny zestaw.
              Jeżeli tak:
                - ustaw status maszyny na "R"
                - wyznacz czas  potrzebny na naprawę maszyny w zależności od ukladu taśmociągu 
                (czas transportu + czas naprawy)
                - ustaw koniec naprawy jako zdarzenie dla danej maszyny
                - zaktualizuj wektor tools_loc dla odpowiedniego zestawu podając numer maszyny, którą on obsługuje
                - zaktualizuj wektor tools_occupied czasem jaki mu to zajmie (2* transport + naprawa)
        """
        if status[machine] == "W":
            t_start[machine] = t
            tools = - 1
            for i in range(m):
                if tools_loc[i] == -1:
                    tools = i
                    break
            if tools == -1:
                status[machine] = "Q"
                events[machine] = min(tools_occupied)
            else:
                status[machine] = "R"
                if setup == "L":
                    transport_time = 2 * (1 + machine)
                elif setup == "G":
                    transport_time = 3
                else:
                    print("Niepoprawny układ! Należy wybrać układ 'L' lub 'G'!")
                    break
                repair_time = np.random.gamma(3, avg_repair_time / 3)
                events[machine] += repair_time + transport_time
                tools_loc[tools] = machine
                tools_occupied[tools] += repair_time + 2 * transport_time

                """
                Gdy maszyna ma status "Q":
                    - wybierz dostępny zestaw naprawczy
                    - ustal status maszyny na "R"
                    - zaktualizuj wektor tools_loc lokalizacją narzedzi i tools_occupied 
                    czasem jaki zajmie ich transport (w dwie strony) i naprawa maszyny
                    -zaktualizuj wektor zdarzeń czasem potrzebnym na naprawę maszyny i transport narzedzi
                """

        elif status[machine] == "Q":
            for i in range(m):
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
        t = min(events)

    # wynik - liste skumulowanych bezczynnosci dla kazdej z maszyn
    return t_cum


def run_model(iterations, horizon, avg_working_time, avg_repair_time, n, m, setup):
    avg_t_cum = []
    for i in range (iterations):
        avg_t_cum.append(model( horizon, avg_working_time, avg_repair_time, n, m, setup))
    return list(map(np.mean, np.transpose(avg_t_cum)))


run_model(iterations, horizon, avg_working_time, avg_repair_time, n, m, "L")
