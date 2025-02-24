import torch 
import torch.nn as nn
import torch.nn.init as init
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class VAE_enhanced(nn.Module):
    """
    Enhanced Variational Autoencoder (VAE):
    This class implements an enhanced version of the Variational Autoencoder (VAE) with 
    batch normalization, dropout regularization, and the option to switch between 
    batch normalization and layer normalization layers (commented out in the current implementation).
    The VAE consists of an encoder that maps the input data to a latent space, 
    a reparameterization step that introduces stochasticity, and a decoder 
    that reconstructs the input data from the latent space.

    Attributes:
    -----------
    encoder - A sequence of fully connected layers with Batch Normalization and ReLU activations, 
    used to map the input data to a hidden representation. Optional Dropout layers are commented out.

    mean_layer - A fully connected layer that maps the hidden representation to the mean of the latent distribution.
    
    logvar_layer - A fully connected layer that maps the hidden representation to the logarithm of the variance 
    of the latent distribution.

    decoder - A sequence of fully connected layers with Batch Normalization, ReLU activations, and Dropout layers, 
    used to reconstruct the input data from the latent space. The final layer uses Sigmoid activation 
    to output data in the range [0, 1].

    Methods:
    --------
    encode(x) - Encodes the input `x` into its latent representation by passing it through the encoder 
    and outputting the mean and log-variance of the latent distribution.
    
    reparameterization(mean, logvar) - Performs the reparameterization trick, where random noise is sampled 
    and combined with the mean and log-variance to generate a latent vector `z`.

    decode(z) - Decodes the latent vector `z` back into the reconstructed data `x_hat`.

    forward(x) - The forward pass of the VAE. Encodes the input `x` into a latent vector, 
    applies the reparameterization trick, and decodes the latent vector back into 
    a reconstruction of the input. Returns the reconstructed data, mean, and log-variance.

    _initialize_weights() - Initializes the weights of the linear layers using Xavier uniform initialization, 
    and sets the biases to zero where applicable.

    Parameters:
    -----------
    input_dim - Dimensionality of the input data (number of features).
    
    hidden_dim - Dimensionality of the hidden layers used in the encoder and decoder.
    
    latent_dim - Dimensionality of the latent space (size of the encoded representation).

    Enhancements:
    -------------
    - Batch Normalization: Applied after each fully connected layer to stabilize and accelerate training.
    - Dropout: Commented out in the encoder, applied in the decoder to prevent overfitting, with a dropout probability of 0.1.
    - Layer Normalization: Commented-out option for layer normalization instead of batch normalization.
    
    """

    def __init__(self, input_dim, hidden_dim, latent_dim):
        super(VAE_enhanced, self).__init__()

        # self.encoder = nn.Sequential(
        #     nn.Linear(input_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU(),
        #     nn.Linear(hidden_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU(),
        #     nn.Linear(hidden_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU()
        # )
        # self.mean_layer = nn.Linear(hidden_dim, latent_dim)
        # self.logvar_layer = nn.Linear(hidden_dim, latent_dim)

        # self.decoder = nn.Sequential(
        #     nn.Linear(latent_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU(),
        #     nn.Linear(hidden_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU(),
        #     nn.Linear(hidden_dim, hidden_dim),
        #     nn.LayerNorm(hidden_dim),
        #     nn.ReLU(),
        #     nn.Linear(hidden_dim, input_dim),
        #     nn.Sigmoid()
        # )

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            # nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            # nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            # nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, hidden_dim), 
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            # nn.Dropout(p=0.2)
        )
        self.mean_layer = nn.Linear(hidden_dim, latent_dim)
        self.logvar_layer = nn.Linear(hidden_dim, latent_dim)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),  
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )

        self._initialize_weights()
     
    def encode(self, x):
        h = self.encoder(x)
        mean, logvar = self.mean_layer(h), self.logvar_layer(h)
        return mean, logvar

    def reparameterization(self, mean, logvar):
        std = torch.exp(0.5 * logvar)
        epsilon = torch.randn_like(std)
        z = mean + std * epsilon
        return z

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mean, logvar = self.encode(x)
        z = self.reparameterization(mean, logvar)
        x_hat = self.decode(z)
        return x_hat, mean, logvar

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)