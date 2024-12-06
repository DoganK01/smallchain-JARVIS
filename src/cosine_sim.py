import torch

def cosine_similarity(vector1, vector2):
    """
    Compute the cosine similarity between two vectors using PyTorch.
    
    Args:
        vector1 (torch.Tensor): First vector.
        vector2 (torch.Tensor): Second vector.
    
    Returns:
        float: Cosine similarity between vector1 and vector2.
    
    Raises:
        ValueError: If inputs are not vectors, dimensions mismatch, or vectors have zero magnitude.
    """
    if not isinstance(vector1, torch.Tensor) or not isinstance(vector2, torch.Tensor):
        raise ValueError("Both inputs must be PyTorch tensors.")
    
    if vector1.ndimension() > 1 or vector2.ndimension() > 1:
        raise ValueError("Inputs must be 1-dimensional vectors. Got shapes: "
                         f"{vector1.shape}, {vector2.shape}")
    
    if vector1.shape != vector2.shape:
        raise ValueError(f"Vectors must have the same dimensions. Got shapes: {vector1.shape}, {vector2.shape}")
    
    # ensure the vectors are not empty
    if vector1.numel() == 0 or vector2.numel() == 0:
        raise ValueError("Vectors must not be empty.")
    
    dot_product = torch.dot(vector1, vector2)
    
    # compute the magnitudes (norms) of the vectors
    magnitude1 = torch.norm(vector1)
    magnitude2 = torch.norm(vector2)
    
    if magnitude1.item() == 0 or magnitude2.item() == 0:
        raise ValueError("One of the vectors has zero magnitude, cannot compute cosine similarity.")
    
    cosine_sim = dot_product / (magnitude1 * magnitude2)
    
    return cosine_sim.item()


if __name__ == "__main__":
    vec1 = torch.tensor([1.0, 2.0, 3.0])
    vec2 = torch.tensor([4.0, 5.0, 6.0])
    try:
        cosine_sim = cosine_similarity(vec1, vec2)
        print(f"Cosine Similarity: {cosine_sim}")
    except ValueError as e:
        print(f"Error: {e}")
