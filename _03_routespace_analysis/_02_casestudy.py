from tqdm import tqdm
import networkx as nx

from utils import pickle_loader, run_or_get_pickle
from _01_motifs import match_all, edge_matcher

def casestudy_motif_frequs(topology, spmode, xlist, max_len_sorted_motifs):
    # 1. identify largest x
    largest_x = max(xlist)
    # 2. load motifs
    unique_id = f"{topology}_{spmode}_{str(largest_x)}"
    pickle_path_motifs = f"./data/03_motifs/{unique_id}_identify_motifs.dill"
    motifs_by_original_length_dict = pickle_loader(pickle_path_motifs)
    print(f"{unique_id}: 1. Motifs loaded.")

    motifs_list = []
    for edge_set_length, motifs in motifs_by_original_length_dict.items():
        motifs_list.extend([motif for _, motif in motifs.items()])

    # 3. get frequencies of motifs
    abs_visits = [len(motif["visits"]) for motif in motifs_list]
    total_visits = sum(abs_visits)
    rel_visits = [visits / total_visits for visits in abs_visits]

    # 4. sort motifs by decreasing number of visits
    sorted_maxx_motif_pairs = sorted(zip(motifs_list, rel_visits), key=lambda pair: pair[1], reverse=True)

    # Extract the sorted motifs from the pairs
    sorted_maxx_motifs, sorted_rel_visits = zip(*sorted_maxx_motif_pairs)

    # 5. shorten list of motifs to max_len_sorted_motifs
    # correct for cases in which there are less motifs than max_len_sorted_motifs
    max_len_sorted_motifs = min(max_len_sorted_motifs, len(motifs_list))
    sorted_maxx_motifs = sorted_maxx_motifs[:max_len_sorted_motifs]
    sorted_rel_visits = sorted_rel_visits[:max_len_sorted_motifs]

    # 2. get frequencies of these motifs for all x
    motiffrequencydict = {str(largest_x): sorted_rel_visits}

    # find values for all other x
    xlist.remove(largest_x)
    for x in xlist:
        unique_id = f"{topology}_{spmode}_{str(x)}"
        pickle_path_motifs = f"./data/03_motifs/{unique_id}_identify_motifs.dill"
        motifs_by_original_length_dict = pickle_loader(pickle_path_motifs)
        print(f"{unique_id}: 1. Motifs loaded.")

        motifs_list = []
        for edge_set_length, motifs in motifs_by_original_length_dict.items():
            motifs_list.extend([motif for _, motif in motifs.items()])

        abs_visits = [len(motif["visits"]) for motif in motifs_list]
        total_visits = sum(abs_visits)

        # we have to check whether the motifs are isomorphic to the ones from the largest x ...
        rel_visits = []
        for maxx_motif in tqdm(sorted_maxx_motifs, desc="Processing Max-x Motifs"):
            len_maxx_motif_edge_set = len(maxx_motif["sets"][0])
            if len_maxx_motif_edge_set in motifs_by_original_length_dict.keys():
                for motif_data in motifs_by_original_length_dict[len_maxx_motif_edge_set].values():
                    if nx.is_isomorphic(maxx_motif["graph"], motif_data["graph"], node_match=match_all,
                                        edge_match=edge_matcher):
                        rel_visits.append(len(motif_data["visits"]) / total_visits)
                        break
                else:
                    print("Motif not found!")
                    rel_visits.append(0)
            else:
                print("Motif not found!")
                rel_visits.append(0)

        motiffrequencydict[str(x)] = rel_visits
    return sorted_maxx_motifs, motiffrequencydict

def case_study_motif_frequencies_wrapped(topology, spmode, xlist, max_len_sorted_motifs):
    unique_id = f"{topology}_{spmode}_{str(sum(xlist))}"
    wrapped_function = run_or_get_pickle(unique_id, "03_casestudy")(casestudy_motif_frequs)
    return wrapped_function(topology, spmode, xlist, max_len_sorted_motifs)

# ####
from utils import casestudy_params
for topology, xlist in casestudy_params["topologies"].items():
    spmode = "all_volume_info"
    max_len_sorted_motifs = casestudy_params["max_len_sorted_motifs"]
    case_study_motif_frequencies_wrapped(topology, spmode, xlist, max_len_sorted_motifs)
