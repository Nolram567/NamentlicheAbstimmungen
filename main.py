import namentlicheAbstimmungen as na
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain

if __name__ == '__main__':

    '''
    Wir laden alle Abstimmungen der 20. Legislaturperiode.
    '''
    dfs20 = na.deserialize(20)
    #dfs19 = na.deserialize(19)
    #dfs18 = na.deserialize(18)

    '''
    Wir generieren das Abstimmungsnetzwerk für die 18., 19., und 20. Legislaturperiode.
    '''
    G1 = na.generate_network(dfs20)
    # G2 = na.generate_network(dfs19)
    # G3 = na.generate_network(dfs18)

    '''
    Wir drucken die Kantenliste mit den entsprechenden Gewichten.
    '''

    print(G1.edges(data=True))
    # print(G2.edges(data=True))
    # print(G3.edges(data=True))

    '''
    Die Daten werden bereinigt, in dem Knoten entfernt werden, die wegen fehlerhafter Benennungen entstanden oder
    anderer Gründe entstanden sind, um die Berechnung der Communities und der Modularität nicht zu verzerren.
    '''

    G1.remove_node("BSW")
    G1.remove_node("Fraktionslos")
    G1.remove_node("Die Linke")
    # G2.remove_node('Fraktionslos')
    # G3.remove_node("Fraktionslos")
    # G3.remove_node("fraktionslos")
    # G3.remove_node("BÜNDNIS`90/DIE GRÜNEN")
    # G3.remove_node("DIE LINKE")

    '''Wir nutzen die Louvain-Methode, um die Community-Partitionierung von G1 zu eruieren, bei der die Modularität
    maximal ist.
    '''
    partition = community_louvain.best_partition(G1, weight='weight')


    '''
    Wir drucken die Communityzugehörigkeit der Knoten.
    '''
    for node, community in partition.items():
        print(f"Knoten {node} ist in der Community {community}")

    '''
    1) Wir berechnen das Netzwerklayout nach dem Spring-Embedding-Algorithmus ('pos')
    2) Wir färben die Knoten nach Communityzugehörigkeit ein und vergeben Labels.
    3) Wir fügen die Kantengewichte hinzu
    4) Wir visualieren das Netzwerk und lassen es ausgeben.
    '''
    pos = nx.spring_layout(G1)
    colors = ['black', 'darkred']

    nx.draw_networkx_nodes(G1, pos, partition.keys(), node_size=1,
                           node_color=[colors[community] if community < 2 else 'gray' for community in
                                       partition.values()])

    nx.draw_networkx_edges(G1, pos, alpha=0.5)

    for node, community in partition.items():
        nx.draw_networkx_labels(G1, pos, labels={node: node}, font_color=colors[community])

    edge_labels = nx.get_edge_attributes(G1, 'weight')
    nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)

    plt.show()

    '''
    #Wir berechnen die gewichtete Modularität der Netzwerke; zusätzlich finden sich hier die Kantenlisten der Abstimmungs-
    netzwerke. 
    '''
    print(na.calculate_weighted_modularity(G1, [{'SPD', 'FDP', 'BÜ90/GR'}, {'DIE LINKE.', 'AfD', 'CDU/CSU'}]))
    #print(na.calculate_weighted_modularity(G2, [{'SPD', 'CDU/CSU'}, {'BÜ90/GR', 'DIE LINKE.', 'AfD', 'FDP'}]))
    #print(na.calculate_weighted_modularity(G3, [{'SPD', 'CDU/CSU'}, {'BÜ90/GR', 'DIE LINKE.'}]))

    '''
     
    LP20 (G1): 0.243;
    [('SPD', 'BÜ90/GR', {'weight': 129}), ('SPD', 'FDP', {'weight': 127}), ('SPD', 'AfD', {'weight': 22}),
    ('SPD', 'DIE LINKE.', {'weight': 39}), ('SPD', 'CDU/CSU', {'weight': 60}), ('CDU/CSU', 'AfD', {'weight': 62}),
    ('CDU/CSU', 'BÜ90/GR', {'weight': 60}), ('CDU/CSU', 'FDP', {'weight': 60}),
    ('CDU/CSU', 'DIE LINKE.', {'weight': 40}), ('BÜ90/GR', 'FDP', {'weight': 127}),
    ('BÜ90/GR', 'AfD', {'weight': 22}), ('BÜ90/GR', 'DIE LINKE.', {'weight': 39}),
    ('FDP', 'AfD', {'weight': 22}), ('FDP', 'DIE LINKE.', {'weight': 39}), ('AfD', 'DIE LINKE.', {'weight': 52})]
    
    LP19 (G2): 0.174;
    [('CDU/CSU', 'SPD', {'weight': 242}), ('CDU/CSU', 'AfD', {'weight': 72}), ('CDU/CSU', 'FDP', {'weight': 129}),
    ('CDU/CSU', 'BÜ90/GR', {'weight': 112}), ('CDU/CSU', 'DIE LINKE.', {'weight': 76}), ('SPD', 'AfD', {'weight': 74}),
    ('SPD', 'FDP', {'weight': 127}), ('SPD', 'BÜ90/GR', {'weight': 110}), ('SPD', 'DIE LINKE.', {'weight': 74}),
    ('AfD', 'FDP', {'weight': 100}), ('AfD', 'DIE LINKE.', {'weight': 92}), ('AfD', 'BÜ90/GR', {'weight': 64}),
    ('FDP', 'BÜ90/GR', {'weight': 123}), ('FDP', 'DIE LINKE.', {'weight': 101}), 
    ('DIE LINKE.', 'BÜ90/GR',{'weight': 162})]
    
    LP18 (G3): 0.495;
    [('CDU/CSU', 'SPD', {'weight': 209}), ('CDU/CSU', 'BÜ90/GR', {'weight': 44}), ('CDU/CSU', 'DIE LINKE.',
     {'weight': 8}), ('SPD', 'BÜ90/GR', {'weight': 47}), ('SPD', 'DIE LINKE.', {'weight': 11}),
    ('DIE LINKE.', 'BÜ90/GR', {'weight': 123})]
    
    '''

    '''
    In diesem Abschnitt generieren wir zunächst ein zufälliges Abstimmungsnetzwerk. 
    Danach suchen wir Communitys und berechnen die Modularität.
    Wir wiederholen diesen Vorgang 1000-mal und berechnen die mittlere Modularität von zufälligen Abstimmungs-
    netzwerken: 0.14299057816260974
    
    Diese Kennziffer lässt sich zwar berechnen, ist aber eigentlich wenig sinnvoll, da i. d. R. in zufälligen Abstimmungsnetzwerken
    keine Communitys bzw. genau eine Community entsteht.
    
    Die Modularität minimal polarisierter Abstimmungsnetzwerke, bei denen alle Fraktionen stets die gleiche Wahl treffen,
    liegt ebenfalls bei 0.14299057816260974, da auch hier nur genau eine Community besteht.
    '''
    mean_modularity = 0
    for _ in range(1000):
        GR = na.generate_random_network(128, 7)
        #print(GR.edges(data=True))
        partition = community_louvain.best_partition(GR, weight='weight')
        community_list = [[]]
        for node, community in partition.items():
            for i, e in enumerate(community_list):
                if community == i:
                    community_list[i].append(node)
                    continue
                if community+1 > len(community_list):
                    community_list.append([node])

        mean_modularity += na.calculate_weighted_modularity(GR, community_list)

    print(f"Die mittlere Modularität von zufälligen Abstimmungsnetzwerken liegt bei {mean_modularity/1000}")


    '''
    Wir generieren ein maximal polarisiertes Abstimmungsnetzwerk mit 6 Fraktionen und 128 Abstimmungen; sie liegt bei 
    0.6667.
    '''
    G1 = na.generate_polarized_network(128, 6)
    print(G1.edges(data=True))
    partition = community_louvain.best_partition(G1, weight='weight')
    print(na.calculate_weighted_modularity(G1, [[0,1,2],[3,4,5]]))