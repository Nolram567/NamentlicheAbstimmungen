import os
import random
import pandas as pd
import networkx as nx
from networkx import Graph


def deserialize(lp: int) -> list:
    """
    Diese Funktion lädt alle Abstimmungen einer Legislaturperiode in einen individuellen pandas.Dataframe und fügt sie
    einer Liste an. Die Abstimmungen liegen als .xls oder .xlsx vor. Der Dataframe hat die folgende Struktur:

    Wahlperiode	Sitzungnr	Abstimmnr	Fraktion/Gruppe	  Name	       Vorname	Titel  ja	nein Enthaltung	ungültig  nichtabgegeben	Bezeichnung	     Bemerkung
    20	            3	        1	          Fraktion	  Mustermann	Max		 Dr.    1	0	     0	        0	         0	         Max Mustermann	 Lorem Ipsum

    :param lp: Die Legislaturperiode, deren namentliche Abstimmungen geladen werden sollen.
    :return: Eine Liste mit pandas.Dataframe, die jeweils eine namentliche Abstimmung enthalten.
    """
    dfs = []
    folder_path = f"Abstimmungen/LP{lp}"

    for file in os.listdir(folder_path):
        if file.endswith('.xls') or file.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path)
            dfs.append(df)

    return dfs

def append_edges(node_list: list, G: Graph) -> None:
    """
    Diese Funktion fügt zwischen allen Knoten, die in node_list übergeben werden, entweder eine Kante im Graphen G hinzu,
    sofern noch keine Kante existiert, oder inkrementiert das Kantengewicht, sofern eine Kante existiert.

    :param node_list: Die Knotenliste.
    :param G: Der Graph, der erweitert wird.
    :return: None
    """

    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            node1 = node_list[i]
            node2 = node_list[j]

            if G.has_edge(node1, node2):
                G[node1][node2]['weight'] += 1
            else:
                G.add_edge(node1, node2, weight=1)

def generate_network(dfl) -> Graph:
    """
    Mit dieser Funktion wird ein Abstimmungsnetzwerk aus einer List von Dataframes generiert.

    :param dfl: Die List mit pandas.Dataframes, generiert von deserialize().
    :return: Das Abstimmungsnetzwerk als networkx.Graph.
    """

    '''
        Alle Einzelabstimmungen, welche in Dataframes gespeichert sind, werden zu einer Abstimmung zusammengefasst, damit
        wir dem Graphen, den wir mit dem Bezeichner G1 instanziieren, für jede einzigartige Fraktion, ein Knoten hinzugefügt
        werden kann.
    '''

    combined_df = pd.concat(dfl, ignore_index=True)
    G = nx.Graph()
    unique_fraktionen = combined_df['Fraktion/Gruppe'].unique()
    # unique_fraktionen = [e for e in unique_fraktionen if e not in ["DIE LINKE.", "Fraktionslos", "BSW"]]
    G.add_nodes_from(unique_fraktionen)

    '''
    Wir iterieren über alle Einzelabstimmungen und fügen genau dann eine Kante zwischen Fraktionen hinzu, wenn sie bei 
    einer Abstimmung die gleiche Entscheidung für 'ja' oder 'nein' getroffen haben. Haben die Fraktionen bereits zuvor 
    diesselbe Entscheidung getroffen, wird das Kantengewicht ihrer Kante inkrementiert.
    '''
    for df in dfl:

        unique_fraktionen = df['Fraktion/Gruppe'].unique()
        # unique_fraktionen = [e for e in unique_fraktionen if e not in ["DIE LINKE.", "Fraktionslos", "BSW"]]
        voted_1 = []
        voted_0 = []

        '''
        Wir behandeln frei Fälle: Die Fraktion stimmt mehrheitlich 'Ja', die Fraktion stimmt mehrheitlich 'Nein' oder 
        die Fraktion enthält sich mehrheitlich.
        '''
        for fraktion in unique_fraktionen:
            if df.loc[df['Fraktion/Gruppe'] == fraktion, 'ja'].mean() > 0.5:
                voted_1.append(fraktion)
            elif df.loc[df['Fraktion/Gruppe'] == fraktion, 'Enthaltung'].mean() > 0.5:
                continue
            else:
                voted_0.append(fraktion)

        append_edges(voted_1, G)
        append_edges(voted_0, G)

    return G

