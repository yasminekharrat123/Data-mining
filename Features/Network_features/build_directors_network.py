import numpy as np
import pandas as pd
from collections import defaultdict
import os
from datetime import datetime

class ActorDirectorCollaborationNetwork:
    def __init__(self):
        """Initialize empty network"""
        self.actor_to_idx = {}  # Maps actor names to indices
        self.director_to_idx = {}  # Maps director IDs to indices
        self.idx_to_actor = {}  # Maps indices to actor names
        self.idx_to_director = {}  # Maps indices to director IDs
        self.adj_matrix = None  # Adjacency matrix (actors x directors)
        self.next_actor_idx = 0  # Next index for actors
        self.next_director_idx = 0  # Next index for directors
    
    def add_actor(self, actor):
        """Add a new actor to the network if not exists"""
        if actor not in self.actor_to_idx:
            self.actor_to_idx[actor] = self.next_actor_idx
            self.idx_to_actor[self.next_actor_idx] = actor
            self.next_actor_idx += 1
            
            # Resize adjacency matrix if necessary
            if self.adj_matrix is not None:
                new_rows = self.next_actor_idx
                new_cols = self.next_director_idx
                new_matrix = np.zeros((new_rows, new_cols), dtype=int)
                if self.adj_matrix.size > 0:
                    new_matrix[:-1, :] = self.adj_matrix
                self.adj_matrix = new_matrix
            else:
                self.adj_matrix = np.zeros((1, 1), dtype=int)
    
    def add_director(self, director):
        """Add a new director to the network if not exists"""
        if director not in self.director_to_idx:
            self.director_to_idx[director] = self.next_director_idx
            self.idx_to_director[self.next_director_idx] = director
            self.next_director_idx += 1
            
            # Resize adjacency matrix if necessary
            if self.adj_matrix is not None:
                new_rows = self.next_actor_idx
                new_cols = self.next_director_idx
                new_matrix = np.zeros((new_rows, new_cols), dtype=int)
                if self.adj_matrix.size > 0:
                    new_matrix[:, :-1] = self.adj_matrix
                self.adj_matrix = new_matrix
            else:
                self.adj_matrix = np.zeros((1, 1), dtype=int)
    
    def add_collaboration(self, actor, director):
        """Add or increment collaboration between an actor and a director"""
        self.add_actor(actor)
        self.add_director(director)
        
        actor_idx = self.actor_to_idx[actor]
        director_idx = self.director_to_idx[director]
        
        self.adj_matrix[actor_idx, director_idx] += 1
    
    def process_movie(self, actors, directors):
        """Process all actor-director collaborations in a movie"""
        if not isinstance(actors, list) or not isinstance(directors, list):
            print('Actors or directors are not in a list')
            return
            
        for actor in actors:
            actor = str(actor).strip()
            for director in directors:
                director = str(director).strip()
                self.add_collaboration(actor, director)
    
    # def get_metrics(self):
    #     """Calculate network metrics"""
    #     n_actors = len(self.actor_to_idx)
    #     n_directors = len(self.director_to_idx)
        
    #     if n_actors == 0 or n_directors == 0:
    #         return {
    #             'num_actors': n_actors,
    #             'num_directors': n_directors,
    #             'num_collaborations': 0,
    #             'density': 0
    #         }
        
    #     # Number of collaborations (non-zero entries in the adjacency matrix)
    #     num_collaborations = np.sum(self.adj_matrix > 0)
        
    #     # Density (actual collaborations / possible collaborations)
    #     density = num_collaborations / (n_actors * n_directors) if (n_actors * n_directors) > 0 else 0
        
    #     return {
    #         'num_actors': n_actors,
    #         'num_directors': n_directors,
    #         'num_collaborations': num_collaborations,
    #         'density': density
    #     }

