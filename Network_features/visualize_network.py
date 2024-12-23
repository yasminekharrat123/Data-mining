import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
from dataclasses import dataclass
import numba
from numpy.typing import NDArray
import pandas as pd

@dataclass
class NetworkNode:
    position: np.ndarray
    displacement: np.ndarray
    degree: int
    
class OptimizedNetworkVisualizer:
    def __init__(self, adj_matrix: np.ndarray, idx_to_actor: Dict[int, str]):
        self.adj_matrix = adj_matrix
        self.idx_to_actor = idx_to_actor
        self.positions = None
        
    @staticmethod
    @numba.jit(nopython=True)
    def _calculate_forces(positions: NDArray, adj_matrix: NDArray, k: float, t: float) -> NDArray:
        """Calculate forces using Numba for acceleration"""
        n_nodes = len(positions)
        displacement = np.zeros_like(positions)
        
        # Repulsive forces - vectorized
        for i in range(n_nodes):
            delta = positions[i] - positions
            dist = np.maximum(0.01, np.sqrt(np.sum(delta * delta, axis=1)))
            dist[i] = 1.0  # Avoid division by zero
            force = (k * k) / dist[:, np.newaxis]
            displacement[i] += np.sum(delta * force / dist[:, np.newaxis], axis=0)
            
        # Attractive forces - only for connected nodes
        edges = np.nonzero(adj_matrix)
        for i, j in zip(edges[0], edges[1]):
            if i < j:  # Avoid double counting
                delta = positions[i] - positions[j]
                dist = max(0.01, np.sqrt(np.sum(delta * delta)))
                force = (dist * dist) / k
                displacement[i] -= (delta / dist) * force
                displacement[j] += (delta / dist) * force
                
        return displacement

    def force_directed_layout(self, iterations: int = 50) -> Dict[int, Tuple[float, float]]:
        """Optimized Fruchterman-Reingold layout algorithm"""
        n_nodes = self.adj_matrix.shape[0]
        k = 1.0 / np.sqrt(n_nodes)
        
        # Initialize positions as numpy array for vectorization
        positions = np.random.uniform(-1, 1, (n_nodes, 2))
        
        # Pre-calculate node degrees
        degrees = np.sum(self.adj_matrix, axis=1)
        
        t = 1.0
        dt = 0.95
        
        for _ in range(iterations):
            # Calculate all forces at once using numba-accelerated function
            displacement = self._calculate_forces(positions, self.adj_matrix, k, t)
            
            # Update positions - vectorized
            displacement_length = np.maximum(0.01, np.sqrt(np.sum(displacement * displacement, axis=1)))
            displacement = displacement / displacement_length[:, np.newaxis]
            delta = np.minimum(displacement_length, t)[:, np.newaxis] * displacement
            positions += delta
            
            # Bound positions - vectorized
            positions = np.clip(positions, -1.0, 1.0)
            t *= dt
        
        # Convert to dictionary format for compatibility
        self.positions = {i: tuple(pos) for i, pos in enumerate(positions)}
        return self.positions

    def get_largest_component(self, max_nodes: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get largest connected component efficiently"""
        sparse_matrix = csr_matrix(self.adj_matrix)
        _, labels = connected_components(sparse_matrix, directed=False)
        
        # Find largest component nodes
        unique_labels, counts = np.unique(labels, return_counts=True)
        largest_component = unique_labels[np.argmax(counts)]
        component_nodes = np.where(labels == largest_component)[0]
        
        if len(component_nodes) > max_nodes:
            # Use vectorized operations for degree calculation
            degrees = np.sum(self.adj_matrix[component_nodes][:, component_nodes], axis=1)
            component_nodes = component_nodes[np.argsort(degrees)[-max_nodes:]]
            
        return component_nodes, self.adj_matrix[np.ix_(component_nodes, component_nodes)]

    def visualize_network(self, min_weight: int = 1, max_nodes: int = 50) -> plt.Figure:
        """Optimized network visualization"""
        component_nodes, sub_matrix = self.get_largest_component(max_nodes)
        
        # Calculate layout once
        self.force_directed_layout()
        
        fig, ax = plt.subplots(figsize=(15, 15))
        
        # Pre-calculate edge properties for efficient plotting
        edges = np.nonzero(sub_matrix)
        weights = sub_matrix[edges]
        mask = weights >= min_weight
        edges = (edges[0][mask], edges[1][mask])
        weights = weights[mask]
        
        # Draw edges efficiently
        for i, j, weight in zip(edges[0], edges[1], weights):
            if i < j:  # Avoid double counting
                start = self.positions[i]
                end = self.positions[j]
                width = np.log1p(weight) * 0.7
                alpha = min(0.8, 0.2 + np.log1p(weight) * 0.1)
                ax.plot([start[0], end[0]], [start[1], end[1]], 
                       color='gray', linewidth=width, alpha=alpha)
                
                if weight > min_weight:
                    ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2,
                           str(weight), fontsize=8,
                           bbox=dict(facecolor='white', alpha=0.7))
        
        # Draw nodes efficiently
        node_positions = np.array([self.positions[i] for i in range(len(component_nodes))])
        ax.scatter(node_positions[:, 0], node_positions[:, 1], c='black', s=100)
        
        # Add labels
        for i, pos in enumerate(node_positions):
            ax.text(pos[0], pos[1] + 0.05, self.idx_to_actor[component_nodes[i]],
                   fontsize=8, ha='center', va='bottom',
                   bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        
        ax.set_title(f'Actor Collaboration Network\n(Showing {len(component_nodes)} most connected nodes)',
                    pad=20)
        ax.axis('off')
        plt.tight_layout()
        return plt


def replace_nconst_with_primary_name_and_update_idx(mappings_file, actors_file):
    # Load the mappings
    mappings = np.load(mappings_file, allow_pickle=True).item()
    actor_to_idx = mappings.get("actor_to_idx", {})
    idx_to_actor = mappings.get("idx_to_actor", {})

    # Load the TSV file into a pandas DataFrame
    actors_df = pd.read_csv(actors_file, sep='\t')

    # Create a dictionary for nconst to primaryName mapping
    nconst_to_name = dict(zip(actors_df["nconst"], actors_df["primaryName"]))

    # Replace nconst in actor_to_idx with primaryName
    updated_actor_to_idx = {
        nconst_to_name.get(nconst, nconst): idx
        for nconst, idx in actor_to_idx.items()
    }

    # Update idx_to_actor to use primaryName instead of nconst
    updated_idx_to_actor = {
        idx: nconst_to_name.get(nconst, nconst)
        for idx, nconst in idx_to_actor.items()
    }

    # Update the mappings dictionary
    mappings["actor_to_idx"] = updated_actor_to_idx
    mappings["idx_to_actor"] = updated_idx_to_actor

    return mappings


def load_and_visualize_snapshot(year: int, min_weight: int = 1, max_nodes: int = 50) -> None:
    """Load and visualize network snapshot efficiently"""
    # Use memory-mapped arrays for large files
    adj_matrix = np.load(f'network_data/snapshot_{year}_adj.npy', mmap_mode='r')
    # mappings = np.load(f'network_data/snapshot_{year}_mappings.npy', allow_pickle=True).item()
    mappings_file = f'network_data/snapshot_{year}_mappings.npy'  # Replace {year} with the actual year
    actors_file = 'final_actors_3_bf.tsv'
    mappings = replace_nconst_with_primary_name_and_update_idx(mappings_file, actors_file)

    visualizer = OptimizedNetworkVisualizer(adj_matrix, mappings['idx_to_actor'])
    plt = visualizer.visualize_network(min_weight=min_weight, max_nodes=max_nodes)
    plt.savefig(f'network_viz/network_snapshot_{year}.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    load_and_visualize_snapshot(year=2024, min_weight=1, max_nodes=50)