def generate_random_network(s: int, n: int) -> Graph:
    """
    Diese Funktion generiert ein zufälliges Abstimmungsnetzwerk, d. h. alle abstimmenden Fraktionen entscheiden willkürlich.

    :param s: Die Zahl der Abstimmungen als Integer
    :param n: Die Zahl der Knoten als Integer.
    :return: Das zufällige Abstimmungsnetzwerk als networkx.Graph.
    """

    G = nx.Graph()
    for i in range(n):
        G.add_node(i)

    for _ in range(s):
        voted_0, voted_1 = [], []

        for x in G.nodes:
            if random.choice([True, False]):
                voted_0.append(x)
            else:
                voted_1.append(x)

        for i in range(len(voted_0)):
            for j in range(i + 1, len(voted_0)):

                node1 = voted_0[i]
                node2 = voted_0[j]

                if G.has_edge(node1, node2):
                    G[node1][node2]['weight'] += 1
                else:
                    G.add_edge(node1, node2, weight=1)

        for i in range(len(voted_1)):
            for j in range(i + 1, len(voted_1)):

                node1 = voted_1[i]
                node2 = voted_1[j]

                if G.has_edge(node1, node2):
                    G[node1][node2]['weight'] += 1
                else:
                    G.add_edge(node1, node2, weight=1)
    return G

def generate_full_network(s: int, n: int) -> Graph:
    '''
    Diese Funktion generiert ein minimal polarisiertes Abstimmungsnetzwerk, d. h. abstimmenden Fraktionen treffen bei
    jeder Abstimmung die gleiche Entscheidung.

    :param s: Die Zahl der Abstimmungen als Integer.
    :param n: Die Zahl der Knoten als Integer.
    :return: Das minimal polarisierte Abstimmungsnetzwerk als networkx.Graph.
    '''
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)

    for _ in range(s):
        voted_0 = []
        [voted_0.append(x) for x in G.nodes]

        for i in range(len(voted_0)):
            for j in range(i + 1, len(voted_0)):

                node1 = voted_0[i]
                node2 = voted_0[j]

                if not G.has_edge(node1, node2):
                    G.add_edge(node1, node2, weight=s)


    return G

def generate_polarized_network(s: int, n: int) -> Graph:
    """
    Diese Funktion generiert ein polarisiertes Abstimmungsnetzwerk mit zwei Communties.

    :param s: Die Zahl der Abstimmungen als Integer.
    :param n: Die Zahl der Knoten als Integer.
    :return: Das polarisierte Abstimmungsnetzwerk als networkx.Graph.
    """

    G = nx.Graph()

    for i in range(n):
        G.add_node(i)


    split = int(round(len(G.nodes)/2))

    voted_0, voted_1 = list(G.nodes)[:split], list(G.nodes)[split:]

    print(voted_0)
    print(voted_1)

    for i in range(len(voted_0)):
        for j in range(i + 1, len(voted_0)):

            node1 = voted_0[i]
            node2 = voted_0[j]

            if not G.has_edge(node1, node2):
                G.add_edge(node1, node2, weight=s)

    for i in range(len(voted_1)):
        for j in range(i + 1, len(voted_1)):

            node1 = voted_1[i]
            node2 = voted_1[j]

            if not G.has_edge(node1, node2):
                G.add_edge(node1, node2, weight=s)

    return G

def calculate_weighted_modularity(G: Graph, communities: list, weight='weight') -> float:
    """
    Die Berechnung der Modularität einer Partitionierung eines gewichteten Graphen nach Newman.

    :param G: Der gewichtete networkx.Graph.
    :param communities: Die Einteilung in Communities als Liste von Listen.
    :param weight: Das verwendete Label für Gewicht im Graphen.
    :return: Die Modularität als float.
    """

    # Berechnung der Gesamtsumme der Kantenwichte
    m = 0
    for e in G.edges(data=True):
        m += e[2]['weight']

    # Zuordnung von jedem Knoten zu seiner Community
    node_to_community = {node: i for i, community in enumerate(communities) for node in community}

    # Initialisierung der Modularität
    Qw = 0
    # Iteration über alle Knotenpaare
    for i in G.nodes():
        for j in G.nodes():
            if i == j:
                continue
            if node_to_community[i] == node_to_community[j]:  # Nur wenn beide Knoten in der gleichen Community sind
                w_ij = G[i][j][weight] if G.has_edge(i, j) else 0
                s_i = sum(G[i][k][weight] for k in G[i])
                s_j = sum(G[j][k][weight] for k in G[j])
                Qw += (w_ij - s_i * s_j / (2 * m))

    # Teilen durch 2m, um die Modularität zu erhalten
    return Qw / (2 * m)