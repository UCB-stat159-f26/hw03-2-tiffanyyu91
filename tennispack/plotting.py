
import matplotlib.pyplot as plt


def plot_player_matches(df):
    """Plot player age against opponent age difference."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for result, color in [("W", "blue"), ("L", "orange")]:
        matches = df[df["result"] == result]
        ax.scatter(
            matches["player_age"],
            matches["age_difference"],
            color=color,
            label="Win" if result == "W" else "Loss",
            alpha=0.5,
            s=20
        )

    ax.axhline(0, color="gray", linestyle="--")
    ax.set_xlabel("Player Age")
    ax.set_ylabel("Player Age - Opponent Age")
    ax.set_title("Career Match Age Differences")
    ax.legend()

    return ax