def load_and_preprocess_data(base_file_path, snapshot_file_path):
    """Load and preprocess the datasets"""
    base_df = pd.read_csv(base_file_path, sep='\t')
    base_df['actors'] = base_df['actors'].apply(lambda x: str(x).split(','))
    base_df['directors'] = base_df['directors'].apply(lambda x: str(x).split(','))
    
    snapshot_df = pd.read_csv(snapshot_file_path, sep='\t')
    snapshot_df['actors'] = snapshot_df['actors'].apply(lambda x: str(x).split(','))
    snapshot_df['directors'] = snapshot_df['directors'].apply(lambda x: str(x).split(','))
    snapshot_df['year'] = pd.to_datetime(snapshot_df['release_date']).dt.year
    
    print(f"Base dataset: {len(base_df)} movies")
    print(f"Snapshot dataset: {len(snapshot_df)} movies")
    
    return base_df, snapshot_df

def save_network(network, filename):
    """Save network to files"""
    os.makedirs('network_data_directors', exist_ok=True)
    
    np.save(f'network_data_directors/{filename}_adj.npy', network.adj_matrix)
    
    mappings = {
        'actor_to_idx': network.actor_to_idx,
        'director_to_idx': network.director_to_idx,
        'idx_to_actor': network.idx_to_actor,
        'idx_to_director': network.idx_to_director
    }
    np.save(f'network_data_directors/{filename}_mappings.npy', mappings)

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

def build_base_network(df):
    """Build initial actor-director collaboration network"""
    network = ActorDirectorCollaborationNetwork()
    
    for _, row in df.iterrows():
        network.process_movie(row['actors'], row['directors'])
    
    return network

def build_snapshot_networks(base_network, snapshot_df, start_year=2000, end_year=2024):
    """Build yearly snapshot networks"""
    snapshots = {}
    current_network = ActorDirectorCollaborationNetwork()
    current_network.actor_to_idx = base_network.actor_to_idx.copy()
    current_network.director_to_idx = base_network.director_to_idx.copy()
    current_network.idx_to_actor = base_network.idx_to_actor.copy()
    current_network.idx_to_director = base_network.idx_to_director.copy()
    current_network.adj_matrix = base_network.adj_matrix.copy()
    current_network.next_actor_idx = base_network.next_actor_idx
    current_network.next_director_idx = base_network.next_director_idx
    
    save_network(base_network, 'base_network')
    print("Saved base network")
    
    for year in range(start_year, end_year + 1):
        year_data = snapshot_df[snapshot_df['year'] == year]
        print(f"\nProcessing year {year}")
        print(f"Number of movies in {year}: {len(year_data)}")
        
        for _, row in year_data.iterrows():
            current_network.process_movie(row['actors'], row['directors'])
        
        snapshots[year] = ActorDirectorCollaborationNetwork()
        snapshots[year].actor_to_idx = current_network.actor_to_idx.copy()
        snapshots[year].director_to_idx = current_network.director_to_idx.copy()
        snapshots[year].idx_to_actor = current_network.idx_to_actor.copy()
        snapshots[year].idx_to_director = current_network.idx_to_director.copy()
        snapshots[year].adj_matrix = current_network.adj_matrix.copy()
        snapshots[year].next_actor_idx = current_network.next_actor_idx
        snapshots[year].next_director_idx = current_network.next_director_idx
        
        save_network(snapshots[year], f'snapshot_{year}')
        
        # metrics = snapshots[year].get_metrics()
        # print(f"Year {year} statistics:")
        # print(f"Actors = {metrics['num_actors']}")
        # print(f"Directors = {metrics['num_directors']}")
        # print(f"Collaborations = {metrics['num_collaborations']}")
        
    return snapshots

def main():
    print("Loading and preprocessing data...")
    base_df, snapshot_df = load_and_preprocess_data(
        'add_movies_actors_5_directors.tsv',
        'filtered_final_movies_5.tsv'
    )
    
    # print("\nBuilding base network...")
    # base_network = build_base_network(base_df)

    new_base_network= load_network("snapshot_2021")

    print("\nBuilding and saving snapshot networks...")
    snapshots = build_snapshot_networks(new_base_network, snapshot_df, start_year=2022, end_year=2024)
    
    return base_network, snapshots

if __name__ == "__main__":
    base_network, snapshots = main()