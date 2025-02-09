import numpy as np
import pandas as pd
from ast import literal_eval
from collections import defaultdict
import os
from datetime import datetime

class CollaborationNetwork:
    def __init__(self):
        """Initialize empty network"""
        self.actor_to_idx = {}  
        self.idx_to_actor = {}  
        self.adj_matrix = None  
        self.next_idx = 0       
    
    def add_actor(self, actor):
        """Add new actor to the network if not exists"""
        if actor not in self.actor_to_idx:
            self.actor_to_idx[actor] = self.next_idx
            self.idx_to_actor[self.next_idx] = actor
            self.next_idx += 1
            
            if self.adj_matrix is not None:
                new_size = len(self.actor_to_idx)
                new_matrix = np.zeros((new_size, new_size), dtype=int)
                if self.adj_matrix.size > 0:
                    new_matrix[:-1, :-1] = self.adj_matrix
                self.adj_matrix = new_matrix
            else:
                self.adj_matrix = np.zeros((1, 1), dtype=int)
    
    def add_collaboration(self, actor1, actor2):
        """Add or increment collaboration between two actors"""
        self.add_actor(actor1)
        self.add_actor(actor2)
        
        idx1 = self.actor_to_idx[actor1]
        idx2 = self.actor_to_idx[actor2]
        
        self.adj_matrix[idx1, idx2] += 1
        self.adj_matrix[idx2, idx1] += 1
    
    def process_movie(self, actors):
        """Process all collaborations in a movie"""
        if not isinstance(actors, list):
            print('actors are not in a list')
            return
            
        for i in range(len(actors)):
            for j in range(i + 1, len(actors)):
                actor1 = str(actors[i]).strip()
                actor2 = str(actors[j]).strip()
                self.add_collaboration(actor1, actor2)
    
    # def get_metrics(self):
    #     """Calculate network metrics"""
    #     n_actors = len(self.actor_to_idx)
    #     if n_actors == 0:
    #         return {
    #             'num_nodes': 0,
    #             'num_edges': 0,
    #             'avg_degree': 0,
    #             'density': 0
    #         }
        
    #     # Number of edges (sum of upper triangle since matrix is symmetric)
    #     num_edges = np.sum(np.triu(self.adj_matrix > 0, k=1))
        
    #     # Average degree
    #     degrees = np.sum(self.adj_matrix > 0, axis=1)
    #     avg_degree = np.mean(degrees)
        
    #     # Density
    #     density = (2 * num_edges) / (n_actors * (n_actors - 1)) if n_actors > 1 else 0
        
    #     return {
    #         'num_nodes': n_actors,
    #         'num_edges': num_edges,
    #         'avg_degree': avg_degree,
    #         'density': density
    #     }

def load_and_preprocess_data(base_file_path, snapshot_file_path):
    """Load and preprocess the datasets"""
    base_df = pd.read_csv(base_file_path, sep='\t')
    base_df['actors'] = base_df['actors'].apply(lambda x: str(x).split(','))
    
    snapshot_df = pd.read_csv(snapshot_file_path, sep='\t')
    snapshot_df['actors'] = snapshot_df['actors'].apply(lambda x: str(x).split(','))
    snapshot_df['year'] = pd.to_datetime(snapshot_df['release_date']).dt.year
    
    print(f"Base dataset: {len(base_df)} movies")
    print(f"Snapshot dataset: {len(snapshot_df)} movies")
    
    return base_df, snapshot_df

def save_network(network, filename):
    """Save network to files"""
    os.makedirs('network_data', exist_ok=True)
    
    np.save(f'network_data/{filename}_adj.npy', network.adj_matrix)
    
    actor_mappings = {
        'actor_to_idx': network.actor_to_idx,
        'idx_to_actor': network.idx_to_actor
    }
    np.save(f'network_data/{filename}_mappings.npy', actor_mappings)

def load_network(filename):
    """Load network from files"""
    network = CollaborationNetwork()
    
    network.adj_matrix = np.load(f'network_data/{filename}_adj.npy')
    
    mappings = np.load(f'network_data/{filename}_mappings.npy', allow_pickle=True).item()
    network.actor_to_idx = mappings['actor_to_idx']
    network.idx_to_actor = mappings['idx_to_actor']
    network.next_idx = len(network.actor_to_idx)
    
    return network

def build_base_network(df):
    """Build initial collaboration network"""
    network = CollaborationNetwork()
    
    for _, row in df.iterrows():
        network.process_movie(row['actors'])
    
    return network

def build_snapshot_networks(base_network, snapshot_df, start_year=2000, end_year=2024):
    """Build yearly snapshot networks"""
    snapshots = {}
    current_network = CollaborationNetwork()
    current_network.actor_to_idx = base_network.actor_to_idx.copy()
    current_network.idx_to_actor = base_network.idx_to_actor.copy()
    current_network.adj_matrix = base_network.adj_matrix.copy()
    current_network.next_idx = base_network.next_idx
    
    save_network(base_network, 'base_network')
    print("Saved base network")
    
    for year in range(start_year, end_year + 1):
        year_data = snapshot_df[snapshot_df['year'] == year]
        print(f"\nProcessing year {year}")
        print(f"Number of movies in {year}: {len(year_data)}")
        
        for _, row in year_data.iterrows():
            current_network.process_movie(row['actors'])
        
        snapshots[year] = CollaborationNetwork()
        snapshots[year].actor_to_idx = current_network.actor_to_idx.copy()
        snapshots[year].idx_to_actor = current_network.idx_to_actor.copy()
        snapshots[year].adj_matrix = current_network.adj_matrix.copy()
        snapshots[year].next_idx = current_network.next_idx
        
        save_network(snapshots[year], f'snapshot_{year}')
        
        metrics = snapshots[year].get_metrics()
        print(f"Year {year} statistics:")
        print(f"Nodes = {metrics['num_nodes']}")
        print(f"Edges = {metrics['num_edges']}")
        
    return snapshots

def main():
    print("Loading and preprocessing data...")
    base_df, snapshot_df = load_and_preprocess_data(
        'additional_movies_actors.tsv',
        'filtered_final_movies_3.tsv'
    )
    
    print("\nBuilding base network...")
    base_network = build_base_network(base_df)

    # new_base_network= load_network("snapshot_2016")
    
    print("\nBuilding and saving snapshot networks...")
    snapshots = build_snapshot_networks(base_network, snapshot_df, start_year=2017, end_year=2024)
    
    return base_network, snapshots

if __name__ == "__main__":
    base_network, snapshots = main()