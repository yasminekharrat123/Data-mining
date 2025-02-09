import numpy as np
import pandas as pd
import os

class ActorDirectorCollaborationNetwork:
    def __init__(self):
        self.actor_to_idx = {}
        self.director_to_idx = {}
        self.idx_to_actor = {}
        self.idx_to_director = {}
        self.adj_matrix = None  # Adjacency matrix (actors x directors)
        self.next_actor_idx = 0
        self.next_director_idx = 0    

def load_network(filename):
    """Load network from files"""
    network = ActorDirectorCollaborationNetwork()
    
    network.adj_matrix = np.load(f'network_data_directors/{filename}_adj.npy')
    
    mappings = np.load(f'network_data_directors/{filename}_mappings.npy', allow_pickle=True).item()
    network.actor_to_idx = mappings['actor_to_idx']
    network.director_to_idx = mappings['director_to_idx']
    network.idx_to_actor = mappings['idx_to_actor']
    network.idx_to_director = mappings['idx_to_director']
    network.next_actor_idx = len(network.actor_to_idx)
    network.next_director_idx = len(network.director_to_idx)
    
    return network

def calculate_average_degree(network, actors):
    """Calculate average degree of a list of actors."""
    sum_degrees = 0
    num_actors = len(actors)
    if num_actors == 0:
        return 0.0
    
    for actor in actors:
        if actor in network.actor_to_idx:
            idx = network.actor_to_idx[actor]
            degree = np.count_nonzero(network.adj_matrix[idx])
        else:
            degree = 0
        sum_degrees += degree
    
    return sum_degrees / num_actors

def calculate_network_heterogeneity(network, actors):
    """Calculate network heterogeneity (average cosine similarity) for a movie's actors."""
    num_actors = len(actors)
    not_found_count = 0

    if num_actors < 2:
        return 0.0, not_found_count

    collaboration_vectors = []
    for actor in actors:
        if actor in network.actor_to_idx:
            idx = network.actor_to_idx[actor]
            collaboration_vectors.append(network.adj_matrix[idx])
        else:
            # Use zero vector with length equal to number of directors
            collaboration_vectors.append(np.zeros(network.adj_matrix.shape[1]))
            not_found_count += 1

    collaboration_vectors = np.array(collaboration_vectors)
    total_similarity = 0.0
    num_pairs = 0

    for i in range(num_actors - 1):
        for j in range(i + 1, num_actors):
            dot_product = np.dot(collaboration_vectors[i], collaboration_vectors[j])
            magnitude_i = np.linalg.norm(collaboration_vectors[i])
            magnitude_j = np.linalg.norm(collaboration_vectors[j])

            if magnitude_i == 0 or magnitude_j == 0:
                cosine_similarity = 0.0
            else:
                cosine_similarity = dot_product / (magnitude_i * magnitude_j)

            total_similarity += cosine_similarity
            num_pairs += 1

    if num_pairs == 0:
        return 0.0, not_found_count

    return total_similarity / num_pairs, not_found_count

def load_and_preprocess_data(snapshot_file_path):
    """Load and preprocess the snapshot dataset."""
    snapshot_df = pd.read_csv(snapshot_file_path, sep='\t')
    snapshot_df['actors'] = snapshot_df['actors'].apply(lambda x: str(x).split(','))
    return snapshot_df

def calculate_movie_features(snapshot_df, start_year=2000, end_year=2024):
    """Calculate features for each movie in the snapshot dataframe."""
    features = []
    
    for year in range(start_year, end_year + 1):
        print(f"\nProcessing year {year}")
        
        # Load the network for the previous year
        if year == start_year:
            network = load_network('base_network')
        else:
            network = load_network(f'snapshot_{year - 1}')
        
        year_data = snapshot_df[snapshot_df['startYear'] == year]
        print(f"Number of movies in {year}: {len(year_data)}")
        
        for _, row in year_data.iterrows():
            movie_id = row['tconst']
            actors = row['actors']
            
            avg_degree = calculate_average_degree(network, actors)
            heterogeneity, not_found = calculate_network_heterogeneity(network, actors)
            
            features.append({
                'movie_id': movie_id,
                'year': year,
                'average_degree': avg_degree,
                'network_heterogeneity': heterogeneity,
                'not_found': not_found
            })
    
    return pd.DataFrame(features)

def main():
    print("Loading and preprocessing data...")
    snapshot_df = load_and_preprocess_data('filtered_final_movies_5.tsv')
    
    print("\nCalculating movie features...")
    features_df = calculate_movie_features(snapshot_df, start_year=2000, end_year=2024)
    
    features_df.to_csv('movie_actors_directors_network_features.tsv', sep='\t', index=False)
    print("\nFeatures saved to movie_network_features.tsv")

if __name__ == "__main__":
    main()