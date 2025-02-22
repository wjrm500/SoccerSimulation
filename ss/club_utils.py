import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def show_club_positions(club, gameweek=None):
    fig = plt.figure()
    fig.add_subplot(111)
    league = club.league
    tables = league.league_tables
    # Rank positions
    ranked_tables = []
    for gw, table in tables.items():
        if gameweek is not None and gw > gameweek:
            break
        ranked_table = []
        table_items = list(table.items())
        table_items.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)
        for i, table_item in enumerate(table_items, 1):
            table_item[1]["Rank"] = i
            ranked_table.append(table_item)
        ranked_tables.append(ranked_table)
    ranks = []
    for ranked_table in ranked_tables[1:]:
        for table_club, table_data in ranked_table:
            if club == table_club:
                ranks.append(table_data["Rank"])
    x = list(range(1, len(ranks) + 1))
    y = ranks
    for i in range(len(league.clubs) + 1):
        plt.gca().axhline(i, color="#bbbbbb", linestyle="--", linewidth=0.75)
    for i in range(len(ranked_tables)):
        if i % 5 == 0:
            plt.gca().axvline(i, color="#bbbbbb", linestyle="--", linewidth=0.75)
    plt.plot(x, y, "-bo")
    plt.xticks(x)
    plt.xlabel("Gameweek", fontsize=12, fontweight="bold", labelpad=8)
    plt.ylabel("League position", fontsize=12, fontweight="bold", labelpad=8)
    plt.xlim(1)
    plt.ylim([0, len(league.clubs) + 1])
    plt.gca().invert_yaxis()
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig
