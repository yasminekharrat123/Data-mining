import numpy as np
import pandas as pd
import os

class CollaborationNetwork:
    def __init__(self):
        """Initialize empty network"""
        self.actor_to_idx = {}  
        self.idx_to_actor = {}  
        self.adj_matrix = None  
        self.next_idx = 0       
    
    def load_network(self, filename):
        """Load network from files"""
        self.adj_matrix = np.load(f'network_data/{filename}_adj.npy')
        
        mappings = np.load(f'network_data/{filename}_mappings.npy', allow_pickle=True).item()
        self.actor_to_idx = mappings['actor_to_idx']
        self.idx_to_actor = mappings['idx_to_actor']
        self.next_idx = len(self.actor_to_idx)

def calculate_average_degree(network, actors):
    """Calculate average degree of a list of actors in the given network."""
    sum_degrees = 0
    num_actors = len(actors)
    if num_actors == 0:
        return 0.0
    
    for actor in actors:
        if actor in network.actor_to_idx:
            idx = network.actor_to_idx[actor]
            # Degree is the number of unique collaborators (non-zero entries)
            degree = np.count_nonzero(network.adj_matrix[idx])
        else:
            degree = 0
        sum_degrees += degree
    
    return sum_degrees / num_actors


def calculate_network_heterogeneity(network, actors):
    """Calculate network heterogeneity (average cosine similarity) for a movie's actors."""
    num_actors = len(actors)
    not_found_count = 0  # Track actors not found in the network

    if num_actors < 2:
        print("Not enough actors to compute similarity. Returning 0.0.")
        return 0.0, not_found_count  # Not enough actors to compute similarity

    # Get the collaboration vectors for the actors in the movie
    collaboration_vectors = []
    for actor in actors:
        if actor in network.actor_to_idx:
            idx = network.actor_to_idx[actor]
            collaboration_vectors.append(network.adj_matrix[idx])
        else:
            # If an actor is not in the network, use a zero vector
            collaboration_vectors.append(np.zeros(network.adj_matrix.shape[0]))
            not_found_count += 1  # Increment not-found count

    collaboration_vectors = np.array(collaboration_vectors)

    # Compute cosine similarity for all pairs of actors
    total_similarity = 0.0
    num_pairs = 0

    for i in range(num_actors - 1):
        for j in range(i + 1, num_actors):
            # Dot product of the two vectors
            dot_product = np.dot(collaboration_vectors[i], collaboration_vectors[j])

            # Magnitude (Euclidean norm) of the two vectors
            magnitude_i = np.linalg.norm(collaboration_vectors[i])
            magnitude_j = np.linalg.norm(collaboration_vectors[j])

            # Avoid division by zero
            if magnitude_i == 0 or magnitude_j == 0:
                cosine_similarity = 0.0
            else:
                cosine_similarity = dot_product / (magnitude_i * magnitude_j)

            total_similarity += cosine_similarity
            num_pairs += 1

    # Average cosine similarity
    if num_pairs == 0:
        return 0.0, not_found_count

    result = total_similarity / num_pairs
    return result, not_found_count

def load_and_preprocess_data(snapshot_file_path):
    """Load and preprocess the snapshot dataset."""
    print(f"Loading dataset from file: {snapshot_file_path}")

    snapshot_df = pd.read_csv(snapshot_file_path, sep='\t')
    print(f"Loaded dataset with {len(snapshot_df)} rows.")

    print("Processing actors column.")
    snapshot_df['actors'] = snapshot_df['actors'].apply(lambda x: str(x).split(','))
    print("Actors column processed.")

    print(f"Snapshot dataset: {len(snapshot_df)} movies")
    return snapshot_df


def calculate_movie_features(snapshot_df, start_year=2000, end_year=2024):
    """Calculate features for each movie in the snapshot dataframe."""
    features = []
    
    for year in range(start_year, end_year + 1):
        print(f"\nProcessing year {year}")
        network = CollaborationNetwork()

        # Load the network for the previous year
        if year == start_year:
            network.load_network('base_network')
        else:
            network.load_network(f'snapshot_{year - 1}')
        
        # Filter movies for the current year
        year_data = snapshot_df[snapshot_df['startYear'] == year]
        print(f"Number of movies in {year}: {len(year_data)}")
        
        for _, row in year_data.iterrows():
            movie_id = row['tconst']  # Adjust column name as per your dataset
            actors = row['actors']
            
            # Calculate features
            avg_degree = calculate_average_degree(network, actors)
            heterogeneity, heterogeneity_not_found = calculate_network_heterogeneity(network, actors)
            
            features.append({
                'movie_id': movie_id,
                'year': year,
                'average_degree': avg_degree,
                'network_heterogeneity': heterogeneity,
                'not_found': heterogeneity_not_found
            })
    
    return pd.DataFrame(features)

def main():
    print("Loading and preprocessing data...")
    snapshot_df = load_and_preprocess_data('filtered_final_movies_3.tsv')
    
    print("\nCalculating movie features...")
    features_df = calculate_movie_features(snapshot_df, start_year=2000, end_year=2024)
    
    features_df.to_csv('movie_network_features.tsv', sep='\t', index=False)
    print("\nFeatures saved to output/movie_network_features.tsv")

if __name__ == "__main__":
    main()