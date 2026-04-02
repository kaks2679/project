"""
src.models.clustering
======================
KMeans-based county development clustering for Kenya.
Author: Stephen Muema
"""

import pandas as pd
import numpy as np
from sklearn.cluster      import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings("ignore")

CLUSTER_NAMES = {
    0: "Tier 1: Developed",
    1: "Tier 2: Emerging",
    2: "Tier 3: Developing",
    3: "Tier 4: Vulnerable",
    4: "Tier 5: Marginalised",
}


class CountyClustering:
    """KMeans clustering of Kenya counties into development tiers."""

    FEATURES = ["Poverty_Rate", "Unemployment_Rate", "Mobile_Penetration",
                "Electricity_Access", "HDI_Score"]

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters   = n_clusters
        self.random_state = random_state
        self.scaler       = StandardScaler()
        self.model        = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20)
        self._fitted      = False

    def fit_predict(self, county_df: pd.DataFrame) -> pd.DataFrame:
        df = county_df.copy()
        X  = df[self.FEATURES].fillna(df[self.FEATURES].mean())
        Xs = self.scaler.fit_transform(X)

        labels = self.model.fit_predict(Xs)
        df["Cluster_Raw"] = labels

        # Re-label by ascending poverty (0 = lowest poverty)
        cluster_pov = df.groupby("Cluster_Raw")["Poverty_Rate"].mean().sort_values()
        rank_map = {old: new for new, old in enumerate(cluster_pov.index)}
        df["Cluster"] = df["Cluster_Raw"].map(rank_map)

        tier_labels = {
            0: "🌿 Emerging (Low Poverty)",
            1: "📈 Developing",
            2: "⚡ Transitioning",
            3: "⚠️ Vulnerable",
            4: "🔴 Critical Need",
        }
        df["Cluster_Label"] = df["Cluster"].map(tier_labels)
        self._fitted = True
        return df.drop(columns=["Cluster_Raw"])

    def elbow_inertias(self, county_df: pd.DataFrame, k_range=range(2, 10)) -> dict:
        """Return inertia for each k (for elbow chart)."""
        X  = county_df[self.FEATURES].fillna(county_df[self.FEATURES].mean())
        Xs = StandardScaler().fit_transform(X)
        return {
            k: KMeans(n_clusters=k, random_state=self.random_state, n_init=10).fit(Xs).inertia_
            for k in k_range
        }

    def pca_2d(self, county_df: pd.DataFrame) -> pd.DataFrame:
        """Return 2D PCA projection of county features."""
        X  = county_df[self.FEATURES].fillna(county_df[self.FEATURES].mean())
        Xs = StandardScaler().fit_transform(X)
        pca = PCA(n_components=2)
        coords = pca.fit_transform(Xs)
        return pd.DataFrame({
            "PC1": coords[:, 0], "PC2": coords[:, 1],
            "County": county_df["County"].values,
            "Cluster_Label": county_df.get("Cluster_Label", ["Unknown"] * len(county_df)),
            "Poverty_Rate": county_df["Poverty_Rate"].values,
        })
